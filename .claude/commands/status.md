# /status

Print a quick system health summary: task counts by status and priority, plus active blockers.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from core.task_store import get_store
from core.models import TaskStatus
from collections import Counter

store = get_store()
all_tasks = store.query_tasks()

by_status = Counter(t.status.value for t in all_tasks)
by_priority = Counter(t.priority.value for t in all_tasks if t.priority)
blocked = [t for t in all_tasks if t.status.value == "blocked"]
escalated = [t for t in all_tasks if t.status.value == "escalated"]

print("=== SmartOps System Status ===\n")
print(f"Total tasks: {len(all_tasks)}\n")
print("By status:")
for s in TaskStatus:
    count = by_status.get(s.value, 0)
    if count:
        print(f"  {s.value:<20} {count}")
print("\nBy priority:")
for p in ["P0", "P1", "P2", "P3"]:
    count = by_priority.get(p, 0)
    if count:
        print(f"  {p}: {count}")
if blocked:
    print(f"\nBlockers ({len(blocked)}):")
    for t in blocked:
        print(f"  [{t.id}] {t.title} — {t.assignee or 'unassigned'}")
if escalated:
    print(f"\nEscalated ({len(escalated)}):")
    for t in escalated:
        print(f"  [{t.id}] {t.title}")
```
