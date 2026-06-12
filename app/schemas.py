from datetime import datetime

from pydantic import BaseModel


class URLBase(BaseModel):
    target_url: str


class URLCreate(URLBase):
    pass


class URLResponse(URLBase):
    short_id: str
    clicks: int
    created_at: datetime

    model_config = {"from_attributes": True}
