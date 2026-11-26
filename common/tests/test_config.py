from pathlib import Path

import pytest

from greenhouse_common.config import load_settings, load_thresholds

CONFIG = """\
[mqtt_broker]
broker_name = 127.0.0.1
port = 1883

[knowledge]
host = 127.0.0.1
port = 5000

[topics]
sensors_status = greenhouse/sensors/status
actuator_commands = greenhouse/actuators/commands
monitor_command = greenhouse/monitor/command
analyzer_command = greenhouse/analyzer/command
planner_plan = greenhouse/planner/plan
reset = greenhouse/reset
"""


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    path = tmp_path / "greenhouse.conf"
    path.write_text(CONFIG)
    return path


def test_reads_values_from_file(config_file: Path) -> None:
    settings = load_settings(config_file, env={})

    assert settings.mqtt_host == "127.0.0.1"
    assert settings.mqtt_port == 1883
    assert settings.knowledge_url == "http://127.0.0.1:5000"
    assert settings.topics.sensors_status == "greenhouse/sensors/status"
    assert settings.topics.reset == "greenhouse/reset"


def test_environment_overrides_addresses(config_file: Path) -> None:
    env = {
        "MQTT_BROKER": "mosquitto",
        "MQTT_PORT": "1884",
        "KNOWLEDGE_HOST": "knowledge",
        "KNOWLEDGE_PORT": "5001",
    }

    settings = load_settings(config_file, env=env)

    assert (settings.mqtt_host, settings.mqtt_port) == ("mosquitto", 1884)
    assert settings.knowledge_url == "http://knowledge:5001"


def test_config_path_from_environment(config_file: Path) -> None:
    settings = load_settings(env={"GREENHOUSE_CONFIG": str(config_file)})

    assert settings.mqtt_port == 1883


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_settings(tmp_path / "missing.conf", env={})


def test_repository_config_is_valid() -> None:
    repo_config = Path(__file__).parents[2] / "greenhouse.conf"

    settings = load_settings(repo_config, env={})

    assert settings.topics.planner_plan == "greenhouse/planner/plan"


def test_loads_thresholds(tmp_path: Path) -> None:
    path = tmp_path / "thresholds.json"
    path.write_text('{"ph": {"ideal": 6.0}}')

    assert load_thresholds(path, env={}) == {"ph": {"ideal": 6.0}}
