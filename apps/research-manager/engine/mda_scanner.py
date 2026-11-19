#!/usr/bin/env python3
"""
mda_scanner.py — Scan the MDA canonical site and report statistics.

Usage:
    python engine/mda_scanner.py
"""

from pathlib import Path
import re
from collections import Counter, defaultdict

MDA_SITE = Path(r"\\dlowenas\HPWorkstation\Desktop\Master HTMl\____ MDA WORKFLOW\canonical\site\moral-decline")

def scan():
    html_files = sorted(MDA_SITE.rglob("MDA-*.html"))
    sections = defaultdict(list)
    
    total_words = 0
    total_images = 0
    total_audio = 0
    has_main_count = 0
    has_glossary_links = 0
    has_citation_badges = 0
    has_mtl = 0
    has_proof_panel = 0

    for f in html_files:
        rel = f.relative_to(MDA_SITE)
        section = rel.parts[0] if rel.parts else "root"
        sections[section].append(f)
        
        html = f.read_text(encoding='utf-8', errors='replace')
        
        # Word count (rough)
        text = re.sub(r'<[^>]+>', ' ', html)
        words = len(text.split())
        total_words += words
        
        # Feature detection
        if '<main' in html.lower():
            has_main_count += 1
        if 'glossary-layer.js' in html:
            has_glossary_links += 1
        if 'source-badge' in html:
            has_citation_badges += 1
        if 'mtl-equation' in html or 'mtl-callout' in html:
            has_mtl += 1
        if 'tp-proving' in html or 'proving-ground' in html:
            has_proof_panel += 1
        
        # Media counts
        total_images += len(re.findall(r'<img', html))
        total_audio += len(re.findall(r'<audio', html))

    print("=" * 60)
    print("MDA SITE SCAN REPORT")
    print("=" * 60)
    print(f"\nTotal Articles: {len(html_files)}")
    print(f"Total Words:    {total_words:,}")
    print(f"Total Images:   {total_images}")
    print(f"Total Audio:    {total_audio}")
    
    print(f"\n--- Feature Coverage ---")
    print(f"Has <main> tag:        {has_main_count}/{len(html_files)} ({100*has_main_count//len(html_files)}%)")
    print(f"Glossary links:        {has_glossary_links}/{len(html_files)} ({100*has_glossary_links//len(html_files)}%)")
    print(f"Citation badges:       {has_citation_badges}/{len(html_files)} ({100*has_citation_badges//len(html_files)}%)")
    print(f"MTL blocks:            {has_mtl}/{len(html_files)} ({100*has_mtl//len(html_files)}%)")
    print(f"Proof panels:          {has_proof_panel}/{len(html_files)} ({100*has_proof_panel//len(html_files)}%)")
    
    print(f"\n--- By Section ---")
    for section, files in sorted(sections.items()):
        print(f"  {section}: {len(files)} articles")
    
    print(f"\n--- Files Missing Features ---")
    for f in html_files:
        html = f.read_text(encoding='utf-8', errors='replace')
        missing = []
        if '<main' not in html.lower():
            missing.append("no <main>")
        if 'glossary-layer.js' not in html:
            missing.append("no glossary")
        if 'source-badge' not in html:
            missing.append("no citations")
        if missing:
            print(f"  {f.name}: {', '.join(missing)}")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    scan()
