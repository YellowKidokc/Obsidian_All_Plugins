"""Local, single-user paper registry. Run: python quantum.py --demo."""
import argparse
import getpass
import threading
from datetime import datetime, timezone
from contextlib import contextmanager
import json
import mimetypes
import os
import shutil
import sqlite3
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


class Library:
    TABLES = ('vaults', 'papers', 'locations', 'tangents', 'tangent_refs', 'events')

    def __init__(self, state, actor=None):
        # Who is acting: --actor / QP_ACTOR / per-request X-QP-Actor header,
        # falling back to the OS user. Each terminal or AI should set its own name.
        try:
            user = getpass.getuser()
        except Exception:
            user = 'unknown'
        self.default_actor = actor or os.environ.get('QP_ACTOR') or f'{user}@cli'
        self._local = threading.local()
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
                CREATE TABLE IF NOT EXISTS events(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    at TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    paper TEXT,
                    source TEXT,
                    target TEXT,
                    details TEXT
                );
                CREATE INDEX IF NOT EXISTS events_paper ON events(paper);
            ''')
            cols = {r['name'] for r in db.execute('PRAGMA table_info(papers)')}
            if 'status' not in cols:            # 'active' or 'stale'
                db.execute("ALTER TABLE papers ADD COLUMN status TEXT DEFAULT 'active'")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    # ── Audit trail ──────────────────────────────────────────────
    # Every change records who did it, when, and from where to where.

    @property
    def actor(self):
        return getattr(self._local, 'actor', None) or self.default_actor

    @contextmanager
    def acting_as(self, actor):
        old = getattr(self._local, 'actor', None)
        self._local.actor = actor or None
        try:
            yield
        finally:
            self._local.actor = old

    def log(self, db, action, paper=None, source=None, target=None, details=None, actor=None):
        db.execute('INSERT INTO events(at,actor,action,paper,source,target,details) VALUES(?,?,?,?,?,?,?)',
                   (datetime.now(timezone.utc).isoformat(timespec='seconds'), actor or self.actor,
                    action, paper, source, target,
                    json.dumps(details, ensure_ascii=False) if details is not None else None))

    def where(self, vault, path):
        with self.connect() as db:
            row = db.execute('SELECT name FROM vaults WHERE id=?', (vault,)).fetchone()
        return f"{row['name'] if row else vault}:{path}"

    def external(self):
        return f'external (seen by {self.actor})'

    def history(self, paper=None, actor=None, limit=100):
        sql, args = 'SELECT * FROM events WHERE 1=1', []
        if paper:
            sql += ' AND paper=?'
            args.append(paper)
        if actor:
            sql += ' AND actor=?'
            args.append(actor)
        sql += ' ORDER BY id DESC LIMIT ?'
        args.append(limit)
        with self.connect() as db:
            return [dict(r) for r in db.execute(sql, args)]

    # ── Paths ────────────────────────────────────────────────────
    # Comparisons are case-insensitive on Windows (normcase) and drive-aware.
    # Vault roots are stored absolute, or relative to the state directory
    # (--portable) so the state folder and vaults can move together.

    @staticmethod
    def same_path(a, b):
        return os.path.normcase(str(Path(a).resolve())) == os.path.normcase(str(Path(b).resolve()))

    @staticmethod
    def inside(path, root):
        path, root = (os.path.normcase(str(Path(p).resolve())) for p in (path, root))
        try:
            return os.path.commonpath([path, root]) == root
        except ValueError:                      # different drives
            return False

    @staticmethod
    def clean(relative):
        return str(relative).replace('\\', '/')

    def root_of(self, stored):
        root = Path(stored)
        return (root if root.is_absolute() else self.state / root).resolve()

    def vault_root(self, vault):
        with self.connect() as db:
            row = db.execute('SELECT root FROM vaults WHERE id=?', (vault,)).fetchone()
        if not row:
            raise ValueError('Unknown vault')
        return self.root_of(row['root'])

    def find_vault(self, name_or_path):
        """Vault id from an id, a name, or a directory path."""
        with self.connect() as db:
            rows = [dict(r) for r in db.execute('SELECT * FROM vaults')]
        for r in rows:
            if name_or_path in (r['id'], r['name']):
                return r['id']
        if Path(name_or_path).is_dir():
            for r in rows:
                if self.same_path(self.root_of(r['root']), name_or_path):
                    return r['id']
        raise ValueError(f'Vault not found: {name_or_path}')

    def resolve(self, vault, relative):
        root = self.vault_root(vault)
        path = (root / self.clean(relative)).resolve()
        if not self.inside(path, root):
            raise ValueError('Path must stay inside its vault')
        return path

    def canonical(self, vault, relative):
        """One spelling per file or folder: the real on-disk path, forward slashes.
        'Papers\\ME.md', 'papers/me.md' and './Papers/ME.md' are the same paper."""
        root = self.resolve(vault, '')
        value = self.resolve(vault, relative).relative_to(root).as_posix()
        return '' if value == '.' else value

    def add_vault(self, name, root, portable=False):
        root = Path(self.clean(root)).resolve()
        if not root.is_dir():
            raise ValueError('Vault directory does not exist')
        with self.connect() as db:
            for row in db.execute('SELECT id, root FROM vaults'):
                if self.same_path(self.root_of(row['root']), root):
                    return row['id']
            stored = str(root)
            if portable:
                try:
                    stored = Path(os.path.relpath(root, self.state)).as_posix()
                except ValueError:              # on another drive: must stay absolute
                    pass
            vid = str(uuid.uuid4())
            db.execute('INSERT INTO vaults(id,name,root) VALUES(?,?,?)', (vid, name, stored))
            return vid

    def register(self, vault, path):
        file = self.resolve(vault, path)
        if not file.is_file() or file.suffix.lower() != '.md':
            raise ValueError('Choose an existing Markdown paper')
        path = self.canonical(vault, path)
        with self.connect() as db:
            new_id = str(uuid.uuid4())
            cur = db.execute("INSERT OR IGNORE INTO papers(id,vault,path,status) VALUES(?,?,?,'active')",
                             (new_id, vault, path))
            if cur.rowcount:
                self.log(db, 'register', new_id, target=self.where(vault, path))
            db.execute("UPDATE papers SET status='active' WHERE vault=? AND path=?", (vault, path))
            return db.execute('SELECT id FROM papers WHERE vault=? AND path=?', (vault, path)).fetchone()['id']

    def batch_register(self, vault, paths):
        return [self.register(vault, p) for p in paths]

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
            if db.execute('INSERT OR IGNORE INTO locations VALUES(?,?,?)', (paper, vault, folder)).rowcount:
                self.log(db, 'show-here', paper, target=self.where(vault, folder or '/'))

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
        with self.connect() as db:
            self.log(db, 'save', paper, target=self.where(row['vault'], row['path']),
                     details={'bytes': len(data)})

    # ── Moving ───────────────────────────────────────────────────

    @staticmethod
    def copy_exclusive(source, target):
        """Copy that works across drives and never overwrites. The bytes land in a
        temp file beside the target first, so a half-written target never appears;
        the target name is then claimed exclusively (hard link, or 'xb' fallback)."""
        temp = target.with_name(f'.{target.name}.{uuid.uuid4().hex[:8]}.moving')
        try:
            with source.open('rb') as src, temp.open('xb') as out:
                shutil.copyfileobj(src, out)
                out.flush()
                os.fsync(out.fileno())
            try:
                os.link(temp, target)           # atomic, fails if target exists
            except FileExistsError:
                raise
            except (OSError, NotImplementedError, AttributeError):
                with temp.open('rb') as src, target.open('xb') as out:   # e.g. exFAT
                    shutil.copyfileobj(src, out)
        finally:
            temp.unlink(missing_ok=True)

    def move(self, paper, vault, folder):
        row = self.paper(paper)
        source = self.resolve(row['vault'], row['path'])
        destination_folder = self.resolve(vault, folder)
        if not destination_folder.is_dir():
            raise ValueError('Destination folder does not exist')
        target = destination_folder / source.name
        if self.same_path(target, source):
            return
        self.copy_exclusive(source, target)     # copy + delete: safe across drives
        try:
            new_path = target.relative_to(self.vault_root(vault)).as_posix()
            with self.connect() as db:
                db.execute('UPDATE papers SET vault=?,path=? WHERE id=?', (vault, new_path, paper))
                self.log(db, 'move', paper, self.where(row['vault'], row['path']), self.where(vault, new_path),
                         details={'from_vault': row['vault'],
                                  'from_folder': row['path'].rpartition('/')[0]})
        except Exception:
            target.unlink()
            raise
        source.unlink()

    def batch_move(self, paper_ids, vault, folder):
        """Move many papers into one folder. All or nothing: every check runs
        before any copy, and copies are removed if anything later fails."""
        destination_folder = self.resolve(vault, folder)
        if not destination_folder.is_dir():
            raise ValueError('Destination folder does not exist')
        root = self.vault_root(vault)
        plan, names = [], set()
        for pid in dict.fromkeys(paper_ids):
            row = self.paper(pid)
            source = self.resolve(row['vault'], row['path'])
            if not source.is_file():
                raise ValueError(f'Missing file for paper {pid}: {row["path"]}')
            target = destination_folder / source.name
            if self.same_path(source, target):
                continue
            key = os.path.normcase(source.name)
            if key in names or target.exists():
                raise FileExistsError(f'Destination already has {source.name}')
            names.add(key)
            plan.append((pid, source, target, self.where(row['vault'], row['path'])))
        copied = []
        try:
            for _, source, target, _ in plan:
                self.copy_exclusive(source, target)
                copied.append(target)
            batch = uuid.uuid4().hex[:8]
            with self.connect() as db:
                for pid, _, target, origin in plan:
                    new_path = target.relative_to(root).as_posix()
                    db.execute('UPDATE papers SET vault=?,path=? WHERE id=?', (vault, new_path, pid))
                    self.log(db, 'batch-move', pid, origin, self.where(vault, new_path),
                             {'batch': batch, 'count': len(plan)})
        except Exception:
            for target in copied:
                target.unlink(missing_ok=True)
            raise
        for _, source, _, _ in plan:
            source.unlink()
        return [p[0] for p in plan]

    def papers_in(self, vault, folder):
        """Active papers directly inside a folder (not subfolders)."""
        folder = self.canonical(vault, folder)
        prefix = folder + '/' if folder else ''
        with self.connect() as db:
            rows = [dict(r) for r in db.execute(
                "SELECT id, path FROM papers WHERE vault=? AND status='active'", (vault,))]
        return [r['id'] for r in rows
                if os.path.normcase(r['path']).startswith(os.path.normcase(prefix))
                and '/' not in r['path'][len(prefix):]]

    def move_folder(self, vault, folder, dest_vault, dest_folder):
        return self.batch_move(self.papers_in(vault, folder), dest_vault, dest_folder)

    # ── Reconciliation ───────────────────────────────────────────
    # Files moved by Obsidian, other tools or by hand: match by file name,
    # mark vanished files stale (records are never deleted), register new files.

    def markdown_files(self, vault):
        root = self.vault_root(vault)
        found = {}
        for md in root.rglob('*.md'):
            rel = md.relative_to(root)
            if any(p.startswith('.') for p in rel.parts):
                continue
            found[os.path.normcase(rel.as_posix())] = rel.as_posix()
        return found

    def reconcile(self, vault):
        on_disk = self.markdown_files(vault)
        with self.connect() as db:
            papers = [dict(r) for r in db.execute('SELECT * FROM papers WHERE vault=?', (vault,))]
        known = {os.path.normcase(p['path']) for p in papers}
        unclaimed = {k: v for k, v in on_disk.items() if k not in known}
        by_name = {}
        for key, rel in unclaimed.items():
            by_name.setdefault(os.path.normcase(Path(rel).name), []).append(key)
        report = dict(moved=[], stale=[], new=[], restored=[], ambiguous=[])
        with self.connect() as db:
            for p in papers:
                if os.path.normcase(p['path']) in on_disk:
                    if p['status'] == 'stale':
                        db.execute("UPDATE papers SET status='active' WHERE id=?", (p['id'],))
                        report['restored'].append(p['id'])
                        self.log(db, 'came-back', p['id'], target=self.where(vault, p['path']),
                                 actor=self.external())
                    continue
                name = os.path.normcase(Path(p['path']).name)
                matches = [k for k in by_name.get(name, []) if k in unclaimed]
                if len(matches) == 1:
                    new = unclaimed.pop(matches[0])
                    db.execute("UPDATE papers SET path=?, status='active' WHERE id=?", (new, p['id']))
                    report['moved'].append({'id': p['id'], 'from': p['path'], 'to': new})
                    self.log(db, 'external-move', p['id'], self.where(vault, p['path']),
                             self.where(vault, new), actor=self.external())
                    continue
                if len(matches) > 1:            # same name in several places: don't guess
                    report['ambiguous'].append({'id': p['id'], 'path': p['path'],
                                                'candidates': [unclaimed[k] for k in matches]})
                if p['status'] != 'stale':
                    db.execute("UPDATE papers SET status='stale' WHERE id=?", (p['id'],))
                    report['stale'].append({'id': p['id'], 'path': p['path']})
                    self.log(db, 'went-missing', p['id'], self.where(vault, p['path']),
                             actor=self.external())
        ambiguous = {c for a in report['ambiguous'] for c in a['candidates']}
        for rel in unclaimed.values():
            if rel not in ambiguous:
                report['new'].append({'id': self.register(vault, rel), 'path': rel})
        return report

    def reconcile_all(self):
        with self.connect() as db:
            vaults = [dict(r) for r in db.execute('SELECT id, name FROM vaults')]
        return {v['name']: self.reconcile(v['id']) for v in vaults}

    # ── Backup ───────────────────────────────────────────────────

    def export_registry(self, file):
        with self.connect() as db:
            data = {t: [dict(r) for r in db.execute(f'SELECT * FROM {t}')] for t in self.TABLES}
        data['format'] = 'quantum-papers-registry/1'
        file = Path(file).resolve()
        temp = file.with_name(f'.{file.name}.{uuid.uuid4().hex[:8]}.saving')
        try:
            temp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
            temp.replace(file)
        finally:
            temp.unlink(missing_ok=True)
        return {t: len(data[t]) for t in self.TABLES}

    def import_registry(self, file):
        """Merge a backup into the registry; rows with the same key are replaced."""
        data = json.loads(Path(file).read_text(encoding='utf-8'))
        if data.get('format') != 'quantum-papers-registry/1':
            raise ValueError('Not a Quantum Papers registry backup')
        counts = {}
        with self.connect() as db:
            for t in self.TABLES:
                cols = {r['name'] for r in db.execute(f'PRAGMA table_info({t})')}
                for row in data.get(t, []):
                    row = {k: v for k, v in row.items() if k in cols}
                    db.execute(f'INSERT OR REPLACE INTO {t}({",".join(row)}) '
                               f'VALUES({",".join("?" * len(row))})', tuple(row.values()))
                counts[t] = len(data.get(t, []))
        return counts

    def snapshot(self):
        with self.connect() as db:
            vaults = [dict(r) for r in db.execute('SELECT * FROM vaults')]
            papers = [dict(r) for r in db.execute('SELECT * FROM papers')]
            locations = [dict(r) for r in db.execute('SELECT * FROM locations')]
        for vault in vaults:
            root = self.root_of(vault.pop('root'))
            vault['folders'] = [''] + sorted(p.relative_to(root).as_posix() for p in root.rglob('*')
                if p.is_dir() and not any(x.startswith('.') for x in p.relative_to(root).parts)
                and self.inside(p, root))
        tangents = self.all_tangents()
        return dict(vaults=vaults, papers=papers, locations=locations, tangents=tangents)


    # ── Tangents ─────────────────────────────────────────────────
    # A tangent IS a registered paper (tangents.paper = its own file).
    # One tangent file, referenced by many papers via tangent_refs.
    # Scopes: deep-dive, proof, worked-example, historical, counterargument, errata

    def add_tangent(self, paper_id, title, scope='deep-dive'):
        self.paper(paper_id)
        tid = str(uuid.uuid4())
        with self.connect() as db:
            db.execute('INSERT INTO tangents VALUES(?,?,?,?,?)',
                       (tid, paper_id, title, scope, 'draft'))
        return tid

    def create_tangent(self, paper_id, scope='deep-dive'):
        """Mark an existing registered paper as a tangent (idempotent)."""
        row = self.paper(paper_id)
        with self.connect() as db:
            existing = db.execute('SELECT id FROM tangents WHERE paper=?', (paper_id,)).fetchone()
            if existing:
                db.execute('UPDATE tangents SET scope=? WHERE id=?', (scope, existing['id']))
                self.log(db, 'tangent-scope', paper_id, details={'scope': scope})
                return existing['id']
            tid = str(uuid.uuid4())
            db.execute('INSERT INTO tangents VALUES(?,?,?,?,?)',
                       (tid, paper_id, Path(row['path']).stem, scope, 'draft'))
            self.log(db, 'tangent-create', paper_id, details={'tangent': tid, 'scope': scope})
        return tid

    def tangent_search(self, query):
        """Tangents whose title or first 500 characters contain every query word."""
        words = [w.lower() for w in query.split()]
        with self.connect() as db:
            rows = [dict(r) for r in db.execute(
                'SELECT t.*, p.vault, p.path FROM tangents t JOIN papers p ON p.id = t.paper')]
        hits = []
        for t in rows:
            try:
                head = self.read(t['paper'])[:500]
            except (ValueError, OSError):
                head = ''
            haystack = (t['title'] + '\n' + head).lower()
            if all(w in haystack for w in words):
                hits.append(dict(t, preview=head))
        return hits

    def link_tangent(self, tangent_id, paper_id, relevance=0.5):
        self.paper(paper_id)
        self.tangent(tangent_id)
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO tangent_refs VALUES(?,?,?)',
                       (tangent_id, paper_id, relevance))
            self.log(db, 'tangent-link', paper_id, details={'tangent': tangent_id, 'relevance': relevance})

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
        root = self.vault_root(vault_id)
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
        root = self.vault_root(vault_id)
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
        root = self.vault_root(vault_id)
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
        path.write_text('# One paper, many places\n\nThis is one original Markdown file.\n\nEdit it from either vault.\n', encoding='utf-8')
    paper = library.register(research, 'Papers/One paper.md')
    library.show_here(paper, writing, 'Ideas')
    note = library.resolve(writing, 'Papers/A linked note.md')
    if not note.exists():
        note.write_text(f'# A linked note\n\nRead [the shared paper](#paper={paper}).\n\nThis link uses its permanent ID and survives moves made here.\n', encoding='utf-8')
    library.register(writing, 'Papers/A linked note.md')


# ── Vault-local setup and the right-click picker ─────────────────
# A vault carries its own registry in a hidden '.quantum' folder at its root,
# with the vault stored relative to it, so moving the whole folder keeps working.

STATE_DIR = '.quantum'


def find_state(path):
    """Walk up from a file or folder to the vault that owns it."""
    for folder in [Path(path).resolve(), *Path(path).resolve().parents]:
        if (folder / STATE_DIR).is_dir():
            return folder
    return None


def init_vault(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError(f'Folder does not exist: {root}')
    library = Library(root / STATE_DIR)
    return library, library.add_vault(root.name, root, portable=True)


def pick(file, actor=None):
    """Right-click flow: move the paper (or also show it) in a folder you choose."""
    import tkinter as tk
    from tkinter import filedialog, messagebox
    tk_root = tk.Tk()
    tk_root.withdraw()
    tk_root.attributes('-topmost', True)
    title = 'Quantum Paper'
    try:
        file = Path(file).resolve()
        vault_root = find_state(file)
        if not vault_root:
            raise ValueError(f'{file.name} is not inside a Quantum Papers folder.\n'
                             'Set one up with: quantum.py --init-vault FOLDER')
        try:
            user = getpass.getuser()
        except Exception:
            user = 'user'
        library, vault = init_vault(vault_root)
        with library.acting_as(actor or os.environ.get('QP_ACTOR') or f'{user} (right-click)'):
            paper = library.register(vault, file.relative_to(vault_root).as_posix())
            choice = ask_action(tk_root, file.name)
            if choice is None:
                return
            if choice == 'history':
                lines = [f"{e['at'][:16].replace('T', ' ')}  {e['actor']}: {e['action']} "
                         f"{e['source'] + ' -> ' if e['source'] else ''}{e['target'] or ''}"
                         for e in reversed(library.history(paper, limit=25))]
                messagebox.showinfo(title, '\n'.join(lines) or 'No history yet.', parent=tk_root)
                return
            verb = 'Move' if choice == 'move' else 'Also show'
            dest = filedialog.askdirectory(parent=tk_root, initialdir=str(file.parent), mustexist=True,
                                           title=f'{verb} "{file.name}" to which folder?')
            if not dest:
                return
            dest = Path(dest).resolve()
            if not Library.inside(dest, vault_root):
                raise ValueError(f'Pick a folder inside {vault_root.name}.')
            folder = dest.relative_to(vault_root).as_posix()
            if choice == 'move':
                library.move(paper, vault, folder)
                messagebox.showinfo(title, f'Moved "{file.name}"\nto {vault_root.name}/{folder}', parent=tk_root)
            else:
                library.show_here(paper, vault, folder)
                messagebox.showinfo(title, f'"{file.name}" now also shows in\n{vault_root.name}/{folder}\n'
                                           '(the file itself did not move)', parent=tk_root)
    except Exception as error:
        messagebox.showerror(title, str(error), parent=tk_root)
    finally:
        tk_root.destroy()


def ask_action(parent, name):
    import tkinter as tk
    result = {'value': None}
    win = tk.Toplevel(parent)
    win.title('Quantum Paper')
    win.attributes('-topmost', True)
    win.resizable(False, False)
    tk.Label(win, text=name, font=('Segoe UI', 11, 'bold'), padx=16, pady=10).pack()

    def choose(value):
        result['value'] = value
        win.destroy()
    for label, value in [('Move it to…', 'move'), ('Also show it in…', 'show'),
                         ('History', 'history'), ('Cancel', None)]:
        tk.Button(win, text=label, width=24, command=lambda v=value: choose(v)).pack(padx=16, pady=3)
    tk.Label(win, text='', pady=2).pack()
    win.bind('<Escape>', lambda e: choose(None))
    win.protocol('WM_DELETE_WINDOW', lambda: choose(None))
    win.grab_set()
    win.focus_force()
    parent.wait_window(win)
    return result['value']


def menu_keys():
    """Explorer reads SystemFileAssociations; Directory Opus and some others read
    the .md file type's own key, so the entry goes in both."""
    import winreg
    keys = [r'Software\Classes\SystemFileAssociations\.md\shell\QuantumPaper']
    try:
        progid = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, '.md')
        if progid:
            keys.append(rf'Software\Classes\{progid}\shell\QuantumPaper')
    except OSError:
        pass
    return keys


def install_menu():
    import winreg
    pythonw = Path(sys.executable).with_name('pythonw.exe')
    exe = pythonw if pythonw.exists() else Path(sys.executable)
    command = f'"{exe}" "{Path(__file__).resolve()}" --pick "%1"'
    for menu in menu_keys():
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, menu) as key:
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, 'Quantum Paper…')
            winreg.SetValueEx(key, 'Icon', 0, winreg.REG_SZ, str(exe))
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, menu + r'\command') as key:
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, command)
    return command


def uninstall_menu():
    import winreg
    for menu in menu_keys():
        for sub in (menu + r'\command', menu):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, sub)
            except FileNotFoundError:
                pass


def undo_last(library):
    """Undo the most recent move that has not been undone yet."""
    with library.connect() as db:
        undone = set()
        for r in db.execute("SELECT details FROM events WHERE action='undo'"):
            d = json.loads(r['details'])
            undone.update({d['event'], d.get('move_event')})
        for e in db.execute("SELECT * FROM events WHERE action='move' ORDER BY id DESC LIMIT 200"):
            d = json.loads(e['details'] or '{}')
            if e['id'] not in undone and 'from_vault' in d:
                break
        else:
            raise ValueError('Nothing to undo')
    library.move(e['paper'], d['from_vault'], d['from_folder'])
    with library.connect() as db:
        back = db.execute("SELECT MAX(id) FROM events WHERE action='move' AND paper=?", (e['paper'],)).fetchone()[0]
        library.log(db, 'undo', e['paper'], e['target'], e['source'],
                    details={'event': e['id'], 'move_event': back})
    return {'undone': e['id'], 'paper': e['paper'], 'back_to': e['source']}


# ── One list of actions ─────────────────────────────────────────
# Each action feeds the CLI (--run NAME key=value), the API (POST /api/run/NAME)
# and the GUI command palette (GET /api/actions). Add an action here once and
# it shows up in all three.
ACTIONS = [
    dict(name='move', group='Organize', label='Move original to another folder',
         args=['paper', 'vault', 'folder'], needs='paper+folder',
         fn=lambda L, a: L.move(a['paper'], a['vault'], a['folder'])),
    dict(name='show', group='Organize', label='Also show in another folder',
         args=['paper', 'vault', 'folder'], needs='paper+folder',
         fn=lambda L, a: L.show_here(a['paper'], a['vault'], a['folder'])),
    dict(name='move-folder', group='Organize', label='Move a whole folder (all or nothing)',
         args=['vault', 'folder', 'dest_vault', 'dest_folder'], needs='folder+folder',
         fn=lambda L, a: {'moved': L.move_folder(a['vault'], a['folder'], a['dest_vault'], a['dest_folder'])}),
    dict(name='register', group='Organize', label='Register a Markdown file',
         args=['vault', 'path'], needs='path',
         fn=lambda L, a: {'id': L.register(a['vault'], a['path'])}),
    dict(name='scan', group='Find', label='Register every Markdown file in all vaults',
         args=[], fn=lambda L, a: L.scan_all()),
    dict(name='reconcile', group='Safety', label='Repair registry after outside changes',
         args=[], fn=lambda L, a: L.reconcile_all()),
    dict(name='undo', group='Safety', label='Undo last move',
         args=[], fn=lambda L, a: undo_last(L)),
    dict(name='history', group='Safety', label='Show history (who changed what)',
         args=[], fn=lambda L, a: {'events': L.history(a.get('paper'))}),
    dict(name='tangent', group='Write', label='Make a tangent of this paper',
         args=['paper'], needs='paper',
         fn=lambda L, a: {'id': L.create_tangent(a['paper'], a.get('scope', 'deep-dive'))}),
    dict(name='export-registry', group='Safety', label='Back up the registry to JSON',
         args=['file'], needs='file',
         fn=lambda L, a: L.export_registry(a['file'])),
]
ACTION_BY_NAME = {a['name']: a for a in ACTIONS}


def run_action(library, name, args):
    action = ACTION_BY_NAME.get(name)
    if not action:
        raise ValueError(f'Unknown action: {name}')
    missing = [k for k in action['args'] if k not in args]
    if missing:
        raise ValueError(f'{name} needs: {", ".join(missing)}')
    for key in ('vault', 'dest_vault'):
        if key in args and args[key]:
            args[key] = library.find_vault(args[key])
    result = action['fn'](library, args)
    return result if isinstance(result, dict) else {'ok': True}


def action_list():
    return [{k: v for k, v in a.items() if k != 'fn'} for a in ACTIONS]


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

        # Each caller names itself with an X-QP-Actor header (or "actor" in the JSON body).
        def do_GET(self):
            with library.acting_as(self.headers.get('X-QP-Actor')):
                return self.get()

        def do_POST(self):
            with library.acting_as(self.headers.get('X-QP-Actor')):
                return self.post()

        def get(self):
            path = urlparse(self.path).path
            try:
                if path == '/api/library':
                    return self.respond(200, library.snapshot())
                if path == '/api/actions':
                    return self.respond(200, {'actions': action_list()})
                if path == '/api/history':
                    return self.respond(200, {'events': library.history()})
                if path.startswith('/api/history/'):
                    return self.respond(200, {'events': library.history(path.rsplit('/', 1)[1])})
                if path.startswith('/api/paper/'):
                    paper = path.rsplit('/', 1)[1]
                    return self.respond(200, dict(**library.paper(paper), content=library.read(paper),
                                                  tangents=library.tangents_for(paper)))
                file = web / ('index.html' if path == '/' else path.lstrip('/'))
                if not Library.inside(file, web) or not file.is_file():
                    return self.respond(404, {'error': 'Not found'})
                self.respond(200, file.read_bytes(), mimetypes.guess_type(file)[0] or 'text/plain')
            except (ValueError, OSError) as error:
                self.respond(400, {'error': str(error)})

        def post(self):
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
                if data.get('actor'):
                    library._local.actor = str(data['actor'])
                action = urlparse(self.path).path
                if action.startswith('/api/run/'):
                    return self.respond(200, run_action(library, action.rsplit('/', 1)[1], data))
                if action == '/api/show':
                    library.show_here(data['paper'], data['vault'], data['folder'])
                elif action == '/api/move':
                    library.move(data['paper'], data['vault'], data['folder'])
                elif action == '/api/batch-move':
                    moved = library.batch_move(data['papers'], data['vault'], data['folder'])
                    return self.respond(200, {'moved': moved})
                elif action == '/api/save':
                    library.save(data['paper'], data['content'])
                elif action == '/api/register':
                    return self.respond(200, {'id': library.register(data['vault'], data['path'])})
                elif action == '/api/batch-register':
                    return self.respond(200, {'ids': library.batch_register(data['vault'], data['paths'])})
                elif action == '/api/reconcile':
                    vault = data.get('vault')
                    return self.respond(200, library.reconcile(vault) if vault else library.reconcile_all())
                elif action == '/api/tangent/add':
                    tid = library.add_tangent(data['paper'], data['title'], data.get('scope', 'deep-dive'))
                    return self.respond(200, {'id': tid})
                elif action == '/api/tangent/create':
                    tid = library.create_tangent(data['paper'], data.get('scope', 'deep-dive'))
                    return self.respond(200, {'id': tid})
                elif action == '/api/tangent/search':
                    return self.respond(200, {'tangents': library.tangent_search(data['query'])})
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
    parser.add_argument('--actor', help='Name recorded in the history for your changes (or set QP_ACTOR)')
    parser.add_argument('--history', nargs='?', const='', metavar='PAPER_OR_PATH',
                        help='Show who changed what; optionally for one paper id or vault-relative path')
    parser.add_argument('--portable', action='store_true', help='Store new --vault roots relative to --state')
    parser.add_argument('--view', help='Apply a view to a vault: all, working, 13roads, canon, drafts, pipeline')
    parser.add_argument('--view-vault', help='Vault name or path for --view')
    parser.add_argument('--view-list', help='List folder visibility for a vault (name or path)')
    parser.add_argument('--scan', action='store_true', help='Auto-register all .md files in all vaults')
    parser.add_argument('--reconcile', action='store_true', help='Repair the registry after external moves')
    parser.add_argument('--move-folder', nargs=4, metavar=('VAULT', 'FOLDER', 'DEST_VAULT', 'DEST_FOLDER'),
                        help='Move every paper directly in FOLDER into DEST_FOLDER (all or nothing)')
    parser.add_argument('--export-registry', metavar='FILE', help='Write the whole registry to a JSON backup')
    parser.add_argument('--import-registry', metavar='FILE', help='Merge a JSON backup into the registry')
    parser.add_argument('--init-vault', metavar='FOLDER', help='Give a folder its own registry in FOLDER/.quantum')
    parser.add_argument('--pick', metavar='FILE', help='Right-click flow: move/show a paper via folder picker')
    parser.add_argument('--install-menu', action='store_true', help='Add "Quantum Paper…" to the .md right-click menu')
    parser.add_argument('--uninstall-menu', action='store_true', help='Remove the right-click menu entry')
    parser.add_argument('--actions', action='store_true', help='List every action (same list as the GUI palette)')
    parser.add_argument('--run', nargs='+', metavar=('ACTION', 'KEY=VALUE'),
                        help='Run any action, e.g. --run move paper=ID vault=Research folder=Papers')
    args = parser.parse_args()
    if args.actions:
        for a in ACTIONS:
            print(f"  {a['group']:<9} {a['name']:<16} {a['label']}  [{' '.join(a['args'])}]")
        sys.exit(0)
    if args.pick:
        pick(args.pick, args.actor)
        sys.exit(0)
    if args.init_vault:
        lib, vid = init_vault(args.init_vault)
        print(f'Ready: {Path(args.init_vault).resolve()} (registry in {lib.state})')
        sys.exit(0)
    if args.install_menu:
        print('Installed:', install_menu())
        sys.exit(0)
    if args.uninstall_menu:
        uninstall_menu()
        print('Removed right-click entry')
        sys.exit(0)
    library = Library(args.state, actor=args.actor)
    for root in args.vault:
        library.add_vault(Path(root).name, root, portable=args.portable)
    if args.demo:
        demo(library)

    try:
        if args.run:
            name, pairs = args.run[0], args.run[1:]
            if any('=' not in p for p in pairs):
                raise ValueError('Arguments must look like key=value')
            print(json.dumps(run_action(library, name, dict(p.split('=', 1) for p in pairs)),
                             indent=2, ensure_ascii=False, default=str))
            sys.exit(0)
        if args.history is not None:
            target = args.history or None
            if target:
                with library.connect() as db:
                    row = db.execute('SELECT id FROM papers WHERE id=? OR path=?',
                                     (target, Library.clean(target).removeprefix('./'))).fetchone()
                target = row['id'] if row else target
            for e in reversed(library.history(target, limit=200)):
                where = f"{e['source']} -> {e['target'] or ''}" if e['source'] else (e['target'] or '')
                print(f"{e['at']}  {e['actor']:<28} {e['action']:<14} {where}  {e['details'] or ''}")
            sys.exit(0)
        if args.import_registry:
            print(json.dumps(library.import_registry(args.import_registry)))
            sys.exit(0)
        if args.export_registry:
            print(json.dumps(library.export_registry(args.export_registry)))
            sys.exit(0)
        if args.reconcile:
            for name, r in library.reconcile_all().items():
                print(f"  {name}: {len(r['moved'])} moved, {len(r['stale'])} stale, "
                      f"{len(r['new'])} new, {len(r['restored'])} restored, {len(r['ambiguous'])} ambiguous")
                for m in r['moved']:
                    print(f"    MOVED {m['from']} -> {m['to']}")
                for s in r['stale']:
                    print(f"    STALE {s['path']}")
                for a in r['ambiguous']:
                    print(f"    AMBIGUOUS {a['path']} -> {', '.join(a['candidates'])}")
            sys.exit(0)
        if args.move_folder:
            v, f, dv, df = args.move_folder
            moved = library.move_folder(library.find_vault(v), f, library.find_vault(dv), df)
            print(f'Moved {len(moved)} papers')
            sys.exit(0)
    except (ValueError, OSError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)

    if args.scan:
        results = library.scan_all()
        for name, r in results.items():
            print(f"  {name}: {r['registered']} new, {r['skipped']} already known")
        total = sum(r['registered'] for r in results.values())
        print(f"  Total new: {total}")
        sys.exit(0)

    # View commands (non-server mode)
    if args.view_list:
        try:
            for f in library.vault_view_list(library.find_vault(args.view_list)):
                status = 'HIDDEN ' if f['hidden'] else 'VISIBLE'
                print(f"  [{status}] {f['name']}")
        except ValueError as error:
            print(error)
    elif args.view:
        target = args.view_vault or (args.vault[0] if args.vault else None)
        if not target:
            print("Specify --view-vault or --vault for the view target")
        else:
            try:
                changes = library.vault_view(library.find_vault(target), args.view)
                for action, old, new in changes:
                    print(f"  {action.upper()}: {old} -> {new}")
                print(f"Applied view '{args.view}': {len(changes)} folders changed")
            except ValueError as error:
                print(error)
    else:
        print(f'Quantum Papers listening on port {args.port}', flush=True)
        ThreadingHTTPServer(('127.0.0.1', args.port), handler(library)).serve_forever()
