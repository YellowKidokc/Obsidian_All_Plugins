"""Regression checks run against the installed ingest wheel."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from config.settings import DatabaseSettings
from db.schema import IngestSession
from openpyxl import Workbook
from orchestrator import IngestOrchestrator
from sqlalchemy.engine import make_url


class OfflinePreviewTest(unittest.TestCase):
    def test_settings_accept_pg_alias_and_escape_password(self):
        with patch.dict(os.environ, {'PG_HOST': 'fixture.invalid', 'PG_PASSWORD': 'sample@:/?#'}):
            url = make_url(DatabaseSettings(_env_file=None).connection_string)
        self.assertEqual(url.host, 'fixture.invalid')
        self.assertEqual(url.password, 'sample@:/?#')

    def test_preserves_sql_column_name(self):
        session = IngestSession(ingest_metadata={'fixture': True})
        self.assertEqual(session.ingest_metadata, {'fixture': True})
        self.assertIn('metadata', IngestSession.__table__.columns)

    def test_installed_previews(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paper = root / 'Précis.md'
            paper.write_text('# Fixture title\n\nAn example paragraph.', encoding='utf-8')
            table = root / 'Table.html'
            table.write_text('<table><tr><th>Term</th></tr><tr><td>Mass</td></tr></table>', encoding='utf-8')
            workbook = Workbook()
            workbook.active.append(['Term', 'Unit'])
            workbook.active.append(['Mass', 'kg'])
            sheet = root / 'Sheet.xlsx'
            workbook.save(sheet)
            engine = IngestOrchestrator()
            try:
                self.assertIn('Mass', json.dumps(engine.preview(str(table))))
                self.assertIn('Mass', json.dumps(engine.preview(str(sheet))))
            finally:
                engine.close()
            result = subprocess.run(
                [sys.executable, '-m', 'orchestrator', str(paper), '--preview',
                 '--db', 'postgresql://unused.invalid/fixture'],
                capture_output=True, check=True, text=True, cwd=root,
            )
            self.assertIn('Fixture title', result.stdout)
            self.assertNotIn('Database initialized', result.stderr)
