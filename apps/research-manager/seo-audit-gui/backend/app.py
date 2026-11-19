from __future__ import annotations

from typing import List, Optional
from pathlib import Path
import re
import json

from fastapi import FastAPI
from pydantic import BaseModel, Field
from yaml import safe_load

app = FastAPI(title="Faith Thru Physics SEO Audit API", version="0.1.0")


class MediaHint(BaseModel):
    type: Optional[str] = None
    kind: Optional[str] = None
    subtype: Optional[str] = None


class PagePayload(BaseModel):
    pagePath: str = Field(..., description="Path to markdown/html page")
    canonicalUrl: Optional[str] = None
    pageType: str = "article"
    series: Optional[str] = None
    seriesSlug: Optional[str] = None
    pageTitle: Optional[str] = None
    h1: Optional[str] = None
    h2: Optional[str] = None
    metaTitle: Optional[str] = None
    metaDescription: Optional[str] = None
    schemaType: Optional[str] = None
    media: Optional[List[MediaHint]] = None
    text: Optional[str] = None


class AuditResponse(BaseModel):
    auditId: str
    status: str
    score: dict
    titleVariantIdeas: list
    descriptionVariants: list
    issues: list
    recommendations: list
    schemaRecommendations: dict
    reviewFlags: list
    suggestedCanonicalPath: Optional[str] = None


def _parse_frontmatter(markdown_text: str):
    if not markdown_text.startswith("---"):
        return {}, markdown_text
    end = markdown_text.find("---", 3)
    if end == -1:
        return {}, markdown_text
    raw = markdown_text[3:end]
    body = markdown_text[end + 3 :]
    try:
        fm = safe_load(raw) or {}
    except Exception:
        fm = {}
    return fm, body


def _safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


def _extract_h1(body: str) -> str:
    # first markdown h1 or markdown title
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line.lstrip("# ").strip()
        if line.startswith("## "):
            continue
    # fallback maybe HTML h1
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, flags=re.IGNORECASE | re.S)
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""


def _read_markdown(path: str):
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="ignore")
    fm, body = _parse_frontmatter(text)
    extracted = {
        "pageTitle": fm.get("title") or fm.get("name"),
        "h1": fm.get("headline") or fm.get("h1") or _extract_h1(body),
        "metaTitle": fm.get("metaTitle") or fm.get("ogTitle") or fm.get("title"),
        "metaDescription": fm.get("metaDescription") or fm.get("description"),
        "schemaType": fm.get("schemaType") or fm.get("type"),
        "canonicalUrl": fm.get("canonical"),
        "text": body.strip(),
    }
    return p, extracted


