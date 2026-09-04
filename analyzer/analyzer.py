import paho.mqtt.client as mqtt
import requests
import json
import configparser
from symptoms import symptoms

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
        # Returns the short-term memory list that compiles together
        # all the sensors until that point
        sensors_info = f"{KNOWLEDGE_HOST}:{KNOWLEDGE_PORT}/short-term"
        response = requests.get(sensors_info)
        return response.json()

    def check_sensors(self, sensors_info):
        if not sensors_info:
            return None

        last_min = sensors_info[-1]
        is_day = last_min["is_day"]

        for metric, limits in thresholds.items():
            if metric not in last_min:
                continue

            value = last_min[metric]

            if "day" in limits:
                alarm_min, alarm_max = limits["day" if is_day else "night"]["alarm"]
            else:
                alarm_min, alarm_max = limits["alarm"]

            if value > alarm_max or value < alarm_min:
                return True

        return False

    def check_symptoms(self, sensors_info):
        if not sensors_info:
            return None

        last_min = sensors_info[-1]
        detected = []

        for name, condition in symptoms.items():
            if condition(last_min):
                detected.append(name)

        return detected

    def twenty_min_average(self, sensors_info):
        temperature = 0
        rel_humidity = 0
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
            rel_humidity += elem["rel_humidity"]
            soil_humidity += elem["soil_humidity"]
            co2 += elem["co2"]
            ph += elem["ph"]
            conductivity += elem["conductivity"]

        avg = {
            "temperature": temperature / len(sensors_info),
            "rel_humidity": rel_humidity / len(sensors_info),
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
        requests.post(url=f"{KNOWLEDGE_HOST}:{KNOWLEDGE_PORT}/short-term/reset")
        print("Knowledge reset")

    def analyze(self):
        sensors_info = self.get_sensors_info()
        if not sensors_info:
            return

        if self.check_sensors(sensors_info):
            print("Alarm state reached. There is a metric completely out of range.")

        detected = self.check_symptoms(sensors_info)
        if detected:
            print("Symptoms detected: ", detected)

        trends = self.check_tendency(sensors_info)
        if trends:
            print("Tendency detected: ", trends)

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.subscribe(TOPIC)
        self.client.loop_forever()

if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.start()