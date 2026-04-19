from dataclasses import dataclass
from datetime import datetime


@dataclass
class Content:
    id: int
    topic: str
    script: str
    status: str
    created_at: datetime
