import json
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pytest
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from adapters import add_ledger, import_projection, import_review, prepare, projections, review_target
from index import Index
from navigation import navigation
from views import export
from workbench import handler


@pytest.fixture
def fixture(tmp_path):
    vault = tmp_path / 'Copied vault'
    series = vault / 'Série One'
    series.mkdir(parents=True)
    folder = series / 'Paper Ω'
    folder.mkdir()
    raw = b'---\r\ndocument_id: TEST.01.SAME\r\n---\r\n\r\n# Pilot\r\n\r\nThe sky is clear.\r\n'
    original = folder / 'Same.md'
    original.write_bytes(raw)
    (series / 'Same.md').write_bytes(raw)
    (series / 'Malformed.md').write_text('---\ndocument_id: ???\n---\n')
    (folder / 'API_RUNS').mkdir()
    (vault / '.obsidian').mkdir()
    (vault / '.obsidian' / 'Hidden.md').write_text('Ignore')
    (vault / 'archive').mkdir()
    (vault / 'archive' / 'Old.md').write_text('Ignore')
    (vault / 'Unselected').mkdir()
    (vault / 'Unselected' / 'Other.md').write_text('Ignore')
    outside = tmp_path / 'outside.md'
    outside.write_text('Never inventory')
    if sys.platform != 'win32':
        (vault / 'link.md').symlink_to(outside)
    index = Index(vault, vault / '.backside' / 'workbench')
    index.scan('fixture', ['Unselected'])
    return index, original, raw


def pick(index, original):
    return next(p for p in index.current()['papers'] if p['path'] == original.relative_to(index.root).as_posix())


def test_scan_identity_version_and_missing(fixture):
    index, original, raw = fixture
    first = index.current()
    assert index.scan('fixture', ['Unselected']) == first['id']
    assert len(first['papers']) == 3
    paper = pick(index, original)
    copies = [p for p in first['papers'] if p['sha256'] == paper['sha256']]
    assert len({p['id'] for p in copies}) == 2
    assert len(first['issues']) == 3
    assert index.source(paper) == raw
    event = add_ledger(index, paper, 'fixture', {'type': 'objection', 'text': 'Unresolved'}, [7, 7])
    original.write_bytes(raw + b'And calm.\r\n')
    index.scan('fixture', ['Unselected'])
    assert pick(index, original)['id'] == paper['id']
    assert pick(index, original)['sha256'] != paper['sha256']
    assert next(r for r in index.current()['records'] if r['id'] == event['id'])['current'] is False
    moved = original.with_name('Moved.md')
    original.rename(moved)
    index.scan('fixture', ['Unselected'])
    assert pick(index, original)['availability'] == 'missing'
    assert pick(index, moved)['id'] != paper['id']


def test_navigation_preserves_authored_bytes_and_is_idempotent(fixture):
    index, original, raw = fixture
    nav = original.parent / '_INDEX.md'
    nav.write_bytes(b'Author\r\n<!-- nav:start -->old<!-- nav:end -->\r\nAfter\r\n')
    first_plan = navigation(index, index.current(), 'fixture')
    assert any(op['action'] == 'replace_generated_block' for op in first_plan['changes'])
    assert b'old' in nav.read_bytes()
    navigation(index, index.current(), 'fixture', apply=True)
    assert nav.read_bytes().startswith(b'Author\r\n<!-- nav:start -->')
    assert nav.read_bytes().endswith(b'<!-- nav:end -->\r\nAfter\r\n')
    assert not navigation(index, index.current(), 'fixture')['changes']
    assert original.read_bytes() == raw


def test_projection_receipts_review_and_export_parity(fixture):
    index, original, raw = fixture
    paper = pick(index, original)
    run = prepare(index, paper, 'fixture', list(projections.TASKS))
    manifest = json.loads((run / 'manifest.json').read_bytes())
    assert len(manifest['tasks']) == 21
    assert (run / manifest['source_file']).read_bytes() == raw
    assert sum(t['status'] == 'done' for t in index.current()['processing']) == 2
    payload = dict(projection='contradiction_pass', source_sha256=paper['sha256'],
                   title='Candidate finding', content_markdown='Possible tension',
                   items=[dict(id='a', text='Candidate', source_refs=[dict(start_line=7, end_line=7)])],
                   limitations=['Needs review'])
    with pytest.raises(ValueError):
        import_projection(index, index.current(), run.name, 'fixture', b'{"truncated":')
    with pytest.raises(ValueError):
        import_projection(index, index.current(), run.name, 'fixture', json.dumps(dict(payload, truncated=True)))
    result = import_projection(index, index.current(), run.name, 'fixture', json.dumps(payload))
    assert json.loads(result.read_bytes())['verification'] == 'generated_unreviewed'
    prepare(index, paper, 'fixture', ['contradiction_pass'])
    assert next(t for t in index.current()['processing'] if t['task'] == 'contradiction_pass')['status'] == 'done'
    target = review_target(index, paper, render_html=True)
    decision = json.dumps(dict(decision='annotated', target=str(target), feedback='Clarify the scope'))
    log = import_review(index, paper, 'Fixture reviewer', decision, [7, 7], target)
    assert 'Clarify the scope' in log.read_text()
    report = export(index, index.current(), 'fixture')
    workbook = load_workbook(report / 'workbench.xlsx', read_only=True)
    excel = {label: value for label, value, _ in workbook['Dashboard'].values}
    fis = json.loads((report / 'fis.json').read_bytes())
    for label, value in fis['totals'].items():
        assert excel[label] == value
        assert f'<td>{label}</td><td>{value}</td>' in (report / 'index.html').read_text()
    result.unlink()
    assert any(t['status'] == 'broken' for t in index.current()['processing'])
    assert original.read_bytes() == raw


