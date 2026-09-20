from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReminderCreate(BaseModel):
    title: str
    description: str | None = None
    due_at: datetime


class ReminderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    due_at: datetime
    status: str
    next_call_at: datetime
    attempts: int
    created_at: datetime