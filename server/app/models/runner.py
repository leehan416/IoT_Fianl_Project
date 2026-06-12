from pydantic import BaseModel, ConfigDict, Field


class RunnerLocation(BaseModel):
    runner_id: str
    latitude: float
    longitude: float
    pace: float | None = None
    battery: int | None = Field(default=None, ge=0, le=100)
    status: str = "normal"
    received_at: str

    model_config = ConfigDict(frozen=True)
