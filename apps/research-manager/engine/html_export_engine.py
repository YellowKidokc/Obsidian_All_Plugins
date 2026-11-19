#!/usr/bin/env python3
"""
html_export_engine.py — Export dashboard data to MDA HTML site formats.

Usage:
    python engine/html_export_engine.py --glossary
    python engine/html_export_engine.py --dashboards
    python engine/html_export_engine.py --all

Outputs:
    shared/data/glossary-terms.json
    shared/js/glossary-layer.js
    shared/css/glossary-layer.css
    site-lib/html/mda/dashboards/*.html
"""

import argparse
import json
import re
from pathlib import Path
from collections import Counter

from mda_bridge import (
    write_glossary_terms,
    write_glossary_layer_js,
    write_glossary_layer_css,
    get_canonical_articles,
    get_article_text,
    inject_asset_links_into_article,
)

# ── Paths ─────────────────────────────────────────────────────────────────────
DASHBOARD_ROOT = Path(r"X:\HTML_Dashboard")
GLOSSARY_DATA = Path(r"\\dlowenas\HPWorkstation\Desktop\Master HTMl\____ MDA WORKFLOW\canonical\subdomains\glossary\glossary_data.json")

# Hard stoplist — broad/common words that should NEVER be inline highlighted
HARD_STOPLIST = {
    'truth', 'time', 'function', 'relationships', 'relationship', 'technology',
    'knowledge', 'faith', 'love', 'god', 'spirit', 'mind', 'soul', 'body',
    'world', 'life', 'death', 'power', 'light', 'dark', 'good', 'evil',
    'right', 'wrong', 'hope', 'fear', 'peace', 'war', 'sin', 'grace',
    'word', 'work', 'way', 'man', 'woman', 'child', 'family', 'church',
    'state', 'nation', 'country', 'people', 'person', 'human', 'being',
    'thing', 'place', 'part', 'form', 'sense', 'order', 'matter', 'energy',
    'force', 'field', 'wave', 'particle', 'space', 'motion', 'action',
    'change', 'process', 'system', 'structure', 'pattern', 'model',
    'data', 'information', 'value', 'level', 'point', 'line', 'area',
    'group', 'set', 'number', 'amount', 'rate', 'ratio', 'percent',
    'year', 'day', 'age', 'era', 'period', 'term', 'name', 'word',
}


def parse_args():
    parser = argparse.ArgumentParser(description="Export dashboard data to MDA HTML formats")
    parser.add_argument("--glossary", action="store_true", help="Export glossary-terms.json")
    parser.add_argument("--dashboards", action="store_true", help="Generate dashboard HTML pages")
    parser.add_argument("--inject-links", action="store_true", help="Inject glossary CSS/JS into all canonical articles")
    parser.add_argument("--all", action="store_true", help="Do everything")
    return parser.parse_args()


# ── Glossary export ───────────────────────────────────────────────────────────

def load_glossary_data():
    """Load glossary from dashboard's glossary_data.json or return empty list."""
    if not GLOSSARY_DATA.exists():
        print(f"[Export] Glossary data not found at {GLOSSARY_DATA}")
        return []
    with open(GLOSSARY_DATA, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('terms', [])


def compute_term_frequencies(terms, article_texts):
    total = len(article_texts)
    frequencies = {}
    for t in terms:
        term_text = t['term'].lower()
        variants = {term_text}
        if not term_text.endswith('s'):
            variants.add(term_text + 's')
        if term_text.endswith('s') and len(term_text) > 2:
            variants.add(term_text[:-1])
        if term_text.endswith('ies'):
            variants.add(term_text[:-3] + 'y')

        count = 0
        for text in article_texts:
            if any(v in text for v in variants):
                count += 1
        frequencies[t['term']] = count / total if total else 0
    return frequencies


def should_inline(term_text, freq, is_canonical, has_math):
    text = term_text.lower().strip()
    if text in HARD_STOPLIST:
        return False
    if len(text) < 4:
        return False
    words = text.split()
    if len(words) == 1 and freq > 0.40:
        return False
    if len(words) == 1 and freq > 0.25:
        return False
    if len(words) >= 2:
        return True
    if is_canonical and has_math:
        return True
    return True


def build_inline_glossary(terms, frequencies):
    output = []
    for t in terms:
        term_text = t['term']
        freq = frequencies.get(term_text, 0)
        inline = should_inline(
            term_text,
            freq,
            t.get('is_canonical', False),
            t.get('has_math', False)
        )
        desc = t.get('description', '')
        short = desc.split('.')[0].strip()[:120] if desc else ''

        entry = {
            'term': term_text,
            'id': t.get('id', term_text.lower().replace(' ', '-')),
            'short': short,
            'definition': desc,
            'category': t.get('category', 'General'),
            'inline': inline,
            'frequency': round(freq, 3),
            'is_canonical': t.get('is_canonical', False),
        }
        output.append(entry)

    output.sort(key=lambda x: (-x['inline'], x['frequency']))
    return output


def export_glossary():
    print("[Export] Loading glossary data...")
    terms = load_glossary_data()
    if not terms:
        print("[Export] No glossary data found. Skipping.")
        return

    print(f"[Export] {len(terms)} terms loaded")
    print("[Export] Reading canonical articles...")
    article_texts = [get_article_text(p) for p in get_canonical_articles()]
    print(f"[Export] {len(article_texts)} articles read")

    print("[Export] Computing frequencies...")
    frequencies = compute_term_frequencies(terms, article_texts)

    print("[Export] Building inline glossary...")
    inline_glossary = build_inline_glossary(terms, frequencies)

    inline_count = sum(1 for t in inline_glossary if t['inline'])
    offline_count = len(inline_glossary) - inline_count
    print(f"[Export] Inline=true: {inline_count}, Inline=false: {offline_count}")

    write_glossary_terms(inline_glossary)


def export_glossary_assets():
    """Copy the glossary JS/CSS from MDA WORKFLOW to shared/."""
    # These are already in MDA WORKFLOW from Kimi's build
    # This function ensures they're present
    pass


# ── Dashboard export ──────────────────────────────────────────────────────────

def export_dashboards():
    print("[Export] Dashboard export not yet implemented.")
    # TODO: Use html_dashboard_generator.py to build standalone pages


# ── Asset injection ───────────────────────────────────────────────────────────

def inject_all_articles():
    articles = get_canonical_articles()
    print(f"[Export] Injecting glossary links into {len(articles)} articles...")
    for article in articles:
        inject_asset_links_into_article(article)
    print("[Export] Done.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    if not any([args.glossary, args.dashboards, args.inject_links, args.all]):
        print("Use --glossary, --dashboards, --inject-links, or --all")
        return

    if args.glossary or args.all:
        export_glossary()
    if args.dashboards or args.all:
        export_dashboards()
    if args.inject_links or args.all:
        inject_all_articles()

    print("\n[Export] Complete.")


if __name__ == '__main__':
    main()
