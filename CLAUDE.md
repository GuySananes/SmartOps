# SmartOps — Codebase Guide

> For Claude and human engineers. This file is the single source of truth for navigating the codebase.

## What This Project Does

SmartOps is a multi-agent task management backend powered by Claude. Five specialized agents — orchestrator, triage, scheduler, reporter, and escalation — each own a distinct responsibility and collaborate through a pluggable registry. The system can ingest raw task descriptions, classify them, assign them to team members, generate status reports, and detect blockers — all autonomously.

## Quick Navigation

| I want to... | Go to |
|---|---|
| See all agents | `agents/` |
| Change an agent's behavior | `.claude/prompts/` |
| Add a new agent | `docs/adding-agents.md` |
| Add or change a tool | `tools/` |
| Run the full demo | `python scripts/run_demo.py` |
| Seed the database | `python scripts/seed_tasks.py` |
| Run unit tests | `pytest tests/` |
| Run evals | `python -m evals.triage_eval --verbose` |
| Use a slash command | `.claude/commands/` |

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

# 3. Run the end-to-end demo
python scripts/run_demo.py

# 4. Or invoke agents individually
python -c "
from agents.triage_agent import TriageAgent
print(TriageAgent().run('Triage all pending tasks'))
"
```

## How to Add a New Agent

Full walkthrough in `docs/adding-agents.md`. Five-step summary:

1. Create `agents/my_agent.py` extending `BaseAgent` — define `_get_tools()` and `_execute_tool()`
2. Add system prompt to `.claude/prompts/my_agent_v1.md`
3. Register in `core/agent_registry.py` inside `_bootstrap()`
4. Write tests in `tests/test_my_agent.py` (mock the Anthropic client)
5. Write evals in `evals/my_agent_eval.py` with fixtures in `evals/fixtures/`

## Key Patterns

**Prompt versioning:** Every agent's system prompt is a versioned file in `.claude/prompts/` (e.g. `triage_v1.md`). Never inline prompts as Python strings. Version bumps go in a new file (`triage_v2.md`) and the `prompt_file` attribute is updated.

**Tool schema:** Tools follow the MCP-style schema that the Anthropic API expects: `name`, `description`, `input_schema`. This makes them self-documenting and testable independently.

**Agentic loop:** `BaseAgent.run()` handles the full tool-use loop. Sub-agents only define their tools and how to execute them — zero boilerplate.

**Shared store:** All tools call `core.task_store.get_store()` — a process-level singleton backed by SQLite. Tests swap it via monkeypatching.

**Thin orchestrator:** The `OrchestratorAgent` has zero domain logic. It routes to sub-agents. This makes every agent independently testable and swappable.

## Testing

```bash
pytest tests/                           # All unit tests (agents are mocked — no API calls)
pytest tests/test_task_store.py -v      # Task store CRUD
pytest tests/test_triage_agent.py -v    # Triage agent with mock responses
```

## Evals

```bash
python -m evals.triage_eval --verbose       # Priority + category accuracy (>90%)
python -m evals.escalation_eval --verbose   # Escalation detection accuracy (>90%)
python -m evals.reporter_eval --verbose     # Report structure validity (>90%)
```

Evals make real API calls. CI blocks merges on agent/prompt changes if any eval regresses below 90%.

## Do Not

- Put domain logic in `orchestrator.py` — that belongs in sub-agents
- Hardcode prompts as Python strings — they go in `.claude/prompts/`
- Merge changes to `agents/` or `.claude/prompts/` without running evals
- Share state between tests — use the `temp_db` fixture from `tests/conftest.py`
