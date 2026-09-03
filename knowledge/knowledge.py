import configparser
import json
import uvicorn
from fastapi import FastAPI

config = configparser.ConfigParser()
config.read("../greenhouse.conf")
PORT = config.getint("knowledge", "port")

app = FastAPI(title="Knowledge")

with open("../thresholds.json", "r") as f:
    thresholds = json.load(f)

@app.get("/thresholds")
def get_thresholds():
    return thresholds

@app.post("/sensors")
async def add_sensors_info(info: dict):
    pass

@app.get("/sensors")
async def get_sensors():
    pass

@app.get("/short-term")
def get_short_term_memory():
    pass

@app.post("/actuators")
def add_actuators_info(info: dict):
    pass

@app.get("/actuators")
def get_actuators():
    pass

@app.post("/short-term/reset")
def reset():
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)