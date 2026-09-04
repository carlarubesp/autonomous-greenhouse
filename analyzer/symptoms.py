import json

with open("../thresholds.json", "r") as f:
    thresholds = json.load(f)

def freezing_risk(info):
    return info["temperature"] < thresholds["temperature"]["night"]["alarm"][0]

def mold_risk(info):
    return (info["temperature"] > thresholds["temperature"]["day"]["alarm"][1]
            and info["soil_humidity"] < thresholds["soil_humidity"]["alarm"][0])

symptoms = {
    "freezing_risk": freezing_risk,
    "mold_risk": mold_risk,
}