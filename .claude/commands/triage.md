# /triage

Classify all tasks currently in `pending_triage` status.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from agents.triage_agent import TriageAgent

agent = TriageAgent()
result = agent.run("Triage all pending tasks in the system.")
print(result)
```
