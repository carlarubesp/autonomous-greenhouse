# 0005. TimescaleDB for traceability, not for control

- Status: Accepted
- Date: 2026-11-19
- Deciders: Carla Rubio Espiñeira

## Context and problem statement

In v0.1.0 all state lives in the memory of the Knowledge service and is lost
on restart. There is no history of readings, decisions or actions, so it is
impossible to explain afterwards what the system did, compare runs, or build
dashboards.

The design also describes a long-term memory: a log of important events, the
corrective action taken and its result.

## Decision drivers

- Transparency: see what happened and why, after the fact.
- Store both time series (readings) and structured events (alarms, plans, actions).
- First-class support in Grafana.
- Runs on a Raspberry Pi (arm64).
- The control loop must keep working if the database is down.

## Considered options

1. TimescaleDB (PostgreSQL extension for time series).
2. InfluxDB.
3. MongoDB (as in the reference project of the course).

## Decision outcome

Chosen option: **TimescaleDB, used only for history and traceability**.

It is PostgreSQL, so time series and relational data (events, plans, runs)
live in one database queried with SQL. Hypertables, compression, retention
and continuous aggregates cover the time-series needs, and Grafana supports
it natively.

**Separation rule:** the Knowledge service remains the single source of truth
for the control loop. No MAPE-K service reads from TimescaleDB to make a
decision. If the database is unavailable, the greenhouse keeps being
controlled and only history is lost.

### Consequences

- Good: one query language (SQL) for readings and events; joins between them are possible.
- Good: the control loop has no new runtime dependency.
- Bad: PostgreSQL uses more resources than a dedicated time-series engine;
  on a Raspberry Pi the database should live on an SSD, not the SD card.
- Bad: features that would need history in the loop (e.g. pattern detection)
  must be designed so they degrade gracefully, or stay outside the loop.

## Pros and cons of the options

### InfluxDB

- Good: purpose-built for metrics; the classic Telegraf, InfluxDB and Grafana stack.
- Bad: structured events and relations fit poorly; the product line was in
  transition between major versions (Flux in v2, SQL in v3) at the time of the decision.

### MongoDB

- Good: flexible JSON documents.
- Bad: time-series and aggregation support are weaker for this use, and Grafana support is not native.

## Links

- ADR-0006 (ingestion), ADR-0004 (time column `ts`).
