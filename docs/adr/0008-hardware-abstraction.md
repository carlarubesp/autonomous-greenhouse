# 0008. Hardware gateway replaces the simulator at the edge

- Status: Accepted
- Date: 2026-11-19
- Deciders: Carla Rubio Espiñeira

## Context and problem statement

The project runs against a simulator, but it should also be usable with real
sensors and actuators on a Raspberry Pi. The hardware will not be built as
part of this project, so the hardware path must be designed and tested
without physical devices.

## Decision drivers

- No changes to the MAPE-K services when switching between simulation and hardware.
- Physical safety: a software failure must not leave a pump or heater running.
- Testable without hardware.

## Considered options

1. A hardware gateway service that speaks the same MQTT contract as the simulator.
2. Hardware access inside the monitor and executor services.
3. A separate code path for hardware in each service.

## Decision outcome

Chosen option: **a `hw-gateway` service that replaces the simulator at the
edge**. Sensors and actuators are only reached through MQTT
(`greenhouse/sensors/status` and `greenhouse/actuators/commands`), so the
gateway publishes readings and obeys commands with the same contract.

The switch is not fully transparent. The gateway also requires:

- Real-time base: ticks are sampling periods and `is_day` comes from the
  system clock or a light sensor (ADR-0004).
- Pulse commands for dosing pumps ("dose for N seconds", then wait for mixing),
  because continuous on/off would overdose.
- Safety enforced in the gateway, not only in the planner: maximum on-time
  per actuator, interlocks (acid and base never together), a safe state per
  actuator applied if contact with the planner is lost, and relays that rest
  in the off state at boot or after a power cut.
- A common interface per sensor and actuator, with fake implementations for
  tests. Real drivers are marked "not validated on hardware".

Simulator and gateway are mutually exclusive Compose profiles (`sim`, `hw`).

### Consequences

- Good: the control loop is identical in simulation and on hardware.
- Good: safety does not depend on the rest of the stack being alive.
- Bad: the message contract gains fields for pulses and actuator state, which
  the simulator must also support.
- Bad: drivers cannot be fully verified without the physical devices.

## Pros and cons of the options

### Hardware access in monitor and executor

- Good: no extra service.
- Bad: couples MAPE-K stages to GPIO and I2C; the services stop being portable.

### Separate code paths per service

- Good: each service can optimise for hardware.
- Bad: duplicated logic and two behaviours to test.

## Links

- ADR-0003, ADR-0004.
- `docs/hardware.md` (bill of materials and wiring; phase 8).
