import json

from greenhouse_common.config import load_settings, load_thresholds
from greenhouse_common.knowledge import KnowledgeClient
from greenhouse_common.log import setup_logging
from greenhouse_common.mqtt import connect, create_client
from symptoms import symptoms

log = setup_logging("analyzer")
settings = load_settings()
topics = settings.topics

MQTT_TOPICS = [(topics.monitor_command, 0), (topics.reset, 0)]

thresholds = load_thresholds()

TREND_THRESHOLD = 0.1


class Analyzer:
    def __init__(self):
        self.last_avg = None
        self.client = create_client()
        self.knowledge = KnowledgeClient(settings.knowledge_url)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, reason_code, properties):
        if not reason_code.is_failure:
            log.info("Connected to broker.")
        else:
            client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_message(self, client, userdata, message):
        msg = message.payload.decode("utf-8").strip()

        if message.topic == topics.monitor_command and msg == "start":
            diagnosis = self.analyze()
            if diagnosis:
                log.debug("Information analyzed and classified.")
                self.command_planner(diagnosis)

        elif message.topic == topics.reset:
            self.reset_knowledge()
            log.info("Knowledge reset")

    def command_planner(self, diagnosis):
        self.client.publish(topics.analyzer_command, json.dumps(diagnosis))
        log.debug("Commanded Planner to start planning")

    def get_sensors_info(self):
        # Returns the short-term memory list that compiles together
        # all the sensors until that point
        return self.knowledge.get_short_term()

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
                log.warning(
                    "ALARM: %s=%s outside of [%s, %s]",
                    metric,
                    value,
                    alarm_min,
                    alarm_max,
                )
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
        self.knowledge.reset_short_term()
        log.info("Knowledge reset")

    def analyze(self):
        sensors_info = self.get_sensors_info()
        if not sensors_info:
            log.info("No sensor data available.")
            return None

        last = sensors_info[-1]

        has_alarm = self.check_sensors(sensors_info)
        if has_alarm:
            log.warning(
                "Alarm state reached. There is a metric completely out of range."
            )

        symptoms = self.check_symptoms(sensors_info)
        if symptoms:
            log.info("Symptoms detected: %s", symptoms)

        trends = self.check_tendency(sensors_info)
        if trends:
            log.info("Tendency detected: %s", trends)

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
        connect(self.client, settings)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPICS)
        self.client.loop_forever()


if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.start()
