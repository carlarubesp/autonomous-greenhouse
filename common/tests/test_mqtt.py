import paho.mqtt.client as mqtt

from greenhouse_common.mqtt import create_client


def test_client_uses_callback_api_v2() -> None:
    client = create_client()

    assert client.callback_api_version == mqtt.CallbackAPIVersion.VERSION2
