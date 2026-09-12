import time
import json
import random
import configparser
import paho.mqtt.client as mqtt
from calculate_metrics import CalculateMetrics

# Load IPs and ports from a static file
config = configparser.ConfigParser()
config.read('../greenhouse.conf')

MQTT_BROKER = config.get("mqtt_broker", "broker_name")
MQTT_PORT = config.getint("mqtt_broker", "port")
HOST = config.get("knowledge", "host")

# Seed for reproducibility
random.seed(42)

class Greenhouse:
    def __init__(self):
        # Metrics
        self.temperature = 20.0
        self.rel_humidity = 70.0
        self.soil_humidity = 40.0
        self.co2 = 800.0
        self.ph = 6.0
        self.conductivity = 2.0

        # Internal clock (1 tick = 1 minute)
        self.clock = 0
        self.is_day = True

        # Actuators
        self.heater = False
        self.fan = False
        self.sprinklers = False
        self.co2_injector = False
        self.water_pump = False
        self.acid_dosing = False
        self.base_dosing = False
        self.nutrient_dosing = False

    def on_connect(self, client, userdata, flags, rc):
        print("\nConnected with result code " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection.")
        elif rc == 0:
            print("Disconnected successfully.")

    def on_message(self, client, userdata, msg):
        topic = msg.topic

        if topic == "greenhouse/actuators/commands":
            self.apply_action(msg.payload.decode("utf-8"))

    def next(self):
        if self.clock >= 1440:
            self.clock = 0
            self.is_day = True

        if self.clock >= 720:
            self.is_day = False

        self.clock += 1

        self.temperature = CalculateMetrics.change_temperature(
            self.temperature, self.is_day, self.heater, self.fan
        )
        self.rel_humidity = CalculateMetrics.change_rel_humidity(
            self.rel_humidity, self.is_day, self.heater, self.sprinklers
        )
        self.soil_humidity = CalculateMetrics.change_soil_humidity(
            self.soil_humidity, self.heater, self.sprinklers, self.water_pump
        )
        self.co2 = CalculateMetrics.change_co2(
            self.co2, self.is_day, self.fan, self.co2_injector
        )
        self.ph = CalculateMetrics.change_ph(
            self.ph, self.acid_dosing, self.base_dosing
        )
        self.conductivity = CalculateMetrics.change_conductivity(
            self.conductivity, self.nutrient_dosing, self.water_pump
        )


    def read_sensors(self):
        return {
            "clock": self.clock,
            "is_day": self.is_day,
            "temperature": round(self.temperature, 2),
            "relative_humidity": round(self.rel_humidity, 2),
            "soil_humidity": round(self.soil_humidity, 2),
            "co2": round(self.co2, 2),
            "ph": round(self.ph, 2),
            "conductivity": round(self.conductivity, 2)
        }

    def apply_action(self, action):
        if action == "HEATER_ON":
            self.heater = True
        elif action == "HEATER_OFF":
            self.heater = False

        elif action == "FAN_ON":
            self.fan = True
        elif action == "FAN_OFF":
            self.fan = False

        elif action == "SPRINKLERS_ON":
            self.sprinklers = True
        elif action == "SPRINKLERS_OFF":
            self.sprinklers = False

        elif action == "WATER_PUMP_ON":
            self.water_pump = True
        elif action == "WATER_PUMP_OFF":
            self.water_pump = False

        elif action == "CO2_ON":
            self.co2_injector = True
        elif action == "CO2_OFF":
            self.co2_injector = False

        elif action == "ACID_DOSING_ON":
            self.acid_dosing = True
        elif action == "ACID_DOSING_OFF":
            self.acid_dosing = False

        elif action == "BASE_DOSING_ON":
            self.base_dosing = True
        elif action == "BASE_DOSING_OFF":
            self.base_dosing = False

        elif action == "NUTRIENT_ON":
            self.nutrient_dosing = True
        elif action == "NUTRIENT_OFF":
            self.nutrient_dosing = False

    def start(self):
        client = mqtt.Client()
        client.on_message = self.on_message

        client.connect(MQTT_BROKER, MQTT_PORT)
        client.subscribe("greenhouse/actuators/commands")
        client.loop_start()

        while True:
            self.next()
            latest_data = self.read_sensors()
            client.publish("greenhouse/sensors/status", json.dumps(latest_data))
            time.sleep(0.5)

if __name__ == "__main__":
    simulator = Greenhouse()
    simulator.start()