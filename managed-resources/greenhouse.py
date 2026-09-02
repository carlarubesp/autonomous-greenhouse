import time
import json
import random
import configparser
import paho.mqtt.client as mqtt

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
        self.CO2 = 800.0
        self.pH = 6.0
        self.conductivity = 2.0

        # Internal clock (1 tick = 1 minute)
        self.clock = 0
        self.isDay = True

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

    # TODO: Finish next function with helper functions to change the temperature
    def next(self):
        if self.clock >= 1440:
            self.clock = 0
            self.isDay = True

        if self.clock >= 720:
            self.isDay = False

        self.clock += 1

    def change_temperature(self):
        outside_temp_day = 35.0
        outside_temp_night = 8.0

        if self.isDay:
            temp_change = (outside_temp_day - self.temperature) * 0.07
        else:
            temp_change = (outside_temp_night - self.temperature) * 0.07

        if self.heater:
            temp_change += 0.5
        if self.fan:
            temp_change -= 0.3

        return max(min(self.temperature + temp_change + random.uniform(-0.15, 0.15), 40), -5)

    def change_rel_humidity(self):
        rel_humidity_day = 55.0
        rel_humidity_night = 80.0

        if self.isDay:
            humidity_change = (rel_humidity_day - self.rel_humidity) * 0.07
        else:
            humidity_change = (rel_humidity_night - self.rel_humidity) * 0.07

        if self.heater:
            humidity_change -= 0.12
        if self.sprinklers:
            humidity_change += 0.16

        return max(min(self.rel_humidity + humidity_change + random.uniform(-0.2, 0.2), 100), 0)

    def change_soil_humidity(self):
        soil_humid_tendency = 25
        humidity_change = (soil_humid_tendency - self.soil_humidity) * 0.08

        if self.heater:
            humidity_change -= 0.3
        if self.sprinklers:
            humidity_change += 0.37
        if self.water_pump:
            humidity_change += 0.4

        return max(min(self.soil_humidity + humidity_change + random.uniform(-0.2, 0.2), 100), 0)

    # TODO: Last 3 helper functions
    def change_co2(self):
        pass

    def change_ph(self):
        pass

    def change_conductivity(self):
        pass

    def read_sensors(self):
        return {
            "clock": self.clock,
            "is day?": self.isDay,
            "temperature": round(self.temperature, 2),
            "relative humidity": round(self.rel_humidity, 2),
            "soil humidity": round(self.soil_humidity, 2),
            "CO2": round(self.CO2, 2),
            "pH": round(self.pH, 2),
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