def test_loopback_browser_flow(fixture):
    from http.server import ThreadingHTTPServer
    from threading import Thread

    index, original, raw = fixture
    paper = pick(index, original)
    row = add_ledger(index, paper, 'fixture', {'type': 'claim', 'text': 'Check the excerpt'}, [7, 7])
    with ThreadingHTTPServer(('127.0.0.1', 0), handler(index)) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f'http://127.0.0.1:{server.server_port}'
        try:
            with urlopen(url + '/api/inventory') as response:
                assert len(json.load(response)['papers']) == 3
            with urlopen(url + f'/?paper={paper["id"]}&record={row["id"]}') as response:
                page = response.read().decode()
                assert '7  The sky is clear.' in page
                assert '1  ---' not in page
            request = Request(url + '/prepare',
                              data=urlencode({'actor': 'fixture', 'paper': paper['id'],
                                              'task': 'lossless_preservation'}).encode(),
                              headers={'Origin': url})
            with urlopen(request) as response:
                assert b'lossless_preservation' in response.read()
            with pytest.raises(HTTPError) as refused:
                urlopen(Request(url + '/prepare', data=b'x=1', headers={'Origin': 'http://other'}))
            assert refused.value.code == 403
        finally:
            server.shutdown()
            thread.join()
    assert original.read_bytes() == raw


def test_cdcm_keeps_axiom_and_cell_denominators_distinct(fixture):
    from analytics import CONSTRAINTS, add_assessment, coherence

    index, original, _ = fixture
    paper = pick(index, original)
    for number in range(4):
        scores = dict.fromkeys(CONSTRAINTS, 1)
        if number == 0:
            scores['empirical'] = -1
        add_assessment(index, index.current(), paper, 'fixture', 'constraints',
                       {'axiom': f'Fixture {number}', 'scores': scores, 'rubric': 'Known-answer fixture'}, [7, 7])
    axiom, cell = [record['data'] for record in coherence(index, index.current(), paper, 'fixture')]
    assert (axiom['numerator'], axiom['denominator'], axiom['value']) == (1, 4, 0.25)
    assert (cell['numerator'], cell['denominator'], cell['value']) == (1, 36, 1 / 36)


def test_typed_graph_uses_current_candidate_edges(fixture):
    from analytics import add_assessment, relationship_graph

    index, original, raw = fixture
    paper = pick(index, original)
    premise = add_ledger(index, paper, 'fixture', {'type': 'premise', 'text': 'First'}, [7, 7])
    claim = add_ledger(index, paper, 'fixture', {'type': 'claim', 'text': 'Second'}, [7, 7])
    add_assessment(index, index.current(), paper, 'fixture', 'relationships',
                   {'source': claim['id'], 'target': premise['id'], 'type': 'depends_on',
                    'rationale': 'Fixture dependency', 'review_state': 'approved'}, [7, 7])
    graph = relationship_graph(index.current(), {paper['id']})
    assert graph['edges'][0]['source'] == claim['id']
    assert graph['edges'][0]['target'] == premise['id']
    assert graph['edges'][0]['review_state'] == 'candidate'
    assert graph['weak_components'] == [sorted([premise['id'], claim['id']])]
    original.write_bytes(raw + b'Changed\r\n')
    index.scan('fixture', ['Unselected'])
    graph = relationship_graph(index.current(), {paper['id']})
    assert graph['edges'] == []
    assert graph['assessment_status'] == 'unassessed'


def test_quantum_registry_identity_survives_a_registered_move(fixture, tmp_path):
    from index import APPS
    sys.path.insert(0, str(APPS / 'quantum'))
    from quantum import Library

    index, original, raw = fixture
    library = Library(tmp_path / 'quantum-state', actor='Fixture owner')
    vault = library.add_vault('Copy', index.root, portable=True)
    paper_id = library.register(vault, original.relative_to(index.root).as_posix())
    library.show_here(paper_id, vault, 'Série One')
    index = Index(index.root, tmp_path / 'workbench-state')
    index.scan('fixture', ['Unselected'], library.db)
    assert pick(index, original)['id'] == paper_id
    assert pick(index, original)['memberships'] == ['Série One']
    (index.root / 'Série One' / 'New folder').mkdir()
    library.move(paper_id, vault, 'Série One/New folder')
    moved = index.root / 'Série One' / 'New folder' / original.name
    assert moved.read_bytes() == raw
    index.scan('fixture', ['Unselected'], library.db)
    assert pick(index, moved)['id'] == paper_id
    assert pick(index, moved)['availability'] == 'present'
    library.move(paper_id, vault, 'Série One/Paper Ω')
    index.scan('fixture', ['Unselected'], library.db)
    assert pick(index, original)['id'] == paper_id
    assert [event['action'] for event in index.current()['quantum_history']].count('move') == 2
    assert original.read_bytes() == raw
