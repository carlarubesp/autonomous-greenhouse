import random

class CalculateMetrics:
    @staticmethod
    def change_temperature(temperature, is_day, heater, fan):
        outside_temp_day = 35.0
        outside_temp_night = 8.0

        if is_day:
            temp_change = (outside_temp_day - temperature) * 0.07
        else:
            temp_change = (outside_temp_night - temperature) * 0.07

        if heater:
            temp_change += 0.5
        if fan:
            temp_change -= 0.3

        return max(min(temperature + temp_change + random.uniform(-0.15, 0.15), 40), -5)

    @staticmethod
    def change_rel_humidity(rel_humidity,is_day, heater, sprinklers):
        rel_humidity_day = 55.0
        rel_humidity_night = 80.0

        if is_day:
            humidity_change = (rel_humidity_day - rel_humidity) * 0.07
        else:
            humidity_change = (rel_humidity_night - rel_humidity) * 0.07

        if heater:
            humidity_change -= 0.12
        if sprinklers:
            humidity_change += 0.16

        return max(min(rel_humidity + humidity_change + random.uniform(-0.2, 0.2), 100), 0)

    @staticmethod
    def change_soil_humidity(soil_humidity, heater, sprinklers, water_pump):
        soil_humid_tendency = 25
        humidity_change = (soil_humid_tendency - soil_humidity) * 0.08

        if heater:
            humidity_change -= 0.3
        if sprinklers:
            humidity_change += 0.37
        if water_pump:
            humidity_change += 0.4

        return max(min(soil_humidity + humidity_change + random.uniform(-0.2, 0.2), 100), 0)

    @staticmethod
    def change_co2(co2, is_day, fan, co2_injector):
        co2_day = 250.0
        co2_night = 550.0

        if is_day:
            co2_change = (co2_day - co2) * 0.05
        else:
            co2_change = (co2_night - co2) * 0.05

        if fan:
            co2_change -= 25
        if co2_injector:
            co2_change += 40

        return max(min(co2 + co2_change + random.uniform(-0.2, 0.2), 2000), 0)

    @staticmethod
    def change_ph(ph, acid_dosing, base_dosing):
        ph_tendency = 6.5
        ph_change = (ph_tendency - ph) * 0.03

        if acid_dosing:
            ph_change -= 0.04
        if base_dosing:
            ph_change += 0.027

        return max(min(ph + ph_change + random.uniform(-0.015, 0.015), 8.0), 0)

    @staticmethod
    def change_conductivity(conductivity,nutrient_dosing, water_pump):
        conduct_tendency = 0.5
        conduct_change = (conduct_tendency - conductivity) * 0.08

        if nutrient_dosing:
            conduct_change += 0.15
        if water_pump:
            conduct_change -= 0.1

        return max(min(conductivity + conduct_change + random.uniform(-0.02, 0.02), 6.0), 0)