def _score(values: dict):
    pageTitle = values.get("pageTitle") or ""
    h1 = values.get("h1") or ""
    meta_title = values.get("metaTitle") or ""
    meta_desc = values.get("metaDescription") or ""
    canonical = values.get("canonicalUrl") or ""
    schema = values.get("schemaType") or ""
    body = values.get("text") or ""
    media_count = int(values.get("media_count") or 0)

    issues = []
    review_flags = []

    title_score = 0
    if pageTitle:
        if 12 <= len(pageTitle) <= 65:
            title_score = 20
        elif len(pageTitle) <= 80:
            title_score = 16
        else:
            title_score = 10
            issues.append({"severity": "low", "id": "TITLE_LONG", "message": "Page title is long; shorten for SEO."})
    else:
        issues.append({"severity": "high", "id": "TITLE_MISSING", "message": "No page title found in frontmatter or payload."})

    h1_score = 0
    if h1:
        if 6 <= len(h1) <= 70:
            h1_score = 20
        else:
            h1_score = 12
            issues.append({"severity": "low", "id": "H1_LENGTH", "message": "Adjust H1 length for readability."})
    else:
        issues.append({"severity": "high", "id": "H1_MISSING", "message": "No H1 found; required for heading structure."})

    if pageTitle and h1 and _safe_slug(pageTitle) != _safe_slug(h1) and all(t in _safe_slug(h1) for t in _safe_slug(pageTitle).split("-")[:2]):
        pass

    meta_title_score = 0
    if meta_title:
        if 30 <= len(meta_title) <= 65:
            meta_title_score = 15
        elif len(meta_title) <= 80:
            meta_title_score = 10
        else:
            issues.append({"severity": "low", "id": "META_TITLE_LONG", "message": "Meta title is long."})
            meta_title_score = 8
    else:
        issues.append({"severity": "medium", "id": "META_TITLE_MISSING", "message": "Meta title missing; add og:title + title tag."})

    desc_score = 0
    if 120 <= len(meta_desc) <= 160:
        desc_score = 15
    elif 80 <= len(meta_desc) < 120 or 160 < len(meta_desc) <= 220:
        desc_score = 10
        issues.append({"severity": "low", "id": "META_DESC_LENGTH", "message": "Meta description length should be near 150 chars."})
    elif not meta_desc:
        issues.append({"severity": "medium", "id": "META_DESC_MISSING", "message": "Meta description missing."})

    url_score = 0
    if canonical and "faiththruphysics.com" in canonical:
        url_score = 10
    elif canonical:
        url_score = 6
        issues.append({"severity": "low", "id": "CANONICAL_URL", "message": "Use canonical URL on faiththruphysics.com if possible."})
    else:
        issues.append({"severity": "low", "id": "CANONICAL_MISSING", "message": "Canonical URL missing."})

    schema_score = 10 if schema in {"Article", "BlogPosting", "PodcastEpisode", "VideoObject", "CollectionPage"} else 4
    if schema and schema not in {"Article", "BlogPosting", "PodcastEpisode", "VideoObject", "CollectionPage"}:
        issues.append({"severity": "low", "id": "SCHEMA_UNKNOWN", "message": "Use a supported schema type (Article/PodcastEpisode/VideoObject)."})

    media_score = 10 if media_count > 0 else 0
    if media_count == 0:
        review_flags.append("NO_MEDIA_METADATA")

    words = len(re.findall(r"\b\w+\b", body))
    content_score = 10 if words >= 450 else 5 if words >= 200 else 2
    if words < 200:
        issues.append({"severity": "low", "id": "CONTENT_SHORT", "message": "Consider richer page body content for better topical depth."})

    score = {
        "overall": int(title_score + h1_score + meta_title_score + desc_score + url_score + schema_score + media_score + content_score),
        "title": title_score,
        "h1": h1_score,
        "meta": meta_title_score,
        "description": desc_score,
        "url": url_score,
        "schema": schema_score,
        "media": media_score,
        "content": content_score,
        "words": words,
    }

    if score["overall"] >= 82:
        status = "green"
    elif score["overall"] >= 65:
        status = "yellow"
    else:
        status = "red"

    # title variants
    clean_title = pageTitle or ""
    series = values.get("series") or ""
    variants = [
        f"{clean_title} | Faith Thru Physics",
        f"{series + ': ' if series else ''}{clean_title}",
        f"{clean_title} | Deep Dive" if clean_title else "",
        f"{clean_title} | {values.get('series', 'Series')} | Faith Thru Physics" if clean_title else "",
    ]

    desc_var = [
        meta_desc,
        f"{clean_title}: a focused page in the {series + ' series' if series else 'Faith Thru Physics'}.",
    ]
    if media_count:
        t = "Audio/video assets" if media_count > 1 else "Primary media"
        desc_var.append(f"Includes {t.lower()} plus contextual notes and references.")

    recommendations = []
    if any(i.get("severity") == "high" for i in issues):
        recommendations.append("Resolve high severity items before publish.")
    if "NO_MEDIA_METADATA" in review_flags:
        recommendations.append("Attach page or series media metadata explicitly.")
    recommendations.append("Keep a short, descriptive og:description aligned with visible page heading.")

    schema_target = schema or "Article"
    schema_reco = {
        "shouldSet": True,
        "type": schema_target,
        "note": "Use PodcastEpisode only for podcast/audio-first pages and VideoObject for standalone video-first pages."
    }

    return score, status, issues, recommendations, review_flags, {
        "titleVariantIdeas": [v for v in variants if v],
        "descriptionVariants": [v for v in desc_var if v],
        "schemaRecommendations": schema_reco,
    }


@app.get("/api/health")
def health():
    return {"ok": True, "service": "seo-audit-api"}


@app.post("/api/audit/page", response_model=AuditResponse)
def audit_page(payload: PagePayload):
    p = Path(payload.pagePath)
    values = payload.dict()

    if p.exists():
        _, extracted = _read_markdown(payload.pagePath)
        for k, v in extracted.items():
            if v:
                values[k] = v

    if values.get("text") is None and payload.text:
        values["text"] = payload.text
    media_count = len(payload.media or [])
    values["media_count"] = media_count

    score, status, issues, recs, flags, body = _score(values)

    audit_id = f"seo-audit-{_safe_slug(values.get('pageTitle') or p.stem)}-{p.stat().st_mtime_ns if p.exists() else 0}"

    # simple canonical fallback
    suggestion = values.get("canonicalUrl")
    if not suggestion:
        suggestion = f"/{_safe_slug(values.get('series') or p.parent.name)}/{p.stem}"

    return AuditResponse(
        auditId=audit_id,
        status=status,
        score=score,
        titleVariantIdeas=body["titleVariantIdeas"],
        descriptionVariants=body["descriptionVariants"],
        issues=issues,
        recommendations=recs,
        schemaRecommendations=body["schemaRecommendations"],
        reviewFlags=flags,
        suggestedCanonicalPath=suggestion,
    )


@app.post("/api/audit/batch")
def audit_batch(pages: List[PagePayload]):
    payloads = [json.loads(audit_page(p).json()) for p in pages]
    total = sum(p["score"]["overall"] for p in payloads)
    avg = round(total / len(payloads), 1) if payloads else 0
    return {
        "count": len(payloads),
        "averageScore": avg,
        "items": payloads,
    }
