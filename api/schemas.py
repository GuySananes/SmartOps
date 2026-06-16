from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

from core.models import Priority, TaskStatus


# ---------------------------------------------------------------------------
# Task schemas
# ---------------------------------------------------------------------------

class CreateTaskRequest(BaseModel):
    title: str
    description: str
    priority: Optional[Priority] = None
    category: Optional[str] = None
    tags: list[str] = []
    estimated_effort: Optional[str] = None
    deadline: Optional[datetime] = None
    assignee: Optional[str] = None


class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    estimated_effort: Optional[str] = None
    deadline: Optional[datetime] = None
    assignee: Optional[str] = None
    escalation_notes: Optional[str] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    priority: Optional[Priority]
    status: TaskStatus
    category: Optional[str]
    tags: list[str]
    estimated_effort: Optional[str]
    deadline: Optional[datetime]
    assignee: Optional[str]
    created_at: datetime
    updated_at: datetime
    escalation_notes: Optional[str]


class EscalationResponse(BaseModel):
    id: str
    task_id: str
    reason: str
    created_at: datetime
    notified: bool


# ---------------------------------------------------------------------------
# Agent job schemas
# ---------------------------------------------------------------------------

class AgentJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentJobResponse(BaseModel):
    job_id: str
    agent: str
    status: AgentJobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Agent trigger request schemas
# ---------------------------------------------------------------------------

class TriageRequest(BaseModel):
    instruction: str = "Triage all pending tasks in the system."


class ScheduleRequest(BaseModel):
    instruction: str = (
        "Schedule all triaged tasks that haven't been assigned yet. "
        "Match each task to the best available team member based on role and capacity."
    )


class ReportRequest(BaseModel):
    report_type: Literal["daily", "weekly", "sprint"] = "daily"
    instruction: Optional[str] = None


class EscalateRequest(BaseModel):
    instruction: str = (
        "Check all active tasks for overdue deadlines, blocked status, "
        "and unassigned P0s. Log escalations and notify owners."
    )


class OrchestrateRequest(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# System schemas
# ---------------------------------------------------------------------------

class TeamMemberCapacity(BaseModel):
    name: str
    role: str
    capacity: int
    current_load: int
    available_slots: int


class TeamCapacityResponse(BaseModel):
    members: list[TeamMemberCapacity]
    total_capacity: int
    total_load: int
    total_available: int


class SprintResponse(BaseModel):
    sprint_number: int
    start: str
    end: str
    active_tasks: int
    capacity: int


class VelocityResponse(BaseModel):
    total_completed: int
    by_assignee: dict[str, int]
    sprint_velocity: int


class SystemStatusResponse(BaseModel):
    status: Literal["ok"]
    agent_count: int
    agents: list[str]
    task_counts: dict[str, int]
    db_path: str
