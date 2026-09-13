class Planner:
    def __init__(self):
        pass

    def on_connect(self, client, userdata, flags, rc):
        pass

    def on_message(self, client, userdata, message):
        pass

    def get_short_term(self):
        pass

    def get_actuators(self):
        pass

    def build_plan(self):
        pass

    def start(self):
        pass

if __name__ == '__main__':
    plan = Planner()
    plan.start()