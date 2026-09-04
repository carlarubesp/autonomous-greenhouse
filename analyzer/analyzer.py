import paho.mqtt.client as mqtt
import requests
import json
import configparser

config = configparser.ConfigParser()
config.read('../greenhouse.conf')

MQTT_BROKER = config.get("mqtt_broker", "broker_name")
MQTT_PORT = config.getint("mqtt_broker", "port")
KNOWLEDGE_HOST = config.get("knowledge", "host")
KNOWLEDGE_PORT = config.getint("knowledge", "port")
TOPIC = "greenhouse/monitor/command"

with open("../thresholds.json", "r") as f:
    thresholds = json.load(f)

TREND_THRESHOLD = 0.1

class Analyzer:
    def __init__(self):
        self.last_avg = None
        self.client = mqtt.Client()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker.")
        else:
            print("Connection failed.")

    def on_message(self, client, userdata, message):
        msg = message.payload.decode('utf-8')
        if message.topic == TOPIC and msg == "start":
            self.analyze()

    def get_sensors_info(self):
        pass

    def check_sensors(self, sensors_info):
        pass

    def check_symptoms(self, sensors_info):
        pass

    def twenty_min_average(self, sensors_info):
        pass

    def check_tendency(self, sensors_info):
        pass

    def reset_knowledge(self):
        requests.post(url=f"{KNOWLEDGE_HOST}:{KNOWLEDGE_PORT}/short-term/reset")
        print("Knowledge reset")

    def analyze(self):
        pass

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.subscribe(TOPIC)
        self.client.loop_forever()

if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.start()