from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    provider: str
    api_base_url: str
