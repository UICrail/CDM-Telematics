#!/usr/bin/env python3
"""
Generate a self-contained wiki markdown file with embedded or local images.
"""
import argparse
import re
import base64
from pathlib import Path
from urllib.parse import quote, urlparse, unquote
import urllib.request

IGNORE = {"_Sidebar.md", "_Footer.md", "_Header.md", "Home.md"}

ORDER_RE = re.compile(r"^\s*(?P<num>\d{2})\b")
H1_RE = re.compile(r"^\s*#\s+(.*)$", re.MULTILINE)
FENCE_RE = re.compile(r"^(```|~~~)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
MD_IMG_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<url>(?:[^)]|\([^)]*\))+)\)")
HTML_IMG_RE = re.compile(r'<img\b[^>]*\bsrc\s*=\s*"([^"]+)"[^>]*>', re.IGNORECASE)
MD_LINK_RE = re.compile(r"(?<!\!)\[(?P<label>[^\]]+)\]\((?P<target>[^)]+)\)")
SETEXT_RE = re.compile(r"^(?P<title>.+?)\n(?P<underline>=+|-+)\s*$", re.MULTILINE)
ATX_RE = re.compile(r"^(?P<hashes>#{1,6})(?P<sp>\s+)(?P<text>.+?)\s*$")


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def find_first_h1(text: str) -> str | None:
    m = H1_RE.search(text)
    return m.group(1).strip() if m else None


def page_title_from_filename(p: Path) -> str:
    return p.stem.replace("-", " ").replace("_", " ").strip()


def extract_order_and_title(p: Path, text: str):
    clean_stem = strip_numeric_prefix(p.stem)
    title = clean_stem.replace("-", " ").replace("_", " ").strip()
    m = ORDER_RE.match(p.stem)
    return (int(m.group("num")) if m else None), title


def strip_numeric_prefix(s: str) -> str:
    """Remove everything up to and including the first hyphen, then strip leading spaces and hyphens.
    Handles both ASCII hyphen (-) and Unicode HYPHEN (‐, U+2010)."""
    if '-' in s:
        result = s.split('-', 1)[1].lstrip(' -\u2010')
        return result
    return s


def extract_sort_key(stem: str):
    """Extract (2-digit number, optional letter) for sorting."""
    m = re.match(r'^\s*(\d{2})([a-z])?\b', stem, re.IGNORECASE)
    if m:
        num = int(m.group(1))
        letter = (m.group(2) or '').lower()
        return (num, letter)
    return (999, '')


def anchor_slug(t: str) -> str:
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t


def normalize_key(s: str) -> str:
    """Normalize a page identifier for dictionary keys (case/sep tolerant)."""
    s = s.strip().lower()
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s)
    return s


def build_page_keyset(title: str, stem: str):
    """Return a set of normalized keys that may refer to this page."""
    keys = set()
    variants = [
        title,
        strip_numeric_prefix(title),
        stem,
        strip_numeric_prefix(stem),
        stem.replace("-", " ").replace("_", " "),
    ]
    for v in variants:
        keys.add(normalize_key(v))
    return keys


def convert_setext_to_atx(text: str) -> str:
    def repl(m):
        title = m.group("title").strip()
        underline = m.group("underline")
        if underline.startswith("="):
            return f"# {title}\n"
        else:
            return f"## {title}\n"
    return SETEXT_RE.sub(repl, text)


def demote_atx_headings_outside_code(text: str) -> str:
    out_lines, in_code = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line.strip()):
            in_code = not in_code
            out_lines.append(line)
            continue
        if not in_code:
            m = ATX_RE.match(line)
            if m:
                level = len(m.group("hashes"))
                new_level = min(level + 1, 6)
                line = "#" * new_level + m.group("sp") + m.group("text")
        out_lines.append(line)
    return "\n".join(out_lines)


def normalize_heading(page_title: str, content: str) -> str:
    """1) Setext→ATX, 2) demote headings, 3) prepend H1 = page title."""
    c = convert_setext_to_atx(content)
    c = demote_atx_headings_outside_code(c)
    return f"# {page_title}\n\n{c.lstrip()}"


def is_absolute_or_special(url: str) -> bool:
    u = url.strip()
    return (
        u.startswith("http://")
        or u.startswith("https://")
        or u.startswith("data:")
        or u.startswith("mailto:")
        or u.startswith("#")
    )


