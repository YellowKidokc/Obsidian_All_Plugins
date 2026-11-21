# Candidate interpretation prompts — review input

Thirteen bounded prompt drafts from the desired-output helper. They are review candidates, not implemented tasks or permission for thirteen paid calls. Extraction, criticism and validation remain separate. The shared execution contract in ../06_REVIEW_CALL.md remains the implementation boundary until reviewed.

Source document SHA-256: 21f0fc43c2a98c6a1372d77235a9da095685082591d7e53b0f29510de02c842c

### P01 Claim extraction — extraction — M05 / Rigor 01

> Extract the distinct assertions made by the target edition. Preserve the author’s level of commitment and wording; do not strengthen a suggestion into a claim. For each item return the exact locator, a concise statement, claim kind (empirical, formal, philosophical, theological, interpretive, definitional, correspondence, or other), domain, scope qualifiers, and whether it is explicit or implied. Distinguish what the source asserts from what it reports as established. Reuse supplied claim IDs only where the match is exact; otherwise use a local proposal key. Do not judge truth or canon. Also list passages that are argumentative but should remain addressable sections rather than separate atoms.

Acceptance after call: local locators resolve; human confirms completeness and granularity.

### P02 Foundation identification — extraction/criticism, separate calls — M06 / Rigor 02

Extraction prompt:

> Identify candidate definitions, axioms, assumptions, presuppositions, boundary conditions, doctrines, and imported results on which the confirmed claims rely. Cite the claim and source locator for each candidate. Record whether the source presents it as asserted, argued, derived, stipulated, disputed, or unclear. Do not infer that a graph root is a foundation merely because it has no recorded parent.

Criticism prompt:

> Given the confirmed foundation ledger, identify hidden premises, equivocations between supplied term senses, circular support, and foundations whose stated standing is unsupported by the supplied bundle. Do not decide doctrine or canon. State what additional evidence or expert review would resolve each issue.

### P03 Derivation criticism — criticism — M07 / Rigor 03

> Examine each supplied derivation against the exact versioned from/to objects. Reconstruct only steps warranted by the supplied expressions and cited rules. Identify skipped steps, added premises, invalid transformations, dimension/domain problems, conclusions already embedded in premises, and bridges between domains. For every issue cite the step and object version. Keep informal mathematical plausibility, formal compilation, and correspondence to prose as separate judgments. Do not claim a theorem was checked unless a runner receipt is supplied.

### P04 Source-support assessment — validation — M08 / Rigor 04

> For each target sentence and supplied source passage, assess whether the passage supports, partially supports, merely resembles, conflicts with, or is irrelevant to the sentence. The runner’s quote-match result establishes only textual matching. Evaluate context, qualification, and whether the sentence overstates the source. Cite both locators. Identify contrary material only when it is in the bundle; otherwise request a research task.

### P05 Scripture-use extraction — extraction — M09 / Rigor 04

> Locate explicit quotations, citations, clear allusions, epigraphs, and structural uses of supplied Scripture passage records in the target edition. For each use cite the exact target locator and proposed passage ID, distinguish verbatim/partial/paraphrase/allusion, state the local purpose, and identify any interpretation or cross-domain bridge asserted nearby. Do not perform theology review in this task and do not create a new passage record when the supplied exact translation/edition already owns the text.

### P06 Theological interpretation comparison — extraction then criticism — M10 / Rigors 02, 04, 07, 08

Extraction prompt:

> State the target edition’s theological reading plainly. Trace its stated steps from supplied passages and named doctrinal or historical sources. Classify the reading as exegesis, doctrine, systematic inference, devotional, speculative, or mixed, explaining mixed cases. Attribute historical witnesses exactly; a witness is not proof.

Criticism prompt:

> Compare the extracted reading with the supplied rival readings and source passages. Identify interpretive steps, disputed premises, tradition-specific assumptions, and places where a theological conclusion is presented as scientific or formal derivation. Give the strongest supplied rival reading fairly. Do not declare doctrine or canon; state what remains a theological judgment.

### P07 Alternatives reconstruction — criticism — M14 / Rigor 07

