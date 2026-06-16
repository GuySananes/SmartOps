from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_task_store
from api.schemas import CreateTaskRequest, EscalationResponse, TaskResponse, UpdateTaskRequest
from core.models import Task, TaskStatus
from core.task_store import TaskStore

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    request: CreateTaskRequest,
    store: TaskStore = Depends(get_task_store),
) -> TaskResponse:
    task = Task(
        title=request.title,
        description=request.description,
        status=TaskStatus.PENDING_TRIAGE,
        priority=request.priority,
        category=request.category,
        tags=request.tags,
        estimated_effort=request.estimated_effort,
        deadline=request.deadline,
        assignee=request.assignee,
    )
    store.create_task(task)
    return TaskResponse.model_validate(task)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    store: TaskStore = Depends(get_task_store),
) -> list[TaskResponse]:
    tasks = store.query_tasks(
        status=status,
        priority=priority,
        assignee=assignee,
        date_from=date_from,
        date_to=date_to,
    )
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    store: TaskStore = Depends(get_task_store),
) -> TaskResponse:
    task = store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    request: UpdateTaskRequest,
    store: TaskStore = Depends(get_task_store),
) -> TaskResponse:
    fields = request.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    task = store.update_task(task_id, **fields)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return TaskResponse.model_validate(task)


@router.get("/{task_id}/escalations", response_model=list[EscalationResponse])
def get_task_escalations(
    task_id: str,
    store: TaskStore = Depends(get_task_store),
) -> list[EscalationResponse]:
    if not store.get_task(task_id):
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    escalations = store.get_escalations(task_id=task_id)
    return [
        EscalationResponse(
            id=e.id,
            task_id=e.task_id,
            reason=e.reason,
            created_at=e.created_at,
            notified=e.notified,
        )
        for e in escalations
    ]
