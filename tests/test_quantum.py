import tempfile
import unittest
from pathlib import Path
from quantum import Library, demo


class QuantumTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.library = Library(self.temp.name)
        demo(self.library)
        self.snapshot = self.library.snapshot()
        self.paper = next(p for p in self.snapshot['papers'] if p['path'].endswith('One paper.md'))
        self.writing = next(v['id'] for v in self.snapshot['vaults'] if v['name'] == 'Writing')

    def test_shared_edit_and_cross_vault_move_preserve_identity_and_link(self):
        paper_id = self.paper['id']
        self.library.save(paper_id, '# Edited from a shared location')
        self.assertEqual(self.library.read(paper_id), '# Edited from a shared location')
        old_path = self.library.resolve(self.paper['vault'], self.paper['path'])
        self.library.move(paper_id, self.writing, 'Papers')
        self.assertFalse(old_path.exists())
        self.assertEqual(self.library.read(paper_id), '# Edited from a shared location')
        linked_note = next(p for p in self.snapshot['papers'] if p['id'] != paper_id)
        self.assertIn('#paper=' + paper_id, self.library.read(linked_note['id']))
        self.assertEqual(self.library.snapshot()['locations'][0]['paper'], paper_id)
        restored = Library(self.temp.name)
        self.assertEqual(restored.read(paper_id), '# Edited from a shared location')
        self.assertEqual(len(list(Path(self.temp.name).rglob('One paper.md'))), 1)

    def test_move_never_overwrites(self):
        target = self.library.resolve(self.writing, 'Papers/One paper.md')
        target.write_text('Existing content')
        with self.assertRaises(FileExistsError):
            self.library.move(self.paper['id'], self.writing, 'Papers')
        self.assertEqual(target.read_text(), 'Existing content')
        self.assertTrue(self.library.read(self.paper['id']))

    def test_vault_boundary_and_idempotent_membership(self):
        with self.assertRaises(ValueError):
            self.library.resolve(self.writing, '../../outside.md')
        self.library.show_here(self.paper['id'], self.writing, 'Ideas')
        self.assertEqual(len(self.library.snapshot()['locations']), 1)

    def test_greek_and_math_survive_read_and_save(self):
        text = '# Master Equation\n\nχ(X) = C_W[∏ Xᵢ] — grace ≠ entropy\n'
        file = self.library.resolve(self.paper['vault'], self.paper['path'])
        file.write_bytes(text.encode('utf-8'))
        self.assertEqual(self.library.read(self.paper['id']), text)
        self.library.save(self.paper['id'], text + 'added χ\n')
        self.assertEqual(file.read_bytes(), (text + 'added χ\n').encode('utf-8'))
        self.assertEqual([p.name for p in file.parent.iterdir() if p.name.endswith('.saving')], [])

    def test_failed_save_leaves_the_paper_whole(self):
        file = self.library.resolve(self.paper['vault'], self.paper['path'])
        before = file.read_bytes()
        with self.assertRaises(UnicodeEncodeError):
            self.library.save(self.paper['id'], 'broken \ud800 text')
        self.assertEqual(file.read_bytes(), before)

    def test_non_utf8_paper_is_refused_not_garbled(self):
        file = self.library.resolve(self.paper['vault'], self.paper['path'])
        file.write_bytes(b'caf\xe9 \x8f')
        with self.assertRaises(ValueError):
            self.library.read(self.paper['id'])
        self.assertEqual(file.read_bytes(), b'caf\xe9 \x8f')

    def test_one_file_is_one_record_however_it_is_spelled(self):
        vault = self.paper['vault']
        spellings = ['Papers/One paper.md', 'Papers\\One paper.md', './Papers/One paper.md', 'Ideas/../Papers/One paper.md']
        if self.library.resolve(vault, 'PAPERS').is_dir():      # case-insensitive disk (Windows)
            spellings.append('papers/ONE PAPER.md')
        self.assertEqual({self.library.register(vault, s) for s in spellings}, {self.paper['id']})
        for folder in ['Ideas', 'Ideas/', '.\\Ideas']:
            self.library.show_here(self.paper['id'], self.writing, folder)
        self.assertEqual(len(self.library.snapshot()['locations']), 1)


if __name__ == '__main__':
    unittest.main()
