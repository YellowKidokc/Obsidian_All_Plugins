import tempfile
import unittest
from pathlib import Path
from quantum import Library, demo, run_action, action_list


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

    def test_actions_run_by_name_and_undo_moves_back(self):
        names = {a['name'] for a in action_list()}
        self.assertTrue({'move', 'show', 'undo', 'reconcile'} <= names)
        self.assertNotIn('fn', action_list()[0])
        run_action(self.library, 'move', {'paper': self.paper['id'], 'vault': 'Writing', 'folder': 'Papers'})
        self.assertEqual(self.library.paper(self.paper['id'])['vault'], self.writing)
        result = run_action(self.library, 'undo', {})
        self.assertEqual(result['paper'], self.paper['id'])
        self.assertEqual(self.library.paper(self.paper['id'])['path'], 'Papers/One paper.md')
        self.assertNotEqual(self.library.paper(self.paper['id'])['vault'], self.writing)
        with self.assertRaises(ValueError):
            run_action(self.library, 'undo', {})
        with self.assertRaises(ValueError):
            run_action(self.library, 'move', {'paper': self.paper['id']})

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


class UpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.library = Library(self.temp.name)
        demo(self.library)
        lib = self.library
        self.research = lib.find_vault('Research')
        self.writing = lib.find_vault('Writing')
        self.ids = []
        for name in ['a.md', 'b.md', 'c.md']:
            lib.resolve(self.research, 'Ideas/' + name).write_text(f'# {name}\n', encoding='utf-8')
            self.ids.append(lib.register(self.research, 'Ideas/' + name))

    def test_batch_move_moves_all(self):
        moved = self.library.batch_move(self.ids, self.writing, 'Ideas')
        self.assertEqual(moved, self.ids)
        for pid in self.ids:
            self.assertEqual(self.library.paper(pid)['vault'], self.writing)
            self.assertTrue(self.library.read(pid).startswith('# '))
        self.assertEqual(list(self.library.resolve(self.research, 'Ideas').glob('*.md')), [])

    def test_batch_move_is_all_or_nothing(self):
        blocker = self.library.resolve(self.writing, 'Ideas/c.md')
        blocker.write_text('keep me', encoding='utf-8')
        with self.assertRaises(FileExistsError):
            self.library.batch_move(self.ids, self.writing, 'Ideas')
        self.assertEqual(blocker.read_text(encoding='utf-8'), 'keep me')
        self.assertFalse(self.library.resolve(self.writing, 'Ideas/a.md').exists())
        for pid in self.ids:
            self.assertEqual(self.library.paper(pid)['vault'], self.research)

    def test_move_folder(self):
        moved = self.library.move_folder(self.research, 'Ideas', self.writing, 'Papers')
        self.assertEqual(set(moved), set(self.ids))

    def test_batch_register(self):
        self.assertEqual(self.library.batch_register(self.research, ['Ideas/a.md', 'Ideas\\b.md']), self.ids[:2])

    def test_reconcile_moved_stale_new_restored(self):
        lib = self.library
        lib.resolve(self.research, 'Ideas/a.md').rename(lib.resolve(self.research, 'Papers/a.md'))
        gone = lib.resolve(self.research, 'Ideas/b.md')
        saved = gone.read_bytes()
        gone.unlink()
        lib.resolve(self.research, 'Papers/fresh.md').write_text('# fresh\n', encoding='utf-8')
        report = lib.reconcile(self.research)
        self.assertEqual(report['moved'][0]['to'], 'Papers/a.md')
        self.assertEqual(lib.read(self.ids[0]), '# a.md\n')
        self.assertEqual([s['id'] for s in report['stale']], [self.ids[1]])
        self.assertEqual(lib.paper(self.ids[1])['status'], 'stale')
        self.assertEqual([n['path'] for n in report['new']], ['Papers/fresh.md'])
        gone.write_bytes(saved)
        self.assertEqual(lib.reconcile(self.research)['restored'], [self.ids[1]])
        self.assertEqual(lib.paper(self.ids[1])['status'], 'active')

    def test_reconcile_does_not_guess_between_duplicates(self):
        lib = self.library
        src = lib.resolve(self.research, 'Ideas/a.md')
        (lib.resolve(self.research, 'Papers') / 'a.md').write_bytes(src.read_bytes())
        (lib.resolve(self.research, '') / 'a.md').write_bytes(src.read_bytes())
        src.unlink()
        report = lib.reconcile(self.research)
        self.assertEqual(len(report['ambiguous']), 1)
        self.assertEqual(report['moved'], [])

    def test_tangent_is_a_paper(self):
        lib = self.library
        lib.save(self.ids[0], '# Displacement data\n\nProhibition and the War on Drugs.\n')
        tid = lib.create_tangent(self.ids[0], 'historical')
        self.assertEqual(lib.create_tangent(self.ids[0], 'historical'), tid)
        self.assertEqual(lib.tangent(tid)['paper'], self.ids[0])
        lib.link_tangent(tid, self.ids[1], 0.9)
        lib.link_tangent(tid, self.ids[2], 0.4)
        self.assertEqual([t['id'] for t in lib.tangent_search('war drugs')], [tid])
        self.assertEqual(lib.tangent_search('soviet'), [])
        self.assertEqual(lib.tangents_for(self.ids[1])['referenced'][0]['id'], tid)
        with self.assertRaises(ValueError):
            lib.link_tangent('nope', self.ids[1])

    def test_cross_drive_move_without_hard_links(self):
        import os
        from unittest import mock
        with mock.patch.object(os, 'link', side_effect=OSError(18, 'Invalid cross-device link')):
            self.library.move(self.ids[0], self.writing, 'Papers')
        self.assertEqual(self.library.read(self.ids[0]), '# a.md\n')
        self.assertFalse(self.library.resolve(self.research, 'Ideas/a.md').exists())
        leftovers = [p for p in Path(self.temp.name).rglob('*') if p.name.endswith('.moving')]
        self.assertEqual(leftovers, [])

    def test_export_import_roundtrip(self):
        backup = Path(self.temp.name) / 'backup.json'
        counts = self.library.export_registry(backup)
        self.assertEqual(counts['papers'], 5)
        fresh = Library(Path(self.temp.name) / 'other-state')
        fresh.import_registry(backup)
        self.assertEqual(fresh.read(self.ids[0]), '# a.md\n')

    def test_history_records_who_moved_what(self):
        lib = self.library
        claude = Library(self.temp.name, actor='claude-terminal-3')
        claude.move(self.ids[0], self.writing, 'Papers')
        with lib.acting_as('gpt-agent'):
            lib.batch_move(self.ids[1:], self.writing, 'Ideas')
        # someone moves a file by hand, reconcile notices
        lib.resolve(self.writing, 'Ideas/b.md').rename(lib.resolve(self.writing, 'Papers/b.md'))
        lib.reconcile(self.writing)
        moves = {(e['paper'], e['action']): e for e in lib.history(limit=500)}
        first = moves[(self.ids[0], 'move')]
        self.assertEqual(first['actor'], 'claude-terminal-3')
        self.assertEqual((first['source'], first['target']), ('Research:Ideas/a.md', 'Writing:Papers/a.md'))
        self.assertEqual(moves[(self.ids[2], 'batch-move')]['actor'], 'gpt-agent')
        ext = moves[(self.ids[1], 'external-move')]
        self.assertTrue(ext['actor'].startswith('external'))
        self.assertEqual(ext['target'], 'Writing:Papers/b.md')
        self.assertEqual([e['action'] for e in lib.history(self.ids[1])][:2], ['external-move', 'batch-move'])

    def test_portable_roots(self):
        state = Path(self.temp.name) / 'portable'
        vault = state / 'vaults' / 'V'
        (vault / 'P').mkdir(parents=True)
        (vault / 'P' / 'x.md').write_text('# x\n', encoding='utf-8')
        lib = Library(state)
        vid = lib.add_vault('V', vault, portable=True)
        pid = lib.register(vid, 'P/x.md')
        with lib.connect() as db:
            self.assertEqual(db.execute('SELECT root FROM vaults').fetchone()['root'], 'vaults/V')
        self.assertEqual(lib.add_vault('V', str(vault).replace('/', '\\')), vid)
        moved = Path(self.temp.name) / 'moved'
        state.rename(moved)
        self.assertEqual(Library(moved).read(pid), '# x\n')


if __name__ == '__main__':
    unittest.main()
