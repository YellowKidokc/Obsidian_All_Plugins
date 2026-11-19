Yes—**one Writing Improvement set, with ten lenses inside it**, each with its own prompt and tag words.

Your “two unrelated things that connect back to the paper” idea fits **Unexpected Connection**. A dichotomy would be two opposing alternatives; your opening could use either approach.

Here’s a first set you can copy into Obsidian.

### 1. Hook & Opening

**Prompt:**  
> Find the most compelling entry point into this paper. Write three possible openings: a concrete everyday situation, a question worth answering, and a surprising observation. Connect each opening to the paper’s actual argument. Recommend the strongest and explain why. Avoid clickbait and invented anecdotes.

**Tag:** `writing/hook`  
**Tag words:** hook, opening, first line, introduction, curiosity, attention, entry point

### 2. Unexpected Connection

**Prompt:**  
> Find three pairs of seemingly unrelated things that could introduce this paper’s central idea. For each pair, explain the real connection and draft a short opening that brings them together. Identify where the comparison stops working. Do not treat an analogy as evidence.

**Tag:** `writing/connection`  
**Tag words:** unexpected connection, juxtaposition, analogy, parallel, metaphor, surprising link, bridge

### 3. Contrast & Tension

**Prompt:**  
> Identify the strongest genuine tension in this paper: an apparent contradiction, competing explanations, or a gap between expectation and reality. Draft two openings built around that tension. Explain what the paper resolves and what remains open. Do not force a false either-or choice.

**Tag:** `writing/tension`  
**Tag words:** contrast, dichotomy, paradox, contradiction, competing explanations, expectation, tension

### 4. Sound Bites & Memorable Lines

**Prompt:**  
> Extract or develop five short, memorable lines that express this paper’s strongest ideas. Make each understandable outside its original paragraph without overstating the argument. Mark which are original quotations and which are suggested rewrites. Recommend where each belongs.

**Tag:** `writing/soundbite`  
**Tag words:** sound bite, memorable line, quotable, takeaway, key phrase, punch line, concise claim

### 5. Continuous Flow

**Prompt:**  
> Read this as one continuous document. Find abrupt transitions, repeated introductions, disconnected sections, and places where the reader must supply a missing step. Recommend a stronger order and rewrite the necessary transitions. Make each section grow naturally from the previous one while preserving the argument.

**Tag:** `writing/flow`  
**Tag words:** flow, continuity, transition, sequence, coherence, narrative thread, disconnected section

### 6. Compression & Cutting

**Prompt:**  
> Make this shorter and stronger. Identify repetition, filler, unnecessary setup, and sentences doing the same job. Produce a tighter version and report the approximate word reduction. Preserve essential evidence, qualifications, citations, and distinctions. If cutting would weaken the reasoning, explain what should stay.

**Tag:** `writing/compression`  
**Tag words:** compress, shorten, tighten, redundancy, repetition, filler, wordiness, cut

### 7. Technical Level & Accessibility

**Prompt:**  
> Assess how much background knowledge this passage assumes. Identify jargon, unexplained concepts, and reasoning steps a general reader may miss. Rewrite it for an intelligent reader without specialist training, aiming roughly at a ninth-grade reading level. Explain difficult ideas before naming them. Preserve technical distinctions that matter.

**Tag:** `writing/accessibility`  
**Tag words:** technical level, jargon, readability, plain language, simplify, explain, background knowledge

### 8. Voice & Naturalness

**Prompt:**  
> Make this sound like a thoughtful person working through an idea across a table. Use everyday words, concrete examples, and varied sentence lengths. Remove academic stiffness, generic AI phrasing, forced slogans, and excessive caveats. Preserve my conviction and meaning. Do not invent personal experiences.

**Tag:** `writing/voice`  
**Tag words:** voice, natural, conversational, authentic, stiff, academic, tone, rhythm

### 9. Argument & Evidence

**Prompt:**  
> Trace the main claim through its supporting reasons and evidence. Identify unsupported leaps, hidden assumptions, ambiguous terms, and places where analogy is doing the work of proof. Distinguish empirical findings, deductions, interpretations, and speculation. Suggest precise repairs and address the strongest reasonable objection.

**Tag:** `writing/argument`  
**Tag words:** claim, evidence, assumption, inference, objection, reasoning, support, overstatement

### 10. Ending & Payoff

**Prompt:**  
> Does the ending deliver on the opening’s promise? Identify the strongest earned conclusion, resolve the questions the paper can answer, and preserve those it cannot. Write two possible endings: one that returns to the opening and one that leaves the reader with a meaningful implication or next question. Avoid introducing an unsupported final claim.

**Tag:** `writing/ending`  
**Tag words:** conclusion, ending, payoff, resolution, implication, closing line, callback

### One master prompt to run the whole set

> Review the supplied writing through these ten lenses: Hook, Unexpected Connection, Contrast, Sound Bites, Flow, Compression, Accessibility, Voice, Argument, and Ending.
>
> First identify the central claim and intended reader. Then assess each lens, quoting the specific passage involved and recommending a concrete improvement. Mark lenses that need no change. Rank the three improvements that would help most.
>
> Preserve the author’s voice, evidence, citations, and degree of certainty. Do not invent facts, quotations, experiences, or sources. Do not rewrite the whole document unless requested.
>
> Finish with the applicable `#writing/...` tags.

