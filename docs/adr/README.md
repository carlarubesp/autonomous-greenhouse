# Architecture Decision Records

This folder records the significant architectural decisions of the project:
what was decided, why, and which alternatives were rejected.

The format follows [MADR](https://adr.github.io/madr/). Start a new record by
copying [`template.md`](template.md) to `NNNN-short-title.md` with the next
free number.

## Status values

- **Proposed**: under discussion, not yet applied.
- **Accepted**: decided; the code follows it (or will, in the phase it belongs to).
- **Superseded by ADR-NNNN**: replaced by a later decision. Old records are
  never deleted or rewritten; a new record supersedes them.
- **Deprecated**: no longer relevant, with no replacement.

## Index

| ADR | Title | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-mape-k-architecture.md) | MAPE-K loop as the control architecture | Accepted |
| [0003](0003-mqtt-control-rest-data.md) | MQTT for control, REST for state | Accepted |
| [0004](0004-time-base.md) | Time base: monotonic sequence and UTC timestamps | Accepted |
| [0005](0005-timescaledb-for-traceability.md) | TimescaleDB for traceability, not for control | Accepted |
| [0006](0006-telegraf-ingestion.md) | Telegraf for data ingestion | Accepted |
| [0007](0007-frontend-react-vite-grafana.md) | Own frontend with React, TypeScript and Vite; Grafana for history | Accepted |
| [0008](0008-hardware-abstraction.md) | Hardware gateway replaces the simulator at the edge | Accepted |
