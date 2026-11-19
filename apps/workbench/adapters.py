"""Offline projection, human-review and typed-ledger adapters."""
import io
import json
import sys
import zipfile
from tempfile import TemporaryDirectory
from pathlib import Path

from index import APPS, VERSION, contained, create, digest, timestamp

sys.path.insert(0, str(APPS / 'paper-projections' / 'BACKSIDE'))
import projections

LEDGER_TYPES = {
    'claim', 'premise', 'proof', 'evidence', 'objection', 'boundary', 'falsifier',
    'lean', 'audit', 'definition', 'equation', 'assumption', 'deduction',
    'empirical_support', 'structural_correspondence', 'proposal',
}


def json_bytes(payload):
    return (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode()


def prepare(index, paper, actor, codes):
    raw = index.source(paper)
    with TemporaryDirectory() as scratch:
        original = Path(scratch) / Path(paper['path']).name
        original.write_bytes(raw)
        run = projections.prepare(original, Path(scratch) / 'runs', codes)
        manifest = projections.load_json(run / 'manifest.json')
        manifest.update(source_path=paper['path'], paper_id=paper['id'], actor=actor)
        destination = index.state / 'projections' / run.name
        for item in run.rglob('*'):
            if item.is_file() and item.name not in {'manifest.json', 'AI_PACKAGE.zip'}:
                create(destination / item.relative_to(run), item.read_bytes())
    create(destination / 'manifest.json', json_bytes(manifest))
    schema = Path(__file__).with_name('projection-result.schema.json')
    create(destination / 'projection-result.schema.json', schema.read_bytes())
    if 'ai_package' in manifest['tasks']:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
            for item in sorted(destination.rglob('*')):
                if item.is_file():
                    archive.write(item, item.relative_to(destination).as_posix())
        create(destination / 'AI_PACKAGE.zip', buffer.getvalue())
    run_record = index.record('runs', paper, actor,
                              {'run_id': run.name, 'path': destination.relative_to(index.state).as_posix(),
                               'tasks': list(manifest['tasks']), 'mode': 'offline'},
                              engine='paper-projections', prompt=VERSION)
    for code, task in manifest['tasks'].items():
        if task['execution'] == 'local':
            artifact = destination / ('AI_PACKAGE.zip' if code == 'ai_package' else manifest['source_file'])
            task_receipt(index, paper, actor, run_record, code, artifact, 'local')
        else:
            index.record('tasks', paper, actor, {'task': code, 'status': 'present_unverified'},
                         engine='paper-projections', prompt=VERSION)
    return destination


def task_receipt(index, paper, actor, run_record, code, artifact, engine):
    run_id = run_record['data']['run_id']
    receipt = artifact.parent / f'{code}.receipt.json'
    data = dict(run_id=run_id, task=code, engine=engine, recorded_at=timestamp(), actor=actor,
                paper_id=paper['id'], document_id=paper['document_id'],
                identity_match='declared' if paper['document_id'] else 'unresolved',
                source_sha256=paper['sha256'], artifact=artifact.relative_to(index.state).as_posix(),
                artifact_sha256=digest(artifact.read_bytes()), status='done')
    create(receipt, json_bytes(data))
    index.record('artifacts', paper, actor, data, engine=engine, validation='validated')
    index.record('tasks', paper, actor, dict(data, receipt=receipt.relative_to(index.state).as_posix(),
                                             receipt_sha256=digest(receipt.read_bytes())),
                 engine=engine, prompt=VERSION, validation='validated')


def import_projection(index, snapshot, run_id, actor, response):
    run_record = next((record for record in snapshot['records'] if record['kind'] == 'runs'
                       and record['data'].get('run_id') == run_id and record['current']), None)
    if not run_record:
        raise ValueError('Choose a current prepared run')
    paper = index.paper(run_record['paper_id'], snapshot)
    folder = contained(index.state, run_record['data']['path'])
    manifest = projections.load_json(folder / 'manifest.json')
    projections.check_snapshot(folder, manifest)
    result = json.loads(response)
    if not isinstance(result, dict):
        raise ValueError('Projection must be a JSON object')
    code = result.get('projection')
    if not isinstance(code, str) or manifest['tasks'].get(code, {}).get('execution') != 'api':
        raise ValueError('Projection was not prepared for this run')
    if result.get('finish_reason') not in (None, 'stop') or result.get('truncated', False) is not False:
        raise ValueError('Incomplete projection')
    result = projections.validate_result(result, code, manifest)
    if any(not isinstance(item.get('text'), str) or not item['text'].strip() for item in result['items']):
        raise ValueError('Each projection item needs text')
    lines = index.source(paper).decode('utf-8-sig').splitlines()
    for item in result['items']:
        for ref in item['source_refs']:
            excerpt = '\n'.join(lines[ref['start_line'] - 1:ref['end_line']])
            if 'quote' in ref and (not isinstance(ref['quote'], str) or not ref['quote']
                                   or ref['quote'] not in excerpt):
                raise ValueError('A quote does not match its source span')
    artifact = folder / 'RESULTS' / f'{code}.json'
    create(artifact, json_bytes(result))
    task_receipt(index, paper, actor, run_record, code, artifact, 'manual-import')
    return artifact


def review_target(index, paper, render_html=False, artifact_id=None):
    raw = index.source(paper)
    name = 'source'
    if artifact_id:
        record = next((r for r in index.current()['records'] if r['id'] == artifact_id
                       and r['kind'] == 'artifacts' and r['current'] and r['paper_id'] == paper['id']), None)
        if not record:
            raise ValueError('Choose a current projection artifact from this paper')
        artifact = contained(index.state, record['data']['artifact'])
        result = artifact.read_bytes()
        if artifact.suffix != '.json' or digest(result) != record['data']['artifact_sha256']:
            raise ValueError('Review requires a verified projection result')
        raw = json.loads(result)['content_markdown'].encode()
        name = 'projection-' + artifact_id
    content = raw
    kind = 'md'
    if render_html:
        from html import escape

        body = escape(raw.decode('utf-8-sig'))
        content = f'<!doctype html><meta charset="utf-8"><title>Source review</title><pre>{body}</pre>'.encode()
        kind = 'html'
    path = index.state / 'review' / paper['id'] / paper['sha256'] / f'{name}.{kind}'
    create(path, content)
    return path


def import_review(index, paper, actor, response, span, target):
    payload = json.loads(response)
    if not isinstance(payload, dict) or payload.get('decision') not in {'approved', 'annotated', 'dismissed'}:
        raise ValueError('Expected a Plannotator annotate --json decision')
    folder = index.state / 'review' / paper['id'] / paper['sha256']
    target = Path(target).absolute()
    if target.parent != folder or target.suffix not in {'.md', '.html'}:
        raise ValueError('Choose an exported review target for this source version')
    if target.stem != 'source' and not target.stem.startswith('projection-'):
        raise ValueError('Unknown review target kind')
    if payload.get('target') != str(target):
        raise ValueError('Decision target differs from the versioned review file')
    artifact = target.stem.removeprefix('projection-') if target.stem != 'source' else None
    if target != review_target(index, paper, target.suffix == '.html', artifact):
        raise ValueError('Review target must match its exported bytes')
    feedback = payload.get('feedback', '')
    if not isinstance(feedback, str):
        raise ValueError('Invalid feedback')
    event = index.record('reviews', paper, actor,
                         {'decision': payload['decision'], 'feedback': feedback,
                          'target': target.relative_to(index.state).as_posix(),
                          'target_sha256': digest(target.read_bytes()), 'projection_artifact_id': artifact,
                          'status': 'human_review'},
                         engine='plannotator-manual', locator=span, validation='recorded')
    log = index.state / 'review' / paper['id'] / 'AI Review Log' / f"{event['id']}.md"
    text = (f"# AI Review Log entry\n\n{actor} · {event['provenance']['recorded_at']}\n\n"
            f"Source SHA-256 `{paper['sha256']}` · Lines {span[0]}–{span[1]}\n\n"
            f"Review outcome **{payload['decision']}**\n\n{feedback}\n")
    create(log, text.encode())
    return log


def add_ledger(index, paper, actor, payload, span):
    if not isinstance(payload, dict) or payload.get('type') not in LEDGER_TYPES:
        raise ValueError('Unknown ledger type')
    if not isinstance(payload.get('text'), str) or not payload['text'].strip():
        raise ValueError('A ledger item needs text')
    return index.record('ledger', paper, actor, payload, engine='manual-ledger', locator=span)


def record_artifact(index, actor, path, kind):
    artifact = dict(path=path.relative_to(index.state).as_posix(), kind=kind,
                    actor=actor, sha256=digest(path.read_bytes()), created_at=timestamp())
    create(path.with_name(path.name + '.receipt.json'), json_bytes(artifact))
    return artifact


def preview_ingest(index, relative, actor):
    """Run the installed ingestion component's local parsers on a copied file."""
    try:
        from orchestrator import IngestOrchestrator
    except ModuleNotFoundError as error:
        raise ValueError('Install apps/ingest-engine into the workbench Python environment') from error

    source = contained(index.root, relative)
    if not source.is_file():
        raise ValueError('Select one local source file')
    raw = source.read_bytes()
    with TemporaryDirectory() as scratch:
        copied = Path(scratch) / source.name
        copied.write_bytes(raw)
        engine = IngestOrchestrator()
        try:
            preview = engine.preview(str(copied))
        finally:
            engine.close()
        if 'error' in preview:
            raise ValueError(preview['error'])
        # Keep the selected address in the receipt and remove the temporary mirror path.
        for key in ('file', 'file_path', 'source'):
            if key in preview and preview[key] == str(copied):
                preview[key] = source.relative_to(index.root).as_posix()
    return {'schema_version': VERSION, 'status': 'candidate', 'actor': actor,
            'engine': 'theophysics-ingest/1.0.0', 'recorded_at': timestamp(),
            'source_path': source.relative_to(index.root).as_posix(),
            'source_sha256': digest(raw), 'preview': preview}
