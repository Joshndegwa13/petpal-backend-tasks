from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TaskCompletionBase(BaseModel):
    task_id: int
    date: datetime

class TaskCompletionCreate(TaskCompletionBase):
    pass

class TaskCompletion(TaskCompletionBase):
    id: int

    class Config:
        from_attributes = True  # Updated line

class TaskBase(BaseModel):
    description: str
    date: Optional[datetime] = None  # Optional for daily tasks
    completed: bool = False
    is_daily: bool = False

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    completions: List[TaskCompletion] = []

    class Config:
        from_attributes = True  # Updated line

class VetVisitBase(BaseModel):
    date: datetime
    notes: str

class VetVisitCreate(VetVisitBase):
    pass

class VetVisit(VetVisitBase):
    id: int

    class Config:
        from_attributes = True  # Updated line
