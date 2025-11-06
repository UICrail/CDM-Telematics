#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from urllib.parse import quote

# Ignore GitHub wiki system pages (adjust as you like)
IGNORE = {"_Sidebar.md", "_Footer.md", "_Header.md", "Home.md"}

# Detect leading 2-digit order like "01 Title" (in title or filename)
ORDER_RE = re.compile(r"^\s*(?P<num>\d{2})\b")

H1_RE = re.compile(r"^\s*#\s+(.*)$", re.MULTILINE)

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def first_h1(text: str) -> str | None:
    m = H1_RE.search(text)
    return m.group(1).strip() if m else None

def page_title_from_filename(p: Path) -> str:
    return p.stem.replace("-", " ").replace("_", " ").strip()

def extract_order_and_title(p: Path, text: str):
    """
    Returns (order:int|None, title:str, source:str)
    - order from first H1 or filename if it starts with NN...
    - title from first H1 (preferred) or filename
    """
    title = first_h1(text) or page_title_from_filename(p)

    # Prefer getting order from the title (if it starts with NN)
    m = ORDER_RE.match(title)
    if m:
        order = int(m.group("num"))
        return order, title, "title"

    # Otherwise try from the filename
    m2 = ORDER_RE.match(p.stem)
    if m2:
        order = int(m2.group("num"))
        return order, title, "filename"

    return None, title, "none"

def slugify(s: str) -> str:
    s = s.strip().lower()
    # Keep digits/letters/spaces/hyphens
    s = re.sub(r"[^0-9a-z\s\-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s

def wiki_page_url(repo: str, page_md: Path) -> str:
    # GitHub wiki uses filename (without .md) URL-encoded
    return f"https://github.com/{repo}/wiki/{quote(page_md.stem)}"

def normalize_page_heading(title: str, content: str) -> tuple[str, str]:
    """
    Ensure page content starts with a single H1 '# {title_no_prefix}'
    - If content already has a leading H1, remove it.
    - Keep the title as-is EXCEPT: if it starts with NN, keep that prefix in H1.
    """
    # Strip any initial H1
    content_wo_h1 = re.sub(r"^\s*#\s+.*?\n+", "", content, count=1)

    # Keep numeric prefix in heading if present
    m = ORDER_RE.match(title)
    if m:
        # Keep full "NN rest..." as heading text
        heading_text = title
    else:
        heading_text = title

    new_head = f"# {heading_text}\n\n"
    return heading_text, new_head + content_wo_h1.lstrip()

def collect_pages(wiki_dir: Path):
    for p in sorted(wiki_dir.glob("*.md")):
        if p.name in IGNORE:
            continue
        yield p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki-dir", required=True, help="Path to checked-out .wiki repo")
    ap.add_argument("--out", required=True, help="Output markdown file path")
    ap.add_argument("--repo", required=True, help="owner/repo (no .wiki)")
    args = ap.parse_args()

    wiki_dir = Path(args.wiki_dir)
    out_path = Path(args.out)

    pages = []
    for md in collect_pages(wiki_dir):
        text = read_text(md)
        order, title, order_src = extract_order_and_title(md, text)
        pages.append({
            "path": md,
            "text": text,
            "order": order,
            "order_src": order_src,
            "title": title,
            "url": wiki_page_url(args.repo, md),
        })

    # Sort: numeric prefix first (ascending), then by filename as tiebreaker.
    pages.sort(key=lambda x: (999 if x["order"] is None else x["order"], x["path"].name.lower()))

    # Build concatenated output
    out = []
    out.append("# Wiki (Concatenated)\n")
    out.append(f"_Source: https://github.com/{args.repo}/wiki_\n")
    out.append("\n---\n")
    out.append("## Contents\n")
    for p in pages:
        # Normalize heading to compute a predictable anchor
        display_title = p["title"]
        anchor = slugify(display_title)
        out.append(f"- [{display_title}](#{anchor})")
    out.append("")

    for p in pages:
        heading_text, normalized = normalize_page_heading(p["title"], p["text"])
        out.append("\n---\n")
        out.append(normalized.rstrip() + "\n")
        # Tiny footnote linking back to the live wiki page
        out.append(f"<sub>Original wiki page: [{p['path'].name}]({p['url']})</sub>\n")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out), encoding="utf-8")

if __name__ == "__main__":
    main()
