"""
Claim Registry

Maintains one durable Excel workbook for extracted claims. Claims are upserted
by stable identity, so rerunning an article refreshes existing rows and adds
only genuinely new claims.
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


CLAIMS_PER_SHEET = 5000
CLAIM_SHEET_PREFIX = "Claims_"

HEADERS = [
    "claim_id",
    "paper_id",
    "article_title",
    "claim_text",
    "claim_kind",
    "source_path",
    "packet_path",
    "first_seen",
    "last_seen",
    "seen_count",
    "review_status",
    "axiom_links",
    "seven_q_slot",
    "evidence_links",
    "contradiction_status",
    "notes",
]


@dataclass
class ClaimRegistryResult:
    workbook_path: str
    added: int
    updated: int
    total_claims: int
    sheets: int


class ClaimRegistry:
    """Append/update extracted claims into one workbook."""

    def __init__(self, workbook_path: str | Path, max_rows_per_sheet: int = CLAIMS_PER_SHEET):
        self.workbook_path = Path(workbook_path)
        self.max_rows_per_sheet = max_rows_per_sheet
        self.workbook_path.parent.mkdir(parents=True, exist_ok=True)

    def update_from_packets(self, packets: list) -> ClaimRegistryResult:
        wb = self._load_or_create()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        existing = self._existing_claims(wb)

        added = 0
        updated = 0
        for packet in packets:
            for claim in packet.claims:
                claim_text = claim.get("text", "").strip()
                if not claim_text:
                    continue
                claim_id = self._claim_id(packet.paper_id, claim_text)
                row_data = self._row_from_packet(packet, claim, claim_id, now)

                location = existing.get(claim_id)
                if location:
                    ws, row = location
                    self._update_existing_row(ws, row, row_data, now)
                    updated += 1
                else:
                    ws = self._next_claim_sheet(wb)
                    row = ws.max_row + 1
                    self._write_row(ws, row, row_data)
                    existing[claim_id] = (ws, row)
                    added += 1

        self._refresh_summary(wb, added, updated, now)
        self._format_workbook(wb)
        wb.save(self.workbook_path)
        return ClaimRegistryResult(
            workbook_path=str(self.workbook_path),
            added=added,
            updated=updated,
            total_claims=len(existing),
            sheets=len([name for name in wb.sheetnames if name.startswith(CLAIM_SHEET_PREFIX)]),
        )

    def _load_or_create(self):
        if self.workbook_path.exists():
            return load_workbook(self.workbook_path)
        wb = Workbook()
        ws = wb.active
        ws.title = f"{CLAIM_SHEET_PREFIX}001"
        ws.append(HEADERS)
        wb.create_sheet("Summary")
        return wb

    def _existing_claims(self, wb) -> dict[str, tuple]:
        existing = {}
        for ws in self._claim_sheets(wb):
            header_map = self._header_map(ws)
            claim_col = header_map.get("claim_id")
            if not claim_col:
                continue
            for row in range(2, ws.max_row + 1):
                claim_id = ws.cell(row=row, column=claim_col).value
                if claim_id:
                    existing[str(claim_id)] = (ws, row)
        return existing

    def _claim_sheets(self, wb) -> list:
        sheets = [wb[name] for name in wb.sheetnames if name.startswith(CLAIM_SHEET_PREFIX)]
        if not sheets:
            ws = wb.create_sheet(f"{CLAIM_SHEET_PREFIX}001")
            ws.append(HEADERS)
            sheets.append(ws)
        return sheets

    def _next_claim_sheet(self, wb):
        sheets = self._claim_sheets(wb)
        ws = sheets[-1]
        if ws.max_row < self.max_rows_per_sheet + 1:
            return ws
        next_index = len(sheets) + 1
        ws = wb.create_sheet(f"{CLAIM_SHEET_PREFIX}{next_index:03d}")
        ws.append(HEADERS)
        return ws

    def _row_from_packet(self, packet, claim: dict, claim_id: str, now: str) -> dict[str, str | int]:
        return {
            "claim_id": claim_id,
            "paper_id": packet.paper_id,
            "article_title": packet.title,
            "claim_text": claim.get("text", ""),
            "claim_kind": claim.get("kind", "claim"),
            "source_path": packet.source_path,
            "packet_path": packet.output_markdown,
            "first_seen": now,
            "last_seen": now,
            "seen_count": 1,
            "review_status": "new",
            "axiom_links": "",
            "seven_q_slot": "",
            "evidence_links": "",
            "contradiction_status": "unreviewed",
            "notes": "",
        }

    def _update_existing_row(self, ws, row: int, row_data: dict, now: str) -> None:
        header_map = self._header_map(ws)
        preserve_fields = {"first_seen", "review_status", "axiom_links", "seven_q_slot", "evidence_links", "contradiction_status", "notes"}
        for key, value in row_data.items():
            if key in preserve_fields:
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

    def _write_row(self, ws, row: int, row_data: dict) -> None:
        header_map = self._header_map(ws)
        for key, value in row_data.items():
            col = header_map.get(key)
            if col:
                ws.cell(row=row, column=col).value = value

    def _header_map(self, ws) -> dict[str, int]:
        if ws.max_row < 1:
            ws.append(HEADERS)
        values = [ws.cell(row=1, column=col).value for col in range(1, max(ws.max_column, len(HEADERS)) + 1)]
        if values[: len(HEADERS)] != HEADERS:
            for col, header in enumerate(HEADERS, 1):
                ws.cell(row=1, column=col).value = header
        return {str(ws.cell(row=1, column=col).value): col for col in range(1, ws.max_column + 1)}

    def _refresh_summary(self, wb, added: int, updated: int, now: str) -> None:
        if "Summary" in wb.sheetnames:
            ws = wb["Summary"]
            ws.delete_rows(1, ws.max_row)
        else:
            ws = wb.create_sheet("Summary", 0)

        total = 0
        sheet_count = 0
        for claim_ws in self._claim_sheets(wb):
            sheet_count += 1
            total += max(claim_ws.max_row - 1, 0)

        rows = [
            ("Claim Registry", ""),
            ("Last Updated", now),
            ("Claims Added This Run", added),
            ("Claims Updated This Run", updated),
            ("Total Claims", total),
            ("Claim Sheets", sheet_count),
            ("Deduplication", "claim_id = sha256(paper_id + normalized claim text)"),
        ]
        for row in rows:
            ws.append(row)

    def _format_workbook(self, wb) -> None:
        header_fill = PatternFill(fill_type="solid", fgColor="00B8D9")
        header_font = Font(bold=True, color="000000")
        for ws in wb.worksheets:
            ws.freeze_panes = "A2"
            for cell in ws[1]:
                cell.font = header_font
                cell.fill = header_fill
            for idx, width in enumerate([18, 18, 36, 80, 16, 45, 45, 20, 20, 12, 18, 28, 16, 28, 22, 35], 1):
                ws.column_dimensions[get_column_letter(idx)].width = width

    def _claim_id(self, paper_id: str, claim_text: str) -> str:
        normalized = self._normalize_claim(claim_text)
        digest = hashlib.sha256(f"{paper_id}|{normalized}".encode("utf-8")).hexdigest()
        return digest[:20]

    def _normalize_claim(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

