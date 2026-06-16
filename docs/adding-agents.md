# Adding a New Agent — Step-by-Step Guide

This guide walks through adding a `SummarizerAgent` that generates one-sentence summaries for completed tasks. Use it as a template for any new agent.

---

## Step 1: Create the agent file

Create `agents/summarizer_agent.py`:

```python
from __future__ import annotations

import json
from typing import Any

from agents.base_agent import BaseAgent
from tools.task_tools import query_tasks, update_task


class SummarizerAgent(BaseAgent):
    name = "summarizer"
    prompt_file = "summarizer_v1.md"

    def _get_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "get_completed_tasks",
                "description": "Get all completed tasks without a summary.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "add_summary",
                "description": "Add a one-sentence summary to a task.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "summary": {"type": "string"},
                    },
                    "required": ["task_id", "summary"],
                },
            },
        ]

    def _execute_tool(self, name: str, tool_input: dict[str, Any]) -> str:
        if name == "get_completed_tasks":
            return query_tasks(status="completed")
        if name == "add_summary":
            return update_task(tool_input["task_id"], escalation_notes=tool_input["summary"])
        return json.dumps({"error": f"Unknown tool: {name}"})
```

## Step 2: Write the system prompt

Create `.claude/prompts/summarizer_v1.md`:

```markdown
# Summarizer Agent

You summarize completed tasks into one clear sentence for changelog and reporting purposes.

## Workflow
1. Call `get_completed_tasks` to retrieve completed tasks.
2. For each task, write a one-sentence summary of what was accomplished.
3. Call `add_summary` to save the summary.

## Summary format
"[Past-tense verb] [what was done] [impact if notable]."
Examples:
- "Patched XSS vulnerability in the comment field, preventing script injection."
- "Upgraded Node.js from 18 to 20 LTS across all frontend services."
```

## Step 3: Register the agent

In `core/agent_registry.py`, add to `_bootstrap()`:

```python
def _bootstrap() -> None:
    from agents.summarizer_agent import SummarizerAgent
    # ... existing registrations ...
    register_agent("summarizer", SummarizerAgent)
```

## Step 4: Write unit tests

Create `tests/test_summarizer_agent.py`:

```python
from unittest.mock import MagicMock, patch
from core.task_store import TaskStore

def test_summarizer_defines_tools() -> None:
    with patch("anthropic.Anthropic"):
        from agents.summarizer_agent import SummarizerAgent
        agent = SummarizerAgent()
        tool_names = {t["name"] for t in agent._get_tools()}
    assert "get_completed_tasks" in tool_names
    assert "add_summary" in tool_names
```

## Step 5: Write evals

Create `evals/summarizer_eval.py` and `evals/fixtures/summarizer_cases.json`:

```json
[
  {
    "task_title": "Fix XSS in comment field",
    "task_description": "Sanitized HTML in user comments",
    "expected_contains": ["XSS", "comment"]
  }
]
```

## Step 6: Update the docs

- Add a row to the Agent Map table in `CLAUDE.md`
- Add an entry in `docs/feature-index.md`
- Update `agents/orchestrator.py` tool schema to include `"summarizer"` in the `enum`

---

That's it. Six steps, no other files change.
