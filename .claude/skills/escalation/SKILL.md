# Skill: escalation

**Trigger:** `/escalate`, scheduled cron, or direct invocation.

## Purpose
Detect tasks that need immediate human attention: overdue, blocked, or unowned P0s. Log escalations and notify owners.

## Inputs
None required. Reads from the task store directly.

## Detection criteria

| Condition | Threshold | Action |
|---|---|---|
| Overdue | Past deadline, still active | Log escalation + notify owner |
| Blocked | Status = blocked | Log escalation + notify owner |
| Unassigned P0 | Priority = P0, no assignee | Log escalation + alert team lead |

## Output

```
Escalation run complete.
- Overdue: N tasks escalated
- Blocked: N tasks escalated
- Unassigned P0s: N tasks escalated
Total: N
```

Or if clean: `"No escalations required."`

## Used by
- `EscalationAgent` (primary)
- `/escalate` command
- Cron schedule (see `.github/workflows/evals.yml`)
