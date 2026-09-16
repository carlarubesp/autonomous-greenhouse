from typing import Optional
from pydantic import BaseModel

class UpdateActuators(BaseModel):
    heater: Optional[bool] = None
    fan: Optional[bool] = None
    sprinklers: Optional[bool] = None
    co2_injector: Optional[bool] = None
    water_pump: Optional[bool] = None
    acid_dosing: Optional[bool] = None
    base_dosing: Optional[bool] = None
    nutrient_dosing: Optional[bool] = None