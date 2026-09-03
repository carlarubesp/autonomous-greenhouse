from pydantic import BaseModel, Field

class ReadSensors(BaseModel):
    clock: int
    is_day: bool = Field(alias="is day?")
    temperature: float
    relative_humidity: float = Field(alias="relative humidity")
    soil_humidity: float = Field(alias="soil humidity")
    co2: float = Field(alias="CO2")
    ph: float = Field(alias="pH")
    conductivity: float