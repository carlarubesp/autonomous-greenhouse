from pydantic import BaseModel

class UpdateActuators(BaseModel):
    heater: bool
    fan: bool
    sprinklers: bool
    co2_injector: bool
    water_pump: bool
    acid_dosing: bool
    base_dosing: bool
    nutrient_dosing: bool