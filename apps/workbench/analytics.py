"""Source-scoped research analytics with explicit denominators."""
import sys

from index import APPS, VERSION

CONSTRAINTS = (
    'empirical', 'internal', 'parsimony', 'predictive', 'falsifiable',
    'causal', 'integration', 'epistemic', 'pragmatic',
)
CDCM_METRICS = {
    'violations_per_axiom': ('violations/axiom', 'negative assessed scores / fully assessed axioms'),
    'violations_per_scored_cell': ('violations/cell', 'negative assessed scores / scored constraint cells'),
}


def coherence(index, snapshot, paper, actor):
    sys.path.insert(0, str(APPS / 'research-backend'))
    from core.coherence.cdcm_analyzer import ConstraintScores, FrameworkMetrics

    assessments = {}
    for row in snapshot['records']:
        if row['kind'] == 'constraints' and row['paper_id'] == paper['id'] and row['current']:
            assessment = row['data']
            assessments[assessment['axiom']] = assessment
    if not assessments:
        return []
    complete = [ConstraintScores(axiom_id=row['axiom'], **{
        f'c{i}_{name}': row['scores'][name] for i, name in enumerate(CONSTRAINTS, 1)
    }) for row in assessments.values() if all(row['scores'].get(name) is not None for name in CONSTRAINTS)]
    all_scores = [score for row in assessments.values() for score in row['scores'].values() if score is not None]
    denominators = [len(complete), len(all_scores)]
    numerators = [sum(axiom.violations for axiom in complete), all_scores.count(-1)]
    values = [FrameworkMetrics(paper['title'], axioms=complete).violation_density() if complete else None,
              numerators[1] / denominators[1] if denominators[1] else None]
    return [
        index.record('metrics', paper, actor, dict(metric=metric, unit=unit, method=method,
                     definition_version=VERSION, numerator=numerator, denominator=denominator,
                     value=value, assessment_status='measured' if denominator else 'unassessed',
                     assessment_ids=[row['id'] for row in snapshot['records'] if row['kind'] == 'constraints'
                                     and row['paper_id'] == paper['id'] and row['current']]),
                     engine='research-backend/cdcm', validation='calculated')
        for (metric, (unit, method)), numerator, denominator, value in
        zip(CDCM_METRICS.items(), numerators, denominators, values)
    ]


def add_assessment(index, snapshot, paper, actor, kind, entry, span):
    if not isinstance(entry, dict):
        raise ValueError('Expected a research record object')
    if kind == 'constraints':
        scores = entry.get('scores')
        axiom = entry.get('axiom')
        if not isinstance(axiom, str) or not axiom.strip() or not isinstance(scores, dict):
            raise ValueError('An assessment needs an axiom and scores')
        if (not scores or not scores.keys() <= set(CONSTRAINTS)
                or any(score is not None and (type(score) is not int or score not in {-1, 0, 1})
                       for score in scores.values())):
            raise ValueError('Supply named constraint scores of -1, 0, 1 or null')
    elif kind == 'relationships':
        ids = {r['id'] for r in snapshot['records'] if r['kind'] in {'ledger', 'atoms'} and r['current']}
        local_ids = {r['id'] for r in snapshot['records'] if r['paper_id'] == paper['id'] and r['id'] in ids}
        if (not isinstance(entry.get('source'), str) or entry['source'] not in local_ids
                or not isinstance(entry.get('target'), str) or entry['target'] not in ids):
            raise ValueError('A directed relationship needs current source and target record IDs')
        if entry.get('type') not in ('supports', 'depends_on', 'contradicts', 'corresponds_to', 'related_to'):
            raise ValueError('Choose a supported relationship type')
        entry = dict(entry, direction='source_to_target', review_state='candidate')
    text_key = {'relationships': 'rationale', 'constraints': 'rubric'}.get(kind, 'text')
    if not isinstance(entry.get(text_key), str) or not entry[text_key].strip():
        raise ValueError(f'Missing {text_key}')
    return index.record(kind, paper, actor, entry, engine='manual-research-record', locator=span)


def translate(index, paper, actor, dictionary, span):
    """Run the retained MTL translator against a versioned, explicitly supplied table."""
    from pathlib import Path

    from index import create, digest

    sys.path.insert(0, str(APPS / 'research-backend'))
    from core.math_translator import MathTranslator

    raw = Path(dictionary).read_bytes()
    dictionary_hash = digest(raw)
    copy = index.state / 'dictionaries' / f'{dictionary_hash}.csv'
    create(copy, raw)
    translator = MathTranslator(str(copy))
    if not translator.translation_table:
        raise ValueError('The MTL CSV has no usable symbol definitions')
    lines = index.source(paper).decode('utf-8-sig').splitlines()
    first, last = span
    if not 1 <= first <= last <= len(lines):
        raise ValueError('Invalid source span')
    source = '\n'.join(lines[first - 1:last])
    result = translator.extract_translations_only(source)
    return index.record('ledger', paper, actor,
                        dict(type='equation', text=str(result), dictionary_sha256=dictionary_hash),
                        engine='research-backend/math-translator', locator=span)
