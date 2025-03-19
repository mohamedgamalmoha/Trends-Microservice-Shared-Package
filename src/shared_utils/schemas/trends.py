import enum
from datetime import datetime
from typing import List, Dict, Optional, Any

import pydantic

from shared_utils.schemas import TaskStatus


class PropertyEnum(enum.Enum):
    WEB_SEARCH = "web"
    YOUTUBE_SEARCH = "youtube"
    NEWS_SEARCH = "news"
    IMAGE_SEARCH = "images"
    FROOGLE_SEARCH = "froogle"


class TrendsQuery(pydantic.BaseModel):
    q: str | List[str] = pydantic.Field(description="Search term(s) or topic(s). Can be a single string or a list of strings.")
    geo: Optional[str] = pydantic.Field(default="Worldwide", description="Geographical region (e.g., 'US', 'DE', 'Worldwide').")
    time: Optional[str] = pydantic.Field(default=None, description="Time range (e.g., 'now 7-d', '2023-01-01 2023-01-31').")
    cat: Optional[int] = pydantic.Field(default=0, description="Category ID (e.g., 0 for all categories, 7 for Arts & Entertainment).")
    gprop: Optional[PropertyEnum] = pydantic.Field(default=None, description="Google property (Web Search, YouTube Search, Image Search).")
    tz: Optional[int] = pydantic.Field(default=0, description="Time zone offset in minutes.")


class TaskRetrieve(pydantic.BaseModel):
    task_id: str
    user_id: int
    status: TaskStatus
    request_data: Optional[TrendsQuery] = None
    schedule_at: datetime
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes=True
