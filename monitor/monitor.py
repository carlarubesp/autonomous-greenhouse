import requests
import paho.mqtt.client as mqtt
import configparser
import json
import os

config = configparser.ConfigParser()
config.read('../greenhouse.conf')

MQTT_BROKER = os.getenv("MQTT_BROKER", config.get("mqtt_broker", "broker_name"))
MQTT_PORT = int(os.getenv("MQTT_PORT", config.getint("mqtt_broker", "port")))
KNOWLEDGE_HOST = os.getenv("KNOWLEDGE_HOST", config.get("knowledge", "host"))
KNOWLEDGE_PORT = int(os.getenv("KNOWLEDGE_PORT", config.getint("knowledge", "port")))

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

        if message.topic == "greenhouse/sensors/status":
            self.insert_sensors_info(msg)
            print("Sensors info inserted")
            self.command_analyzer()

        elif message.topic == "greenhouse/reset":
            self.reset_knowledge()
            print("Knowledge reset")

    def command_analyzer(self):
        self.client.publish("greenhouse/monitor/command", "start")
        print("Commanded Analyzer to start analyzing")

    def insert_sensors_info(self, sensors_info):
        requests.post(url=f"http://{KNOWLEDGE_HOST}:{KNOWLEDGE_PORT}/sensors",
                      json=json.loads(sensors_info))
        print(f"{sensors_info}")

    def reset_knowledge(self):
        requests.post(url=f"http://{KNOWLEDGE_HOST}:{KNOWLEDGE_PORT}/short-term/reset")
        print("Knowledge reset")

    def start(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Connect to the mqtt broker
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.subscribe(MQTT_TOPICS)
        self.client.loop_forever()

if __name__ == "__main__":
    monitor = Monitor()
    monitor.start()