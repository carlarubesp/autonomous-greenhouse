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

    # TODO: Update internal clock and use helper functions
    def next(self):
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

    # TODO: see which MQTT commands can activate the actuators.
    def apply_action(self, action):
        pass

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