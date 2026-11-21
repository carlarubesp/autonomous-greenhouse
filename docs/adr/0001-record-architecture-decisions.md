# 0001. Record architecture decisions

- Status: Accepted
- Date: 2026-11-19
- Deciders: Carla Rubio Espiñeira

## Context and problem statement

Version 0.1.0 was built as a course project. Its design rationale lives in
`docs/design.typ`, which describes the system as it was meant to be but does
not record which alternatives were considered or why they were rejected.

The redesign towards v1.0.0 introduces several decisions with long-term
consequences (storage, ingestion, frontend, hardware support). Without a
record, the reasoning behind them is lost and later changes risk undoing a
decision without knowing why it was made.

## Decision drivers

- Make the reasoning behind the architecture reviewable by anyone reading the repository.
- Keep each decision small, dated and immutable, so its history can be followed.
- Low overhead: writing a record must take minutes, not hours.

## Considered options

1. Architecture Decision Records (ADRs) in the repository, MADR format.
2. Extend the design document (`docs/design.typ`) with a decisions chapter.
3. Keep decisions in pull request descriptions only.

## Decision outcome

Chosen option: **ADRs in `docs/adr/`, MADR format**, because each decision
becomes a small versioned file that travels with the code, is reviewed in the
same pull request as the change it justifies, and keeps its history when
superseded.

### Consequences

- Good: every significant change can point to the record that justifies it.
- Good: superseded records stay, so the evolution of the design is visible.
- Bad: records must be kept in sync; a pull request that contradicts an
  accepted ADR must also add a superseding one.

## Pros and cons of the options

### Design document chapter

- Good: one place to read.
- Bad: a single document is rewritten over time and loses the history of each decision.

### Pull request descriptions only

- Good: no extra files.
- Bad: hard to find later and not available offline with the code.

## Links

- [MADR](https://adr.github.io/madr/)
- Michael Nygard, "Documenting Architecture Decisions" (2011)
