#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from urllib.parse import quote

IGNORE = {"_Sidebar.md", "_Footer.md", "_Header.md", "Home.md"}

ORDER_RE = re.compile(r"^\s*(?P<num>\d{2})\b")
H1_RE = re.compile(r"^\s*#\s+(.*)$", re.MULTILINE)

# Fences for skipping heading demotion
FENCE_RE = re.compile(r"^(```|~~~)")

# Wiki-style links: [[Page]] or [[Page|Text]]
WIKI_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")

# Inline Markdown images (keeps optional title inside the () token)
MD_IMG_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<url>[^)]+)\)")

# HTML <img ... src="...">
HTML_IMG_RE = re.compile(r'(<img\b[^>]*\bsrc\s*=\s*")[^"]+(")', re.IGNORECASE)

# Standard Markdown links (NOT images): [text](target)
MD_LINK_RE = re.compile(r"(?<!\!)\[(?P<label>[^\]]+)\]\((?P<target>[^)]+)\)")

# Setext headings
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
    # Strip prefix from stem first, then convert to title
    clean_stem = strip_numeric_prefix(p.stem)
    title = clean_stem.replace("-", " ").replace("_", " ").strip()
    # Extract order from original stem
    m = ORDER_RE.match(p.stem)
    return (int(m.group("num")) if m else None), title


def strip_numeric_prefix(s: str) -> str:
    """Remove everything up to and including the first hyphen, then strip leading spaces."""
    if '-' in s:
        return s.split('-', 1)[1].lstrip()
    return s


def extract_sort_key(stem: str):
    """Extract (2-digit number, optional letter) for sorting.
    Examples: '01-Title' -> (1, ''), '01a-Title' -> (1, 'a'), '99b-Title' -> (99, 'b')
    """
    m = re.match(r'^\s*(\d{2})([a-z])?\b', stem, re.IGNORECASE)
    if m:
        num = int(m.group(1))
        letter = (m.group(2) or '').lower()
        return (num, letter)
    return (999, '')  # Default for pages without numeric prefix


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


def to_raw_wiki_url(repo: str, path_like: str) -> str:
    s = path_like.strip()
    if s.startswith(("'", '"')) and s.endswith(("'", '"')) and len(s) >= 2:
        s = s[1:-1]
        return f"https://raw.githubusercontent.com/{repo}.wiki/HEAD/{quote(s)}"
    parts = s.split(" ", 1)
    url_part = parts[0]
    suffix = (" " + parts[1]) if len(parts) > 1 else ""
    url_part = url_part.lstrip("./")
    return f"https://raw.githubusercontent.com/{repo}.wiki/HEAD/{quote(url_part)}{suffix}"


def rewrite_markdown_images(text: str, repo: str) -> str:
    def repl(m):
        alt = m.group("alt")
        url_token = m.group("url").strip()

        # Extract just the actual URL (before optional title)
        url_only = url_token.split(" ", 1)[0].strip(' "\'')

        if is_absolute_or_special(url_only):
            return m.group(0)

        new_url = to_raw_wiki_url(repo, url_token)
        return f"![{alt}]({new_url})"

    return MD_IMG_RE.sub(repl, text)


def rewrite_html_images(text: str, repo: str) -> str:
    def repl(m):
        full = m.group(0)
        m2 = re.search(r'\bsrc\s*=\s*"([^"]+)"', full, flags=re.IGNORECASE)
        if not m2:
            return full
        src_val = m2.group(1)
        if is_absolute_or_special(src_val):
            return full
        new_src = f'https://raw.githubusercontent.com/{repo}.wiki/HEAD/{quote(src_val.lstrip("./"))}'
        return re.sub(r'(\bsrc\s*=\s*")[^"]+(")', r'\1' + new_src + r'\2', full, flags=re.IGNORECASE)
    return HTML_IMG_RE.sub(repl, text)


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
            # also try without numeric prefix
            key2 = normalize_key(strip_numeric_prefix(page))
            anchor = page_anchor_map.get(key2)
        if anchor:
            return f"[{label}](#{anchor})"
        return m.group(0)  # leave unchanged if not found
    return WIKI_LINK_RE.sub(repl, text)


def rewrite_md_links_to_local(text: str, page_anchor_map: dict) -> str:
    """
    Rewrite [label](Target) where Target is a relative reference to another page:
      - Foo-Page
      - Foo Page
      - Foo-Page.md / ./Foo Page.md / subdirs/Foo-Page.md (uses basename)
    """
    def repl(m):
        label = m.group("label")
        target = m.group("target").strip()

        # Keep absolute/special links
        if is_absolute_or_special(target):
            return m.group(0)

        # Remove title part if present: "url \"title\""
        url_only = target.split(" ", 1)[0]
        # Drop anchors and queries
        url_only = url_only.split("#", 1)[0].split("?", 1)[0]
        # Use basename and drop extension if .md
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--repo", required=True, help="owner/repo (without .wiki)")
    args = ap.parse_args()

    wiki_dir = Path(args.wiki_dir)
    out_path = Path(args.out)

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

    # Sort by 2-digit number, then optional letter (a, b, c...)
    pages.sort(key=lambda x: extract_sort_key(x["path"].stem))

    # Build anchor map (many keys → one anchor), based on final section titles
    page_anchor_map = {}
    final_titles = [p["title"] for p in pages]
    for p in pages:
        anchor = anchor_slug(p["title"])
        for k in build_page_keyset(p["title"], p["stem"]):
            page_anchor_map.setdefault(k, anchor)

    # Second pass: transform content
    output_sections = []

    # TOC
    toc = []
    toc.append("# Wiki (Concatenated)\n")
    toc.append(f"_Source: local concatenation of wiki pages_\n")
    toc.append("\n---\n## Contents\n")
    for p in pages:
        toc.append(f"- [{p['title']}](#{anchor_slug(p['title'])})")
    toc.append("")  # blank line

    output_sections.append("\n".join(toc))

    for p in pages:
        # 1) Rewrite wiki links to local anchors
        t = rewrite_wiki_links_to_local(p["raw"], page_anchor_map)
        # 2) Rewrite standard relative links to local anchors
        t = rewrite_md_links_to_local(t, page_anchor_map)
        # 3) Rewrite relative images to raw wiki URLs
        t = rewrite_markdown_images(t, args.repo)
        t = rewrite_html_images(t, args.repo)
        # 4) Demote headings and add H1 section title
        section = normalize_heading(p["title"], t).rstrip()
        # 5) Add small provenance footnote
        url = f"https://github.com/{args.repo}/wiki/{quote(p['path'].stem)}"
        section += f"\n\n<sub>Original page: [{p['path'].name}]({url})</sub>\n"
        output_sections.append("\n---\n" + section)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(output_sections) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
