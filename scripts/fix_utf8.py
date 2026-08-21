#!/usr/bin/env python3
"""fix_utf8.py — Fix encoding issues across the HTML dashboard fork."""

import re
from pathlib import Path

TARGET_DIR = Path(r"X:\HTML_Dashboard")

# Files to patch
FILES_TO_FIX = [
    r"engine\template_engine.py",
    r"core\auto_linker_v2.py",
    r"ui\tabs\auto_linker_tab_v3.py",
    r"ui\main_window_v2.py",
    r"ui\tabs\api_query_tab.py",
]

def fix_file(filepath: Path):
    text = filepath.read_text(encoding='utf-8', errors='replace')
    original = text

    # Pattern: open(path, 'r') or open(path, 'w') without encoding
    # Be careful not to double-patch already-fixed ones
    text = re.sub(
        r"with\s+open\(([^,]+),\s*['\"]([rw])['\"]\)\s+as\s+f:",
        r"with open(\1, '\2', encoding='utf-8') as f:",
        text
    )
    # Pattern: open(path) — default is 'r'
    text = re.sub(
        r"with\s+open\(([^)]+)\)\s+as\s+f:",
        r"with open(\1, 'r', encoding='utf-8') as f:",
        text
    )

    if text != original:
        filepath.write_text(text, encoding='utf-8')
        print(f"  Fixed: {filepath}")
    else:
        print(f"  OK:    {filepath}")


def main():
    print("Fixing UTF-8 encoding in target files...")
    for rel in FILES_TO_FIX:
        fp = TARGET_DIR / rel
        if fp.exists():
            fix_file(fp)
        else:
            print(f"  SKIP:  {fp} (not found)")
    print("\nDone.")


if __name__ == '__main__':
    main()
