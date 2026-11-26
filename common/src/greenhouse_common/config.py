"""Configuration shared by every service.

Values come from ``greenhouse.conf``; environment variables override the
broker and Knowledge addresses (Docker Compose sets them). Paths are relative
to the service folder by default, which is where each service runs from.
"""

import configparser
import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = "../greenhouse.conf"
DEFAULT_THRESHOLDS_PATH = "../thresholds.json"


@dataclass(frozen=True)
class Topics:
    """MQTT topic names, from the ``[topics]`` section of the configuration."""

    sensors_status: str
    actuator_commands: str
    monitor_command: str
    analyzer_command: str
    planner_plan: str
    reset: str


@dataclass(frozen=True)
class Settings:
    mqtt_host: str
    mqtt_port: int
    knowledge_host: str
    knowledge_port: int
    topics: Topics

    @property
    def knowledge_url(self) -> str:
        return f"http://{self.knowledge_host}:{self.knowledge_port}"


def load_settings(
    path: str | Path | None = None, env: Mapping[str, str] | None = None
) -> Settings:
    """Read the configuration file and apply environment overrides.

    The file is ``path``, else ``$GREENHOUSE_CONFIG``, else
    ``../greenhouse.conf``. Overrides: ``MQTT_BROKER``, ``MQTT_PORT``,
    ``KNOWLEDGE_HOST`` and ``KNOWLEDGE_PORT``.
    """
    env = os.environ if env is None else env
    config_path = Path(path or env.get("GREENHOUSE_CONFIG", DEFAULT_CONFIG_PATH))

    parser = configparser.ConfigParser()
    if not parser.read(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    topics = parser["topics"]
    return Settings(
        mqtt_host=env.get("MQTT_BROKER", parser.get("mqtt_broker", "broker_name")),
        mqtt_port=int(env.get("MQTT_PORT", parser.get("mqtt_broker", "port"))),
        knowledge_host=env.get("KNOWLEDGE_HOST", parser.get("knowledge", "host")),
        knowledge_port=int(env.get("KNOWLEDGE_PORT", parser.get("knowledge", "port"))),
        topics=Topics(
            sensors_status=topics["sensors_status"],
            actuator_commands=topics["actuator_commands"],
            monitor_command=topics["monitor_command"],
            analyzer_command=topics["analyzer_command"],
            planner_plan=topics["planner_plan"],
            reset=topics["reset"],
        ),
    )


def load_thresholds(
    path: str | Path | None = None, env: Mapping[str, str] | None = None
) -> dict[str, Any]:
    """Read the metric thresholds.

    The file is ``path``, else ``$GREENHOUSE_THRESHOLDS``, else
    ``../thresholds.json``.
    """
    env = os.environ if env is None else env
    thresholds_path = Path(
        path or env.get("GREENHOUSE_THRESHOLDS", DEFAULT_THRESHOLDS_PATH)
    )
    with thresholds_path.open() as f:
        thresholds: dict[str, Any] = json.load(f)
    return thresholds
