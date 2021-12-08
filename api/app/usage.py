import re
from datetime import datetime

from pydantic import BaseModel, validator


class UsageDetail(BaseModel):
    loc: str
    started_at: datetime
    stopped_at: datetime

    @validator("loc")
    def loc_is_correct_format(cls, v):
        if re.match(r"^(washer|dryer):\d+:\d+$", v) is None:
            raise ValueError("loc format is invalid")
        return v
