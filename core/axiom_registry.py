"""
Axiom Registry

Maintains a durable Excel workbook for axiom candidates and 7QS handles.
Rows are upserted by stable identity so reruns refresh existing records and
only add genuinely new candidates.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


ROWS_PER_SHEET = 5000
AXIOM_PREFIX = "Axioms_"
SEVEN_Q_PREFIX = "SevenQ_"

AXIOM_HEADERS = [
    "axiom_id",
    "paper_id",
    "article_title",
    "candidate_text",
    "candidate_status",
    "source_path",
    "packet_path",
    "first_seen",
    "last_seen",
    "seen_count",
    "canon_status",
    "canonical_axiom_id",
    "law_family",
    "depends_on",
    "supports",
    "contradicts",
    "seven_q_slot",
    "reviewer_notes",
]

SEVEN_Q_HEADERS = [
    "seven_q_id",
    "paper_id",
    "article_title",
    "handle_text",
    "handle_status",
    "source_path",
    "packet_path",
    "first_seen",
    "last_seen",
    "seen_count",
    "question_slot",
    "classification",
    "falsification_note",
    "posture_note",
    "reviewer_notes",
]


@dataclass
class AxiomRegistryResult:
    workbook_path: str
    axioms_added: int
    axioms_updated: int
    seven_q_added: int
    seven_q_updated: int
    total_axioms: int
    total_seven_q: int


class AxiomRegistry:
    """Append/update axiom candidates and 7QS handles into one workbook."""

    def __init__(self, workbook_path: str | Path, max_rows_per_sheet: int = ROWS_PER_SHEET):
        self.workbook_path = Path(workbook_path)
        self.max_rows_per_sheet = max_rows_per_sheet
        self.workbook_path.parent.mkdir(parents=True, exist_ok=True)

    def update_from_packets(self, packets: list) -> AxiomRegistryResult:
        wb = self._load_or_create()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        existing_axioms = self._existing(wb, AXIOM_PREFIX, AXIOM_HEADERS[0], AXIOM_HEADERS)
        existing_seven_q = self._existing(wb, SEVEN_Q_PREFIX, SEVEN_Q_HEADERS[0], SEVEN_Q_HEADERS)

        axioms_added = 0
        axioms_updated = 0
        seven_q_added = 0
        seven_q_updated = 0

        for packet in packets:
            for item in packet.axiom_items:
                text = item.get("text", "").strip()
                if not text:
                    continue
                item_id = self._stable_id("axiom", packet.paper_id, text)
                row_data = self._axiom_row(packet, item, item_id, now)
                location = existing_axioms.get(item_id)
                if location:
                    ws, row = location
                    self._update_row(ws, row, row_data, now, preserve={
                        "first_seen", "canon_status", "canonical_axiom_id", "law_family",
                        "depends_on", "supports", "contradicts", "seven_q_slot", "reviewer_notes",
                    })
                    axioms_updated += 1
                else:
                    ws = self._next_sheet(wb, AXIOM_PREFIX, AXIOM_HEADERS)
                    row = ws.max_row + 1
                    self._write_row(ws, row, row_data)
                    existing_axioms[item_id] = (ws, row)
                    axioms_added += 1

            for item in packet.seven_q_items:
                text = item.get("text", "").strip()
                if not text:
                    continue
                item_id = self._stable_id("seven_q", packet.paper_id, text)
                row_data = self._seven_q_row(packet, item, item_id, now)
                location = existing_seven_q.get(item_id)
                if location:
                    ws, row = location
                    self._update_row(ws, row, row_data, now, preserve={
                        "first_seen", "question_slot", "classification",
                        "falsification_note", "posture_note", "reviewer_notes",
                    })
                    seven_q_updated += 1
                else:
                    ws = self._next_sheet(wb, SEVEN_Q_PREFIX, SEVEN_Q_HEADERS)
                    row = ws.max_row + 1
                    self._write_row(ws, row, row_data)
                    existing_seven_q[item_id] = (ws, row)
                    seven_q_added += 1

        self._refresh_summary(
            wb,
            now,
            axioms_added,
            axioms_updated,
            seven_q_added,
            seven_q_updated,
            len(existing_axioms),
            len(existing_seven_q),
        )
        self._format_workbook(wb)
        wb.save(self.workbook_path)

        return AxiomRegistryResult(
            workbook_path=str(self.workbook_path),
            axioms_added=axioms_added,
            axioms_updated=axioms_updated,
            seven_q_added=seven_q_added,
            seven_q_updated=seven_q_updated,
            total_axioms=len(existing_axioms),
            total_seven_q=len(existing_seven_q),
        )

    def _load_or_create(self):
        if self.workbook_path.exists():
            return load_workbook(self.workbook_path)
        wb = Workbook()
        ws = wb.active
        ws.title = f"{AXIOM_PREFIX}001"
        ws.append(AXIOM_HEADERS)
        ws = wb.create_sheet(f"{SEVEN_Q_PREFIX}001")
        ws.append(SEVEN_Q_HEADERS)
        wb.create_sheet("Summary")
        return wb

    def _existing(self, wb, prefix: str, id_header: str, headers: list[str]) -> dict[str, tuple]:
        existing = {}
        for ws in self._sheets(wb, prefix, headers):
            header_map = self._header_map(ws, headers)
            id_col = header_map.get(id_header)
            if not id_col:
                continue
            for row in range(2, ws.max_row + 1):
                value = ws.cell(row=row, column=id_col).value
                if value:
                    existing[str(value)] = (ws, row)
        return existing

    def _sheets(self, wb, prefix: str, headers: list[str]) -> list:
        sheets = [wb[name] for name in wb.sheetnames if name.startswith(prefix)]
        if not sheets:
            ws = wb.create_sheet(f"{prefix}001")
            ws.append(headers)
            sheets.append(ws)
        return sheets

    def _next_sheet(self, wb, prefix: str, headers: list[str]):
        sheets = self._sheets(wb, prefix, headers)
        ws = sheets[-1]
        if ws.max_row < self.max_rows_per_sheet + 1:
            return ws
        ws = wb.create_sheet(f"{prefix}{len(sheets) + 1:03d}")
        ws.append(headers)
        return ws

    def _axiom_row(self, packet, item: dict, item_id: str, now: str) -> dict[str, str | int]:
        return {
            "axiom_id": item_id,
            "paper_id": packet.paper_id,
            "article_title": packet.title,
            "candidate_text": item.get("text", ""),
            "candidate_status": item.get("status", "candidate"),
            "source_path": packet.source_path,
            "packet_path": packet.output_markdown,
            "first_seen": now,
            "last_seen": now,
            "seen_count": 1,
            "canon_status": "candidate",
            "canonical_axiom_id": "",
            "law_family": self._guess_law_family(item.get("text", "")),
            "depends_on": "",
            "supports": "",
            "contradicts": "",
            "seven_q_slot": "",
            "reviewer_notes": "",
        }

    def _seven_q_row(self, packet, item: dict, item_id: str, now: str) -> dict[str, str | int]:
        text = item.get("text", "")
        return {
            "seven_q_id": item_id,
            "paper_id": packet.paper_id,
            "article_title": packet.title,
            "handle_text": text,
            "handle_status": item.get("status", "candidate"),
            "source_path": packet.source_path,
            "packet_path": packet.output_markdown,
            "first_seen": now,
            "last_seen": now,
            "seen_count": 1,
            "question_slot": self._guess_question_slot(text),
            "classification": "",
            "falsification_note": "falsification" if re.search(r"falsification", text, re.IGNORECASE) else "",
            "posture_note": "posture" if re.search(r"humility|surrender|posture before inquiry", text, re.IGNORECASE) else "",
            "reviewer_notes": "",
        }

    def _write_row(self, ws, row: int, row_data: dict) -> None:
        header_map = self._header_map(ws, list(row_data.keys()))
        for key, value in row_data.items():
            col = header_map.get(key)
            if col:
                ws.cell(row=row, column=col).value = value

    def _update_row(self, ws, row: int, row_data: dict, now: str, preserve: set[str]) -> None:
        header_map = self._header_map(ws, list(row_data.keys()))
        for key, value in row_data.items():
            if key in preserve:
                continue
            col = header_map.get(key)
            if col:
                ws.cell(row=row, column=col).value = value
        if "last_seen" in header_map:
            ws.cell(row=row, column=header_map["last_seen"]).value = now
        if "seen_count" in header_map:
            cell = ws.cell(row=row, column=header_map["seen_count"])
            try:
                cell.value = int(cell.value or 0) + 1
            except (TypeError, ValueError):
                cell.value = 1

    def _header_map(self, ws, headers: list[str]) -> dict[str, int]:
        if ws.max_row < 1:
            ws.append(headers)
        current = [ws.cell(row=1, column=col).value for col in range(1, max(ws.max_column, len(headers)) + 1)]
        if current[: len(headers)] != headers:
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col).value = header
        return {str(ws.cell(row=1, column=col).value): col for col in range(1, ws.max_column + 1)}

    def _refresh_summary(
        self,
        wb,
        now: str,
        axioms_added: int,
        axioms_updated: int,
        seven_q_added: int,
        seven_q_updated: int,
        total_axioms: int,
        total_seven_q: int,
    ) -> None:
        if "Summary" in wb.sheetnames:
            ws = wb["Summary"]
            ws.delete_rows(1, ws.max_row)
        else:
            ws = wb.create_sheet("Summary", 0)

        rows = [
            ("Axiom Registry", ""),
            ("Last Updated", now),
            ("Axioms Added This Run", axioms_added),
            ("Axioms Updated This Run", axioms_updated),
            ("7QS Added This Run", seven_q_added),
            ("7QS Updated This Run", seven_q_updated),
            ("Total Axiom Candidates", total_axioms),
            ("Total 7QS Handles", total_seven_q),
            ("Deduplication", "sha256(kind + paper_id + normalized text)"),
        ]
        for row in rows:
            ws.append(row)

    def _format_workbook(self, wb) -> None:
        header_fill = PatternFill(fill_type="solid", fgColor="4ADE80")
        header_font = Font(bold=True, color="000000")
        for ws in wb.worksheets:
            ws.freeze_panes = "A2"
            for cell in ws[1]:
                cell.font = header_font
                cell.fill = header_fill
            for idx, width in enumerate([20, 18, 36, 90, 18, 45, 45, 20, 20, 12, 18, 24, 20, 28, 28, 28, 16, 36], 1):
                ws.column_dimensions[get_column_letter(idx)].width = width

    def _stable_id(self, kind: str, paper_id: str, text: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", " ", text.lower())
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return hashlib.sha256(f"{kind}|{paper_id}|{normalized}".encode("utf-8")).hexdigest()[:20]

    def _guess_law_family(self, text: str) -> str:
        match = re.search(r"\bLaw\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b", text, re.IGNORECASE)
        return match.group(0) if match else ""

    def _guess_question_slot(self, text: str) -> str:
        match = re.search(r"\bQ([0-7])\b", text, re.IGNORECASE)
        if match:
            return f"Q{match.group(1)}"
        if re.search(r"posture before inquiry|humility|surrender", text, re.IGNORECASE):
            return "Q0"
        if re.search(r"falsification", text, re.IGNORECASE):
            return "Falsification"
        if re.search(r"classif", text, re.IGNORECASE):
            return "Classification"
        return ""

