#!/usr/bin/env python3
"""
mda_bridge.py — Bridges the HTML dashboard to the MDA WORKFLOW site.

Knows the file paths, folder structure, and output formats for the
MDA HTML site. Other engines call this to write their output.
"""

import json
from pathlib import Path
from datetime import datetime

# ── MDA WORKFLOW paths ────────────────────────────────────────────────────────
MDA_WORKFLOW = Path(r"\\dlowenas\HPWorkstation\Desktop\Master HTMl\____ MDA WORKFLOW")
MDA_SHARED_DATA = MDA_WORKFLOW / "shared" / "data"
MDA_SHARED_JS = MDA_WORKFLOW / "shared" / "js"
MDA_SHARED_CSS = MDA_WORKFLOW / "shared" / "css"
MDA_SITE_LIB = MDA_WORKFLOW / "site-lib" / "html" / "mda" / "dashboards"
MDA_CANONICAL = MDA_WORKFLOW / "canonical" / "site" / "moral-decline"

# ── Writers ───────────────────────────────────────────────────────────────────

def write_glossary_terms(data: list[dict]):
    """Write glossary-terms.json for inline tooltip engine."""
    MDA_SHARED_DATA.mkdir(parents=True, exist_ok=True)
    path = MDA_SHARED_DATA / "glossary-terms.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[MDA Bridge] Wrote {path} ({len(data)} terms)")


def write_glossary_layer_js(js_code: str):
    """Write glossary-layer.js frontend engine."""
    MDA_SHARED_JS.mkdir(parents=True, exist_ok=True)
    path = MDA_SHARED_JS / "glossary-layer.js"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(js_code)
    print(f"[MDA Bridge] Wrote {path}")


def write_glossary_layer_css(css_code: str):
    """Write glossary-layer.css styles."""
    MDA_SHARED_CSS.mkdir(parents=True, exist_ok=True)
    path = MDA_SHARED_CSS / "glossary-layer.css"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(css_code)
    print(f"[MDA Bridge] Wrote {path}")


def write_dashboard_html(filename: str, html_content: str):
    """Write a standalone dashboard HTML page."""
    MDA_SITE_LIB.mkdir(parents=True, exist_ok=True)
    path = MDA_SITE_LIB / filename
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[MDA Bridge] Wrote dashboard: {path}")


def inject_asset_links_into_article(article_path: Path):
    """Ensure an article has glossary CSS/JS links. Idempotent."""
    if not article_path.exists():
        return
    html = article_path.read_text(encoding='utf-8', errors='replace')

    css_link = '<link rel="stylesheet" href="/shared/css/glossary-layer.css">'
    js_script = '<script defer src="/shared/js/glossary-layer.js" data-glossary-json="/shared/data/glossary-terms.json"></script>'

    modified = html
    if css_link not in modified:
        modified = modified.replace('</head>', f'  {css_link}\n</head>', 1)
    if js_script not in modified:
        modified = modified.replace('</body>', f'  {js_script}\n</body>', 1)

    if modified != html:
        article_path.write_text(modified, encoding='utf-8')
        print(f"[MDA Bridge] Linked assets in {article_path.name}")


def get_canonical_articles() -> list[Path]:
    """Return all MDA article HTML paths."""
    return sorted(MDA_CANONICAL.rglob("MDA-*.html"))


def get_article_text(article_path: Path) -> str:
    """Extract plain text from an article HTML."""
    import re
    html = article_path.read_text(encoding='utf-8', errors='replace')
    # Strip tags
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text
