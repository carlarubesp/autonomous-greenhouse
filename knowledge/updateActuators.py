from pydantic import BaseModel


class UpdateActuators(BaseModel):
    heater: bool | None = None
    fan: bool | None = None
    sprinklers: bool | None = None
    co2_injector: bool | None = None
    water_pump: bool | None = None
    acid_dosing: bool | None = None
    base_dosing: bool | None = None
    nutrient_dosing: bool | None = None
