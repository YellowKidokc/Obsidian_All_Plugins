"""Local, single-user paper registry. Run: python quantum.py --demo."""
import argparse
from contextlib import contextmanager
import json
import mimetypes
import sqlite3
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


class Library:
    def __init__(self, state):
        self.state = Path(state).resolve()
        self.state.mkdir(parents=True, exist_ok=True)
        self.db = self.state / 'registry.sqlite'
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS vaults(id TEXT PRIMARY KEY, name TEXT, root TEXT UNIQUE);
                CREATE TABLE IF NOT EXISTS papers(id TEXT PRIMARY KEY, vault TEXT, path TEXT, UNIQUE(vault,path));
                CREATE TABLE IF NOT EXISTS locations(paper TEXT, vault TEXT, folder TEXT,
                    UNIQUE(paper,vault,folder));
                CREATE TABLE IF NOT EXISTS tangents(
                    id TEXT PRIMARY KEY,
                    paper TEXT NOT NULL,
                    title TEXT NOT NULL,
                    scope TEXT DEFAULT 'deep-dive',
                    status TEXT DEFAULT 'draft',
                    FOREIGN KEY(paper) REFERENCES papers(id)
                );
                CREATE TABLE IF NOT EXISTS tangent_refs(
                    tangent TEXT NOT NULL,
                    paper TEXT NOT NULL,
                    relevance REAL DEFAULT 0.5,
                    UNIQUE(tangent, paper),
                    FOREIGN KEY(tangent) REFERENCES tangents(id),
                    FOREIGN KEY(paper) REFERENCES papers(id)
                );
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def resolve(self, vault, relative):
        with self.connect() as db:
            row = db.execute('SELECT root FROM vaults WHERE id=?', (vault,)).fetchone()
        if not row:
            raise ValueError('Unknown vault')
        root = Path(row['root']).resolve()
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Path must stay inside its vault')
        return path

    def canonical(self, vault, relative):
        """One spelling per file or folder: the real on-disk path, forward slashes.
        'Papers\\ME.md', 'papers/me.md' and './Papers/ME.md' are the same paper."""
        root = self.resolve(vault, '')
        value = self.resolve(vault, relative).relative_to(root).as_posix()
        return '' if value == '.' else value

    def add_vault(self, name, root):
        root = Path(root).resolve()
        if not root.is_dir():
            raise ValueError('Vault directory does not exist')
        with self.connect() as db:
            db.execute('INSERT OR IGNORE INTO vaults VALUES(?,?,?)',
                       (str(uuid.uuid4()), name, str(root)))
            return db.execute('SELECT id FROM vaults WHERE root=?', (str(root),)).fetchone()['id']

    def register(self, vault, path):
        file = self.resolve(vault, path)
        if not file.is_file() or file.suffix.lower() != '.md':
            raise ValueError('Choose an existing Markdown paper')
        path = self.canonical(vault, path)
        with self.connect() as db:
            db.execute('INSERT OR IGNORE INTO papers VALUES(?,?,?)', (str(uuid.uuid4()), vault, path))
            return db.execute('SELECT id FROM papers WHERE vault=? AND path=?', (vault, path)).fetchone()['id']

    def paper(self, paper_id):
        with self.connect() as db:
            row = db.execute('SELECT * FROM papers WHERE id=?', (paper_id,)).fetchone()
        if not row:
            raise ValueError('Unknown paper')
        return dict(row)

    def show_here(self, paper, vault, folder):
        self.paper(paper)
        if not self.resolve(vault, folder).is_dir():
            raise ValueError('Destination folder does not exist')
        folder = self.canonical(vault, folder)
        with self.connect() as db:
            db.execute('INSERT OR IGNORE INTO locations VALUES(?,?,?)', (paper, vault, folder))

    # Papers are UTF-8. Never lean on the Windows default (cp1252): it cannot hold
    # χ, ∏, ≠ and friends, and a failed write used to leave the paper empty.
    def read(self, paper):
        row = self.paper(paper)
        raw = self.resolve(row['vault'], row['path']).read_bytes()
        try:
            return raw.decode('utf-8-sig').replace('\r\n', '\n')
        except UnicodeDecodeError:
            raise ValueError('This paper is not saved as UTF-8, so it was not opened. Nothing was changed.')

    def save(self, paper, content):
        row = self.paper(paper)
        file = self.resolve(row['vault'], row['path'])
        old = file.read_bytes() if file.exists() else b''
        text = content.replace('\r\n', '\n')
        if b'\r\n' in old:                      # keep the paper's own line endings
            text = text.replace('\n', '\r\n')
        data = (b'\xef\xbb\xbf' if old.startswith(b'\xef\xbb\xbf') else b'') + text.encode('utf-8')
        # Write beside the paper, then swap: the original is whole until the new one is whole.
        temp = file.with_name(f'.{file.name}.{uuid.uuid4().hex[:8]}.saving')
        try:
            temp.write_bytes(data)
            temp.replace(file)
        finally:
            temp.unlink(missing_ok=True)

    def move(self, paper, vault, folder):
        row = self.paper(paper)
        source = self.resolve(row['vault'], row['path'])
        destination_folder = self.resolve(vault, folder)
        if not destination_folder.is_dir():
            raise ValueError('Destination folder does not exist')
        target = destination_folder / source.name
        if target == source:
            return
        # Exclusive creation prevents overwriting an existing destination.
        with target.open('xb') as output:
            output.write(source.read_bytes())
        try:
            with self.connect() as db:
                db.execute('UPDATE papers SET vault=?,path=? WHERE id=?',
                           (vault, target.relative_to(self.resolve(vault, '')).as_posix(), paper))
        except Exception:
            target.unlink()
            raise
        source.unlink()

    def snapshot(self):
        with self.connect() as db:
            vaults = [dict(r) for r in db.execute('SELECT * FROM vaults')]
            papers = [dict(r) for r in db.execute('SELECT * FROM papers')]
            locations = [dict(r) for r in db.execute('SELECT * FROM locations')]
        for vault in vaults:
            root = Path(vault.pop('root'))
            vault['folders'] = [''] + sorted(p.relative_to(root).as_posix() for p in root.rglob('*')
                if p.is_dir() and not any(x.startswith('.') for x in p.relative_to(root).parts)
                and p.resolve().is_relative_to(root.resolve()))
        tangents = self.all_tangents()
        return dict(vaults=vaults, papers=papers, locations=locations, tangents=tangents)


    # ── Tangents ─────────────────────────────────────────────────
    # A tangent is a deep-dive paper that backs up claims in other papers.
    # One tangent file, referenced by many papers via tangent_refs.
    # Scopes: deep-dive, proof, worked-example, historical, counterargument, errata

    def add_tangent(self, paper_id, title, scope='deep-dive'):
        self.paper(paper_id)
        tid = str(uuid.uuid4())
        with self.connect() as db:
            db.execute('INSERT INTO tangents VALUES(?,?,?,?,?)',
                       (tid, paper_id, title, scope, 'draft'))
        return tid

    def link_tangent(self, tangent_id, paper_id, relevance=0.5):
        self.paper(paper_id)
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO tangent_refs VALUES(?,?,?)',
                       (tangent_id, paper_id, relevance))

    def tangent(self, tangent_id):
        with self.connect() as db:
            row = db.execute('SELECT * FROM tangents WHERE id=?', (tangent_id,)).fetchone()
        if not row:
            raise ValueError('Unknown tangent')
        return dict(row)

    def tangents_for(self, paper_id):
        with self.connect() as db:
            direct = [dict(r) for r in db.execute(
                'SELECT * FROM tangents WHERE paper=?', (paper_id,))]
            refs = [dict(r) for r in db.execute(
                '''SELECT t.*, tr.relevance FROM tangent_refs tr
                   JOIN tangents t ON t.id = tr.tangent
                   WHERE tr.paper=?''', (paper_id,))]
        return {'authored': direct, 'referenced': refs}

    def all_tangents(self):
        with self.connect() as db:
            tangents = [dict(r) for r in db.execute('SELECT * FROM tangents')]
            for t in tangents:
                refs = [dict(r) for r in db.execute(
                    'SELECT paper, relevance FROM tangent_refs WHERE tangent=?', (t['id'],))]
                t['refs'] = refs
        return tangents

    # ── Vault View Switching ──────────────────────────────────────
    # Dot-prefixed folders are hidden from Obsidian's file explorer.
    # These methods toggle visibility to create "views" of a vault.

    ROADS = [
        "10_ROAD_01_THERE_IS_ONE_GOD", "11_ROAD_02_GOD_CAN_BE_KNOWN",
        "12_ROAD_03_MATH_IS_MORAL", "13_ROAD_04_PHYSICS_PROVES_ETHICS",
        "14_ROAD_05_CONSCIOUSNESS_IS_REAL", "15_ROAD_06_LOVE_IS_A_LAW",
        "16_ROAD_07_EVIL_IS_ENTROPY", "17_ROAD_08_TIME_HAS_DIRECTION",
        "18_ROAD_09_DEATH_IS_NOT_FINAL", "19_ROAD_10_JESUS_IS_THE_PROOF",
        "20_ROAD_11_SCRIPTURE_ENCODES_PHYSICS", "21_ROAD_12_THE_CHURCH_IS_THE_LAB",
        "22_ROAD_13_HEAVEN_IS_INEVITABLE",
    ]
    SUPPORT = [
        "00_INBOX", "00_THE_AXIOMS", "01_MASTER_EQUATION_SUBSTRATE",
        "02_SERIES_REGISTRY_AND_CANON", "03_CORE_EQUATIONS_REFERENCE",
        "04_CROSS_REFERENCES_AND_LINKS", "05_GOVERNANCE_PROCESS",
        "06_MEDIA_PRODUCTION", "07_TEMPLATES_AND_TOOLS", "08_LEGACY_AND_ARCHIVE",
        "50_PRODUCTION_AND_PUBLICATION",
    ]
    ALWAYS_DOTTED = {".data", ".templates", ".obsidian", ".trash"}

    # ── Auto-scan ────────────────────────────────────────────────
    # Walk all registered vaults and register every .md file found.

    def scan_vault(self, vault_id):
        with self.connect() as db:
            row = db.execute('SELECT root FROM vaults WHERE id=?', (vault_id,)).fetchone()
        if not row:
            raise ValueError('Unknown vault')
        root = Path(row['root'])
        registered, skipped = 0, 0
        for md in root.rglob('*.md'):
            if any(p.startswith('.') for p in md.relative_to(root).parts):
                continue
            rel = md.relative_to(root).as_posix()
            try:
                self.register(vault_id, rel)
                registered += 1
            except (ValueError, Exception):
                skipped += 1
        return {'registered': registered, 'skipped': skipped}

    def scan_all(self):
        with self.connect() as db:
            vaults = [dict(r) for r in db.execute('SELECT id, name FROM vaults')]
        results = {}
        for v in vaults:
            results[v['name']] = self.scan_vault(v['id'])
        return results
    VIEWS = {
        "all": "*",
        "working": ["00_INBOX", "02_WORKING", "06_MEDIA", "ZZZZ_MASTER_TEMPLATE"],
        "13roads": ROADS + SUPPORT,
        "canon": ["01_CANON", "02_SERIES_REGISTRY_AND_CANON"],
        "drafts": ["00_INBOX", "02_WORKING"],
        "pipeline": ["00_INBOX", "01_CANON", "02_WORKING", "06_MEDIA"],
    }

    def vault_view(self, vault_id, view_name):
        with self.connect() as db:
            row = db.execute('SELECT root FROM vaults WHERE id=?', (vault_id,)).fetchone()
        if not row:
            raise ValueError('Unknown vault')
        root = Path(row['root'])
        show_list = self.VIEWS.get(view_name)
        if show_list is None:
            raise ValueError(f'Unknown view. Available: {", ".join(self.VIEWS)}')

        changed = []
        for d in sorted(root.iterdir()):
            if not d.is_dir():
                continue
            name = d.name
            real = name[1:] if (name.startswith('.') and not name.startswith('..') and len(name) > 1 and name[1] != '.') else name
            if name in self.ALWAYS_DOTTED or real in self.ALWAYS_DOTTED:
                continue
            is_dotted = name.startswith('.') and name not in self.ALWAYS_DOTTED
            if show_list == "*":
                if is_dotted:
                    new_path = d.parent / real
                    if not new_path.exists():
                        d.rename(new_path)
                        changed.append(('show', name, real))
            else:
                should_show = real in show_list
                if should_show and is_dotted:
                    new_path = d.parent / real
                    if not new_path.exists():
                        d.rename(new_path)
                        changed.append(('show', name, real))
                elif not should_show and not is_dotted:
                    new_path = d.parent / ('.' + name)
                    if not new_path.exists():
                        d.rename(new_path)
                        changed.append(('hide', name, '.' + name))
        return changed

    def vault_view_list(self, vault_id):
        with self.connect() as db:
            row = db.execute('SELECT root FROM vaults WHERE id=?', (vault_id,)).fetchone()
        if not row:
            raise ValueError('Unknown vault')
        root = Path(row['root'])
        result = []
        for d in sorted(root.iterdir()):
            if not d.is_dir():
                continue
            name = d.name
            is_dotted = name.startswith('.') and name not in self.ALWAYS_DOTTED
            result.append({'name': name, 'hidden': is_dotted})
        return result


