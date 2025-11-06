#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from urllib.parse import quote

IGNORE = {"_Sidebar.md", "_Footer.md", "_Header.md", "Home.md"}

ORDER_RE = re.compile(r"^\s*(?P<num>\d{2})\b")
H1_RE = re.compile(r"^\s*#\s+(.*)$", re.MULTILINE)

# Wiki-style link patterns:
# [[Page]]
# [[Page|Custom Text]]
WIKI_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")

def rewrite_wiki_links(text: str, repo: str) -> str:
    """
    Convert wiki-style links [[Page]] or [[Page|Text]]
    to standard markdown links pointing to the live wiki page.
    """
    def repl(match):
        page = match.group(1).strip()
        label = match.group(2).strip() if match.group(2) else page

        # Convert spaces to hyphens in wiki page URLs (GitHub behavior)
        slug = page.replace(" ", "-")
        return f"[{label}](https://github.com/{repo}/wiki/{quote(slug)})"

    return WIKI_LINK_RE.sub(repl, text)


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def find_first_h1(text: str) -> str | None:
    m = H1_RE.search(text)
    return m.group(1).strip() if m else None


def page_title_from_filename(p: Path) -> str:
    return p.stem.replace("-", " ").replace("_", " ").strip()


def extract_order_and_title(p: Path, text: str):
    title = find_first_h1(text) or page_title_from_filename(p)

    # Try numeric prefix in heading
    m = ORDER_RE.match(title)
    if m:
        return int(m.group("num")), title

    # Try numeric prefix in filename
    m2 = ORDER_RE.match(p.stem)
    if m2:
        return int(m2.group("num")), title

    return None, title


def normalize_heading(title: str, content: str) -> str:
    # Strip existing initial heading if present
    content = re.sub(r"^\s*#\s+.*?\n+", "", content, count=1)
    return f"# {title}\n\n{content.lstrip()}"


def wiki_page_url(repo: str, page_md: Path) -> str:
    return f"https://github.com/{repo}/wiki/{quote(page_md.stem)}"


def collect_pages(wiki_dir: Path):
    for p in sorted(wiki_dir.glob("*.md")):
        if p.name in IGNORE:
            continue
        yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--repo", required=True, help="owner/repo (without .wiki)")
    args = ap.parse_args()

    wiki_dir = Path(args.wiki_dir)
    out_path = Path(args.out)

    pages = []
    for md in collect_pages(wiki_dir):
        raw = read_text(md)

        # Rewrite internal wiki-style links
        text = rewrite_wiki_links(raw, args.repo)

        order, title = extract_order_and_title(md, text)
        pages.append({
            "path": md,
            "text": text,
            "order": 999 if order is None else order,
            "title": title,
            "url": wiki_page_url(args.repo, md),
        })

    pages.sort(key=lambda x: (x["order"], x["path"].name.lower()))

    out = []
    out.append("# Wiki (Concatenated)\n")
    out.append(f"_Source: https://github.com/{args.repo}/wiki_\n")
    out.append("\n---\n## Contents\n")

    def anchor(t):  # predictable markdown anchor
        t = t.lower()
        t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
        return t

    for p in pages:
        out.append(f"- [{p['title']}](#{anchor(p['title'])})")
    out.append("")

    for p in pages:
        out.append("\n---\n")
        page_block = normalize_heading(p["title"], p["text"]).rstrip()
        out.append(page_block + "\n")
        out.append(f"<sub>Original page: [{p['path'].name}]({p['url']})</sub>\n")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