**For the classification settings in your screenshot**, I’d use this extra instruction:

> Classify each passage by the writing work it most needs or could best support. Assign at most two categories. Use tag words as clues, not automatic matches. A passage discussing an “opening” does not necessarily need a stronger hook. Leave a passage unclassified when none of the categories fits. Classification identifies the work; the associated editing prompt performs it.

The descriptions above are ready to adapt into those fields. I’d need a sample exported taxonomy JSON to make an import file that matches your plugin’s exact format.


Yes—keep Claim & Evidence and Objections & Alternatives as your two argument checks. The other categories can focus on what makes a paper more useful, understandable, and worth finishing.

I’d add these six to the writing set:
11. Purpose & Stakes
Prompt:
Identify the question this paper answers and why the answer matters. Does the reader understand what is at stake early enough? Suggest a short passage that makes the significance concrete without exaggerating its importance.

Tag: writing/stakes
Tag words: purpose, significance, relevance, stakes, consequence, why it matters
12. Definitions & Consistency
Prompt:
Find important terms that are undefined, introduced too late, or used with different meanings. Explain each term plainly at its first necessary appearance. Flag places where the argument shifts meanings, especially between everyday, scientific, philosophical, and theological usage.

Tag: writing/definitions
Tag words: definition, terminology, ambiguity, consistency, meaning, distinction
13. Examples & Grounding
Prompt:
Identify abstract passages that would benefit from a concrete example, brief scenario, or comparison. Suggest examples that clarify the actual idea. Explain what each example demonstrates and where it stops being a useful comparison. Do not invent research findings or personal experiences.

Tag: writing/examples
Tag words: example, illustration, concrete, scenario, analogy, grounding
14. Reader Questions & Missing Steps
Prompt:
Read this as an intelligent person encountering the subject for the first time. At each major step, ask: “What would I need explained before accepting or understanding the next sentence?” Identify missing connections, unanswered questions, and assumptions about the reader’s knowledge. Suggest the smallest useful addition for each gap.

Tag: writing/reader-gaps
Tag words: missing step, reader question, explanation, context, confusion, prerequisite
15. Pacing & Emphasis
Prompt:
Assess where the paper moves too slowly, rushes an important idea, or gives minor points too much space. Identify where the reader needs a pause, an example, a shorter explanation, or a clearer statement of the central insight. Recommend changes that make the strongest ideas stand out without turning every paragraph into a slogan.

Tag: writing/pacing
Tag words: pacing, emphasis, balance, density, momentum, breathing room
16. Contribution & Originality
Prompt:
State what this paper contributes: a new argument, a useful synthesis, a clearer explanation, a proposed mechanism, or a new question. Distinguish the contribution from background material. Suggest wording that makes the contribution clear without claiming originality or priority that has not been established.

Tag: writing/contribution
Tag words: contribution, originality, novelty, synthesis, insight, advancement

The strongest additions for your papers would be Definitions, Reader Questions, and Contribution. They help answer three things a reader needs to know: What do you mean? How did you get there? What does this add?


11. Purpose & Stakes
Prompt:
Identify the question this paper answers and why the answer matters. Does the reader understand what is at stake early enough? Suggest a short passage that makes the significance concrete without exaggerating its importance.

Tag: writing/stakes
Tag words: purpose, significance, relevance, stakes, consequence, why it matters
12. Definitions & Consistency
Prompt:
Find important terms that are undefined, introduced too late, or used with different meanings. Explain each term plainly at its first necessary appearance. Flag places where the argument shifts meanings, especially between everyday, scientific, philosophical, and theological usage.

Tag: writing/definitions
Tag words: definition, terminology, ambiguity, consistency, meaning, distinction
13. Examples & Grounding
Prompt:
Identify abstract passages that would benefit from a concrete example, brief scenario, or comparison. Suggest examples that clarify the actual idea. Explain what each example demonstrates and where it stops being a useful comparison. Do not invent research findings or personal experiences.

Tag: writing/examples
Tag words: example, illustration, concrete, scenario, analogy, grounding
14. Reader Questions & Missing Steps
Prompt:
Read this as an intelligent person encountering the subject for the first time. At each major step, ask: “What would I need explained before accepting or understanding the next sentence?” Identify missing connections, unanswered questions, and assumptions about the reader’s knowledge. Suggest the smallest useful addition for each gap.

Tag: writing/reader-gaps
Tag words: missing step, reader question, explanation, context, confusion, prerequisite
15. Pacing & Emphasis
Prompt:
Assess where the paper moves too slowly, rushes an important idea, or gives minor points too much space. Identify where the reader needs a pause, an example, a shorter explanation, or a clearer statement of the central insight. Recommend changes that make the strongest ideas stand out without turning every paragraph into a slogan.

