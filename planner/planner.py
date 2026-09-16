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
        if message.topic == "greenhouse/analyzer/command":
            diagnosis = json.loads(message.payload.decode("utf-8"))
            self.build_plan(diagnosis)

        elif message.topic == "greenhouse/reset":
            print("Planner received reset.")

    def get_actuators(self):
        actuators_info = f"http://{KNOWLEDGE_HOST}:{KNOWLEDGE_PORT}/actuators"
        response = requests.get(actuators_info)
        return response.json()

    def apply_hysteresis(self, current_state, value, limits, increases):
        low, high = limits["secure"]
        ideal = limits["ideal"]

        if increases:
            if current_state:
                return value < ideal
            else:
                return value < low
        else:
            if current_state:
                return value > ideal
            else:
                return value > high

    def consider(self, actuator, metric_name, value, limits, increases,
                 plan, claimed, reasons):
        if actuator in claimed:
            return

        previous = plan[actuator]
        desired = self.apply_hysteresis(previous, value, limits, increases)
        plan[actuator] = desired
        claimed.add(actuator)

        if desired != previous:
            reasons.append(
                f"{metric_name}={value:.2f} -> {actuator} "
                f"{'ON' if desired else 'OFF'}"
            )

    def build_plan(self, diagnosis):
        reading = diagnosis["reading"]
        is_day = reading["is_day"]

        current = self.get_actuators()
        if current is None:
            print("Could not read actuator state, skipping plan.")
            return

        plan = dict(current)
        claimed = set()
        reasons = []

        temp = reading["temperature"]
        temp_limits = thresholds["temperature"]["day" if is_day else "night"]
        self.consider("heater", "temperature", temp, temp_limits,
                      increases=True, plan=plan, claimed=claimed, reasons=reasons)
        self.consider("fan", "temperature", temp, temp_limits,
                      increases=False, plan=plan, claimed=claimed, reasons=reasons)

        ph = reading["ph"]
        self.consider("acid_dosing", "ph", ph, thresholds["ph"],
                      increases=False, plan=plan, claimed=claimed, reasons=reasons)
        self.consider("base_dosing", "ph", ph, thresholds["ph"],
                      increases=True, plan=plan, claimed=claimed, reasons=reasons)

        sh = reading["soil_humidity"]
        sh_limits = thresholds["soil_humidity"]
        self.consider("water_pump", "soil_humidity", sh, sh_limits,
                      increases=True, plan=plan, claimed=claimed, reasons=reasons)
        self.consider("sprinklers", "soil_humidity", sh, sh_limits,
                      increases=True, plan=plan, claimed=claimed, reasons=reasons)

        rh = reading["relative_humidity"]
        rh_limits = thresholds["relative_humidity"]
        self.consider("sprinklers", "relative_humidity", rh, rh_limits,
                      increases=True, plan=plan, claimed=claimed, reasons=reasons)

        co2 = reading["co2"]
        co2_limits = thresholds["co2"]
        self.consider("co2_injector", "co2", co2, co2_limits,
                      increases=True, plan=plan, claimed=claimed, reasons=reasons)

        ce = reading["conductivity"]
        ce_limits = thresholds["conductivity"]
        self.consider("nutrient_dosing", "conductivity", ce, ce_limits,
                      increases=True, plan=plan, claimed=claimed, reasons=reasons)

        payload = {
            "clock": diagnosis["clock"],
            "plan": plan,
            "reasons": reasons,
        }
        self.client.publish("greenhouse/planner/plan", json.dumps(payload))
        if reasons:
            print(f"Plan at clock {diagnosis['clock']}: {reasons}")
        else:
            print(f"Plan at clock {diagnosis['clock']}: no changes")

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPICS)
        self.client.loop_forever()

if __name__ == '__main__':
    plan = Planner()
    plan.start()