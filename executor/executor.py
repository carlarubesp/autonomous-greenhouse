import json

from greenhouse_common.config import load_settings
from greenhouse_common.knowledge import KnowledgeClient
from greenhouse_common.log import setup_logging
from greenhouse_common.mqtt import connect, create_client

log = setup_logging("executor")
settings = load_settings()
topics = settings.topics

MQTT_TOPICS = [(topics.planner_plan, 0), (topics.reset, 0)]

ACTUATOR_COMMANDS = {
    "heater": ("HEATER_ON", "HEATER_OFF"),
    "fan": ("FAN_ON", "FAN_OFF"),
    "sprinklers": ("SPRINKLERS_ON", "SPRINKLERS_OFF"),
    "co2_injector": ("CO2_ON", "CO2_OFF"),
    "water_pump": ("WATER_PUMP_ON", "WATER_PUMP_OFF"),
    "acid_dosing": ("ACID_DOSING_ON", "ACID_DOSING_OFF"),
    "base_dosing": ("BASE_DOSING_ON", "BASE_DOSING_OFF"),
    "nutrient_dosing": ("NUTRIENT_ON", "NUTRIENT_OFF"),
}


class Executor:
    def __init__(self):
        self.client = create_client()
        self.knowledge = KnowledgeClient(settings.knowledge_url)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if not reason_code.is_failure:
            log.info("Connected to broker.")
        else:
            client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_message(self, client, userdata, message):
        if message.topic == topics.planner_plan:
            payload = json.loads(message.payload.decode("utf-8"))
            self.execute(payload)

        elif message.topic == topics.reset:
            log.info("Executor received reset.")

    def get_actuators(self):
        return self.knowledge.get_actuators()

    def update_actuators(self, changes):
        return self.knowledge.update_actuators(changes)

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
            self.client.publish(topics.actuator_commands, cmd)
            changes[actuator] = desired
            log.info("Executed: %s", cmd)

        if not changes:
            return

        self.update_actuators(changes)

    def start(self):
        connect(self.client, settings)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPICS)
        self.client.loop_forever()


if __name__ == "__main__":
    executor = Executor()
    executor.start()
