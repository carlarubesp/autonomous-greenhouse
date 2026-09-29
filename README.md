# Autonomous Greenhouse

An autonomous greenhouse controller built on the MAPE-K loop. It monitors
six environmental metrics, detects critical states and trends, and uses
actuators to keep the plants alive.

## Overview

The system simulates a greenhouse environment:
1. The **Monitor** reads sensor data from the simulator and forwards it
   to the knowledge base.
2. The **Analyzer** evaluates the current state every minute. If any
   metric reaches an alarm threshold, it acts immediately. Otherwise,
   it performs a full evaluation every 20 simulated minutes.
3. The **Planner** decides which actuators to turn on or off, applying
   hysteresis to avoid thrashing and a priority hierarchy to resolve
   conflicts between metrics.
4. The **Executor** applies the plan to the actuators via MQTT and
   updates the shared actuator state in the knowledge base.
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

### Option A — Docker (recommended)

```bash
docker compose up --build
```

This starts the broker, the knowledge base, and all five MAPE-K
components on a single bridge network. Configuration files
(`greenhouse.conf` and `thresholds.json`) are mounted as volumes, so
they can be edited without rebuilding the images.

To stop everything:

```bash
docker compose down
```

### Option B — Local

1. Install Mosquitto and start it:

   ```bash
   sudo apt install mosquitto mosquitto-clients
   sudo systemctl start mosquitto
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Start each component in its own terminal, in this order:

   ```bash
   # Terminal 1 — knowledge base
   cd knowledge && uvicorn knowledge:app --host 0.0.0.0 --port 5000

   # Terminal 2 — monitor
   cd monitor && python monitor.py

   # Terminal 3 — analyzer
   cd analyzer && python analyzer.py

   # Terminal 4 — planner
   cd planner && python planner.py

   # Terminal 5 — executor
   cd executor && python executor.py

   # Terminal 6 — simulator
   cd managed-resources && python greenhouse.py
   ```

## Components
| Component | Role | Communication |
|---|---|---|
| `managed-resources/` | Simulates sensors and actuators | MQTT (publish), MQTT (subscribe) |
| `monitor/` | Ingests sensor data into the knowledge base | MQTT (subscribe), HTTP (POST) |
| `analyzer/` | Detects alarms, symptoms and trends | MQTT (subscribe/publish), HTTP (GET) |
| `planner/` | Builds actuator plans with hysteresis and priority | MQTT (subscribe/publish), HTTP (GET) |
| `executor/` | Applies plans to actuators via MQTT | MQTT (subscribe/publish), HTTP (POST/GET) |
| `knowledge/` | FastAPI service holding memory and state | HTTP (REST) |

## Project structure

    autonomous-greenhouse/
    ├── analyzer/              # MAPE-K Analyzer
    ├── docs/                  # Design document (Typst source + PDF)
    ├── executor/              # MAPE-K Executor
    ├── knowledge/             # FastAPI knowledge base
    ├── managed-resources/     # Greenhouse simulator
    ├── monitor/               # MAPE-K Monitor
    ├── planner/               # MAPE-K Planner
    ├── docker-compose.yml     # Orchestrates the full pipeline
    ├── greenhouse.conf        # Shared configuration
    ├── mosquitto.conf         # Mosquitto configuration
    ├── requirements.txt       # Python dependencies
    └── thresholds.json        # Metric thresholds (ideal / secure / alarm)

## Design decisions

- **MAPE-K over a single PID loop** — the system requires a clean
  separation between reasoning (analyzer, planner) and actuation
  (executor), so each layer can evolve independently.
- **MQTT for control, HTTP for data** — MQTT is a natural fit for
  asynchronous, decoupled events; HTTP is simpler for synchronous reads
  and writes of shared state.
- **Hysteresis in the planner** — the thresholds for turning an
  actuator on and off are different, to avoid thrashing when a metric
  sits near a boundary.
- **Priority hierarchy** — when two metrics want the same actuator in
  opposite directions, the one with higher priority wins. Temperature
  and pH come first (they can kill the plant in minutes), then soil
  moisture and relative humidity, then CO₂ and conductivity.
- **Bounded short-term memory** — the analyzer's window is capped at 20
  readings (one simulated 20-minute window), keeping memory and query
  cost bounded regardless of runtime.

## Future work

- [ ] Long-term memory aggregation (9 logs ≈ 3 h) and pattern detection
- [ ] Unit tests for `check_sensors`, `check_trends` and `build_plan`
- [ ] Prometheus + Grafana dashboards
- [ ] Replace the simulator with real sensor hardware

## License

MIT — see [LICENSE](LICENSE).