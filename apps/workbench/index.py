"""Versioned, read-only manuscript inventory and append-only workbench records."""
import hashlib
import json
import re
import sqlite3
import stat
import sys
from contextlib import closing
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

APPS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APPS / 'dashboard' / 'tools'))
from folder_snapshot import capture, timestamp

VERSION = '1.0'
EXCLUDED = {'archive', 'archives', 'node_modules', '__pycache__', '_index.md', 'ai review log.md'}
MEDIA = {'.mp3', '.wav', '.m4a', '.mp4', '.webm', '.png', '.jpg', '.jpeg', '.webp', '.svg', '.pdf'}
METRICS = {
    'words': ('tokens', 'Unicode word matches with internal apostrophes'),
    'paragraphs': ('blocks', 'nonempty contiguous nonblank lines'),
    'lines': ('lines', 'decoded source splitlines'),
    'citation_markers': ('markers', 'literal Markdown footnote reference markers'),
}
KINDS = {
    'atoms', 'ledger', 'relationships', 'constraints', 'mappings', 'objections',
    'media', 'metrics', 'tasks', 'runs', 'artifacts', 'issues', 'reviews',
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def key(*parts):
    return str(uuid5(NAMESPACE_URL, json.dumps(parts, ensure_ascii=False)))


def linked(path):
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400)


def contained(root, relative):
    candidate = root / relative
    if not candidate.is_relative_to(root) or '..' in candidate.relative_to(root).parts:
        raise ValueError('Path leaves its selected root')
    cursor = root
    for part in candidate.relative_to(root).parts:
        cursor = cursor / part
        if linked(cursor):
            raise ValueError(f'Link or reparse point: {cursor}')
    return candidate


def create(path, data):
    """Publish complete new artifacts without overwriting existing files."""
    from os import link
    from tempfile import NamedTemporaryFile

    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(data)
    staged = Path(temporary.name)
    try:
        link(staged, path)
    except FileExistsError:
        if linked(path) or path.read_bytes() != data:
            raise
    finally:
        staged.unlink()


def read_quantum(db_path, root):
    if not db_path:
        return {}, {}, []
    uri = Path(db_path).resolve(strict=True).as_uri() + '?mode=ro'
    with closing(sqlite3.connect(uri, uri=True)) as db:
        vaults = {vid: (Path(db_path).resolve().parent / path).resolve()
                  for vid, path in db.execute('SELECT id,root FROM vaults')}
        papers = {path: pid for pid, vault, path in db.execute('SELECT id,vault,path FROM papers')
                  if vaults.get(vault) == root}
        db.row_factory = sqlite3.Row
        locations = {}
        for row in db.execute('SELECT * FROM locations ORDER BY paper,vault,folder'):
            if row['paper'] in papers.values() and vaults.get(row['vault']) == root:
                locations.setdefault(row['paper'], []).append(row['folder'])
        history = [dict(row) for row in db.execute('SELECT * FROM events ORDER BY rowid')
                   if row['paper'] in papers.values()]
    return papers, locations, history


def spans(text, paper_id, source_hash):
    start = None
    lines = text.splitlines()
    for number, line in enumerate([*lines, ''], 1):
        if line.strip() and start is None:
            start = number
        if not line.strip() and start is not None:
            yield dict(id=key(paper_id, source_hash, start), start_line=start, end_line=number - 1,
                       text='\n'.join(lines[start - 1:number - 1]))
            start = None


def metadata(text):
    if not text.startswith('---\n'):
        return None, None
    closing = re.search(r'(?m)^---[ \t]*$', text[4:])
    if closing is None:
        return None, 'Unclosed frontmatter'
    declarations = re.findall(r'(?m)^document_id:[ \t]*(.*)$', text[4:4 + closing.start()])
    if not declarations:
        return None, None
    if len(declarations) == 1:
        value = declarations[0].strip().strip('"\'')
        if re.fullmatch(r'[A-Z]{3,5}\.\d{2}\.[A-Z0-9-]+', value):
            return value, None
    return None, 'Malformed or repeated document_id'


