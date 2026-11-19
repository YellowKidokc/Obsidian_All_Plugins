"""Views and exports driven by a single captured workbench snapshot."""
import io
from html import escape
from pathlib import Path
from urllib.parse import quote, urlencode

from adapters import json_bytes, projections, record_artifact
from analytics import CDCM_METRICS, relationship_graph
from index import METRICS, VERSION, contained, create, digest, key, timestamp


def html_document(title, body):
    return f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title>
<style>
:root {{color-scheme:light;background:#f5f3ed;color:#242c27;font:16px system-ui}}
body {{max-width:1120px;margin:auto;padding:1.75rem}}
a {{color:#205e49}} main,section,aside {{min-width:0}}
.layout {{display:grid;grid-template-columns:minmax(12rem,1fr) minmax(0,3fr);gap:1.5rem}}
.panel {{padding:1.15rem;border:1px solid #d7dbcf;background:#fffdf5;border-radius:.65rem}}
pre {{white-space:pre-wrap;overflow-wrap:anywhere;background:#eeefe6;padding:1rem}}
mark {{display:block;background:#e0f1bb}} nav a {{margin-right:.7rem}} li {{margin:.4rem 0}}
table {{width:100%;border-collapse:collapse}} td,th {{text-align:left;padding:.4rem;border-bottom:1px solid #dadfd5}}
small {{overflow-wrap:anywhere}} @media(max-width:700px) {{.layout {{grid-template-columns:1fr}}}}
</style><body>{body}</body></html>'''


def href(**query):
    return '/?' + escape(urlencode(query), quote=True)


def paper_list(papers):
    return '<ul>' + ''.join(
        f'<li><a href="{href(paper=paper["id"])}">{escape(paper["path"])}</a>'
        f' · {escape(paper["availability"])}</li>' for paper in papers
    ) + '</ul>'


def table(headers, rows):
    head = ''.join(f'<th>{escape(title)}</th>' for title in headers)
    body = ''.join('<tr>' + ''.join(f'<td>{escape(str(value)) if value is not None else "—"}</td>'
                                   for value in row) + '</tr>' for row in rows)
    return f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def workspace(index, snapshot, query):
    series = query.get('series', [''])[0]
    folder = query.get('folder', [''])[0]
    paper_id = query.get('paper', [''])[0]
    record_id = query.get('record', [''])[0]
    selected = next((paper for paper in snapshot['papers'] if paper['id'] == paper_id), None)
    if selected:
        series, folder = selected['series'], selected['folder']
    side = '<h2>Series</h2><ul>' + ''.join(
        f'<li><a href="{href(series=name)}">{escape(name)}</a></li>' for name in snapshot['series']
    ) + '</ul>'
    if series:
        folders = sorted({paper['folder'] for paper in snapshot['papers'] if paper['series'] == series})
        side += '<h2>Folders</h2><ul>' + ''.join(
            f'<li><a href="{href(series=series, folder=name)}">{escape(name)}</a></li>' for name in folders
        ) + '</ul>'
    candidates = [paper for paper in snapshot['papers']
                  if (not series or paper['series'] == series) and (not folder or paper['folder'] == folder)]
    body = '<h2>Papers</h2>' + paper_list(candidates)
    if selected:
        p = selected
        paper_names = {paper['id']: paper['path'] for paper in snapshot['papers']}
        current_records = [r for r in snapshot['records'] if r['current']]
        scope = query.get('scope', ['paper'])[0]
        kind = query.get('type', [''])[0]
        rows = [r for r in current_records if r['kind'] == 'ledger'
                and (not kind or r['data']['type'] == kind)
                and (scope == 'corpus' or r['paper_id'] == p['id']
                     or (scope == 'series' and r['paper_id'] in {q['id'] for q in snapshot['papers']
                                                                 if q['series'] == series}))]
        record = next((r for r in rows if r['id'] == record_id), None)
        target = index.paper(record['paper_id'], snapshot) if record else p
        locator = record['provenance']['locator'] if record else None
        body = (f'<h2>{escape(p["title"])}</h2><p>{escape(p["path"])}</p>'
                f'<small>SHA-256 {escape(p["sha256"])}</small>')
        if p['availability'] != 'present':
            body += f'<p>Source {escape(p["availability"])}.</p>'
        else:
            lines = index.source(target).decode('utf-8-sig').splitlines()
            first, last = locator or (1, len(lines))
            excerpt = '\n'.join(f'{i}  {lines[i - 1]}' for i in range(first, last + 1))
            body += (f'<h3>Source · {escape(target["path"])}</h3>'
                     f'<pre>{escape(excerpt)}</pre>')
        body += '<h3>Quantum registry</h3>' + table(('Membership',), ((name,) for name in p['memberships']))
        events = [event for event in snapshot['quantum_history'] if event['paper'] == paper_id]
        if events:
            body += table(('Time', 'Actor', 'Action', 'Source', 'Target'),
                          ((event['at'], event['actor'], event['action'], event['source'], event['target'])
                           for event in events))
        body += '<h3>Processing</h3>' + table(('Task', 'State'), (
            (task['task'], task['status']) for task in snapshot['processing'] if task['paper_id'] == paper_id
        ))
        body += '<h3>Ledger</h3><nav>' + ' '.join(
            f'<a href="{href(paper=paper_id, scope=s, type=kind)}">{s.title()}</a>'
            for s in ('paper', 'series', 'corpus')
        ) + '</nav><nav>' + ' '.join(
            f'<a href="{href(paper=paper_id, scope=scope, type=k)}">{k.title() or "All"}</a>'
            for k in ('', 'claim', 'premise', 'proof', 'evidence', 'lean', 'audit', 'objection', 'definition')
        ) + '</nav><ul>' + ''.join(
            f'<li><a href="{href(paper=paper_id, scope=scope, type=kind, record=r["id"])}">'
            f'{escape(r["data"]["type"])} · {escape(r["data"]["text"])}</a> · '
            f'{escape(paper_names[r["paper_id"]])}</li>' for r in rows
        ) + '</ul>'
        body += '<h3>Named media</h3><ul>' + ''.join(
            f'<li><a href="/media?path={quote(item["path"])}">{escape(item["name"])}</a></li>'
            for item in snapshot['media'] if item['paper_id'] == paper_id
        ) + '</ul>'
        body += '<h3>Projection runs</h3><ul>' + ''.join(
            f'<li><a href="/projection?run={quote(r["id"])}">{escape(r["data"]["run_id"])}</a></li>'
            for r in current_records if r['paper_id'] == paper_id and r['kind'] == 'runs'
        ) + '</ul>'
        if p['availability'] == 'present':
            options = ''.join(f'<label><input type="checkbox" name="task" value="{code}">'
                              f'{escape(task["title"])}</label><br>'
                              for code, task in projections.TASKS.items())
            body += (f'<form method="post" action="/prepare"><details><summary>Prepare projections offline</summary>'
                     f'<input type="hidden" name="paper" value="{escape(paper_id, quote=True)}">'
                     f'{options}<label>Operator <input name="actor" required></label> '
                     f'<button>Prepare selected</button></details></form>')
        body += '<h3>Review history</h3>' + table(('Reviewer', 'Decision', 'Feedback', 'Version'), (
            (r['actor'], r['data']['decision'], r['data']['feedback'], 'current' if r['current'] else 'older')
            for r in snapshot['records'] if r['kind'] == 'reviews' and r['paper_id'] == paper_id))
    return html_document('Obsidian Workbench',
                         f'<header><h1>Obsidian Workbench</h1><a href="/">All papers</a></header>'
                         f'<div class="layout"><aside class="panel">{side}</aside>'
                         f'<main class="panel">{body}</main></div>')


def dashboard_rows(snapshot):
    return [('Papers', len(snapshot['papers'])),
            ('Available', sum(p['availability'] == 'present' for p in snapshot['papers'])),
            ('Passages', len(snapshot['passages'])),
            ('Processing complete', sum(p['status'] == 'done' for p in snapshot['processing']))]


def export(index, snapshot, actor):
    from openpyxl import Workbook
    from openpyxl.chart import BarChart, Reference

    folder = index.state / 'exports' / key(snapshot['id'], timestamp())
    summary = dashboard_rows(snapshot)
    graph = relationship_graph(snapshot, {paper['id'] for paper in snapshot['papers']})
    payload = dict(snapshot, totals=dict(summary), graph=graph)
    workbook = Workbook()
    dashboard = workbook.active
    dashboard.title = 'Dashboard'
    dashboard.append(('Measure', 'Snapshot value', 'Recalculate from rows'))
    formulas = ("=COUNTA(Papers!A:A)-1", '=COUNTIF(Papers!E:E,"present")',
                "=COUNTA(Passages!A:A)-1", '=COUNTIF(Processing!C:C,"done")')
    for row, formula in zip(summary, formulas):
        dashboard.append((*row, formula))
    chart = BarChart()
    chart.title = 'Snapshot totals'
    chart.add_data(Reference(dashboard, min_col=2, min_row=1, max_row=5), titles_from_data=True)
    chart.set_categories(Reference(dashboard, min_col=1, min_row=2, max_row=5))
    dashboard.add_chart(chart, 'E2')
    dashboard.freeze_panes = 'A2'
    dashboard.column_dimensions['A'].width = 26
    dashboard.column_dimensions['B'].width = 18
    dashboard.column_dimensions['C'].width = 28

    report_sections = []
    def sheet(name, headers, rows):
        tab = workbook.create_sheet(name)
        tab.append(headers)
        rows = list(rows)
        report_sections.append((name, headers, rows))
        for row in rows:
            tab.append(row)
            for cell in tab[tab.max_row]:
                if isinstance(cell.value, str):
                    cell.data_type = 's'
        tab.freeze_panes = 'A2'
        tab.auto_filter.ref = tab.dimensions
        return tab

    papers = sheet('Papers', ('ID', 'Path', 'Series', 'Document ID declaration', 'State', 'SHA-256'), (
        (p['id'], p['path'], p['series'], p['document_id'], p['availability'], p['sha256'])
        for p in snapshot['papers']))
    for n, paper in enumerate(snapshot['papers'], 2):
        if paper['availability'] == 'present':
            name = f"{paper['sha256']}.md"
            create(folder / 'sources' / name, index.source(paper))
            papers.cell(n, 2).hyperlink = 'sources/' + name
    sheet('Passages', ('ID', 'Paper', 'Source SHA-256', 'Start line', 'End line'), (
        (p['id'], p['paper_id'], p['source_sha256'], p['start_line'], p['end_line'])
        for p in snapshot['passages']))
    sheet('Processing', ('Paper', 'Task', 'State'),
          ((p['paper_id'], p['task'], p['status']) for p in snapshot['processing']))
    sheet('Metric dictionary', ('Metric', 'Unit', 'Method', 'Definition version'),
          ((name, unit, method, VERSION) for name, (unit, method) in (METRICS | CDCM_METRICS).items()))
    keys = ('paper_id', 'metric', 'value', 'unit', 'numerator', 'denominator',
            'definition_version', 'source_sha256', 'assessment_status')
    observations = snapshot['metrics'] + [
        dict(r['data'], paper_id=r['paper_id'], source_sha256=r['provenance']['source_sha256'])
        for r in snapshot['records'] if r['kind'] == 'metrics' and r['current']]
    sheet('Observations', keys, ((m[k] for k in keys) for m in observations))
    sheet('Media', ('Paper', 'Name', 'Path', 'Source SHA-256', 'SHA-256'),
          ((m['paper_id'], m['name'], m['path'], m['source_sha256'], m['sha256']) for m in snapshot['media']))
    sheet('Issues', ('Paper', 'Issue'), ((m['paper_id'], m['message']) for m in snapshot['issues']))
    for kind in ('atoms', 'ledger', 'constraints', 'mappings', 'relationships', 'objections',
                 'runs', 'artifacts', 'reviews'):
        sheet(kind.capitalize(), ('ID', 'Paper', 'Actor', 'Source SHA-256', 'Current',
                                  'Locator', 'Engine', 'Recorded at', 'Data preview', 'Details in FIS JSON'), (
            (r['id'], r['paper_id'], r['actor'], r['provenance']['source_sha256'], r['current'],
             str(r['provenance']['locator']), r['provenance']['engine'], r['provenance']['recorded_at'],
             json_bytes(r['data']).decode()[:2000], 'fis.json · ' + r['id']) for r in snapshot['records'] if r['kind'] == kind))
    source_links = ''.join(
        f'<li><a href="sources/{paper["sha256"]}.md">{escape(paper["path"])}</a></li>'
        for paper in snapshot['papers'] if paper['availability'] == 'present')
    sections = ''.join(
        f'<details open><summary>{escape(name)} ({len(rows)})</summary>{table(headers, rows)}</details>'
        for name, headers, rows in report_sections)
    html = html_document('Workbench export', '<h1>Workbench export</h1>'
                         + table(('Measure', 'Total'), summary)
                         + f'<h2>Preserved sources</h2><ul>{source_links}</ul>'
                         + sections)
    stream = io.BytesIO()
    workbook.save(stream)
    paths = {
        'workbench.xlsx': stream.getvalue(),
        'fis.json': json_bytes(payload),
        'relationships.json': json_bytes(graph),
        'index.html': html.encode(),
    }
    for name, raw in paths.items():
        create(folder / name, raw)
        record_artifact(index, actor, folder / name, 'snapshot-export')
    create(folder / 'manifest.json', json_bytes(dict(snapshot_id=snapshot['id'], actor=actor,
                                                    files={name: digest(raw) for name, raw in paths.items()})))
    return folder
