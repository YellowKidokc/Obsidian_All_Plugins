"""
Production Packet Engine

Builds the next-stage production page packet for articles:
executive summary, plain-English layer, contradiction audit, math extraction,
and axiom/claim mapping. This is a deterministic first pass intended to create
usable review artifacts before optional model checkpoints refine the language.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Any


ARTICLE_EXTENSIONS = {".md", ".markdown", ".html", ".htm", ".txt"}

SKIP_NAMES = {
    "agents.md",
    "readme.md",
}

SKIP_SUBSTRINGS = {
    "session_notes",
    "_index",
}

AXIOM_PATTERNS = [
    re.compile(r"\baxiom\s+([A-Z]?-?\d+|[IVXLCDM]+)?\b", re.IGNORECASE),
    re.compile(r"\blaw\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b", re.IGNORECASE),
    re.compile(r"\bkill condition\s+(\d+)?\b", re.IGNORECASE),
    re.compile(r"\bfalsification criteri(?:a|on)\b", re.IGNORECASE),
    re.compile(r"\bmaster equation\b", re.IGNORECASE),
    re.compile(r"\b7[- ]question\b", re.IGNORECASE),
]

CONTRADICTION_PATTERNS = [
    re.compile(r"\bcontradict(?:s|ion|ory)?\b", re.IGNORECASE),
    re.compile(r"\btension\b", re.IGNORECASE),
    re.compile(r"\bconflict(?:s|ing)?\b", re.IGNORECASE),
    re.compile(r"\binconsistent\b", re.IGNORECASE),
    re.compile(r"\bhowever\b", re.IGNORECASE),
    re.compile(r"\byet\b", re.IGNORECASE),
    re.compile(r"\bbut\b", re.IGNORECASE),
    re.compile(r"\bnot\b.{0,80}\bprove[sd]?\b", re.IGNORECASE),
    re.compile(r"\bprove[sd]?\b.{0,120}\bnot\b", re.IGNORECASE),
]

CLAIM_PATTERNS = [
    re.compile(r"\btherefore\b", re.IGNORECASE),
    re.compile(r"\bthis (?:shows|proves|demonstrates|implies|establishes)\b", re.IGNORECASE),
    re.compile(r"\bwe (?:show|prove|demonstrate|establish|argue)\b", re.IGNORECASE),
    re.compile(r"\bclaim\b", re.IGNORECASE),
    re.compile(r"\btheorem\b", re.IGNORECASE),
]

SEVEN_Q_PATTERNS = [
    re.compile(r"\bQ[0-7]\b", re.IGNORECASE),
    re.compile(r"\bseven[- ]question\b", re.IGNORECASE),
    re.compile(r"\b7Q\b", re.IGNORECASE),
    re.compile(r"\bclassif(?:y|ier|ication)\b", re.IGNORECASE),
    re.compile(r"\bfalsification\b", re.IGNORECASE),
    re.compile(r"\bposture before inquiry\b", re.IGNORECASE),
    re.compile(r"\bhumility\b|\bsurrender\b", re.IGNORECASE),
]

MATH_BLOCK_PATTERNS = [
    re.compile(r"\$\$(.*?)\$\$", re.DOTALL),
    re.compile(r"\\\[(.*?)\\\]", re.DOTALL),
    re.compile(r"\\\((.*?)\\\)", re.DOTALL),
    re.compile(r"\$(?!\$)(.*?)(?<!\$)\$", re.DOTALL),
]

MATH_LINE_PATTERN = re.compile(
    r"(?:\\frac|\\sum|\\int|\\partial|\\nabla|\\chi|χ|ψ|Φ|∂|∇|Σ|Ω|≤|≥|≠|≈|=|\^|_|\bNoether\b|\btanh\b)",
    re.IGNORECASE,
)


@dataclass
class ProductionPacket:
    source_path: str
    output_markdown: str
    output_json: str
    title: str
    paper_id: str
    executive_summary: str
    plain_english: str
    contradictions: list[dict[str, str]]
    math_items: list[dict[str, str]]
    axiom_items: list[dict[str, str]]
    seven_q_items: list[dict[str, str]]
    claims: list[dict[str, str]]
    open_obligations: list[str]


class ProductionPacketEngine:
    """Generate production-ready review packets for article files."""

    def __init__(self, output_root: str | Path):
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)

    def build_folder(self, source_folder: str | Path, recursive: bool = False) -> list[ProductionPacket]:
        source = Path(source_folder)
        if not source.exists():
            raise FileNotFoundError(f"Source folder not found: {source}")

        files = source.rglob("*") if recursive else source.glob("*")
        packets: list[ProductionPacket] = []
        for path in sorted(files):
            if self._should_process(path):
                packets.append(self.build_file(path))
        self._write_index(packets)
        return packets

    def build_file(self, source_path: str | Path) -> ProductionPacket:
        source = Path(source_path)
        raw = self._read_text(source)
        clean = self._to_plain_text(raw, source.suffix.lower())
        title = self._extract_title(clean, source)
        paper_id = self._extract_paper_id(source, clean)
        paragraphs = self._paragraphs(clean)
        sentences = self._sentences(clean)

        claims = self._extract_claims(sentences)
        contradictions = self._extract_contradictions(sentences)
        math_items = self._extract_math(raw, clean)
        axiom_items = self._extract_axioms(sentences)
        seven_q_items = self._extract_seven_q(sentences)
        executive_summary = self._executive_summary(title, paragraphs, claims)
        plain_english = self._plain_english(title, paragraphs, claims, math_items)
        open_obligations = self._open_obligations(contradictions, math_items, claims, seven_q_items)

        slug = self._slug(source.stem)
        markdown_path = self.output_root / f"{slug}.production-packet.md"
        json_path = self.output_root / f"{slug}.production-packet.json"

        packet = ProductionPacket(
            source_path=str(source),
            output_markdown=str(markdown_path),
            output_json=str(json_path),
            title=title,
            paper_id=paper_id,
            executive_summary=executive_summary,
            plain_english=plain_english,
            contradictions=contradictions,
            math_items=math_items,
            axiom_items=axiom_items,
            seven_q_items=seven_q_items,
            claims=claims,
            open_obligations=open_obligations,
        )

        markdown_path.write_text(self._render_markdown(packet, clean), encoding="utf-8")
        json_path.write_text(json.dumps(asdict(packet), indent=2, ensure_ascii=False), encoding="utf-8")
        return packet

    def _should_process(self, path: Path) -> bool:
        if not path.is_file() or path.suffix.lower() not in ARTICLE_EXTENSIONS:
            return False
        name = path.name.lower()
        if name in SKIP_NAMES:
            return False
        return not any(token in name for token in SKIP_SUBSTRINGS)

    def _read_text(self, path: Path) -> str:
        for encoding in ("utf-8-sig", "utf-8", "cp1252"):
            try:
                return path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        return path.read_text(errors="replace")

    def _to_plain_text(self, text: str, suffix: str) -> str:
        text = re.sub(
            r"<!--\s*MEDIA_CALLOUT_START\s*-->.*?<!--\s*MEDIA_CALLOUT_END\s*-->",
            " ",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if suffix in {".html", ".htm"}:
            text = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", text)
            text = re.sub(r"(?i)<br\s*/?>", "\n", text)
            text = re.sub(r"(?i)</p>|</div>|</section>|</article>|</h[1-6]>", "\n", text)
            text = re.sub(r"<[^>]+>", " ", text)
            text = unescape(text)
        text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
        text = re.sub(r"(?m)^>\s*\[!info\].*(?:\n>\s?.*)*", " ", text)
        text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
        text = re.sub(r"\A(?:I)?---\s.*?^---\s", " ", text, flags=re.DOTALL | re.MULTILINE)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        return re.sub(r"[ \t]+", " ", text)

    def _extract_title(self, text: str, source: Path) -> str:
        for match in re.finditer(r"(?m)^#\s+(.+?)\s*$", text):
            title = self._clean_title(match.group(1))
            if self._looks_like_title(title):
                return title[:140]

        yaml_title = re.search(r'(?mi)^title:\s*["\']([^"\']+)["\']', text)
        if yaml_title:
            title = self._clean_title(yaml_title.group(1))
            if self._looks_like_title(title):
                return title[:140]

        for line in text.splitlines():
            clean = line.strip()
            if clean.startswith("#"):
                clean = clean.lstrip("#").strip()
            clean = self._clean_title(clean)
            if self._looks_like_title(clean):
                return clean[:140]
        return source.stem.replace("_", " ").replace("-", " ").strip().title()

    def _clean_title(self, text: str) -> str:
        text = text.strip().strip('"').strip("'")
        text = re.sub(r"\.md$", "", text, flags=re.IGNORECASE)
        return text.strip()

    def _looks_like_title(self, text: str) -> bool:
        if len(text) < 5 or len(text) > 180:
            return False
        lowered = text.lower()
        bad_prefixes = (">", "-", "*", "|", "title:", "uuid:", "date_created:", "status:", "series:")
        bad_tokens = ("media_callout", "[!abstract]", "[!info]", "coming soon", "download", "podcast")
        if lowered.startswith(bad_prefixes):
            return False
        if any(token in lowered for token in bad_tokens):
            return False
        return True

    def _extract_paper_id(self, source: Path, text: str) -> str:
        match = re.search(r"\b(GTQ[-_ ]?\d+[A-Z]?)\b", source.stem + "\n" + text, re.IGNORECASE)
        if match:
            return match.group(1).replace("_", "-").replace(" ", "-").upper()
        return source.stem

    def _paragraphs(self, text: str) -> list[str]:
        parts = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n+", text)]
        return [p for p in parts if len(p) > 80 and not p.startswith("|")]

    def _sentences(self, text: str) -> list[str]:
        compact = re.sub(r"\s+", " ", text)
        pieces = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", compact)
        return [p.strip() for p in pieces if len(p.strip()) > 35]

    def _extract_claims(self, sentences: list[str]) -> list[dict[str, str]]:
        items = []
        for sentence in sentences:
            if any(pattern.search(sentence) for pattern in CLAIM_PATTERNS):
                items.append({"kind": "claim", "text": self._clip(sentence)})
            if len(items) >= 12:
                break
        return items

    def _extract_contradictions(self, sentences: list[str]) -> list[dict[str, str]]:
        items = []
        for sentence in sentences:
            hits = [p.pattern for p in CONTRADICTION_PATTERNS if p.search(sentence)]
            if hits:
                items.append({
                    "status": "suspected",
                    "reason": "contradiction-or-tension language detected",
                    "text": self._clip(sentence),
                })
            if len(items) >= 12:
                break
        return items

    def _extract_math(self, raw: str, clean: str) -> list[dict[str, str]]:
        items: list[dict[str, str]] = []
        seen: set[str] = set()

        for pattern in MATH_BLOCK_PATTERNS:
            for match in pattern.finditer(raw):
                expr = re.sub(r"\s+", " ", match.group(1)).strip()
                self._add_math_item(items, seen, expr, "math_block")

        for line in clean.splitlines():
            stripped = line.strip()
            if len(stripped) < 4 or len(stripped) > 260:
                continue
            if MATH_LINE_PATTERN.search(stripped):
                self._add_math_item(items, seen, stripped, "math_line")
            if len(items) >= 40:
                break
        return items

    def _add_math_item(self, items: list[dict[str, str]], seen: set[str], expr: str, kind: str) -> None:
        if not expr:
            return
        key = expr.lower()
        if key in seen:
            return
        seen.add(key)
        items.append({
            "kind": kind,
            "expression": self._clip(expr, 320),
            "plain_language": "[pending model/human translation]",
            "isomorphism_note": "[pending]",
        })

    def _extract_axioms(self, sentences: list[str]) -> list[dict[str, str]]:
        items = []
        for sentence in sentences:
            if any(pattern.search(sentence) for pattern in AXIOM_PATTERNS):
                items.append({
                    "status": "candidate",
                    "text": self._clip(sentence),
                })
            if len(items) >= 16:
                break
        return items

    def _extract_seven_q(self, sentences: list[str]) -> list[dict[str, str]]:
        items = []
        for sentence in sentences:
            if any(pattern.search(sentence) for pattern in SEVEN_Q_PATTERNS):
                items.append({
                    "status": "candidate",
                    "text": self._clip(sentence),
                })
            if len(items) >= 16:
                break
        return items

    def _executive_summary(
        self,
        title: str,
        paragraphs: list[str],
        claims: list[dict[str, str]],
    ) -> str:
        first = self._clip(paragraphs[0], 260) if paragraphs else f"{title} needs source text before a full summary can be produced."
        second = self._clip(claims[0]["text"], 240) if claims else "The main claim needs review against the extracted claims and evidence."
        third = "The packet separates publishable language from unresolved math, axiom, and contradiction obligations."
        return f"{first} {second} {third}"

    def _plain_english(
        self,
        title: str,
        paragraphs: list[str],
        claims: list[dict[str, str]],
        math_items: list[dict[str, str]],
    ) -> str:
        base = paragraphs[:3] if paragraphs else [title]
        text = " ".join(self._clip(p, 300) for p in base)
        if claims:
            text += " In simpler terms, the article is trying to establish: " + self._clip(claims[0]["text"], 260)
        if math_items:
            text += " The math layer has been extracted separately so equations can be translated and checked without blurring them into the prose."
        return self._clip(text, 1800)

    def _open_obligations(
        self,
        contradictions: list[dict[str, str]],
        math_items: list[dict[str, str]],
        claims: list[dict[str, str]],
        seven_q_items: list[dict[str, str]],
    ) -> list[str]:
        obligations = []
        if contradictions:
            obligations.append("Review suspected contradictions/tensions and mark as resolved, live tension, or true contradiction.")
        if math_items:
            obligations.append("Translate each extracted equation into plain English and verify the isomorphism claim.")
        if claims:
            obligations.append("Attach evidence, axiom links, and falsification criteria to the strongest claims.")
        if seven_q_items:
            obligations.append("Map detected 7QS handles to the exact question slot and mark missing slots.")
        if not obligations:
            obligations.append("Add reviewer notes; deterministic pass found no strong claim, math, or contradiction handles.")
        return obligations

    def _render_markdown(self, packet: ProductionPacket, article_text: str) -> str:
        now = datetime.now().strftime("%Y-%m-%d")
        laws = self._frontmatter_list(packet.axiom_items, "Law")
        axioms = self._frontmatter_list(packet.axiom_items, "Axiom")
        contradiction_state = "contradicted" if packet.contradictions else "hypothesis"
        contradiction_score = 0.35 if packet.contradictions else 1.0

        return "\n".join([
            "---",
            f'title: "{self._yaml_escape(packet.title)}"',
            f'paper_id: "{self._yaml_escape(packet.paper_id)}"',
            'series: "Genesis to Quantum"',
            "status: production_packet",
            "type: paper",
            f"epistemic_state: {contradiction_state}",
            f"laws: {json.dumps(laws, ensure_ascii=False)}",
            f"axioms: {json.dumps(axioms, ensure_ascii=False)}",
            'seven_q: ""',
            "rubric_score: 0.0",
            "verdict: HOLD",
            "fact_check_score: 0.0",
            "math_score: 0.0",
            f"contradiction_score: {contradiction_score}",
            "timeline_score: 0.0",
            "voice_score: 0.0",
            "cross_domain_score: 0.0",
            f"word_count: {len(article_text.split())}",
            "reading_level: 0.0",
            f'created: "{now}"',
            f'updated: "{now}"',
            "author: POF 2828",
            'ai_partners: ["Codex"]',
            'tags: ["production-packet", "needs-review"]',
            "provenance: mixed",
            "depends_on: []",
            "supports: []",
            f"relates_to: {json.dumps([packet.paper_id], ensure_ascii=False)}",
            "contradicts: []",
            "supersedes: []",
            "related: []",
            "---",
            "",
            "> [!metadata] Facts",
            f"> **Paper ID:** {packet.paper_id}",
            "> **Status:** production_packet",
            "> **Type:** paper",
            f"> **Epistemic State:** {contradiction_state}",
            "> **Verdict:** HOLD",
            "> **Composite Score:** 0.0",
            "> **Provenance:** mixed",
            "> **Depends On:** [pending]",
            "> **Supports:** [pending]",
            f"> **Contradicts / Tensions:** {len(packet.contradictions)} suspected",
            "",
            "> [!abstract] Executive Summary",
            f"> {packet.executive_summary}",
            "",
            "## Plain English",
            "",
            packet.plain_english,
            "",
            "## Article",
            "",
            article_text.strip() or "[pending]",
            "",
            "## Academic Summary",
            "",
            "### Abstract",
            "",
            packet.executive_summary,
            "",
            "### Key Claims",
            "",
            self._render_list(packet.claims, "text"),
            "",
            "### Methodology",
            "",
            "[pending reviewer description]",
            "",
            "### Evidence Summary",
            "",
            "[pending evidence links]",
            "",
            "### Limitations",
            "",
            "- Deterministic packet pass; language should be refined by the summary checkpoint.",
            "- Contradictions are suspected tensions until reviewed.",
            "",
            "### Falsification Criteria",
            "",
            self._render_list(packet.axiom_items, "text") if packet.axiom_items else "- [pending]",
            "",
            "> [!info] Cross-References",
            f"> **Laws:** {', '.join(laws) if laws else '[pending]'}",
            f"> **Axioms:** {', '.join(axioms) if axioms else '[pending]'}",
            "> **Related Papers:** [pending]",
            "> **Concepts:** [pending]",
            "> **Depends On:** [pending]",
            "> **Downstream:** [pending]",
            "> **External References:** [pending]",
            f"> **Contradicts / Tensions:** {len(packet.contradictions)} suspected",
            "",
            "> [!example]- Data And Evidence",
            "> | Metric | Score |",
            "> |---|---:|",
            "> | Fact Check | 0.0 |",
            "> | Math | 0.0 |",
            f"> | Contradiction | {contradiction_score} |",
            "> | Timeline | 0.0 |",
            "> | Coherence | 0.0 |",
            "> | Voice | 0.0 |",
            "> | Cross-Domain | 0.0 |",
            "> | Composite | 0.0 |",
            "> | Verdict | HOLD |",
            ">",
            "> **Claim Checks:** see Key Claims",
            ">",
            "> **Math Checks:** see Extracted Math below",
            ">",
            "> **Timeline Checks:** [pending]",
            ">",
            "> **Bibliography:** [pending]",
            "",
            "## Contradiction Audit",
            "",
            self._render_dict_list(packet.contradictions, ["status", "reason", "text"]) if packet.contradictions else "- No suspected contradiction language found in deterministic pass.",
            "",
            "## Extracted Math",
            "",
            self._render_math(packet.math_items),
            "",
            "## Axiom / Claim Map",
            "",
            self._render_dict_list(packet.axiom_items, ["status", "text"]) if packet.axiom_items else "- No explicit axiom/law handles found in deterministic pass.",
            "",
            "## 7QS Handles",
            "",
            self._render_dict_list(packet.seven_q_items, ["status", "text"]) if packet.seven_q_items else "- No explicit 7QS handles found in deterministic pass.",
            "",
            "> [!success] Framework Impact",
            "> **What this establishes:**",
            "> [pending reviewer judgment]",
            ">",
            "> **What this suggests:**",
            "> [pending reviewer judgment]",
            "",
            "> [!warning] Open Obligations",
            "> **What this does NOT prove:**",
            "> This packet does not prove the claims; it prepares the claims, equations, and tensions for review.",
            ">",
            "> **What must be tested next:**",
            "\n".join(f"> - {item}" for item in packet.open_obligations),
            "",
        ])

    def _render_list(self, items: list[dict[str, str]], field: str) -> str:
        if not items:
            return "- [pending]"
        return "\n".join(f"{idx}. {item.get(field, '[pending]')}" for idx, item in enumerate(items, 1))

    def _render_dict_list(self, items: list[dict[str, str]], fields: list[str]) -> str:
        rows = []
        for idx, item in enumerate(items, 1):
            body = "; ".join(f"{field}: {item.get(field, '')}" for field in fields)
            rows.append(f"{idx}. {body}")
        return "\n".join(rows)

    def _render_math(self, items: list[dict[str, str]]) -> str:
        if not items:
            return "- No equations or math-heavy lines found in deterministic pass."
        rows = []
        for idx, item in enumerate(items, 1):
            rows.append(f"{idx}. `{item['expression']}`")
            rows.append(f"   - Plain English: {item['plain_language']}")
            rows.append(f"   - Isomorphism: {item['isomorphism_note']}")
        return "\n".join(rows)

    def _frontmatter_list(self, items: list[dict[str, str]], token: str) -> list[str]:
        found = []
        for item in items:
            text = item.get("text", "")
            if re.search(rf"\b{token}\b", text, re.IGNORECASE):
                found.append(self._clip(text, 70))
        return found[:8]

    def _write_index(self, packets: list[ProductionPacket]) -> None:
        if not packets:
            return
        lines = ["# Production Packet Index", ""]
        for packet in packets:
            rel = Path(packet.output_markdown).name
            lines.append(f"- [{packet.paper_id} - {packet.title}]({rel})")
        (self.output_root / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _slug(self, text: str) -> str:
        slug = re.sub(r"[^A-Za-z0-9._-]+", "-", text.strip()).strip("-")
        return slug or "article"

    def _clip(self, text: str, limit: int = 420) -> str:
        clean = re.sub(r"\s+", " ", text).strip()
        if len(clean) <= limit:
            return clean
        return clean[: limit - 3].rstrip() + "..."

    def _yaml_escape(self, text: str) -> str:
        return text.replace("\\", "\\\\").replace('"', '\\"')
