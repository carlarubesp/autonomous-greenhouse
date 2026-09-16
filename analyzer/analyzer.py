import paho.mqtt.client as mqtt
import requests
import json
import configparser
from symptoms import symptoms
import os

config = configparser.ConfigParser()
config.read('../greenhouse.conf')

MQTT_BROKER = os.getenv("MQTT_BROKER", config.get("mqtt_broker", "broker_name"))
MQTT_PORT = int(os.getenv("MQTT_PORT", config.getint("mqtt_broker", "port")))
KNOWLEDGE_HOST = os.getenv("KNOWLEDGE_HOST", config.get("knowledge", "host"))
KNOWLEDGE_PORT = int(os.getenv("KNOWLEDGE_PORT", config.getint("knowledge", "port")))

MQTT_TOPICS = [("greenhouse/monitor/command", 0),
               ("greenhouse/reset", 0)]

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
            client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_message(self, client, userdata, message):
        msg = message.payload.decode('utf-8').strip()

        if message.topic == "greenhouse/monitor/command" and msg == "start":
            diagnosis = self.analyze()
            if diagnosis:
                print("Information analyzed and classified.")
                self.command_planner(diagnosis)

        elif message.topic == "greenhouse/reset":
            self.reset_knowledge()
            print("Knowledge reset")

    def command_planner(self, diagnosis):
        self.client.publish("greenhouse/analyzer/command", json.dumps(diagnosis))
        print("Commanded Planner to start planning")

    def get_sensors_info(self):
        # Returns the short-term memory list that compiles together
        # all the sensors until that point
        sensors_info = f"http://{KNOWLEDGE_HOST}:{KNOWLEDGE_PORT}/short-term"
        response = requests.get(sensors_info)
        return response.json()

    def check_sensors(self, sensors_info):
        if not sensors_info:
            return False

        last_min = sensors_info[-1]
        is_day = last_min["is_day"]

        for metric, limits in thresholds.items():
            if metric not in last_min:
                continue

            value = last_min[metric]

            if "day" in limits and "night" in limits:
                alarm_min, alarm_max = limits["day" if is_day else "night"]["alarm"]
            else:
                alarm_min, alarm_max = limits["alarm"]

            if value > alarm_max or value < alarm_min:
                print(f"ALARM: {metric}={value} outside of [{alarm_min}, {alarm_max}]")
                return True

        return False

    def check_symptoms(self, sensors_info):
        if not sensors_info:
            return []

        last_min = sensors_info[-1]
        detected = []

        for name, condition in symptoms.items():
            if condition(last_min):
                detected.append(name)

        return detected

    def twenty_min_average(self, sensors_info):
        temperature = 0
        relative_humidity = 0
        soil_humidity = 0
        co2 = 0
        ph = 0
        conductivity = 0

        if not sensors_info:
            return None

        clock = sensors_info[-1]["clock"]
        if clock == 0 or clock % 20 != 0:
            return None

        for elem in sensors_info:
            temperature += elem["temperature"]
            relative_humidity += elem["relative_humidity"]
            soil_humidity += elem["soil_humidity"]
            co2 += elem["co2"]
            ph += elem["ph"]
            conductivity += elem["conductivity"]

        avg = {
            "temperature": temperature / len(sensors_info),
            "relative_humidity": relative_humidity / len(sensors_info),
            "soil_humidity": soil_humidity / len(sensors_info),
            "co2": co2 / len(sensors_info),
            "ph": ph / len(sensors_info),
            "conductivity": conductivity / len(sensors_info),
        }

        return avg

    def check_tendency(self, sensors_info):
        avg = self.twenty_min_average(sensors_info)

        if avg is None:
            return {}

        if self.last_avg is None:
            self.last_avg = avg
            return {}

        trends = {}
        for metric, value in avg.items():
            previous = self.last_avg[metric]
            diff = value - previous

            if previous != 0 and abs(diff) / abs(previous) > TREND_THRESHOLD:
                trends[metric] = "going up" if diff > 0 else "going down"

        self.last_avg = avg
        return trends

    def reset_knowledge(self):
        requests.post(url=f"http://{KNOWLEDGE_HOST}:{KNOWLEDGE_PORT}/short-term/reset")
        print("Knowledge reset")

    def analyze(self):
        sensors_info = self.get_sensors_info()
        if not sensors_info:
            print("No sensor data available.")
            return None

        last = sensors_info[-1]

        has_alarm = self.check_sensors(sensors_info)
        if has_alarm:
            print("Alarm state reached. There is a metric completely out of range.")

        symptoms = self.check_symptoms(sensors_info)
        if symptoms:
            print("Symptoms detected: ", symptoms)

        trends = self.check_tendency(sensors_info)
        if trends:
            print("Tendency detected: ", trends)

        diagnosis = {
            "clock": last["clock"],
            "is_day": last["is_day"],
            "reading": last,
            "alarm": has_alarm,
            "symptoms": symptoms,
            "trends": trends,
        }

        return diagnosis

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPICS)
        self.client.loop_forever()

if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.start()