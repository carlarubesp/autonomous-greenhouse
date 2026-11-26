"""MQTT client factory."""

import paho.mqtt.client as mqtt

from greenhouse_common.config import Settings


def create_client() -> mqtt.Client:
    """Return a paho-mqtt client that uses the callback API version 2."""
    return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)


def connect(client: mqtt.Client, settings: Settings) -> None:
    """Connect ``client`` to the broker in ``settings``."""
    client.connect(settings.mqtt_host, settings.mqtt_port)
