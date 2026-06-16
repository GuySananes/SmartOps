# Onboarding — SmartOps

Get from zero to a running API in under 10 minutes.

## Prerequisites

- Python 3.9+
- An Anthropic API key ([get one here](https://console.anthropic.com))
- pip

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

For development (lint, type check, tests):
```bash
pip install -r requirements-dev.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your `ANTHROPIC_API_KEY`. The other defaults are fine for local development.

### 3. Start the API server

```bash
py -m uvicorn api.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** — you'll see the full interactive API with all 18 endpoints. You can create tasks, trigger agents, and poll for results directly from the browser.

### 4. Seed the database (optional, for a realistic demo state)

```bash
py scripts/seed_tasks.py
```

This creates 20 realistic tasks in various states (pending, triaged, scheduled, blocked, completed).

### 5. Try the CLI demo

```bash
py scripts/run_demo.py
```

Seeds the DB and runs the full agent pipeline: triage → schedule → report → escalate. Good for seeing all agents fire in sequence with real output.

### 6. Try the slash commands (Claude Code only)

```
/triage          — classify all pending tasks
/report daily    — generate today's status report
/escalate        — check for overdue and blocked tasks
/status          — quick system health summary
```

---

## Key concepts

### Agents
Each agent is a Python class in `agents/`. It has a system prompt (in `.claude/prompts/`), a set of tools, and an agentic loop that calls Claude until the task is complete. Read `CLAUDE.md` for the full agent map.

### Tools
Functions in `tools/` that agents call during their loop. They interact with the task store, notify owners, or query team capacity. Each returns a JSON string.

### Task store
SQLite database (`smartops.db`) managed by `core/task_store.py`. All tools access it through `get_store()`, a process-level singleton.

### API layer
FastAPI app in `api/`. Agent-trigger endpoints (`POST /agents/*`) return `202 Accepted` immediately with a `job_id`. The agent runs in the background — poll `GET /agents/jobs/{job_id}` until `status` is `completed`.

### Evals
Accuracy tests that make real API calls to verify agent behavior. Run them before merging prompt or agent changes:
```bash
py -m evals.triage_eval --verbose
```

---

## Next steps

- Read `docs/agent-design.md` for the architectural decisions behind the system
- Read `docs/adding-agents.md` to add a new agent to the system
- Read `docs/api.md` for the full tool-layer API reference
- Run the unit tests: `py -m pytest tests/ -v`