def github_blob_to_raw(url: str) -> str:
    """Convert GitHub blob URL to raw URL."""
    # Convert /blob/ to /raw/ in GitHub URLs
    if 'github.com' in url and '/blob/' in url:
        return url.replace('/blob/', '/raw/')
    return url


def extract_image_from_html(html_content: bytes, base_url: str) -> str | None:
    """Try to extract actual image URL from HTML page."""
    try:
        html_str = html_content.decode('utf-8', errors='ignore')
        # Look for og:image meta tag (common in GitHub pages)
        match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html_str)
        if match:
            img_url = match.group(1)
            # Convert blob URLs to raw before returning
            return github_blob_to_raw(img_url) if img_url.startswith('http') else img_url
        # Look for img tags
        match = re.search(r'<img[^>]+src="([^"]+)"[^>]*>', html_str)
        if match:
            img_url = match.group(1)
            # Make absolute if relative
            if img_url.startswith('/'):
                parsed = urlparse(base_url)
                img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
            elif not img_url.startswith('http'):
                return None
            # Convert blob URLs to raw before returning
            return github_blob_to_raw(img_url)
    except Exception as e:
        print(f"Warning: Failed to extract image from HTML: {e}")
    return None


def download_image(url: str) -> bytes | None:
    """Download image from URL and return bytes. Handles HTML pages that link to images."""
    try:
        # Follow redirects and get actual content
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        
        with urllib.request.urlopen(request, timeout=10) as response:
            content_type = response.headers.get('Content-Type', '')
            data = response.read()
            
            # Comprehensive HTML detection
            is_html = (
                'text/html' in content_type or
                'application/xhtml' in content_type or
                data.startswith(b'<!DOCTYPE') or
                data.startswith(b'<!doctype') or
                data.startswith(b'<html') or
                data.startswith(b'<HTML') or
                data.startswith(b'<?xml') or
                b'<html' in data[:200].lower() or
                b'<!doctype html' in data[:200].lower()
            )
            
            if is_html:
                print(f"Got HTML page for {url}, attempting to extract image URL...")
                img_url = extract_image_from_html(data, url)
                if img_url:
                    print(f"Found image URL: {img_url}")
                    # Recursively download the actual image (with depth limit)
                    if '_recursion_depth' not in url:
                        return download_image(img_url + '?_recursion_depth=1')
                    else:
                        print(f"Warning: Recursion depth limit reached for {url}")
                        return None
                else:
                    print(f"Warning: Got HTML but couldn't extract image URL for {url}")
                    return None
            
            # Verify content type is an image
            if not content_type.startswith('image/'):
                print(f"Warning: Non-image content type '{content_type}' for {url}")
                print(f"  Content start: {data[:100]}")
                return None
            
            # Verify data looks like an image (starts with common image magic bytes)
            image_signatures = [
                b'\xFF\xD8\xFF',  # JPEG
                b'\x89PNG',  # PNG
                b'GIF87a',  # GIF
                b'GIF89a',  # GIF
                b'<svg',  # SVG
                b'<?xml',  # SVG (with XML declaration)
            ]
            
            if not any(data.startswith(sig) for sig in image_signatures):
                print(f"Warning: Data doesn't start with known image signature for {url}")
                print(f"  First bytes: {data[:20]}")
                return None
                
            return data
    except Exception as e:
        print(f"Warning: Failed to download {url}: {e}")
        return None


def get_image_mime_type(url: str, data: bytes) -> str:
    """Determine MIME type from URL or data."""
    url_lower = url.lower()
    if url_lower.endswith('.png'):
        return 'image/png'
    elif url_lower.endswith('.jpg') or url_lower.endswith('.jpeg'):
        return 'image/jpeg'
    elif url_lower.endswith('.gif'):
        return 'image/gif'
    elif url_lower.endswith('.svg'):
        return 'image/svg+xml'
    elif url_lower.endswith('.webp'):
        return 'image/webp'
    # Default to PNG
    return 'image/png'