Tag: writing/pacing
Tag words: pacing, emphasis, balance, density, momentum, breathing room
16. Contribution & Originality
Prompt:
State what this paper contributes: a new argument, a useful synthesis, a clearer explanation, a proposed mechanism, or a new question. Distinguish the contribution from background material. Suggest wording that makes the contribution clear without claiming originality or priority that has not been established.

Tag: writing/contribution
Tag words: contribution, originality, novelty, synthesis, insight, advancemen


1. Narrative Architecture
Add to Structure & Flow
Propose three genuinely different ways to organize this paper: one beginning with a concrete situation, one following the central reasoning, and one examining a disagreement. Map each opening, body beat, and closing to specific material already in the paper. Explain what each arrangement helps the reader understand. Preserve the thesis; flag a narrower alternative rather than silently changing it.

Tag: writing/architecture
Tag words: narrative spine, structure, outline, sequence, scene, debate, alternative opening
2. Honest Trust Moves
Add to Argument & Reader Questions
Identify where the paper could earn trust through a fair concession, an acknowledged uncertainty, or a consistent standard applied to the author’s own position. Ask whether the reasoning would still seem fair if the opposing sides were reversed. Recommend only concessions the source material supports; do not manufacture balance or weaken a sound conclusion.

Tag: writing/trust
Tag words: concession, fairness, uncertainty, consistency, swap test, qualification, reader resistance
3. Source-to-Story Mapping
Add to Purpose & Focus
For every proposed story beat, example, or memorable line, identify the exact claim, passage, or section it serves. Flag attractive material that does not advance the paper. Distinguish what comes from the source from what you are proposing as a new illustration. Never invent quotations, events, evidence, or move-library IDs.

Tag: writing/source-mapping
Tag words: source alignment, relevance, canonical point, supporting passage, digression, narrative purpose
4. The Carry-Away Question
Add to Ending & Payoff
Develop three short questions the reader could carry into another conversation or situation after finishing this paper. Each should express the paper’s central concern without requiring specialist vocabulary or assuming agreement with the conclusion. Recommend the strongest and show how the ending could earn it.

Tag: writing/carry-question
Tag words: portable question, reflection, takeaway, closing question, application, participation

Then add this shared instruction above the whole writing set:
Treat the paper as one connected argument. Preserve its thesis, voice, evidence, and degree of certainty. Recommend structural changes before rewriting sentences when structure is the larger problem. Offer genuinely different alternatives, map recommendations to source passages, and explain their purpose. Use named story moves or move IDs only when their definitions have been supplied. The writer chooses the architecture before you produce a full rewrite.

That gives the existing prompts a stronger method without requiring a separate category for every technique.


d organize the highlights into six groups:
Highlight group	Words and phrases
Authority declarations	canonical, authoritative, controlling, official, final, approved, ratified, adopted
Supersession & relationships	supersedes, superseded by, replaces, replaced by, successor, predecessor
Version & revision	version, v1/v2/v3, revised, revision, amended, prior version, previous version
Historical & withdrawn	deprecated, obsolete, retired, withdrawn, archived, historical, legacy
Provisional status	draft, proposed, candidate, working model
Copies & provenance	reference, source copy, duplicate, rendered copy, derivative, conflict copy


Use current as a contextual clue: “current theory” and “electrical current” should not receive the same interpretation. Match longer phrases such as “superseded by” before matching individual words.

Paste-ready assessment prompt:
Assess this document’s canon and lineage status using the supplied comparison documents and provenance records. Keep document function separate from authority: a paper remains a paper, while its claims, proofs, evidence, dependencies, and canon status receive separately linked classifications.

Identify authority declarations, supersession relationships, version sequences, dates, and copy relationships. Quote the relevant evidence and identify its source document.

Rank evidence in this order:
1. Explicit canonical or supersession declaration
2. Version family and sequence
3. Internal document date
4. Path or filename date
5. Hash-linked copies and derivatives
6. Filesystem timestamp as a weak fallback
Do not treat a document’s self-description as “canonical,” its folder placement, or its newer date alone as proof of current authority. Check whether a controlling successor supersedes it. A newer version number establishes sequence, not necessarily adoption.

Return:
- document_function
- status: CURRENT, PRIOR, RETIRED, SYSTEM, SOURCE, or UNRESOLVED
- content_signal
- lineage_signal
- destination
- era
- confidence
- evidence
- decision_concordance: PASS or HOLD
Assign PASS only when content and lineage signals agree and the evidence is adequate. Disagreement or insufficient evidence requires HOLD. If status cannot be established, assign UNRESOLVED and route to REVIEW. State which missing evidence would resolve the uncertainty.

Use CURRENT_MASTER_EQUATION and PRIOR_MASTER_EQUATION only for documents in the master-equation family. Use SYSTEM_SUPPORT for system-support material and SOURCE_REFERENCE for source-reference material. Do not invent a destination for RETIRED documents; use REVIEW until its routing rule is defined.

Tags for this set:

#canon/authority · #canon/lineage · #canon/supersession · #canon/version · #canon/provenance · #canon/review

And yes, we can use these words more consistently in your own notes. A short declaration block would make later assessments much easier: