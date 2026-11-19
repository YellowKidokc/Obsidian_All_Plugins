"""Plan or apply bounded folder index updates using the cached inventory."""
import html
import os
import posixpath
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import quote

from adapters import json_bytes
from index import contained, create, digest, key, timestamp
from views import html_document

START = b'<!-- nav:start -->'
END = b'<!-- nav:end -->'


def title(text):
    return text.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]').replace('\n', ' ')


def navigation(index, snapshot, actor, apply=False):
    plan, html_sections = [], []
    folders = {f['path']: f for f in snapshot['folders']}
    papers = [p for p in snapshot['papers'] if p['availability'] == 'present']
    output = index.state / 'navigation' / key(snapshot['id'], timestamp())
    for folder in folders:
        direct = [p for p in papers if p['folder'] == folder]
        children = [f for f in folders if f != folder and posixpath.dirname(f) in {folder, '' if folder == '.' else folder}]
        readme = next((p for p in direct if Path(p['path']).stem.casefold() in {'readme', 'purpose'}), None)
        purpose = 'Structural inventory'
        if readme:
            first = next((line.strip() for line in index.source(readme).decode('utf-8-sig').splitlines()
                          if line.strip() and not line.startswith('#')), '')
            if first:
                purpose = title(first)
        lines = [f'## {title(folders[folder]["name"])}', '', purpose, '',
                 f'{len(direct)} Markdown files · {len(children)} child folders']
        if folder != '.':
            lines.extend(['', '[Parent folder](../_INDEX.md)'])
        lines.extend(['', '### Folders'])
        for child in children:
            link = quote(posixpath.relpath(child, folder) + '/_INDEX.md')
            lines.append(f'- [{title(folders[child]["name"])}]({link})')
        lines.extend(['', '### Files'])
        for paper in direct:
            filename = Path(paper['path']).name
            lines.append(f'- [{title(filename)}]({quote(filename)}) · '
                         f'{sum(p["paper_id"] == paper["id"] for p in snapshot["passages"])} source blocks')
        if direct:
            from datetime import datetime, timezone
            date = datetime.fromtimestamp(max(p['modified_ns'] for p in direct) / 1e9, timezone.utc)
            lines += ['', f'Latest source change: {date.date().isoformat()} UTC']
        block = START + b'\n' + '\n'.join(lines).encode() + b'\n' + END
        relative = Path(folder) / '_INDEX.md'
        try:
            target = contained(index.root, relative)
            before = target.read_bytes()
        except FileNotFoundError:
            target = contained(index.root, relative.parent) / relative.name
            before = None
        if before is None:
            after = block + b'\n'
        elif before.count(START) == before.count(END) == 1 and before.index(START) < before.index(END):
            after = before[:before.index(START)] + block + before[before.index(END) + len(END):]
        else:
            plan.append(dict(path=relative.as_posix(), action='hold', reason='Authored or malformed index'))
            continue
        html_sections.append(f'<section><h2>{html.escape(folder)}</h2><ul>' + ''.join(
            f'<li><a href="{html.escape((index.root / p["path"]).as_uri(), quote=True)}">'
            f'{html.escape(p["title"])}</a></li>' for p in direct) + '</ul></section>')
        if before == after:
            continue
        entry = dict(path=relative.as_posix(), action='create' if before is None else 'replace_generated_block',
                     before_sha256=digest(before) if before is not None else None, after_sha256=digest(after))
        plan.append(entry)
        if apply:
            recovery = output / 'operations' / key(relative.as_posix())
            if before is not None:
                create(recovery / 'original.md', before)
            create(recovery / 'receipt.json', json_bytes(dict(entry, actor=actor, intended_at=timestamp())))
            if before is None:
                create(target, after)
            else:
                with NamedTemporaryFile(dir=target.parent, delete=False) as staged:
                    staged.write(after)
                temporary = Path(staged.name)
                try:
                    if target.read_bytes() != before:
                        raise ValueError(f'Index changed during apply: {relative}')
                    os.chmod(temporary, target.stat().st_mode)
                    temporary.replace(target)
                finally:
                    temporary.unlink(missing_ok=True)
            create(recovery / 'applied.json', json_bytes(dict(at=timestamp(), actor=actor)))
    if apply:
        create(output / 'index.html', html_document('Folder navigation', '<h1>Folders</h1>' + ''.join(html_sections)).encode())
        create(output / 'manifest.json', json_bytes(dict(actor=actor, snapshot=snapshot['id'], operations=plan)))
    return dict(changes=plan, output=str(output) if apply else None)
