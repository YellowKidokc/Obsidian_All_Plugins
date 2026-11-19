"""Run the integrated Obsidian workbench against a selected local folder."""
import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from html import escape
from urllib.parse import urlencode

from adapters import (
    add_ledger, import_projection, import_review, prepare, projections, review_target,
)
from analytics import add_assessment, coherence, translate
from index import Index, contained, digest
from navigation import navigation
from views import export, html_document, workspace


def handler(index):
    class Handler(BaseHTTPRequestHandler):
        def respond(self, body, content_type='text/html; charset=utf-8', status=200):
            if isinstance(body, str):
                body = body.encode()
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(body)

        def local_host(self):
            port = self.server.server_port
            return self.headers.get('Host') in {f'localhost:{port}', f'127.0.0.1:{port}'}

        def do_GET(self):
            if not self.local_host():
                return self.respond('Unknown Host', 'text/plain', 403)
            path = urlsplit(self.path)
            query = parse_qs(path.query)
            try:
                snapshot = index.current()
                if path.path == '/':
                    return self.respond(workspace(index, snapshot, query))
                if path.path == '/api/inventory':
                    selected = {k: snapshot[k] for k in ('schema_version', 'id', 'series', 'papers', 'folders', 'processing')}
                    return self.respond(json.dumps(selected), 'application/json')
                if path.path == '/projection':
                    record = next((r for r in snapshot['records'] if r['kind'] == 'runs'
                                   and r['id'] == query.get('run', [''])[0]), None)
                    if record:
                        directory = contained(index.state, record['data']['path'])
                        manifest = projections.load_json(directory / 'manifest.json')
                        files = {manifest['source_file'], 'manifest.json', 'projection-result.schema.json'}
                        files.update(f'PROMPTS/{code}.txt' for code, task in manifest['tasks'].items()
                                     if task['execution'] == 'api')
                        files.update(f'RESULTS/{code}.json' for code in manifest['tasks']
                                     if (directory / 'RESULTS' / f'{code}.json').is_file())
                        if 'ai_package' in manifest['tasks']:
                            files.add('AI_PACKAGE.zip')
                        name = query.get('file', [''])[0]
                        if name in files:
                            return self.respond(contained(directory, name).read_bytes(),
                                                'application/zip' if name.endswith('.zip') else 'text/plain; charset=utf-8')
                        if not name:
                            links = ''.join('<li><a href="/projection?' + escape(urlencode(
                                {'run': record['id'], 'file': filename}), quote=True) + '">' +
                                escape(filename) + '</a></li>' for filename in sorted(files))
                            return self.respond(html_document('Projection package',
                                '<h1>Projection package</h1><ul>' + links + '</ul>'))
                if path.path == '/media':
                    item = next((m for m in snapshot['media'] if m['path'] == query.get('path', [''])[0]), None)
                    if item:
                        target = contained(index.root, item['path'])
                        raw = target.read_bytes()
                        if digest(raw) != item['sha256']:
                            return self.respond('Media changed. Scan again.', 'text/plain', 409)
                        mime = mimetypes.guess_type(target)[0] or 'application/octet-stream'
                        if mime == 'image/svg+xml':
                            mime = 'application/octet-stream'
                        return self.respond(raw, mime)
                return self.respond('Not found', 'text/plain', 404)
            except (OSError, ValueError) as error:
                return self.respond(str(error), 'text/plain', 400)

        def do_POST(self):
            if (not self.local_host() or self.headers.get('Origin') != f'http://{self.headers.get("Host")}'
                    or self.headers.get_content_type() != 'application/x-www-form-urlencoded'
                    or self.path != '/prepare'):
                return self.respond('Unsupported request', 'text/plain', 403)
            try:
                size = int(self.headers.get('Content-Length', 0))
                if not 0 < size <= 8192:
                    raise ValueError('Invalid request length')
                form = parse_qs(self.rfile.read(size).decode())
                actor = form.get('actor', [''])[0].strip()
                if not actor:
                    raise ValueError('Enter the operator name')
                paper = index.paper(form['paper'][0])
                prepare(index, paper, actor, form.get('task', []))
                self.send_response(303)
                self.send_header('Location', '/?paper=' + paper['id'])
                self.send_header('Content-Length', '0')
                self.end_headers()
            except (KeyError, OSError, ValueError) as error:
                self.respond(str(error), 'text/plain', 400)

    return Handler


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--root', type=Path, required=True, help='Explicitly selected copied Markdown root')
    cli.add_argument('--state', type=Path, help='Backside or external output directory')
    cli.add_argument('--actor', default='workbench-cli')
    commands = cli.add_subparsers(dest='command', required=True)
    scan = commands.add_parser('scan')
    scan.add_argument('--exclude', action='append', default=[])
    scan.add_argument('--quantum-db')
    serve = commands.add_parser('serve')
    serve.add_argument('--port', type=int, default=8766)
    commands.add_parser('export')
    nav = commands.add_parser('navigation')
    nav.add_argument('--apply', action='store_true')
    package = commands.add_parser('prepare')
    package.add_argument('paper')
    package.add_argument('codes', nargs='+', choices=[*projections.TASKS, 'all'])
    result = commands.add_parser('import-projection')
    result.add_argument('run')
    result.add_argument('response', type=Path)
    ledger = commands.add_parser('add-ledger')
    ledger.add_argument('paper')
    ledger.add_argument('entry', type=Path)
    ledger.add_argument('span', type=int, nargs=2)
    assessment = commands.add_parser('add-research-record')
    assessment.add_argument('paper')
    assessment.add_argument('kind', choices=['atoms', 'constraints', 'relationships', 'mappings', 'objections'])
    assessment.add_argument('entry', type=Path)
    assessment.add_argument('span', type=int, nargs=2)
    commands.add_parser('calculate-cdcm').add_argument('paper')
    mtl = commands.add_parser('translate-math')
    mtl.add_argument('paper')
    mtl.add_argument('dictionary', type=Path)
    mtl.add_argument('span', type=int, nargs=2)
    target = commands.add_parser('review-target')
    target.add_argument('paper')
    target.add_argument('--html', action='store_true')
    review = commands.add_parser('import-review')
    review.add_argument('paper')
    review.add_argument('target')
    review.add_argument('response', type=Path)
    review.add_argument('span', type=int, nargs=2)
    args = cli.parse_args()
    try:
        index = Index(args.root, args.state or args.root / '.backside' / 'workbench')
        command = args.command
        if command == 'scan':
            print(index.scan(args.actor, args.exclude, args.quantum_db))
            return
        snapshot = index.current()
        if command == 'serve':
            with ThreadingHTTPServer(('127.0.0.1', args.port), handler(index)) as server:
                print(f'Workbench listening on http://127.0.0.1:{server.server_port}', flush=True)
                server.serve_forever()
        elif command == 'export':
            print(export(index, snapshot, args.actor))
        elif command == 'navigation':
            print(json.dumps(navigation(index, snapshot, args.actor, args.apply), ensure_ascii=False, indent=2))
        elif command == 'import-projection':
            print(import_projection(index, snapshot, args.run, args.actor, args.response.read_bytes()))
        else:
            paper = index.paper(args.paper, snapshot)
            if command == 'prepare':
                print(prepare(index, paper, args.actor, list(projections.TASKS) if 'all' in args.codes else args.codes))
            elif command == 'review-target':
                print(review_target(index, paper, args.html))
            elif command == 'import-review':
                print(import_review(index, paper, args.actor, args.response.read_bytes(), args.span, args.target))
            elif command == 'translate-math':
                print(translate(index, paper, args.actor, args.dictionary, args.span)['id'])
            elif command == 'calculate-cdcm':
                print(json.dumps(coherence(index, snapshot, paper, args.actor)))
            elif command == 'add-research-record':
                print(add_assessment(index, snapshot, paper, args.actor, args.kind,
                                     json.loads(args.entry.read_bytes()), args.span)['id'])
            elif command == 'add-ledger':
                print(add_ledger(index, paper, args.actor, json.loads(args.entry.read_bytes()), args.span)['id'])
    except (OSError, ValueError) as error:
        cli.error(str(error))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
