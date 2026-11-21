# 0007. Own frontend with React, TypeScript and Vite; Grafana for history

- Status: Accepted
- Date: 2026-11-19
- Deciders: Carla Rubio Espiñeira

## Context and problem statement

v0.1.0 has no user interface; the only output is container logs. The system
needs a way to see the greenhouse live, understand why the controller acts,
and inspect history. Some interactions (manual override, editing thresholds,
launching scenarios) need custom controls.

## Decision drivers

- A live view tailored to the domain: metrics against their ranges, actuator
  state, and the reasons behind each plan.
- Rich historical charts without building them from scratch.
- Typed integration with the Knowledge API.
- Mainstream, maintainable tooling.

## Considered options

1. Own web app (React, TypeScript, Vite) for the live view and controls, with Grafana panels embedded for history.
2. Grafana only.
3. A Python UI framework (Streamlit or NiceGUI).

## Decision outcome

Chosen option: **own React + TypeScript app built with Vite, embedding Grafana for history**.

- Live data: MQTT over WebSockets (mqtt.js), with a read-only broker user.
- State and configuration: the Knowledge REST API, with TypeScript types
  generated from its OpenAPI schema.
- History: Grafana panels embedded with iframes, plus an "Open in Grafana" link.
- One entry point behind nginx: `/` frontend, `/grafana`, `/api`, `/mqtt`.

Write operations from the browser need an access model, recorded in its own
ADR before the controls are built (phase 5).

### Consequences

- Good: each tool does what it is best at: domain UI in React, time-series exploration in Grafana.
- Good: TypeScript types follow the API automatically.
- Bad: two UIs to keep visually consistent; embedding requires enabling
  anonymous read-only access in Grafana.
- Bad: a JavaScript toolchain in a Python repository.

## Pros and cons of the options

### Grafana only

- Good: no frontend code.
- Bad: no domain-specific live view or controls; explaining the controller's decisions is awkward.

### Streamlit or NiceGUI

- Good: same language as the backend, fast to build.
- Bad: less control over layout and real-time behaviour; less representative of production frontends.

## Links

- ADR-0003 (MQTT and REST), ADR-0005 (storage).
