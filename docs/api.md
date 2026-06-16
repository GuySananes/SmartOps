# API Reference

SmartOps is a backend library today. This document describes its internal tool API — the interface agents use to interact with the task store and notification layer.

---

## Task Tools (`tools/task_tools.py`)

### `create_task(title, description, priority, category, tags, estimated_effort, deadline_hint?, assignee?)`

Creates a new task with status `triaged`.

| Param | Type | Description |
|---|---|---|
| `title` | str | Concise task title |
| `description` | str | Full task description |
| `priority` | str | `P0` \| `P1` \| `P2` \| `P3` |
| `category` | str | `incident` \| `deployment` \| `feature` \| `bug` \| `chore` \| `research` |
| `tags` | list[str] | Relevant labels |
| `estimated_effort` | str | `30m`, `2h`, `1d`, etc. |
| `deadline_hint` | str? | Natural language hint |
| `assignee` | str? | Team member name |

**Returns:** JSON-serialized `Task`

---

### `get_task(task_id)`

Returns a single task by ID.

**Returns:** JSON-serialized `Task`, or `{"error": "Task X not found"}`

---

### `query_tasks(status?, priority?, assignee?, date_from?, date_to?)`

Returns all tasks matching the given filters. All parameters optional.

**Returns:** JSON array of `Task` objects

---

### `get_pending_tasks()`

Shorthand for `query_tasks(status="pending_triage")`.

---

### `assign_task(task_id, assignee, deadline)`

Assigns a task to a team member and marks it `scheduled`.

| Param | Type | Description |
|---|---|---|
| `task_id` | str | Task to assign |
| `assignee` | str | Team member full name |
| `deadline` | str | ISO 8601 datetime |

**Returns:** `{"success": true, "task": Task}`

---

## Notification Tools (`tools/notify_tools.py`)

### `notify_owner(task_id, message)`

Sends a notification to the task's assigned owner. Currently logs to stdout — replace with email/Slack in production.

### `log_escalation(task_id, reason)`

Records an `Escalation` in the DB and marks the task as `escalated`.

---

## Search Tools (`tools/search_tools.py`)

### `search_similar_tasks(query)`

Full-text search across task titles, descriptions, and tags. Returns up to 5 matches.

### `get_team_capacity()`

Returns all team members with `current_load` and `available_slots`.

### `get_open_sprint()`

Returns current sprint metadata: number, start/end dates, active task count.

### `check_overdue_tasks()`

Returns all active tasks with a deadline in the past.

### `check_blocked_tasks()`

Returns all tasks with `status = blocked`.

### `get_unassigned_p0s()`

Returns P0 tasks with no assignee.

### `compute_velocity()`

Returns completion metrics: total completed, by assignee, sprint velocity.

---

## Data Models (`core/models.py`)

### `Task`

| Field | Type | Notes |
|---|---|---|
| `id` | str | 8-char UUID prefix, auto-generated |
| `title` | str | |
| `description` | str | |
| `priority` | `Priority?` | `P0`–`P3` |
| `status` | `TaskStatus` | Default: `pending_triage` |
| `category` | str? | |
| `tags` | list[str] | |
| `estimated_effort` | str? | |
| `deadline` | datetime? | |
| `assignee` | str? | |
| `created_at` | datetime | |
| `updated_at` | datetime | |
| `escalation_notes` | str? | |

### `TaskStatus` values

`pending_triage` → `triaged` → `scheduled` → `in_progress` → `completed`

Side states: `blocked`, `escalated`