class Index:
    def __init__(self, root, state):
        self.root = Path(root).absolute()
        if linked(self.root):
            raise ValueError('Select a real folder')
        self.root = self.root.resolve(strict=True)
        self.state = Path(state).resolve()
        if self.root.is_relative_to(self.state) or (
            self.state.is_relative_to(self.root)
            and self.state.relative_to(self.root).parts[0].casefold() != '.backside'
        ):
            raise ValueError('Use a separate output folder or the selected root’s .backside')
        self.database = self.state / 'workbench.sqlite'

    def connect(self):
        return sqlite3.connect(self.database, timeout=30)

    def current(self):
        if not self.database.exists():
            raise ValueError('Scan a selected folder first')
        with closing(self.connect()) as db:
            row = db.execute('SELECT payload FROM snapshots ORDER BY rowid DESC LIMIT 1').fetchone()
            if row is None:
                raise ValueError('Scan a selected folder first')
            result = json.loads(row[0])
            self.check_root(result)
            result['records'] = [json.loads(item[0]) for item in db.execute(
                'SELECT payload FROM records ORDER BY rowid')]
        papers = {p['id']: p for p in result['papers']}
        latest = {}
        for record in result['records']:
            paper = papers.get(record['paper_id'])
            current = paper and paper['availability'] == 'present' and paper['sha256'] == record['provenance']['source_sha256']
            record['current'] = bool(current)
            if record['kind'] == 'tasks':
                payload = record['data']
                receipt_path = payload.get('receipt')
                status = payload['status']
                if not current:
                    status = 'stale'
                elif receipt_path:
                    try:
                        receipt = contained(self.state, receipt_path).read_bytes()
                        artifact = contained(self.state, payload['artifact']).read_bytes()
                        status = 'done' if (digest(receipt) == payload['receipt_sha256']
                                            and digest(artifact) == payload['artifact_sha256']) else 'broken'
                    except (OSError, ValueError):
                        status = 'broken'
                latest[(record['paper_id'], payload['task'])] = dict(
                    paper_id=record['paper_id'], task=payload['task'], status=status)
        result['processing'] = list(latest.values())
        return result

    def check_root(self, snapshot):
        if snapshot['root'] != str(self.root):
            raise ValueError('This workbench state belongs to a different root')

    def scan(self, actor, excluded=(), quantum_db=None):
        excluded = {Path(item).as_posix().casefold() for item in excluded}
        if self.database.exists():
            self.current()  # Reject a state directory bound to another root before writing blobs.
        inventory = capture([self.root], exclude=lambda path: (
            path.name.startswith('.') or path.name.casefold() in EXCLUDED
            or path.relative_to(self.root).as_posix().casefold() in excluded))
        if not inventory['complete']:
            raise ValueError('Dashboard inventory was incomplete. Retry before publishing a snapshot.')
        registered, locations, history = read_quantum(quantum_db, self.root)
        now = timestamp()
        papers, folders, issues, media, observations, passages = [], [], [], [], [], []

        def walk(node):
            relative = Path(node['path']).relative_to(self.root).as_posix()
            if node['kind'] != 'folder':
                return
            folders.append(dict(path=relative, name=node['name'], files=node['files']))
            for child in node['children']:
                if child['kind'] == 'folder':
                    walk(child)
                    continue
                if child['kind'] != 'file':
                    continue
                source = Path(child['path']).relative_to(self.root)
                path = source.as_posix()
                if source.suffix.lower() in MEDIA:
                    media.append(dict(path=path, name=source.stem, folder=source.parent.as_posix()))
                if source.suffix.lower() != '.md':
                    continue
                paper_id = registered.get(path) or key(str(self.root), path)
                raw = contained(self.root, source).read_bytes()
                source_hash = digest(raw)
                paper = dict(id=paper_id, path=path, folder=source.parent.as_posix(),
                             series=source.parts[0] if len(source.parts) > 1 else '.',
                             title=source.stem, availability='present', document_id=None,
                             sha256=source_hash, modified_ns=child['modified_ns'],
                             memberships=locations.get(paper_id, []))
                papers.append(paper)
                try:
                    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
                except UnicodeDecodeError:
                    issues.append(dict(paper_id=paper_id, message='Unreadable UTF-8 source'))
                    paper['availability'] = 'blocked'
                    continue
                paper['document_id'], issue = metadata(text)
                if issue:
                    issues.append(dict(paper_id=paper_id, message=issue))
                create(self.state / 'sources' / f'{source_hash}.md', raw)
                blocks = list(spans(text, paper_id, source_hash))
                passages.extend(dict(paper_id=paper_id, source_sha256=source_hash, **block)
                                for block in blocks)
                counts = [len(re.findall(r"\b[^\W_]+(?:[’'][^\W_]+)*\b", text)), len(blocks),
                          len(text.splitlines()), len(re.findall(r'\[\^[^\]\n]+\](?!:)', text))]
                for (metric, (unit, method)), value in zip(METRICS.items(), counts):
                    observations.append(dict(paper_id=paper_id, metric=metric, value=value,
                                             unit=unit, numerator=value, denominator=None,
                                             method=method, definition_version=VERSION,
                                             source_sha256=source_hash, assessment_status='measured'))

        walk(inventory['roots'][0])
        for item in media:
            owners = [paper for paper in papers if paper['folder'] == item['folder']]
            owner = owners[0] if len(owners) == 1 else None
            item.update(paper_id=owner['id'] if owner else None,
                        source_sha256=owner['sha256'] if owner else None,
                        sha256=digest(contained(self.root, item['path']).read_bytes()))
        claims = {}
        for paper in papers:
            if paper['document_id']:
                claims.setdefault(paper['document_id'], []).append(paper)
        for document_id, matches in claims.items():
            if len(matches) > 1:
                for paper in matches:
                    issues.append(dict(paper_id=paper['id'], message=f'Conflicting declaration {document_id}'))

        self.state.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as db, db:
            db.execute('''CREATE TABLE IF NOT EXISTS snapshots(
                       id TEXT PRIMARY KEY, payload TEXT NOT NULL)''')
            db.execute('''CREATE TABLE IF NOT EXISTS records(
                       id TEXT PRIMARY KEY, payload TEXT NOT NULL)''')
            db.execute('BEGIN IMMEDIATE')
            previous = db.execute('SELECT payload FROM snapshots ORDER BY rowid DESC LIMIT 1').fetchone()
            if previous:
                previous = json.loads(previous[0])
                self.check_root(previous)
                seen = {paper['id'] for paper in papers}
                papers.extend(dict(paper, availability='missing') for paper in previous['papers']
                              if paper['id'] not in seen)
            snapshot = dict(schema_version=VERSION, root=str(self.root), papers=papers,
                            series=sorted({p['series'] for p in papers}),
                            folders=folders, passages=passages, metrics=observations,
                            media=media, issues=issues, quantum_history=history)
            fingerprint = digest(json.dumps(snapshot, sort_keys=True).encode())
            if previous and previous['fingerprint'] == fingerprint:
                return previous['id']
            snapshot.update(id=key(fingerprint, now), fingerprint=fingerprint, created_at=now, actor=actor)
            db.execute('INSERT INTO snapshots VALUES (?,?)', (snapshot['id'], json.dumps(snapshot)))
            return snapshot['id']

    def paper(self, paper_id, snapshot=None):
        for paper in (snapshot or self.current())['papers']:
            if paper['id'] == paper_id and paper['availability'] == 'present':
                return paper
        raise ValueError('Paper is missing, blocked, or unknown')

    def source(self, paper):
        raw = contained(self.state, f"sources/{paper['sha256']}.md").read_bytes()
        if digest(raw) != paper['sha256']:
            raise ValueError('Preserved source failed its hash check')
        return raw

    def record(self, kind, paper, actor, data, *, engine, locator=None, validation='candidate', prompt=None):
        from uuid import uuid4

        if kind not in KINDS:
            raise ValueError('Unknown record type')
        if locator:
            first, last = locator
            if type(first) is not int or type(last) is not int or not (
                1 <= first <= last <= len(self.source(paper).decode('utf-8-sig').splitlines())
            ):
                raise ValueError('Invalid source span')
        record = dict(id=str(uuid4()), kind=kind, paper_id=paper['id'], actor=actor, data=data,
                      provenance=dict(source_sha256=paper['sha256'], locator=locator, engine=engine,
                                      schema_version=VERSION, prompt_version=prompt,
                                      recorded_at=timestamp(), validation=validation))
        with closing(self.connect()) as db, db:
            db.execute('INSERT INTO records VALUES (?,?)', (record['id'], json.dumps(record)))
        return record