def to_raw_wiki_url(repo: str, path_like: str) -> str:
    """Convert wiki path to raw GitHub URL."""
    s = path_like.strip()
    if s.startswith(("'", '"')) and s.endswith(("'", '"')) and len(s) >= 2:
        s = s[1:-1]
        return f"https://raw.githubusercontent.com/{repo}.wiki/HEAD/{quote(s)}"
    parts = s.split(" ", 1)
    url_part = parts[0]
    url_part = url_part.lstrip("./")
    return f"https://raw.githubusercontent.com/{repo}.wiki/HEAD/{quote(url_part)}"


def process_images(text: str, repo: str, embed: bool, images_dir: Path | None, image_cache: dict) -> str:
    """Process markdown and HTML images - either embed as base64 or save to folder."""
    
    def process_img(url: str, alt: str = "") -> str:
        """Process a single image URL."""
        url_clean = url.split(" ", 1)[0].strip(' "\'')
        
        if is_absolute_or_special(url_clean):
            if not url_clean.startswith("http"):
                return url  # Keep data: URIs and anchors as-is
            # Convert GitHub blob URLs to raw URLs
            full_url = github_blob_to_raw(url_clean)
        else:
            full_url = to_raw_wiki_url(repo, url)
        
        # Check cache
        if full_url in image_cache:
            return image_cache[full_url]
        
        # Download image
        img_data = download_image(full_url)
        if not img_data:
            # If it's a blob URL, convert to raw and try again
            if '/blob/' in full_url:
                raw_url = github_blob_to_raw(full_url)
                if raw_url != full_url:
                    print(f"Retrying with raw URL: {raw_url}")
                    img_data = download_image(raw_url)
                    if img_data:
                        full_url = raw_url  # Use raw URL for cache
                    else:
                        # Still failed - keep original URL but warn
                        print(f"ERROR: Failed to download even after converting to raw: {raw_url}")
                        image_cache[full_url] = url
                        return url
            else:
                image_cache[full_url] = url  # Keep original on failure
                return url
        
        if embed:
            # Embed as base64 data URI
            mime_type = get_image_mime_type(full_url, img_data)
            b64_data = base64.b64encode(img_data).decode('ascii')
            new_url = f"data:{mime_type};base64,{b64_data}"
        else:
            # Save to images directory
            if images_dir is None:
                image_cache[full_url] = url
                return url
            
            # Generate filename from URL - decode URL encoding first
            parsed = urlparse(full_url)
            filename = Path(parsed.path).name
            if not filename:
                filename = f"image_{len(image_cache)}.png"
            
            # URL-decode the filename to get actual filename with spaces/special chars
            filename = unquote(filename)
            
            img_path = images_dir / filename
            
            # Only write if file doesn't already exist (avoid duplicates)
            if not img_path.exists():
                img_path.write_bytes(img_data)
            
            # Use actual filename (with spaces) for markdown reference
            # This works with Pandoc/LaTeX and most markdown viewers
            new_url = f"images/{filename}"
        
        image_cache[full_url] = new_url
        return new_url
    
    # Process markdown images
    def repl_md(m):
        alt = m.group("alt")
        url_token = m.group("url").strip()
        new_url = process_img(url_token, alt)
        return f"![{alt}]({new_url})"
    
    text = MD_IMG_RE.sub(repl_md, text)
    
    # Process HTML images
    def repl_html(m):
        full = m.group(0)
        src_url = m.group(1)
        new_url = process_img(src_url)
        return full.replace(f'src="{src_url}"', f'src="{new_url}"')
    
    text = HTML_IMG_RE.sub(repl_html, text)
    
    return text


def collect_pages(wiki_dir: Path):
    for p in sorted(wiki_dir.glob("*.md")):
        if p.name in IGNORE:
            continue
        yield p


def rewrite_wiki_links_to_local(text: str, page_anchor_map: dict) -> str:
    """[[Page]] / [[Page|Text]] -> local anchors if known."""
    def repl(m):
        page = m.group(1).strip()
        label = m.group(2).strip() if m.group(2) else page
        key = normalize_key(page)
        anchor = page_anchor_map.get(key)
        if not anchor:
            key2 = normalize_key(strip_numeric_prefix(page))
            anchor = page_anchor_map.get(key2)
        if anchor:
            return f"[{label}](#{anchor})"
        return m.group(0)
    return WIKI_LINK_RE.sub(repl, text)


