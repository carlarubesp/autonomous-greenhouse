# 0002. MAPE-K loop as the control architecture

- Status: Accepted (documented retroactively; decided for v0.1.0)
- Date: 2026-11-19
- Deciders: Carla Rubio Espiñeira

## Context and problem statement

The greenhouse must keep six metrics (temperature, relative humidity, soil
humidity, CO2, pH and conductivity) inside safe ranges using eight binary
actuators. Several actuators affect more than one metric, and some goals
conflict: plant survival comes first, energy saving second.

The controller needs an architecture that separates sensing, reasoning and
acting, so that each part can be changed, tested and replaced on its own
(for example, swapping the simulator for real hardware).

## Decision drivers

- Plant safety: alarms must be handled before anything else.
- Separation of concerns between reasoning (analysis, planning) and actuation.
- Each part replaceable and testable in isolation.
- Explainability: it must be possible to say why the system acted.

## Considered options

1. MAPE-K loop (Monitor, Analyze, Plan, Execute over shared Knowledge), one service per stage.
2. One PID (or on/off) controller per metric.
3. A single monolithic control service.

## Decision outcome

Chosen option: **MAPE-K loop with one service per stage**, because it
separates detection (alarms, symptoms, trends) from decision (plans with
priorities and hysteresis) and from actuation, and gives a natural place to
record why each action was taken (the diagnosis and the plan's reasons).

### Consequences

- Good: the analyzer and the planner can evolve independently; the managed
  resource (simulator or hardware) can be swapped without touching them.
- Good: each stage produces an inspectable message (diagnosis, plan), which
  the dashboards and the frontend can show.
- Bad: more moving parts than a single controller: six services, a broker and
  the latency of a message chain on every reading.
- Bad: the stages must agree on message formats; this needs shared models and
  tests (planned in phase 0).

## Pros and cons of the options

### One PID or on/off controller per metric

- Good: simple, well understood, fast.
- Bad: independent loops fight over shared actuators (the fan affects
  temperature, CO2 and humidity); there is no place to resolve conflicts or
  apply a priority hierarchy.

### Single monolithic service

- Good: no network between stages, easy to debug.
- Bad: reasoning and actuation are coupled; replacing the simulator or
  testing the planner alone becomes harder.

## Links

- IBM, "An architectural blueprint for autonomic computing" (2006).
- `docs/design.typ`: design considerations per stage.
