# SmartOps — Codebase Guide

> For Claude and human engineers. This file is the single source of truth for navigating the codebase.

## What This Project Does

SmartOps is a multi-agent task management system powered by Claude. Five specialized agents — orchestrator, triage, scheduler, reporter, and escalation — each own a distinct responsibility and collaborate through a pluggable registry. A FastAPI web layer exposes all functionality as REST endpoints with background job support for long-running agent calls.

## Quick Navigation

| I want to... | Go to |
|---|---|
| Start the API server | `py -m uvicorn api.main:app --reload --port 8000` |
| See all API routes | `http://localhost:8000/docs` |
| See all agents | `agents/` |
| Change an agent's behavior | `.claude/prompts/` |
| Add a new agent | `docs/adding-agents.md` |
| Add or change a tool | `tools/` |
| Add an API endpoint | `api/routers/` |
| Run the CLI demo | `py scripts/run_demo.py` |
| Seed the database | `py scripts/seed_tasks.py` |
| Run unit tests | `py -m pytest tests/` |
| Run evals | `py -m evals.triage_eval --verbose` |
| Use a slash command | `.claude/commands/` |

## API Layer (`api/`)

| File | Purpose |
|---|---|
| `api/main.py` | App factory, lifespan hook (bootstraps registry), CORS, router registration |
| `api/schemas.py` | All HTTP request/response Pydantic models |
| `api/job_store.py` | In-process async job registry for background agent runs |
| `api/dependencies.py` | FastAPI `Depends` wrappers for `get_store()` and `get_job_store()` |
| `api/routers/tasks.py` | `/tasks` — CRUD + escalation history |
| `api/routers/agents.py` | `/agents` — trigger agents + poll job status |
| `api/routers/system.py` | `/system` — health, capacity, sprint, velocity, overdue, blocked |

**Background job pattern:** Agent endpoints return `202` immediately with a `job_id`. The agent runs in a `ThreadPoolExecutor` via `asyncio.run_in_executor()`. Poll `GET /agents/jobs/{job_id}` until `status` is `completed` or `failed`.

**Tool functions return JSON strings** — always `json.loads()` before using in HTTP responses. The `api/routers/` files handle this at the boundary.

## Agent Map

| Agent | File | Responsibility | System Prompt |
|---|---|---|---|
| Orchestrator | `agents/orchestrator.py` | Routes user intent to the right sub-agent | `orchestrator_v1.md` |
| Triage | `agents/triage_agent.py` | Classifies raw tasks (priority, category, tags, effort) | `triage_v1.md` |
| Scheduler | `agents/scheduler_agent.py` | Assigns tasks to team members with deadlines | `scheduler_v1.md` |
| Reporter | `agents/reporter_agent.py` | Generates daily/weekly/sprint status reports | `reporter_v1.md` |
| Escalation | `agents/escalation_agent.py` | Detects overdue, blocked, unassigned P0 tasks | `escalation_v1.md` |

All agents extend `agents/base_agent.py`, which owns the Anthropic tool-use loop.

## How to Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY

# 3. Start the API server
py -m uvicorn api.main:app --reload --port 8000
# Docs at http://localhost:8000/docs

# 4. Or run the CLI demo
py scripts/run_demo.py
```

## How to Add a New Agent

Full walkthrough in `docs/adding-agents.md`. Five-step summary:

1. Create `agents/my_agent.py` extending `BaseAgent` — define `_get_tools()` and `_execute_tool()`
2. Add system prompt to `.claude/prompts/my_agent_v1.md`
3. Register in `core/agent_registry.py` inside `_bootstrap()`
4. Write tests in `tests/test_my_agent.py` (mock the Anthropic client)
5. Write evals in `evals/my_agent_eval.py` with fixtures in `evals/fixtures/`

To expose via HTTP, add a route to `api/routers/agents.py` following the same background-job pattern as the existing five endpoints.

## Key Patterns

**Prompt versioning:** Every agent's system prompt is a versioned file in `.claude/prompts/` (e.g. `triage_v1.md`). Never inline prompts as Python strings. Version bumps go in a new file (`triage_v2.md`) and the `prompt_file` attribute is updated.

**Tool schema:** Tools follow the MCP-style schema that the Anthropic API expects: `name`, `description`, `input_schema`. This makes them self-documenting and testable independently.

**Agentic loop:** `BaseAgent.run()` handles the full tool-use loop. Sub-agents only define their tools and how to execute them — zero boilerplate.

**Shared store:** All tools call `core.task_store.get_store()` — a process-level singleton backed by SQLite. Tests swap it via monkeypatching.

**Thin orchestrator:** The `OrchestratorAgent` has zero domain logic. It routes to sub-agents. This makes every agent independently testable and swappable.

**`POST /tasks` bypasses `tools/task_tools.create_task()`** — that tool hardcodes `status=TRIAGED` (for agent use). The HTTP endpoint constructs `Task` directly with `status=PENDING_TRIAGE`.

## Testing

```bash
py -m pytest tests/                      # All unit tests (agents are mocked — no API calls)
py -m pytest tests/test_task_store.py -v # Task store CRUD
py -m pytest tests/test_triage_agent.py -v # Triage agent with mock responses
```

## Evals

```bash
py -m evals.triage_eval --verbose        # Priority + category accuracy (>90%)
py -m evals.escalation_eval --verbose    # Escalation detection accuracy (>90%)
py -m evals.reporter_eval --verbose      # Report structure validity (>90%)
```

Evals make real API calls. CI blocks merges on agent/prompt changes if any eval regresses below 90%.

## Do Not

- Put domain logic in `orchestrator.py` — that belongs in sub-agents
- Hardcode prompts as Python strings — they go in `.claude/prompts/`
- Merge changes to `agents/` or `.claude/prompts/` without running evals
- Share state between tests — use the `temp_db` fixture from `tests/conftest.py`
- Call tool functions directly in HTTP responses without `json.loads()` first
