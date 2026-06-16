from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from core.models import Task, TaskStatus
from core.task_store import TaskStore


class _TextBlock:
    def __init__(self, text: str) -> None:
        self.text = text
        self.type = "text"


class _ToolUseBlock:
    def __init__(self, tool_id: str, name: str, input_data: dict) -> None:
        self.id = tool_id
        self.name = name
        self.input = input_data
        self.type = "tool_use"


class _Response:
    def __init__(self, stop_reason: str, content: list) -> None:
        self.stop_reason = stop_reason
        self.content = content


def test_triage_agent_defines_required_tools() -> None:
    with patch("anthropic.Anthropic"):
        from agents.triage_agent import TriageAgent

        agent = TriageAgent()
        tool_names = {t["name"] for t in agent._get_tools()}

    assert "create_task" in tool_names
    assert "get_pending_tasks" in tool_names
    assert "search_similar_tasks" in tool_names
    assert "get_open_sprint" in tool_names


def test_triage_agent_loads_prompt() -> None:
    with patch("anthropic.Anthropic"):
        from agents.triage_agent import TriageAgent

        agent = TriageAgent()

    assert len(agent.system_prompt) > 0


def test_triage_agent_create_task_tool(
    temp_db: TaskStore, sample_pending_task: Task
) -> None:
    """TriageAgent should call create_task and persist the classified task."""
    from agents.triage_agent import TriageAgent

    tool_call = _ToolUseBlock(
        "call_1",
        "create_task",
        {
            "title": "Fix login bug",
            "description": "Mobile Safari login fails",
            "priority": "P1",
            "category": "bug",
            "tags": ["auth", "mobile"],
            "estimated_effort": "2h",
        },
    )
    responses = [
        _Response("tool_use", [tool_call]),
        _Response("end_turn", [_TextBlock("Triaged 1 task: P1 bug.")]),
    ]

    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = responses

        agent = TriageAgent()
        result = agent.run("Triage all pending tasks")

    triaged = temp_db.query_tasks(status="triaged")
    assert len(triaged) == 1
    assert triaged[0].priority is not None
    assert triaged[0].priority.value == "P1"
    assert triaged[0].category == "bug"
    assert "Triaged 1 task" in result


def test_triage_agent_search_similar_tasks_tool(temp_db: TaskStore) -> None:
    """search_similar_tasks tool should return matching tasks from the store."""
    from agents.triage_agent import TriageAgent

    existing = Task(
        title="Fix auth bug",
        description="Users can't log in",
        status=TaskStatus.TRIAGED,
    )
    temp_db.create_task(existing)

    with patch("anthropic.Anthropic"):
        agent = TriageAgent()
        result_json = agent._execute_tool("search_similar_tasks", {"query": "auth"})

    results = json.loads(result_json)
    assert len(results) >= 1
    assert any("auth" in r["title"].lower() for r in results)
