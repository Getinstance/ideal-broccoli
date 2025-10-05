from pydantic import BaseModel


class ScrapResponse(BaseModel):
    message: str
