from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class TaskStatus(str, Enum):
    PENDING_TRIAGE = "pending_triage"
    TRIAGED = "triaged"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ESCALATED = "escalated"


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    description: str
    priority: Optional[Priority] = None
    status: TaskStatus = TaskStatus.PENDING_TRIAGE
    category: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    estimated_effort: Optional[str] = None
    deadline: Optional[datetime] = None
    assignee: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    escalation_notes: Optional[str] = None


class Escalation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    task_id: str
    reason: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notified: bool = False


class TeamMember(BaseModel):
    name: str
    role: str
    current_load: int
    capacity: int
    available_slots: int = 0
