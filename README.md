# SmartOps

> Multi-agent task management powered by Claude — triage, schedule, report, escalate.

[![CI](https://github.com/GuySananes/SmartOps/actions/workflows/ci.yml/badge.svg)](https://github.com/GuySananes/SmartOps/actions/workflows/ci.yml)
![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue)

## What it demonstrates

- **Multi-agent orchestration** — 5 specialized Claude agents, each owning a distinct responsibility
- **FastAPI web layer** — 18 REST endpoints; agent jobs run in the background with job polling
- **Pluggable agent registry** — add or swap agents with a single registry entry; no other files change
- **Versioned prompts with eval-gated CI** — system prompts are committed files; accuracy regressions block merges
- **Claude tool use** — each agent runs a full agentic loop with structured JSON tools
- **Professional documentation** — `CLAUDE.md`, ADRs, onboarding guide, feature index, slash commands

## Architecture

```
HTTP Client / Browser
        │
        ▼
   FastAPI (api/)              ← 18 REST endpoints, background job queue
        │
        ▼
OrchestratorAgent              ← routes intent, never handles domain logic
        │
        ├── TriageAgent        ← classifies raw tasks (priority, category, tags, effort)
        ├── SchedulerAgent     ← assigns tasks to team members with deadlines
        ├── ReporterAgent      ← generates daily / weekly / sprint reports
        └── EscalationAgent    ← detects overdue, blocked, unassigned P0s
                 │
                 ▼
          Tools (task_tools, notify_tools, search_tools)
                 │
                 ▼
          TaskStore (SQLite)
```

## Quickstart

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# 3a. Start the API server
py -m uvicorn api.main:app --reload --port 8000
# → Interactive docs at http://localhost:8000/docs

# 3b. Or run the CLI demo
py scripts/run_demo.py
```

## API Overview

The REST API is organized into three routers:

### `/tasks` — Task CRUD

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tasks` | Create a task (starts as `pending_triage`) |
| `GET` | `/tasks` | List tasks — filter by `status`, `priority`, `assignee`, date range |
| `GET` | `/tasks/{id}` | Get a task by ID |
| `PATCH` | `/tasks/{id}` | Update any task fields |
| `GET` | `/tasks/{id}/escalations` | Escalation history for a task |

### `/agents` — Trigger AI Agents

All agent endpoints return `202 Accepted` immediately with a `job_id`. Poll `GET /agents/jobs/{job_id}` for the result — agent calls can take 10–60 seconds.

| Method | Endpoint | What runs |
|---|---|---|
| `POST` | `/agents/triage` | Classify all pending tasks |
| `POST` | `/agents/schedule` | Assign triaged tasks to team members |
| `POST` | `/agents/report` | Generate daily / weekly / sprint report |
| `POST` | `/agents/escalate` | Check for overdue, blocked, unassigned P0s |
| `POST` | `/agents/orchestrate` | Free-form message routed to the right agent |
| `GET` | `/agents/jobs/{id}` | Poll job status (`pending` → `running` → `completed`) |
| `GET` | `/agents/jobs` | List all jobs |

### `/system` — Health & Analytics

| Endpoint | Returns |
|---|---|
| `GET /system/status` | Agent count, task breakdown by status, DB path |
| `GET /system/capacity` | Team members with current load and available slots |
| `GET /system/sprint` | Current sprint number, dates, active tasks |
| `GET /system/velocity` | Completed task count by team member |
| `GET /system/overdue` | Tasks past their deadline |
| `GET /system/blocked` | Tasks with blocked status |
| `GET /system/unassigned-p0s` | P0 tasks with no assignee |

## Agent Overview

| Agent | File | Key tools |
|---|---|---|
| Orchestrator | `agents/orchestrator.py` | `route_to_agent`, `get_agent_registry` |
| Triage | `agents/triage_agent.py` | `create_task`, `search_similar_tasks` |
| Scheduler | `agents/scheduler_agent.py` | `assign_task`, `get_team_capacity` |
| Reporter | `agents/reporter_agent.py` | `query_tasks`, `compute_velocity` |
| Escalation | `agents/escalation_agent.py` | `check_overdue_tasks`, `log_escalation` |

## Design Decisions

**Thin orchestrator:** Business logic lives in sub-agents, not in the routing layer. The orchestrator is testable in isolation — it just checks names and passes payloads.

**Prompt versioning:** Every agent's system prompt is a committed file in `.claude/prompts/` (e.g. `triage_v1.md`). Prompts are diffed and reviewed like code. A new version is a new file.

**Eval-gated CI:** Changes to `agents/` or `.claude/prompts/` trigger eval runs in CI. Accuracy below 90% blocks the merge. Regressions are caught before they reach main, not after.

**Async job queue:** Agent calls are LLM-backed and slow. The API returns `202` immediately with a job ID; the agent runs in a thread pool so the event loop is never blocked.

**Pluggable registry:** Adding an agent is 5 steps and touches 2 files. Swapping one is 1 line. See `docs/adding-agents.md`.

## Running Tests

```bash
py -m pytest tests/ -v              # Unit tests (no API calls — agents are mocked)
py -m evals.triage_eval --verbose   # Accuracy eval (makes real API calls)
```

## Project Structure

```
smartops/
├── api/             # FastAPI web layer — routers, schemas, background job store
├── agents/          # One file per agent; base_agent.py owns the tool-use loop
├── core/            # models, task store, config, agent registry
├── tools/           # Task CRUD, notifications, search — callable by any agent
├── evals/           # Accuracy tests with fixture data
├── tests/           # Unit tests (mocked Anthropic client)
├── scripts/         # seed_tasks.py, run_demo.py
├── docs/            # Onboarding, ADRs, feature index, adding agents
├── .claude/
│   ├── commands/    # /triage, /report, /escalate, /status, /add-task
│   ├── prompts/     # Versioned system prompts for each agent
│   └── skills/      # Reusable skill definitions
└── CLAUDE.md        # Codebase guide for Claude and human engineers
```

## Extending SmartOps

See [`docs/adding-agents.md`](docs/adding-agents.md) for a full walkthrough with a concrete example.
