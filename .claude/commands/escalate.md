# /escalate

Run the escalation agent: check for overdue, blocked, and unassigned P0 tasks.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from agents.escalation_agent import EscalationAgent

agent = EscalationAgent()
result = agent.run(
    "Check all active tasks for overdue deadlines, blocked status, and unassigned P0s. "
    "Log escalations and notify owners where needed."
)
print(result)
```
