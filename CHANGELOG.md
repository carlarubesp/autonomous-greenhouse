# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Architecture Decision Records in `docs/adr/` (ADR-0001 to ADR-0008).
- Contribution guide, pull request template and issue templates.
- This changelog.

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
