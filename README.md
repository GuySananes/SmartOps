# SmartOps

> Multi-agent task management powered by Claude — triage, schedule, report, escalate.

[![CI](https://github.com/your-username/smartops/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/smartops/actions/workflows/ci.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)

## What it demonstrates

- **Multi-agent orchestration** — 5 specialized Claude agents, each owning a distinct responsibility
- **Pluggable agent registry** — add or swap agents with a single registry entry; no other files change
- **Versioned prompts with eval-gated CI** — system prompts are committed files; accuracy regressions block merges
- **Claude tool use** — each agent runs a full agentic loop with structured JSON tools
- **Professional documentation** — `CLAUDE.md`, ADRs, onboarding guide, feature index, slash commands

## Architecture

```
User / CLI
     │
     ▼
OrchestratorAgent          ← routes intent, never handles domain logic
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

# 3. Run the full demo
python scripts/run_demo.py
```

The demo seeds 20 realistic tasks and runs the complete agent pipeline: triage → schedule → report → escalate.

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

**Eval-gated CI:** Changes to `agents/` or `.claude/prompts/` trigger eval runs in CI. Accuracy below 90% blocks the merge. This means regressions are caught before they reach main, not after.

**Pluggable registry:** Adding an agent is 5 steps and touches 2 files. Swapping one is 1 line. See `docs/adding-agents.md`.

## Extending SmartOps

See [`docs/adding-agents.md`](docs/adding-agents.md) for a full walkthrough with a concrete example.

## Running Tests

```bash
pytest tests/ -v               # Unit tests (no API calls — agents are mocked)
python -m evals.triage_eval    # Accuracy eval (makes real API calls)
```

## Project Structure

```
smartops/
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
