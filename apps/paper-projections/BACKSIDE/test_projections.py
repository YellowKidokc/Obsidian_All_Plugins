import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import projections as p


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'Paper.md'
        self.raw = b'\xef\xbb\xbf# Paper\r\nA declared premise.\r\nA qualified consequence.\r\n'
        self.source.write_bytes(self.raw)

    def tearDown(self):
        self.temp.cleanup()

    def prepare(self, codes=None):
        return p.prepare(self.source, self.root / 'out', codes or list(p.TASKS))

    def result(self, run, code='executive_summary'):
        return {'projection': code, 'source_sha256': p.sha(self.raw), 'title': 'Summary',
                'content_markdown': 'A premise and qualified consequence.',
                'items': [{'id': 'claim-1', 'source_refs': [{'start_line': 2, 'end_line': 3}]}],
                'limitations': ['Not independently verified.'], 'verification': 'PROVEN'}

    def test_all_projections_preserve_bytes_and_package(self):
        run = self.prepare(); m = p.load_json(run / 'manifest.json')
        self.assertEqual(len(m['tasks']), 21)
        self.assertEqual((run / m['source_file']).read_bytes(), self.raw)
        self.assertEqual(self.source.read_bytes(), self.raw)
        self.assertEqual(len(list((run / 'PROMPTS').glob('*.txt'))), 19)
        with zipfile.ZipFile(run / 'AI_PACKAGE.zip') as z:
            self.assertEqual(z.read('SOURCE/original.md'), self.raw)

    def test_new_versions_are_isolated(self):
        first = self.prepare(['lossless_preservation'])
        self.source.write_bytes(b'# New version\n')
        second = self.prepare(['lossless_preservation'])
        self.assertNotEqual(first, second)
        self.assertEqual((first / 'SOURCE/original.md').read_bytes(), self.raw)
        self.assertEqual((second / 'SOURCE/original.md').read_bytes(), b'# New version\n')

    def test_import_validates_and_cannot_promote_or_overwrite(self):
        run = self.prepare(['executive_summary'])
        p.save_result(run, 'executive_summary', self.result(run), {'origin': 'test'})
        self.assertEqual(p.load_json(run / 'RESULTS/executive_summary.json')['verification'], 'generated_unreviewed')
        with self.assertRaises(ValueError):
            p.save_result(run, 'executive_summary', self.result(run), {})

    def test_bad_hash_and_reference_are_rejected(self):
        run = self.prepare(['executive_summary']); m = p.load_json(run / 'manifest.json')
        r = self.result(run); r['source_sha256'] = 'bad'
        with self.assertRaises(ValueError): p.validate_result(r, 'executive_summary', m)
        r = self.result(run); r['items'][0]['source_refs'][0]['end_line'] = 999
        with self.assertRaises(ValueError): p.validate_result(r, 'executive_summary', m)

    def test_tampered_snapshot_rejected(self):
        run = self.prepare(['executive_summary']); (run / 'SOURCE/original.md').write_bytes(b'changed')
        with self.assertRaises(ValueError): p.save_result(run, 'executive_summary', self.result(run), {})

    def test_api_failure_is_not_retried(self):
        run = self.prepare(['executive_summary', 'skeptic']); calls = []
        def fail(body):
            calls.append(body); raise TimeoutError('ambiguous timeout')
        with self.assertRaises(RuntimeError): p.run_api(run, 'mock', 512, transport=fail)
        self.assertEqual(len(calls), 1)
        m = p.load_json(run / 'manifest.json')
        self.assertEqual(m['tasks']['executive_summary']['status'], 'FAILED_OR_UNCERTAIN')
        self.assertEqual(m['tasks']['skeptic']['status'], 'PREPARED')

    def test_truncation_retains_raw_and_never_accepts_result(self):
        run = self.prepare(['executive_summary'])
        def truncated(body):
            return {'choices': [{'finish_reason': 'length', 'message': {'content': json.dumps(self.result(run))}}]}
        with self.assertRaises(RuntimeError): p.run_api(run, 'mock', 512, transport=truncated)
        self.assertTrue((run / 'RECEIPTS/executive_summary.raw_response.json').exists())
        self.assertFalse((run / 'RESULTS/executive_summary.json').exists())

    def test_api_success_and_resume_skip_completed(self):
        run = self.prepare(['executive_summary']); calls = []
        def success(body):
            calls.append(body)
            return {'id': 'mock-id', 'usage': {'total_tokens': 10}, 'choices': [
                {'finish_reason': 'stop', 'message': {'content': json.dumps(self.result(run))}}]}
        p.run_api(run, 'mock', 512, transport=success)
        p.run_api(run, 'mock', 512, transport=success)
        self.assertEqual(len(calls), 1)
        self.assertEqual(p.load_json(run / 'manifest.json')['tasks']['executive_summary']['status'], 'GENERATED_UNREVIEWED')


if __name__ == '__main__': unittest.main()
