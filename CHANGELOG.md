# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Architecture Decision Records in `docs/adr/` (ADR-0001 to ADR-0008).
- Contribution guide, pull request template and issue templates.
- This changelog.
- uv workspace: a `pyproject.toml` per service and a single `uv.lock` with
  pinned versions of every dependency.
- Development tooling: ruff (lint and format), mypy (types) and pre-commit
  hooks that run them on every commit.
- Shared `greenhouse-common` package with settings, topics, thresholds, the
  MQTT client factory, a Knowledge REST client and logging set-up, with unit
  tests (pytest).
- `LOG_LEVEL` environment variable (default `INFO`).

### Changed

- Docker images install dependencies with `uv sync --frozen`, so builds are
  reproducible. The build context is now the repository root.
- Local run instructions use `uv sync` and `uv run`.
- MQTT clients use the paho-mqtt callback API version 2 (the deprecated
  version 1 warning is gone from the logs).
- Every service uses the shared package instead of its own copy of the
  configuration loading, and logs with `logging` instead of `print`. Service
  logs now appear in `docker compose logs` (they were stuck in the stdout
  buffer); per-reading messages are at debug level.
- The `[topics]` section of `greenhouse.conf` lists the topics actually used.

### Removed

- Per-service `requirements.txt` and `.dockerignore` files, replaced by the
  workspace manifests and a root `.dockerignore`.
- Unused `requests` dependency of the simulator.

## [0.1.0] - 2026-09-29

Course project for *Autonomous Systems* (Università degli Studi dell'Aquila).

### Added

- Greenhouse simulator with six metrics and eight actuators.
- MAPE-K services: Monitor, Analyzer, Planner, Executor and Knowledge.
- MQTT for control and a REST API (FastAPI) for shared state.
- Hysteresis-based planning with a priority hierarchy.
- Docker Compose setup for the whole stack.
- Design considerations document (`docs/design.typ`).

[Unreleased]: https://github.com/carlarubesp/autonomous-greenhouse/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/carlarubesp/autonomous-greenhouse/releases/tag/v0.1.0
