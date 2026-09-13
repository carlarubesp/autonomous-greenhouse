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

MQTT_TOPICS = [("greenhouse/analyzer/command", 0),
               ("greenhouse/reset", 0)]

with open("../thresholds.json", "r") as f:
    thresholds = json.load(f)

class Planner:
    def __init__(self):
        self.client = mqtt.Client()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker.")
        else:
            client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_message(self, client, userdata, message):
        pass

    def get_actuators(self):
        actuators_info = f"http://{KNOWLEDGE_HOST}:{KNOWLEDGE_PORT}/actuators"
        response = requests.get(actuators_info)
        return response.json()

    def apply_hysteresis(self, current_state, value, limits, increases):
        pass

    def consider(self, actuator, metric_name, value, limits, increases,
                 plan, claimed, reasons):
        pass

    def build_plan(self, diagnosis):
        pass

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPICS)
        self.client.loop_forever()

if __name__ == '__main__':
    plan = Planner()
    plan.start()