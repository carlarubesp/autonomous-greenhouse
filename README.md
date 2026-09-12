# Autonomous Greenhouse

An autonomous greenhouse controller built on the MAPE-K loop. It monitors
six environmental metrics, detects critical states and trends, and uses
actuators to keep the plants alive.

## Overview

The system simulates a greenhouse environment:
1. The **Monitor** reads the sensors from the simulator and forwards the
   information to the knowledge base.
2. The **Analyzer** evaluates the current state every minute. If any
   metric reaches an alarm threshold, it acts immediately. Otherwise,
   it performs a full evaluation every 20 minutes.
3. The **Planner** *(in progress)* decides which actuators to turn on or
   off, applying hysteresis to avoid thrashing.
4. The **Executor** *(in progress)* applies the plan to the actuators via
   MQTT.
5. The **Knowledge** base holds the shared state: sensor readings,
   actuator state, metric thresholds and aggregated logs.

## Architecture

The MAPE-K loop is implemented as five independent services that
communicate in two ways:
- **MQTT**: the control plane. All MAPE-K components subscribe to
  topics under the `greenhouse/...` name.
- **HTTP REST**: the data plane. A FastAPI service exposes the
  knowledge base through endpoints such as `/short-term`, `/actuators`
  and `/logs`, used for reads and writes.

## Tech stack

- **Python 3**: language used across all components
- **Eclipse Mosquitto**: MQTT broker for the control plane
- **FastAPI + Uvicorn**: REST API for the knowledge base
- **Pydantic**: data validation
- **Docker + Docker Compose**: containerization and orchestration

## How to run

### Option A: Docker
`docker compose up` will start the full pipeline once all components
are containerized. This is the recommended way to run the project
regardless of your operating system.

### Option B: Local
1. Install Mosquitto and start it.
2. Create a virtual environment and install dependencies.
3. Start each component in its own terminal, in this order:
   ```bash
   # Terminal 1 — knowledge base
   cd knowledge && uvicorn knowledge:app --host 0.0.0.0 --port 5000
    
   # Terminal 2 — monitor
   cd monitor && python monitor.py
    
   # Terminal 3 — analyzer
   cd analyzer && python analyzer.py
    
   # Terminal 4 — simulator
   cd managed-resources && python greenhouse.py
   ```

## Components
| Component | Role | Communication |
|---|---|---|
| `managed-resources/` | Simulates sensors and actuators | MQTT (publish), MQTT (subscribe) |
| `monitor/` | Ingests sensor data into the knowledge base | MQTT (subscribe), HTTP (POST) |
| `analyzer/` | Detects alarms, symptoms and trends | MQTT (subscribe/publish), HTTP (GET) |
| `planner/` | Builds actuator plans *(in progress)* | MQTT (subscribe/publish), HTTP (GET) |
| `executor/` | Applies plans to actuators *(in progress)* | MQTT (subscribe/publish), HTTP (POST/GET) |
| `knowledge/` | FastAPI service holding memory and state | HTTP (REST) |

## Project structure

    autonomous-greenhouse/
    ├── analyzer/              # MAPE-K Analyzer
    ├── docs/                  # Design document (Typst source + PDF)
    ├── executor/              # MAPE-K Executor (in progress)
    ├── knowledge/             # FastAPI knowledge base
    ├── managed-resources/     # Greenhouse simulator
    ├── monitor/               # MAPE-K Monitor
    ├── planner/               # MAPE-K Planner (in progress)
    ├── greenhouse.conf        # Shared configuration
    ├── mosquitto.conf         # Mosquitto configuration
    └── thresholds.json        # Metric thresholds (ideal / secure / alarm)

<!-- TODO: Design decisions
- MAPE-K justification
- MQTT for control, HTTP for data
- Hysteresis to avoid thrashing
- Bounded short-term memory (20 readings)
-->

<!-- TODO: Future work
- [ ] Planner with hysteresis
- [ ] Executor
- [ ] Docker Compose
- [ ] Long-term memory (9 logs)
- [ ] Grafana
- [ ] Unit tests
-->

<!-- TODO: License — MIT, once LICENSE file is added -->