def demo(library):
    for name in ['Research', 'Writing']:
        root = library.state / 'demo-vaults' / name
        (root / 'Papers').mkdir(parents=True, exist_ok=True)
        (root / 'Ideas').mkdir(exist_ok=True)
        library.add_vault(name, root)
    snapshot = library.snapshot()
    research, writing = [next(v['id'] for v in snapshot['vaults'] if v['name'] == n)
                         for n in ['Research', 'Writing']]
    if snapshot['papers']:
        return
    path = library.resolve(research, 'Papers/One paper.md')
    if not path.exists():
        path.write_text('# One paper, many places\n\nThis is one original Markdown file.\n\nEdit it from either vault.\n')
    paper = library.register(research, 'Papers/One paper.md')
    library.show_here(paper, writing, 'Ideas')
    note = library.resolve(writing, 'Papers/A linked note.md')
    if not note.exists():
        note.write_text(f'# A linked note\n\nRead [the shared paper](#paper={paper}).\n\nThis link uses its permanent ID and survives moves made here.\n')
    library.register(writing, 'Papers/A linked note.md')


def handler(library):
    web = Path(__file__).parent / 'web'

    class Handler(BaseHTTPRequestHandler):
        def respond(self, status, data, content_type='application/json'):
            body = json.dumps(data).encode() if content_type == 'application/json' else data
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlparse(self.path).path
            try:
                if path == '/api/library':
                    return self.respond(200, library.snapshot())
                if path.startswith('/api/paper/'):
                    paper = path.rsplit('/', 1)[1]
                    return self.respond(200, dict(**library.paper(paper), content=library.read(paper)))
                file = web / ('index.html' if path == '/' else path.lstrip('/'))
                if not file.resolve().is_relative_to(web.resolve()) or not file.is_file():
                    return self.respond(404, {'error': 'Not found'})
                self.respond(200, file.read_bytes(), mimetypes.guess_type(file)[0] or 'text/plain')
            except (ValueError, OSError) as error:
                self.respond(400, {'error': str(error)})

        def do_POST(self):
            # Require same-origin JSON; no cross-origin write access.
            if self.headers.get('Origin') not in (None, 'http://' + self.headers.get('Host', '')):
                return self.respond(403, {'error': 'Origin rejected'})
            if self.headers.get('Content-Type') != 'application/json':
                return self.respond(415, {'error': 'JSON required'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if size < 0 or size > 2_000_000:
                    raise ValueError('Request too large')
                data = json.loads(self.rfile.read(size))
                action = urlparse(self.path).path
                if action == '/api/show':
                    library.show_here(data['paper'], data['vault'], data['folder'])
                elif action == '/api/move':
                    library.move(data['paper'], data['vault'], data['folder'])
                elif action == '/api/save':
                    library.save(data['paper'], data['content'])
                elif action == '/api/register':
                    return self.respond(200, {'id': library.register(data['vault'], data['path'])})
                elif action == '/api/tangent/add':
                    tid = library.add_tangent(data['paper'], data['title'], data.get('scope', 'deep-dive'))
                    return self.respond(200, {'id': tid})
                elif action == '/api/tangent/link':
                    library.link_tangent(data['tangent'], data['paper'], data.get('relevance', 0.5))
                elif action == '/api/tangent/list':
                    return self.respond(200, library.tangents_for(data['paper']))
                elif action == '/api/tangents':
                    return self.respond(200, {'tangents': library.all_tangents()})
                elif action == '/api/view':
                    changes = library.vault_view(data['vault'], data['view'])
                    return self.respond(200, {'ok': True, 'changes': changes})
                elif action == '/api/view/list':
                    folders = library.vault_view_list(data['vault'])
                    return self.respond(200, {'folders': folders})
                elif action == '/api/scan':
                    vault = data.get('vault')
                    if vault:
                        result = library.scan_vault(vault)
                    else:
                        result = library.scan_all()
                    return self.respond(200, result)
                else:
                    return self.respond(404, {'error': 'Not found'})
                self.respond(200, {'ok': True})
            except (ValueError, KeyError, OSError, sqlite3.Error) as error:
                self.respond(400, {'error': str(error)})
    return Handler


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', default=str(Path.home() / '.quantum-papers'))
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--demo', action='store_true')
    parser.add_argument('--vault', action='append', default=[], help='Existing vault directory; repeat for more vaults')
    parser.add_argument('--view', help='Apply a view to a vault: all, working, 13roads, canon, drafts, pipeline')
    parser.add_argument('--view-vault', help='Vault name or path for --view')
    parser.add_argument('--view-list', help='List folder visibility for a vault (name or path)')
    parser.add_argument('--scan', action='store_true', help='Auto-register all .md files in all vaults')
    args = parser.parse_args()
    library = Library(args.state)
    for root in args.vault:
        library.add_vault(Path(root).name, root)
    if args.demo:
        demo(library)

    if args.scan:
        results = library.scan_all()
        for name, r in results.items():
            print(f"  {name}: {r['registered']} new, {r['skipped']} already known")
        total = sum(r['registered'] for r in results.values())
        print(f"  Total new: {total}")
        sys.exit(0)

    # View commands (non-server mode)
    if args.view_list:
        snap = library.snapshot()
        vault_id = None
        for v in snap['vaults']:
            if v['name'] == args.view_list:
                vault_id = v['id']; break
        if not vault_id:
            # Try by path
            with library.connect() as db:
                row = db.execute('SELECT id FROM vaults WHERE root=?', (str(Path(args.view_list).resolve()),)).fetchone()
                if row: vault_id = row['id']
        if vault_id:
            for f in library.vault_view_list(vault_id):
                status = 'HIDDEN ' if f['hidden'] else 'VISIBLE'
                print(f"  [{status}] {f['name']}")
        else:
            print(f"Vault not found: {args.view_list}")
    elif args.view:
        target = args.view_vault or (args.vault[0] if args.vault else None)
        if not target:
            print("Specify --view-vault or --vault for the view target")
        else:
            snap = library.snapshot()
            vault_id = None
            for v in snap['vaults']:
                if v['name'] == target:
                    vault_id = v['id']; break
            if not vault_id:
                with library.connect() as db:
                    row = db.execute('SELECT id FROM vaults WHERE root=?', (str(Path(target).resolve()),)).fetchone()
                    if row: vault_id = row['id']
            if vault_id:
                changes = library.vault_view(vault_id, args.view)
                for action, old, new in changes:
                    print(f"  {action.upper()}: {old} -> {new}")
                print(f"Applied view '{args.view}': {len(changes)} folders changed")
            else:
                print(f"Vault not found: {target}")
    else:
        print(f'Quantum Papers listening on port {args.port}', flush=True)
        ThreadingHTTPServer(('127.0.0.1', args.port), handler(library)).serve_forever()
