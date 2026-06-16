from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers import agents, system, tasks
from core.agent_registry import _bootstrap

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    _bootstrap()
    logger.info("SmartOps API started — agent registry bootstrapped")
    yield
    logger.info("SmartOps API shutting down")


app = FastAPI(
    title="SmartOps API",
    description=(
        "Multi-agent task management system powered by Claude. "
        "Trigger AI agents via HTTP and poll for results."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(system.router, prefix="/system", tags=["System"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/", include_in_schema=False)
def root() -> dict:
    return {"name": "SmartOps API", "version": "0.1.0", "docs": "/docs"}
