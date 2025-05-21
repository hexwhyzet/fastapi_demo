from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.pending
    priority: int = 1


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: int
    created_at: datetime
