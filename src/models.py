from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field


class TaskStatus(str, Enum):
    pending = "в ожидании"
    in_progress = "в работе"
    completed = "завершено"


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
