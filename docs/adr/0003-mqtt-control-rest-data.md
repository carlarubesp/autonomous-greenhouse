# 0003. MQTT for control, REST for state

- Status: Accepted (documented retroactively; decided for v0.1.0)
- Date: 2026-11-19
- Deciders: Carla Rubio Espiñeira

## Context and problem statement

The MAPE-K services need two kinds of communication: events that trigger the
next stage (a new reading, a diagnosis, a plan, an actuator command) and
reads and writes of shared state (recent readings, actuator state,
thresholds). The managed resource, whether simulator or hardware, must be
reachable through a protocol that small devices support.

## Decision drivers

- Decoupling: a stage should not need to know who consumes its output.
- Support on constrained devices (Raspberry Pi, microcontrollers).
- Simple, synchronous access to shared state.

## Considered options

1. MQTT for events (control plane) and an HTTP REST API for shared state (data plane).
2. MQTT for everything, with retained messages as state.
3. HTTP for everything (services call each other directly).

## Decision outcome

Chosen option: **MQTT for control, REST for state**. MQTT is the standard
publish/subscribe protocol in IoT and decouples producers from consumers.
The Knowledge service exposes state over REST (FastAPI), which is simpler for
request/response access and self-documents with OpenAPI.

### Consequences

- Good: the managed resource only talks MQTT, so hardware can replace the
  simulator at the edge (see ADR-0008).
- Good: new consumers (Telegraf, the frontend) subscribe without changing producers.
- Bad: two protocols to secure, monitor and test.
- Bad: state can be read over REST while related events are still in flight;
  ordering must be handled explicitly (see ADR-0004).

## Pros and cons of the options

### MQTT only

- Good: one protocol.
- Bad: request/response over MQTT is awkward; retained messages are a poor
  substitute for queries over recent history.

### HTTP only

- Good: one protocol, easy to debug.
- Bad: services call each other directly, so they are coupled; devices must
  poll or run an HTTP server.

## Links

- ADR-0004, ADR-0008.