def rewrite_md_links_to_local(text: str, page_anchor_map: dict) -> str:
    """Rewrite [label](Target) where Target is a relative reference to another page."""
    def repl(m):
        label = m.group("label")
        target = m.group("target").strip()
        
        if is_absolute_or_special(target):
            return m.group(0)
        
        url_only = target.split(" ", 1)[0]
        url_only = url_only.split("#", 1)[0].split("?", 1)[0]
        name = Path(url_only).name
        if name.lower().endswith(".md"):
            name = name[:-3]
        name = name.replace("-", " ").replace("_", " ").strip()
        
        key = normalize_key(name)
        anchor = page_anchor_map.get(key) or page_anchor_map.get(normalize_key(strip_numeric_prefix(name)))
        if anchor:
            return f"[{label}](#{anchor})"
        return m.group(0)
    return MD_LINK_RE.sub(repl, text)


def main():
    ap = argparse.ArgumentParser(description="Generate self-contained wiki markdown")
    ap.add_argument("--wiki-dir", required=True, help="Wiki directory path")
    ap.add_argument("--out", required=True, help="Output markdown file (base name)")
    ap.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    ap.add_argument("--embed-images", action="store_true",
                    help="Embed images as base64 (default: save to subfolder)")
    ap.add_argument("--timestamp", help="Generation timestamp for version info")
    args = ap.parse_args()
    
    wiki_dir = Path(args.wiki_dir)
    # Adjust output filename based on mode
    base_out = Path(args.out)
    if args.embed_images:
        out_path = base_out.parent / f"{base_out.stem}_embedded{base_out.suffix}"
    else:
        out_path = base_out.parent / f"{base_out.stem}_with_subfolder{base_out.suffix}"
    
    # Setup images directory if not embedding
    images_dir = None
    if not args.embed_images:
        images_dir = out_path.parent / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
    
    image_cache = {}
    
    # First pass: read all pages, compute titles/orders
    pages = []
    for md in collect_pages(wiki_dir):
        raw = read_text(md)
        order, title = extract_order_and_title(md, raw)
        pages.append({
            "path": md,
            "raw": raw,
            "order": 999 if order is None else order,
            "title": title,
            "stem": md.stem,
        })
    
    # Sort by 2-digit number, then optional letter
    pages.sort(key=lambda x: extract_sort_key(x["path"].stem))
    
    # Build anchor map
    page_anchor_map = {}
    for p in pages:
        anchor = anchor_slug(p["title"])
        for k in build_page_keyset(p["title"], p["stem"]):
            page_anchor_map.setdefault(k, anchor)
    
    # Second pass: transform content
    output_sections = []
    
    # TOC with version info
    repo_name = args.repo.split('/')[-1]
    toc = []
    toc.append(f"# {repo_name} compiled wiki pages\n")
    toc.append(f"_Self-contained version with {'embedded' if args.embed_images else 'local'} images_\n")
    
    # Add version preamble if timestamp provided
    if args.timestamp:
        toc.append("\n## Version\n")
        toc.append(f"This document was generated on {args.timestamp}\n")
    
    # Note: Table of Contents is auto-generated by Pandoc using --toc flag
    
    output_sections.append("\n".join(toc))
    
    for p in pages:
        # 1) Rewrite wiki links to local anchors
        t = rewrite_wiki_links_to_local(p["raw"], page_anchor_map)
        # 2) Rewrite standard relative links to local anchors
        t = rewrite_md_links_to_local(t, page_anchor_map)
        # 3) Process images
        t = process_images(t, args.repo, args.embed_images, images_dir, image_cache)
        # 4) Demote headings and add H1 section title
        section = normalize_heading(p["title"], t).rstrip()
        # 5) Add provenance footnote
        url = f"https://github.com/{args.repo}/wiki/{quote(p['path'].stem)}"
        section += f"\n\n<sub>Original page: [{p['path'].name}]({url})</sub>\n"
        output_sections.append("\n---\n" + section)
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(output_sections) + "\n", encoding="utf-8")
    
    print(f"✓ Generated {out_path}")
    if not args.embed_images and images_dir:
        img_count = len(list(images_dir.glob("*")))
        print(f"✓ Downloaded {img_count} images to {images_dir}")


if __name__ == "__main__":
    main()