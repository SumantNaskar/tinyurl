from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional

class ShortenRequest(BaseModel):
    long_url: HttpUrl
    custom_alias: Optional[str] = Field(None, min_length=3, max_length=20, pattern="^[a-zA-Z0-9_-]+$")
    expires_in_days: Optional[int] = Field(None, gt=0, le=3650)

class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None

class StatsResponse(BaseModel):
    short_code: str
    long_url: str
    click_count: int
    created_at: datetime
    