# /report [daily|weekly|sprint]

Generate a structured status report. Pass the report type as an argument (default: daily).

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

report_type = "$ARGUMENTS" if "$ARGUMENTS" else "daily"

from agents.reporter_agent import ReporterAgent

agent = ReporterAgent()
result = agent.run(f"Generate a {report_type} status report.")
print(result)
```
