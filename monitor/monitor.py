import json

from greenhouse_common.config import load_settings
from greenhouse_common.knowledge import KnowledgeClient
from greenhouse_common.log import setup_logging
from greenhouse_common.mqtt import connect, create_client

log = setup_logging("monitor")
settings = load_settings()
topics = settings.topics

MQTT_TOPICS = [(topics.sensors_status, 0), (topics.reset, 0)]


class Monitor:
    def __init__(self):
        self.client = create_client()
        self.knowledge = KnowledgeClient(settings.knowledge_url)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if not reason_code.is_failure:
            log.info("Connected to broker.")
        else:
            log.error("Connection failed.")

    def on_message(self, client, userdata, message):
        msg = message.payload.decode("utf-8")

        if message.topic == topics.sensors_status:
            self.insert_sensors_info(msg)
            log.debug("Sensors info inserted")
            self.command_analyzer()

        elif message.topic == topics.reset:
            self.reset_knowledge()
            log.info("Knowledge reset")

    def command_analyzer(self):
        self.client.publish(topics.monitor_command, "start")
        log.debug("Commanded Analyzer to start analyzing")

    def insert_sensors_info(self, sensors_info):
        self.knowledge.add_reading(json.loads(sensors_info))
        log.debug("Reading: %s", sensors_info)

    def reset_knowledge(self):
        self.knowledge.reset_short_term()
        log.info("Knowledge reset")

    def start(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Connect to the mqtt broker
        connect(self.client, settings)
        self.client.subscribe(MQTT_TOPICS)
        self.client.loop_forever()


if __name__ == "__main__":
    monitor = Monitor()
    monitor.start()
