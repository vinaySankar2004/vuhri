# Learner model

The learner model is an inspectable evidence system. It is not a hidden personality summary.

## Memory categories

- Identity and privacy boundaries explicitly supplied by the user
- Goals at inquiry, session, space, and long-term levels
- Declared and inferred interaction preferences
- Capability within a defined context and level
- Specific misconceptions and their correction state
- Tentative patterns about conditions that help or hinder learning
- Commitments, open threads, and review suggestions

## Evidence strength

Keep these evidence types distinct:

1. User declaration
2. Recognition
3. Immediate explanation
4. Assisted attempt
5. Independent attempt
6. Transfer to a different problem
7. Delayed retrieval
8. Timed or constrained performance
9. External assessment

An attempt also records available notes, hints, timing, source, and relevant situational context. One poor attempt should not erase stronger evidence.

## Descriptive states

Inferred preferences use `candidate`, `tentative`, `supported`, `confirmed`, `contradicted`, or `deprecated`.

Capability uses `unassessed`, `introduced`, `developing`, `reliable-with-support`, `reliable-independently`, `demonstrated-in-transfer`, or `stale`.

Do not invent numerical mastery precision without a validated model and sufficient structured data.

## Contradictions

Retain supporting evidence and counterevidence. Update the scope or current interpretation without deleting history. A direct user correction changes active behavior immediately.

## Storage pattern

Use three layers:

1. Session evidence records meaningful events and attempts.
2. Atomic learner records distill reusable beliefs. Standing preferences live one per file in `local/preferences/`, each with its evidence.
3. Compact indexes route agents to relevant records. `local/PROFILE.md` indexes the preferences in one line each and is read at every session start.

Archive old sessions when needed, but preserve links from active learner records to their evidence.

## User control

The user can ask what is remembered, request evidence, correct a belief, change its scope, remove reminders, export a profile, or delete a topic and its derived state. Deletion should identify claims that lose their only supporting evidence.

## Write threshold

Write durable memory only when it may improve a future interaction. Quick factual questions normally create none. Collect inferred preferences as candidates and distill them at meaningful checkpoints instead of editing the profile after every message.

