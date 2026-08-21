# SEO Audit GUI (Draft)

This folder contains a lightweight local API + web UI to generate structured SEO recommendations for
content pages in the Faith Thru Physics workflow.

## Start

1. Install backend deps:

- python -m venv .venv
- .\.venv\Scripts\Activate.ps1
- pip install -r backend\\requirements.txt

2. Run API:

- uvicorn backend.app:app --reload --host 127.0.0.1 --port 8080

3. Open UI:

- Load `frontend/index.html` directly in a browser, or serve it any way you prefer.

## Endpoints

- `POST /api/audit/page` (single page payload)
- `POST /api/audit/batch` (multiple pages at once)
- `GET /api/health`

## Output

- JSON response includes score breakdown + title/description variants + review flags.
- Designed to support review workflow:
  - green: clean
  - yellow: minor cleanup
  - red: needs review

## Notes

- This is a conservative starter. It does not replace legal/content review.
- For page inheritance or media source validation, pass explicit context in payload.
