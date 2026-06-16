# Onboarding — SmartOps

Get from zero to a running demo in under 10 minutes.

## Prerequisites

- Python 3.11+
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

### 3. Run the demo

```bash
python scripts/run_demo.py
```

This seeds the database with 20 realistic tasks and runs the full agent pipeline: triage → schedule → report → escalate. You'll see each agent's output in your terminal.

### 4. Try the slash commands

If you're using Claude Code:
```
/triage          — classify all pending tasks
/report daily    — generate today's status report
/escalate        — check for overdue and blocked tasks
/status          — quick system health summary
```

## Key concepts

### Agents
Each agent is a Python class in `agents/`. It has a system prompt (in `.claude/prompts/`), a set of tools, and an agentic loop that calls Claude until the task is complete. Read `CLAUDE.md` for the agent map.

### Tools
Tools are functions in `tools/` that agents call during their loop. They interact with the task store, notify owners, or query team capacity. Each tool returns a JSON string.

### Task store
SQLite database (`smartops.db`) managed by `core/task_store.py`. All tools access it through `get_store()`, a process-level singleton.

### Evals
Accuracy tests that make real API calls to verify agent behavior. Run them before merging prompt or agent changes:
```bash
python -m evals.triage_eval --verbose
```

## Next steps

- Read `docs/agent-design.md` for the architectural decisions behind the system
- Read `docs/adding-agents.md` to add a new agent to the system
- Run the unit tests: `pytest tests/ -v`
