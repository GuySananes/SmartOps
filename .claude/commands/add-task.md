# /add-task [description]

AI-assisted task intake. Takes a natural language description, prompts for missing details, then routes to the triage agent.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

description = "$ARGUMENTS"
if not description:
    description = input("Describe the task: ").strip()

from core.models import Task
from core.task_store import get_store
from agents.triage_agent import TriageAgent

# Create as pending_triage
task = Task(title=description[:80], description=description)
get_store().create_task(task)
print(f"Created task {task.id}. Running triage...\n")

agent = TriageAgent()
result = agent.run(f"Triage the task with id {task.id}: {description}")
print(result)
```
