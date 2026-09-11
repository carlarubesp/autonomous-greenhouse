import json

with open("../thresholds.json", "r") as f:
    thresholds = json.load(f)


def _temp_alarm_max(info):
    """Returns the high temperature alarm for the current day/night profile."""
    profile = "day" if info["is_day"] else "night"
    return thresholds["temperature"][profile]["alarm"][1]


def freezing_risk(info):
    return info["temperature"] < thresholds["temperature"]["night"]["alarm"][0]


def heating_risk(info):
    return (info["temperature"] > _temp_alarm_max(info)
            and info["soil_humidity"] < thresholds["soil_humidity"]["alarm"][0])


def mold_risk(info):
    return (info["temperature"] > _temp_alarm_max(info)
            and info["soil_humidity"] > thresholds["soil_humidity"]["alarm"][1])


symptoms = {
    "freezing_risk": freezing_risk,
    "heating_risk": heating_risk,
    "mold_risk": mold_risk,
}