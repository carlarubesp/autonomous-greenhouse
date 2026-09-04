import requests
import paho.mqtt.client as mqtt
import configparser

config = configparser.ConfigParser()
config.read('../greenhouse.conf')

MQTT_BROKER = config.get("mqtt_broker", "broker_name")
MQTT_PORT = config.getint("mqtt_broker", "port")
KNOWLEDGE_HOST = config.get("knowledge", "host")
KNOWLEDGE_PORT = config.getint("knowledge", "port")
MQTT_TOPICS = [("greenhouse/sensors/status", 0),
               ("greenhouse/reset", 0)]

class Monitor:
    def __init__(self):
        self.client = mqtt.Client()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker.")
        else:
            print("Connection failed.")

    def on_message(self, client, userdata, message):
        msg = message.payload.decode("utf-8")
        pass

    def command_analyzer(self):
        pass

    def insert_sensors_info(self, sensors_info):
        pass

    def reset_knowledge(self):
        pass

    def start(self):
        pass

if __name__ == "__main__":
    monitor = Monitor()
    monitor.start()