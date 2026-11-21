# 0004. Time base: monotonic sequence and UTC timestamps

- Status: Accepted
- Date: 2026-11-19
- Deciders: Carla Rubio Espiñeira

## Context and problem statement

In v0.1.0 every reading carries `clock`, a simulated minute from 0 to 1439
that wraps to 0 at midnight and drives the day/night profile. It is not
enough for three reasons:

- Ordering: because `clock` wraps, it cannot tell whether a message is newer
  than another across midnight.
- Storage: a time-series database needs an absolute timestamp.
- Real time: the simulator runs faster than real time (one simulated minute
  every 0.5 s), and real hardware runs in real time, so durations such as
  cooldowns are ambiguous.

## Decision drivers

- Correct ordering of readings, diagnoses and plans.
- A single time column for storage and dashboards.
- Same control logic for simulation and hardware.

## Considered options

1. Keep `clock` and add a monotonic sequence number `seq` plus a UTC timestamp `ts`.
2. Keep `clock` and add a day counter.
3. Replace `clock` with real time everywhere.

## Decision outcome

Chosen option: **`clock` + `seq` + `ts`**.

- `seq`: integer set by the producer of each reading, starting at 0 and
  never wrapping. Diagnoses, plans and actuator state carry the `seq` of the
  reading they come from, and are used to discard out-of-order messages.
- `ts`: UTC timestamp (ISO 8601) set by whoever produces the message. It is
  the time column of the database.
- `clock`: kept as the simulated time of day; it selects the day/night profile.

Control durations (cooldowns, minimum on-time, windows) are expressed in
ticks of the data source. With the simulator a tick is one simulated minute;
with hardware it is one sampling period. The tick length is configuration.

### Consequences

- Good: ordering works across midnight and restarts of consumers.
- Good: simulation speed can change without changing the control logic.
- Bad: one more field in every message; producers must set it correctly.
- Bad: `seq` restarts if the producer restarts; consumers must accept a reset
  (a lower `seq` together with a new `run_id`, introduced in phase 4).

## Pros and cons of the options

### Day counter

- Good: minimal change.
- Bad: two fields to compare; still no absolute time for storage.

### Real time everywhere

- Good: one notion of time.
- Bad: simulations can no longer run faster than real time, which makes
  experiments slow.

## Links

- ADR-0005 (storage), ADR-0008 (hardware).
