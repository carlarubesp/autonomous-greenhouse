from pydantic import BaseModel

class ReadSensors(BaseModel):
    clock: int
    is_day: bool
    temperature: float
    relative_humidity: float
    soil_humidity: float
    co2: float
    ph: float
    conductivity: float