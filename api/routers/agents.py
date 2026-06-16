from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from agents.escalation_agent import EscalationAgent
from agents.orchestrator import OrchestratorAgent
from agents.reporter_agent import ReporterAgent
from agents.scheduler_agent import SchedulerAgent
from agents.triage_agent import TriageAgent
from api.dependencies import get_job_store
from api.job_store import JobStore
from api.schemas import (
    AgentJobResponse,
    AgentJobStatus,
    EscalateRequest,
    OrchestrateRequest,
    ReportRequest,
    ScheduleRequest,
    TriageRequest,
)

router = APIRouter()

_executor = ThreadPoolExecutor(max_workers=4)


async def _run_agent_job(
    job_id: str,
    agent_cls: type,
    instruction: str,
    job_store: JobStore,
) -> None:
    await job_store.update(job_id, status=AgentJobStatus.RUNNING)
    try:
        loop = asyncio.get_event_loop()
        agent = agent_cls()
        result: str = await loop.run_in_executor(_executor, agent.run, instruction)
        await job_store.update(
            job_id,
            status=AgentJobStatus.COMPLETED,
            result=result,
            completed_at=datetime.utcnow(),
        )
    except Exception as exc:
        await job_store.update(
            job_id,
            status=AgentJobStatus.FAILED,
            error=str(exc),
            completed_at=datetime.utcnow(),
        )


@router.post("/triage", response_model=AgentJobResponse, status_code=202)
async def trigger_triage(
    request: TriageRequest,
    background_tasks: BackgroundTasks,
    job_store: JobStore = Depends(get_job_store),
) -> AgentJobResponse:
    job = await job_store.create("triage")
    background_tasks.add_task(
        _run_agent_job, job.job_id, TriageAgent, request.instruction, job_store
    )
    return job


@router.post("/schedule", response_model=AgentJobResponse, status_code=202)
async def trigger_schedule(
    request: ScheduleRequest,
    background_tasks: BackgroundTasks,
    job_store: JobStore = Depends(get_job_store),
) -> AgentJobResponse:
    job = await job_store.create("scheduler")
    background_tasks.add_task(
        _run_agent_job, job.job_id, SchedulerAgent, request.instruction, job_store
    )
    return job


@router.post("/report", response_model=AgentJobResponse, status_code=202)
async def trigger_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    job_store: JobStore = Depends(get_job_store),
) -> AgentJobResponse:
    instruction = request.instruction or f"Generate a {request.report_type} status report."
    job = await job_store.create("reporter")
    background_tasks.add_task(
        _run_agent_job, job.job_id, ReporterAgent, instruction, job_store
    )
    return job


@router.post("/escalate", response_model=AgentJobResponse, status_code=202)
async def trigger_escalate(
    request: EscalateRequest,
    background_tasks: BackgroundTasks,
    job_store: JobStore = Depends(get_job_store),
) -> AgentJobResponse:
    job = await job_store.create("escalation")
    background_tasks.add_task(
        _run_agent_job, job.job_id, EscalationAgent, request.instruction, job_store
    )
    return job


@router.post("/orchestrate", response_model=AgentJobResponse, status_code=202)
async def trigger_orchestrate(
    request: OrchestrateRequest,
    background_tasks: BackgroundTasks,
    job_store: JobStore = Depends(get_job_store),
) -> AgentJobResponse:
    job = await job_store.create("orchestrator")
    background_tasks.add_task(
        _run_agent_job, job.job_id, OrchestratorAgent, request.message, job_store
    )
    return job


@router.get("/jobs", response_model=list[AgentJobResponse])
def list_jobs(
    job_store: JobStore = Depends(get_job_store),
) -> list[AgentJobResponse]:
    return job_store.all()


@router.get("/jobs/{job_id}", response_model=AgentJobResponse)
async def get_job(
    job_id: str,
    job_store: JobStore = Depends(get_job_store),
) -> AgentJobResponse:
    job = await job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return job
