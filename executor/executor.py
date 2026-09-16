import paho.mqtt.client as mqtt
import requests
import json
import configparser
import os

config = configparser.ConfigParser()
config.read('../greenhouse.conf')

MQTT_BROKER = os.getenv("MQTT_BROKER", config.get("mqtt_broker", "broker_name"))
MQTT_PORT = int(os.getenv("MQTT_PORT", config.getint("mqtt_broker", "port")))
KNOWLEDGE_HOST = os.getenv("KNOWLEDGE_HOST", config.get("knowledge", "host"))
KNOWLEDGE_PORT = int(os.getenv("KNOWLEDGE_PORT", config.getint("knowledge", "port")))

MQTT_TOPICS = [("greenhouse/planner/plan", 0),
               ("greenhouse/reset", 0)]

ACTUATOR_COMMANDS = {
    "heater":          ("HEATER_ON",          "HEATER_OFF"),
    "fan":             ("FAN_ON",             "FAN_OFF"),
    "sprinklers":      ("SPRINKLERS_ON",      "SPRINKLERS_OFF"),
    "co2_injector":    ("CO2_ON",             "CO2_OFF"),
    "water_pump":      ("WATER_PUMP_ON",      "WATER_PUMP_OFF"),
    "acid_dosing":     ("ACID_DOSING_ON",     "ACID_DOSING_OFF"),
    "base_dosing":     ("BASE_DOSING_ON",     "BASE_DOSING_OFF"),
    "nutrient_dosing": ("NUTRIENT_ON",        "NUTRIENT_OFF"),
}

class Executor:
    def __init__(self):
        self.client = mqtt.Client()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker.")
        else:
            client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_message(self, client, userdata, message):
        if message.topic == "greenhouse/planner/plan":
            payload = json.loads(message.payload.decode("utf-8"))
            self.execute(payload)

        elif message.topic == "greenhouse/reset":
            print("Executor received reset.")

    def get_actuators(self):
        actuators = f"http://{KNOWLEDGE_HOST}:{KNOWLEDGE_PORT}/actuators"
        response = requests.get(actuators)
        return response.json()

    def update_actuators(self, changes):
        return requests.post(f"http://{KNOWLEDGE_HOST}:{KNOWLEDGE_PORT}/actuators",
                      json=changes)

    def execute(self, payload):
        plan = payload.get("plan", {})
        if not plan:
            return

        current = self.get_actuators()
        changes = {}

        for actuator, desired in plan.items():
            if actuator not in ACTUATOR_COMMANDS:
                continue
            desired = bool(desired)
            if current.get(actuator, False) == desired:
                continue

            on_cmd, off_cmd = ACTUATOR_COMMANDS[actuator]
            cmd = on_cmd if desired else off_cmd
            self.client.publish("greenhouse/actuators/commands", cmd)
            changes[actuator] = desired
            print(f"Executed: {cmd}")

        if not changes:
            return

        self.update_actuators(changes)

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPICS)
        self.client.loop_forever()

if __name__ == '__main__':
    executor = Executor()
    executor.start()