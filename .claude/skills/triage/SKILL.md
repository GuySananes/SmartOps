# Skill: triage

**Trigger:** `/triage`, direct agent invocation, or when raw task descriptions need classification.

## Purpose
Classify a raw task description into a structured Task with priority, category, tags, and effort estimate.

## Inputs

| Field | Type | Description |
|---|---|---|
| `description` | string | Raw task description from user or external system |
| `context` | string? | Additional context (sprint goals, team constraints) |

## Outputs

```json
{
  "title": "Concise task title",
  "priority": "P0 | P1 | P2 | P3",
  "category": "incident | deployment | feature | bug | chore | research",
  "tags": ["tag1", "tag2"],
  "estimated_effort": "2h",
  "deadline_hint": "end of sprint"
}
```

## Examples

**Input:** "prod DB is down, nobody can log in"
**Output:** `{ priority: "P0", category: "incident", tags: ["database", "auth", "production"] }`

**Input:** "update the color of the submit button to match brand guidelines"
**Output:** `{ priority: "P3", category: "chore", tags: ["ui", "design"], estimated_effort: "30m" }`

## Used by
- `TriageAgent` (primary)
- `OrchestratorAgent` (via route_to_agent)
- `/triage` command
- `/add-task` command