> Construct the strongest defensible version of each supplied alternative using its own sources and vocabulary. Compare all accounts on the declared evidence floor, claim budget, assumptions, tuning, explanatory reach, failure conditions, and open problems. Flag missing primary material and any asymmetry of treatment. A “none found” conclusion requires the search/comparison scope to be stated and is never a claim that no alternative exists.

### P08 Failure and boundaries — criticism — M15 / Rigor 08

> For each confirmed material claim, identify its scope limits, kill condition or counterexample where appropriate, strongest objection supported by the bundle, and any unanswered consequence. Separate “no falsifier because this is definitional/theological” from “falsifier not supplied.” Evaluate an existing response only in a separate validation pass against explicit criteria. Preserve open problems and failed attempts.

### P09 Dependency proposal — extraction — M03/M16 / Rigor 09

> Propose typed directed dependencies only where the supplied text gives a locator showing that the target relies on the source. Return from/to record editions, relation type, direction, evidence locator, and why the dependency is load-bearing. Do not infer validity, foundation status, or approval from graph proximity. Mark every new edge proposed. Do not alter existing reviewed edges; flag conflicts for human review.

Traversal, cycle detection, and impact calculation remain local Python tasks.

### P10 Contribution comparison — criticism/validation — M17 / Rigor 10

> Compare the target’s confirmed claims and results with the named supplied prior works. Identify exact overlap, difference, synthesis, method, prediction, result, or explanatory framing, with locators on both sides. Do not use absence from the bundle as evidence of novelty. State the comparison-set limits and downgrade overbroad contribution language. Preserve separate attribution for origin, formulation, drafting, revision, formalization, execution, checking, and critique.

### P11 Story/quotation classification — extraction/validation — M18

> Classify each supplied story by standing (historical, personal, invented, composite, parable retelling) and purpose (illustration or proposed evidence). Extract provenance, teller/speaker, date, format, used-in target, and stated evidentiary limit. For quotations, assess attribution only from supplied source records; the runner supplies exact-string results. Never treat an invented illustration as evidence. Do not prohibit a sourced historical account or testimony from evidentiary use; instead name the provenance, reliability question, and limitation requiring human review.

### P12 Media semantic QA — validation — M19/O06

> Compare the supplied transcript, caption, alt text, diagram, or media summary against the exact source edition and listed claims. Identify omitted qualifiers, new claims, misleading visual encodings, attribution errors, and accessibility failures. Do not report file duration, dimensions, codecs, hashes, or path status; those are runner observations. Cite timestamps/regions and source locators.

### P13 Contradiction proposal — criticism — O04

> Identify pairs of supplied statements that may be contradictory, contrary, scope-dependent, temporally superseded, or merely use different term senses. Quote short located spans and give the logical form of the tension. Do not declare a contradiction from vector similarity or shared keywords. Request missing sense/version records where needed.

## Separate canon-assessment task

Canon assessment is not another general review. It consumes already validated outputs and asks whether one exact edition is eligible for an authorized human ruling.

Candidate prompt:

> Assess the canon eligibility of the exact target edition using only the supplied governing rules, rulings, RIGOR-10 assessments, open findings, source/receipt bindings, attribution record, and responses. Do not redo extraction or invent missing reviews. For each governing criterion return met, unmet, disputed, not applicable, or unknown with evidence references. List blockers, conditions, minority/contrary findings, stale inputs, and reserved decisions. The only permitted recommendation values are `recommend_eligible`, `recommend_eligible_with_conditions`, `not_yet`, `recommend_reject`, or `cannot_assess`. You cannot alter `canon_state`, create a ruling, or imply that confidence or model agreement is authority.

Canon-assessment response extension:

```json
{
  "target": {"record_id": "...", "edition_id": "...", "source_hash": "sha256:..."},
  "criteria": [{"criterion_id": "...", "result": "met | unmet | disputed | not_applicable | unknown", "evidence_refs": [], "reason": "..."}],
  "open_findings": [],
  "stale_inputs": [],
  "conditions": [],
  "recommendation": "recommend_eligible | recommend_eligible_with_conditions | not_yet | recommend_reject | cannot_assess",
  "canon_state_echo": "unassigned or existing ruled state only",
  "ruling_required_from": "David or cited delegated authority"
}
```

A host validator rejects any attempted state change, new ruling, silent ID change, or recommendation that is not bound to the exact target edition/hash.
