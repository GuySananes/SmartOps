# Skill: report

**Trigger:** `/report [daily|weekly|sprint]`, direct invocation.

## Purpose
Generate a structured markdown status report from task data for a given time period or sprint.

## Inputs

| Field | Type | Description |
|---|---|---|
| `type` | string | `daily`, `weekly`, or `sprint` |
| `date` | string? | Target date (ISO 8601). Defaults to today. |

## Output

Markdown report with the following sections:
1. **Summary** — 2-3 sentence overview
2. **Completed** — tasks done in the period
3. **In Progress** — active tasks with owners and deadlines
4. **Blockers** — stuck tasks with reasons
5. **Velocity** — completion metrics by team member
6. **Next Priorities** — top 3 upcoming tasks

## Examples

**Input:** `type: "daily"`
**Output:** Markdown daily standup report with today's completions, blockers, and next actions.

**Input:** `type: "sprint"`
**Output:** Full sprint retrospective with velocity chart data, carry-over tasks, and team performance.

## Used by
- `ReporterAgent` (primary)
- `/report` command
