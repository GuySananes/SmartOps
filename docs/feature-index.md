# Feature Index

Every feature in SmartOps, alphabetically indexed. Useful for navigating the codebase quickly.

---

## A

**Agent registry** — `core/agent_registry.py`
Pluggable dictionary mapping agent names to classes. Add an agent by calling `register_agent()`. The orchestrator looks agents up at runtime via `get_agent()`.

**Agent system prompts** — `.claude/prompts/`
Versioned markdown files controlling each agent's behavior. One file per agent per version (e.g. `triage_v1.md`). Loaded at agent init from disk.

**Assign task** — `tools/task_tools.py:assign_task()`
Marks a task as `scheduled`, sets the assignee and deadline. Called by the Scheduler Agent.

## C

**Commands (slash)** — `.claude/commands/`
Runnable Claude Code slash commands. Each file is a markdown prompt with executable Python. Available: `/triage`, `/report`, `/escalate`, `/status`, `/add-task`.

**Config** — `core/config.py`
Loads `ANTHROPIC_API_KEY`, `DATABASE_PATH`, `MODEL_ID`, `LOG_LEVEL` from `.env`.

**Create task** — `tools/task_tools.py:create_task()`
Inserts a triaged task into the store. Called by the Triage Agent after classification.

## E

**Escalation agent** — `agents/escalation_agent.py`
Detects overdue, blocked, and unassigned P0 tasks. Logs escalations via `tools/notify_tools.py`. Designed to run on a cron schedule.

**Evals** — `evals/`
Accuracy tests against fixture data. Each eval makes real API calls. CI blocks merges on agent/prompt changes if accuracy < 90%.

## L

**Log escalation** — `tools/notify_tools.py:log_escalation()`
Records an `Escalation` in the DB and marks the task as `escalated`.

## M

**Models** — `core/models.py`
Pydantic v2 models: `Task`, `TaskStatus`, `Priority`, `Escalation`, `TeamMember`.

## N

**Notify owner** — `tools/notify_tools.py:notify_owner()`
Prints a notification message to stdout and logs it. (Replace with email/Slack in production.)

## O

**Orchestrator agent** — `agents/orchestrator.py`
Entry point. Receives natural language intent and routes to the correct sub-agent. Intentionally thin — no domain logic.

## P

**Prompts** — `.claude/prompts/`
See: Agent system prompts

## Q

**Query tasks** — `tools/task_tools.py:query_tasks()`
Filters tasks by status, priority, assignee, or date range. Used by Reporter and Escalation agents.

## R

**Reporter agent** — `agents/reporter_agent.py`
Generates `daily`, `weekly`, or `sprint` status reports from task data. Includes velocity metrics and blocker summaries.

## S

**Scheduler agent** — `agents/scheduler_agent.py`
Assigns triaged tasks to team members. Matches by role and available capacity. Sets deadlines based on priority.

**Seed tasks** — `scripts/seed_tasks.py`
Populates the DB with 20 realistic tasks in various states for demo and eval use.

**Skills** — `.claude/skills/`
Reusable reasoning modules: `triage`, `report`, `escalation`. Each has a `SKILL.md` defining inputs, outputs, and examples.

**Search similar tasks** — `tools/search_tools.py:search_similar_tasks()`
Text search across task titles, descriptions, and tags. Used by Triage Agent to detect duplicates.

## T

**Task store** — `core/task_store.py`
SQLite-backed persistence. Singleton accessed via `get_store()`. Tables: `tasks`, `escalations`.

**Team capacity** — `tools/search_tools.py:get_team_capacity()`
Returns team members with their current task load and available slots.

**Triage agent** — `agents/triage_agent.py`
Classifies raw task descriptions into structured tasks with priority, category, tags, and effort estimate.

## V

**Velocity** — `tools/search_tools.py:compute_velocity()`
Counts completed tasks, by assignee. Used by Reporter Agent for sprint metrics.
