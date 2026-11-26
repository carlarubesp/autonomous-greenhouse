import uvicorn
from fastapi import FastAPI

from greenhouse_common.config import load_settings, load_thresholds
from readSensors import ReadSensors
from updateActuators import UpdateActuators

settings = load_settings()

app = FastAPI(title="Knowledge")

thresholds = load_thresholds()

short_term_memory: list[ReadSensors] = []
actuators_state = {
    "heater": False,
    "fan": False,
    "sprinklers": False,
    "co2_injector": False,
    "water_pump": False,
    "acid_dosing": False,
    "base_dosing": False,
    "nutrient_dosing": False,
}


@app.get("/thresholds")
def get_thresholds():
    return thresholds


@app.post("/sensors")
def update_sensors(information: ReadSensors):
    short_term_memory.append(information)
    if len(short_term_memory) > 20:
        short_term_memory.pop(0)
    return short_term_memory


@app.get("/short-term")
def get_short_term_memory():
    return short_term_memory


@app.post("/actuators")
def update_actuators(update: UpdateActuators):
    changes = update.model_dump(exclude_none=True)
    actuators_state.update(changes)
    return actuators_state


@app.get("/actuators")
def get_actuators():
    return actuators_state


@app.post("/short-term/reset")
def reset():
    short_term_memory.clear()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.knowledge_port)
