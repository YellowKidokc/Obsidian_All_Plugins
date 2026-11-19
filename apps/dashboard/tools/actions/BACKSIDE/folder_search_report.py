"""Read-only folder intelligence report.

Inventories a folder and writes review artifacts. Source files and folders are
never renamed, moved, merged, or deleted.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path


TEXT_EXTENSIONS = {".md", ".txt", ".html", ".htm", ".py", ".json", ".yaml", ".yml", ".csv"}
IGNORED_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "_folder_reports"}
GENERIC_WORDS = {"a", "an", "and", "copy", "draft", "file", "final", "new", "of", "old", "the", "to", "version"}
COMMON_NAME_ISSUES = {
    "teh": "the", "recieve": "receive", "seperate": "separate", "definately": "definitely",
    "occured": "occurred", "untill": "until", "wierd": "weird", "thier": "their",
    "arguement": "argument", "goverment": "government", "conciousness": "consciousness",
    "theopyhiscs": "theophysics", "theophsyics": "theophysics", "lanes": "Lean (if this is about Lean 4)",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def words(value: str) -> list[str]:
    return [part.lower() for part in re.findall(r"[A-Za-z][A-Za-z']+", value)]


def normalized_title(path: Path) -> str:
    value = path.stem.lower()
    value = re.sub(r"\b(?:copy|draft|final|old|new|rev|revision|version|v)\s*\d*\b", " ", value)
    value = re.sub(r"\b\d{4}[-_]?\d{2}[-_]?\d{2}\b|\b\d+\b", " ", value)
    tokens = [token for token in words(value) if token not in GENERIC_WORDS]
    return " ".join(tokens)


def simhash(text: str) -> int:
    tokens = words(text)
    if not tokens:
        return 0
    weights = [0] * 64
    for token in tokens[:50_000]:
        hashed = int.from_bytes(hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest(), "big")
        for bit in range(64):
            weights[bit] += 1 if hashed & (1 << bit) else -1
    result = 0
    for bit, weight in enumerate(weights):
        if weight >= 0:
            result |= 1 << bit
    return result


def readable_text(path: Path, limit: int = 1_000_000) -> str | None:
    if path.suffix.lower() not in TEXT_EXTENSIONS or path.stat().st_size > limit:
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part.lower() in IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            yield path


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a read-only folder search and similarity report.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--title-threshold", type=float, default=0.78)
    parser.add_argument("--near-text-distance", type=int, default=8)
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"Folder does not exist: {root}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = (args.output or (root / "_folder_reports" / f"folder_search_{stamp}")).resolve()
    output.mkdir(parents=True, exist_ok=False)

    inventory: list[dict] = []
    folder_counts: Counter[str] = Counter()
    exact_groups: defaultdict[tuple[int, str], list[str]] = defaultdict(list)
    title_candidates: list[tuple[str, str]] = []
    text_fingerprints: list[tuple[str, int]] = []
    name_issues: list[dict] = []
    scan_errors: list[dict] = []

    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            stat = path.stat()
            digest = sha256(path)
            created = datetime.fromtimestamp(stat.st_ctime).astimezone()
            modified = datetime.fromtimestamp(stat.st_mtime).astimezone()
            record = {
                "relative_path": rel,
                "folder": path.parent.relative_to(root).as_posix() or ".",
                "filename": path.name,
                "extension": path.suffix.lower(),
                "bytes": stat.st_size,
                "created_local": created.isoformat(timespec="seconds"),
                "created_date": created.date().isoformat(),
                "modified_local": modified.isoformat(timespec="seconds"),
                "sha256": digest,
            }
            inventory.append(record)
            folder_counts[record["folder"]] += 1
            exact_groups[(stat.st_size, digest)].append(rel)

            title = normalized_title(path)
            if title:
                title_candidates.append((rel, title))

            text = readable_text(path)
            if text and len(words(text)) >= 20:
                text_fingerprints.append((rel, simhash(text)))

            for token in words(path.stem):
                if token in COMMON_NAME_ISSUES:
                    name_issues.append({"relative_path": rel, "token": token, "suggestion": COMMON_NAME_ISSUES[token], "reason": "known spelling/name issue"})
            if re.search(r"(?i)\buntitled\b|\bnew[ _-]+(?:document|folder)\b", path.stem):
                name_issues.append({"relative_path": rel, "token": path.stem, "suggestion": "review for a descriptive title", "reason": "placeholder name"})
            if re.search(r"[_-]{3,}|\s{2,}", path.stem):
                name_issues.append({"relative_path": rel, "token": path.stem, "suggestion": "normalize repeated separators", "reason": "separator anomaly"})
        except OSError as exc:
            scan_errors.append({"path": rel, "error": str(exc)})

    inventory.sort(key=lambda row: row["relative_path"].lower())
    folder_rows = [{"folder": folder, "direct_file_count": count} for folder, count in sorted(folder_counts.items())]
    date_counts = Counter(row["created_date"] for row in inventory)
    date_rows = [{"created_date": date, "file_count": count} for date, count in sorted(date_counts.items())]

    title_rows: list[dict] = []
    for index, (left_path, left_title) in enumerate(title_candidates):
        for right_path, right_title in title_candidates[index + 1:]:
            ratio = SequenceMatcher(None, left_title, right_title).ratio()
            if ratio >= args.title_threshold:
                title_rows.append({"left_path": left_path, "right_path": right_path, "similarity": round(ratio, 3), "left_normalized": left_title, "right_normalized": right_title})
    title_rows.sort(key=lambda row: (-row["similarity"], row["left_path"].lower()))

    duplicate_rows = []
    for (size, digest), paths in exact_groups.items():
        if len(paths) > 1:
            group_id = digest[:12]
            for rel in sorted(paths):
                duplicate_rows.append({"group_id": group_id, "bytes": size, "sha256": digest, "relative_path": rel})

    near_text_rows: list[dict] = []
    for index, (left_path, left_hash) in enumerate(text_fingerprints):
        for right_path, right_hash in text_fingerprints[index + 1:]:
            distance = (left_hash ^ right_hash).bit_count()
            if distance <= args.near_text_distance:
                near_text_rows.append({"left_path": left_path, "right_path": right_path, "simhash_distance": distance, "review_note": "Lower is closer; inspect content before any decision."})
    near_text_rows.sort(key=lambda row: (row["simhash_distance"], row["left_path"].lower()))

    one_file = [row for row in folder_rows if row["direct_file_count"] == 1]
    two_file = [row for row in folder_rows if row["direct_file_count"] == 2]

    fields = ["relative_path", "folder", "filename", "extension", "bytes", "created_local", "created_date", "modified_local", "sha256"]
    write_csv(output / "inventory.csv", inventory, fields)
    write_csv(output / "folder_counts.csv", folder_rows, ["folder", "direct_file_count"])
    write_csv(output / "created_date_groups.csv", date_rows, ["created_date", "file_count"])
    write_csv(output / "similar_titles.csv", title_rows, ["left_path", "right_path", "similarity", "left_normalized", "right_normalized"])
    write_csv(output / "exact_duplicates.csv", duplicate_rows, ["group_id", "bytes", "sha256", "relative_path"])
    write_csv(output / "near_text_matches.csv", near_text_rows, ["left_path", "right_path", "simhash_distance", "review_note"])
    write_csv(output / "possible_name_issues.csv", name_issues, ["relative_path", "token", "suggestion", "reason"])
    write_csv(output / "one_file_folders_REVIEW_ONLY.csv", one_file, ["folder", "direct_file_count"])
    write_csv(output / "two_file_folders_REVIEW_ONLY.csv", two_file, ["folder", "direct_file_count"])

    summary = {
        "root": str(root), "generated_utc": datetime.now(timezone.utc).isoformat(), "read_only_scan": True,
        "files": len(inventory), "folders_with_direct_files": len(folder_rows), "created_dates": len(date_rows),
        "similar_title_pairs": len(title_rows), "exact_duplicate_files": len(duplicate_rows),
        "near_text_pairs": len(near_text_rows), "possible_name_issues": len(name_issues),
        "one_file_folders": len(one_file), "two_file_folders": len(two_file), "scan_errors": scan_errors,
        "important_limits": [
            "SHA-256 proves byte identity only; it does not measure closeness or authorize deletion.",
            "Near-text similarity is heuristic and supports review only.",
            "Folder counts include direct files, not all descendant files.",
            "Created time on Windows can reflect a copy event rather than original authorship.",
            "One-file and two-file folders are candidates for review, not deletion instructions.",
        ],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Folder Search Report", "", f"- Root: `{root}`", f"- Files: {len(inventory):,}",
        f"- Folders containing files: {len(folder_rows):,}", f"- Similar-title pairs: {len(title_rows):,}",
        f"- Exact-duplicate file rows: {len(duplicate_rows):,}", f"- Near-text pairs: {len(near_text_rows):,}",
        f"- Possible filename/spelling issues: {len(name_issues):,}", f"- One-file folders: {len(one_file):,}",
        f"- Two-file folders: {len(two_file):,}", "", "## Safety and interpretation", "",
    ] + [f"- {item}" for item in summary["important_limits"]]
    lines += ["", "## Files produced", "", "Open the CSV files beside this report to review the underlying rows."]
    (output / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    safe_root = html.escape(str(root))
    html_report = f"""<!doctype html><meta charset=\"utf-8\"><title>Folder Search Report</title>
