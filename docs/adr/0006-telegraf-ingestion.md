# 0006. Telegraf for data ingestion

- Status: Accepted
- Date: 2026-11-19
- Deciders: Carla Rubio Espiñeira

## Context and problem statement

The messages that flow over MQTT (readings, actuator state, diagnoses, plans
and events) must reach TimescaleDB (ADR-0005). Something has to subscribe to
the broker, parse the JSON payloads and write them in batches, buffering if
the database is temporarily unavailable.

## Decision drivers

- No changes to the MAPE-K services: storage must be a passive observer.
- Reliability: batching and buffering when the database is down.
- Widely used, documented tooling.
- Little custom code to maintain.

## Considered options

1. Telegraf (`inputs.mqtt_consumer` with the `json_v2` parser, `outputs.postgresql`).
2. A custom Python ingestion service.
3. The Knowledge service writes to the database directly (as the course's reference project does with MongoDB).

## Decision outcome

Chosen option: **Telegraf**, configured declaratively in the repository.
It is the industry-standard agent for moving IoT and metrics data, it already
implements batching and buffering, and it keeps ingestion out of the control services.

Configuration rules:

- One `inputs.mqtt_consumer` per JSON topic (readings, actuator state,
  diagnoses, plans, events). Not `greenhouse/#`: some topics carry plain-text
  payloads (`start`, `HEATER_ON`) that the JSON parser would reject.
- QoS 1 with a persistent session, so messages published while Telegraf
  restarts are not lost.
- The time column is `ts` from the payload (ADR-0004), not the reception time.

### Consequences

- Good: zero ingestion code in the services; adding a stream is a configuration change.
- Good: buffering and retries come built in.
- Bad: one more container and a configuration language to learn.
- Bad: payload changes must be mirrored in the Telegraf parser configuration;
  this is checked by an end-to-end test once the stack has one.

## Pros and cons of the options

### Custom Python service

- Good: full control, same language as the rest, easy to unit test.
- Bad: reimplements batching, buffering and reconnection that Telegraf already provides.

### Knowledge writes directly

- Good: no extra component.
- Bad: couples the source of truth of the control loop to the database,
  against the separation rule of ADR-0005.

## Links

- ADR-0005, ADR-0004.
