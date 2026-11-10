"""Interactive front door for the File Action Hub."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BACKSIDE = ROOT / "BACKSIDE"
INBOX = ROOT / "INBOX"
OUTBOX = ROOT / "OUTBOX"


def browse(kind: str) -> Path | None:
    try:
        import tkinter as tk
        from tkinter import filedialog

        window = tk.Tk()
        window.withdraw()
        if kind == "folder":
            selected = filedialog.askdirectory(title="Choose a folder")
        else:
            selected = filedialog.askopenfilename(title="Choose a file")
        window.destroy()
        return Path(selected) if selected else None
    except Exception:
        return None


def inbox_items() -> list[Path]:
    return sorted(
        (path for path in INBOX.iterdir() if path.name.lower() != "readme.txt" and not path.name.startswith(".")),
        key=lambda path: path.name.lower(),
    )


def choose_target(initial: str | None = None) -> Path | None:
    if initial:
        candidate = Path(initial.strip('"')).expanduser()
        if candidate.exists():
            return candidate.resolve()
        print(f"Not found: {candidate}")

    while True:
        items = inbox_items()
        print("\nWHAT DO YOU WANT TO WORK ON?")
        if items:
            print("Inbox:")
            for number, item in enumerate(items, 1):
                kind = "folder" if item.is_dir() else "file"
                print(f"  [{number}] {item.name} ({kind})")
        else:
            print("  Inbox is empty.")
        print("  [B] Browse for a folder")
        print("  [F] Browse for a file")
        print("  [P] Paste a path")
        print("  [Q] Quit")
        answer = input("Choose: ").strip()
        if answer.lower() == "q":
            return None
        if answer.lower() == "b":
            selected = browse("folder")
            if selected and selected.exists():
                return selected.resolve()
            print("Nothing selected.")
            continue
        if answer.lower() == "f":
            selected = browse("file")
            if selected and selected.exists():
                return selected.resolve()
            print("Nothing selected.")
            continue
        if answer.lower() == "p":
            pasted = Path(input("Paste the path: ").strip().strip('"')).expanduser()
            if pasted.exists():
                return pasted.resolve()
            print(f"Not found: {pasted}")
            continue
        if answer.isdigit() and 1 <= int(answer) <= len(items):
            return items[int(answer) - 1].resolve()
        print("Please choose one of the listed options.")


def run(command: list[str]) -> bool:
    print("\nRunning:", " ".join(f'\"{part}\"' if " " in part else part for part in command))
    completed = subprocess.run(command, check=False)
    if completed.returncode:
        print(f"Action ended with code {completed.returncode}.")
        return False
    return True


def output_folder(label: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTBOX / f"{label}_{stamp}"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def confirm_apply() -> bool:
    return input("Type YES to perform the reviewed action: ").strip().upper() == "YES"


def conversion(target: Path, action: str, label: str, extra: list[str] | None = None) -> None:
    destination = output_folder(label)
    command = [sys.executable, str(BACKSIDE / "convert.py"), action, str(target), "--out", str(destination)]
    if extra:
        command.extend(extra)
    if run(command) and confirm_apply():
        run(command + ["--apply"])
        print(f"Output: {destination}")
    else:
        print("Cancelled. No conversion output was created.")


def folder_report(target: Path) -> None:
    if not target.is_dir():
        print("Folder Search Report needs a folder.")
        return
    destination = output_folder("folder_search")
    if run([sys.executable, str(BACKSIDE / "folder_search_report.py"), str(target), "--output", str(destination)]):
        print(f"Report: {destination / 'REPORT.html'}")
        try:
            subprocess.Popen(["cmd", "/c", "start", "", str(destination / "REPORT.html")])
        except OSError:
            pass


def flatten(target: Path) -> None:
    if not target.is_dir():
        print("Flatten needs a folder.")
        return
    command = [sys.executable, str(BACKSIDE / "flatten.py"), str(target)]
    print("\nPREVIEW ONLY")
    if run(command) and confirm_apply():
        run(command + ["--apply"])
    else:
        print("Cancelled. Nothing changed.")


def research_intake() -> None:
    launcher = ROOT / "FOLDER_RESEARCH_INTAKE.bat"
    if launcher.exists():
        subprocess.run(["cmd", "/c", "call", str(launcher)], check=False)
    else:
        print("Folder Research Intake launcher was not found.")


def choose_markdown_format() -> str | None:
    formats = ["docx", "html", "pdf", "pptx", "odt", "rtf", "epub", "txt"]
    print("\nOUTPUT FORMAT")
    for number, value in enumerate(formats, 1):
        print(f"  [{number}] {value}")
    answer = input("Choose: ").strip()
    if answer.isdigit() and 1 <= int(answer) <= len(formats):
        return formats[int(answer) - 1]
    print("No format selected.")
    return None


def action_menu(target: Path) -> str:
    print(f"\nCURRENT ITEM: {target}")
    print("  [1] Folder Search Report")
    print("  [2] Folder Research Intake")
    print("  [3] Convert anything to Markdown")
    print("  [4] Convert Markdown to another format")
    print("  [5] Excel workbook to CSV book folder")
    print("  [6] CSV book folder to Excel workbook")
    print("  [7] Flatten a folder (preview, then explicit approval)")
    print("  [N] Choose a different file or folder")
    print("  [Q] Done")
    return input("Choose an action: ").strip().lower()


def main() -> int:
    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    initial = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None
    target = choose_target(initial)
    while target is not None:
        choice = action_menu(target)
        if choice == "1":
            folder_report(target)
        elif choice == "2":
            research_intake()
        elif choice == "3":
            conversion(target, "tomd", "to_markdown")
        elif choice == "4":
            format_name = choose_markdown_format()
            if format_name:
                conversion(target, "frommd", f"markdown_to_{format_name}", ["--to", format_name])
        elif choice == "5":
            conversion(target, "excel2csv", "excel_to_csv")
        elif choice == "6":
            conversion(target, "csv2excel", "csv_to_excel")
        elif choice == "7":
            flatten(target)
        elif choice == "n":
            target = choose_target()
        elif choice == "q":
            break
        else:
            print("Please choose one of the listed actions.")
            continue

        again = input("\nRun another action? [Y/n]: ").strip().lower()
        if again == "n":
            break
    print(f"\nDone. Outputs are kept in: {OUTBOX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
