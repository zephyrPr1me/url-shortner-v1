from datetime import UTC, datetime

from pydantic import BaseModel, Field, HttpUrl


class URLBase(BaseModel):
    target_url: HttpUrl


class URLCreate(URLBase):
    pass


class URLResponse(URLBase):
    short_id: str
    clicks: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {
        "from_attributes": True,
        "ser_json_timedelta": "iso8601",
    }