<style>body{{font:16px Arial;max-width:900px;margin:40px auto;line-height:1.5;color:#202124}}table{{border-collapse:collapse}}td,th{{padding:8px 14px;border-bottom:1px solid #ddd;text-align:left}}.warn{{background:#fff4ce;padding:14px}}</style>
<h1>Folder Search Report</h1><p><b>Root:</b> {safe_root}</p>
<table><tr><th>Measure</th><th>Count</th></tr>
<tr><td>Files</td><td>{len(inventory):,}</td></tr><tr><td>Folders containing files</td><td>{len(folder_rows):,}</td></tr>
<tr><td>Similar-title pairs</td><td>{len(title_rows):,}</td></tr><tr><td>Exact-duplicate file rows</td><td>{len(duplicate_rows):,}</td></tr>
<tr><td>Near-text pairs</td><td>{len(near_text_rows):,}</td></tr><tr><td>Possible name issues</td><td>{len(name_issues):,}</td></tr>
<tr><td>One-file folders</td><td>{len(one_file):,}</td></tr><tr><td>Two-file folders</td><td>{len(two_file):,}</td></tr></table>
<p class=\"warn\"><b>Review only.</b> This action changed no source file or folder. Small-folder lists are not deletion instructions.</p>
<p>Open the CSV files in this report folder for the complete evidence.</p>"""
    (output / "REPORT.html").write_text(html_report, encoding="utf-8")

    print(f"Report written to: {output}")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
