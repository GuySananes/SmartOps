from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from core.models import Priority, Task, TaskStatus
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


def test_scheduler_agent_defines_required_tools() -> None:
    with patch("anthropic.Anthropic"):
        from agents.scheduler_agent import SchedulerAgent

        agent = SchedulerAgent()
        tool_names = {t["name"] for t in agent._get_tools()}

    assert "get_triaged_tasks" in tool_names
    assert "get_team_capacity" in tool_names
    assert "assign_task" in tool_names


def test_scheduler_assigns_task(
    temp_db: TaskStore, sample_triaged_task: Task
) -> None:
    """SchedulerAgent should assign a triaged task to a team member."""
    from agents.scheduler_agent import SchedulerAgent

    tool_call = _ToolUseBlock(
        "call_1",
        "assign_task",
        {
            "task_id": sample_triaged_task.id,
            "assignee": "Alice Chen",
            "deadline": "2026-06-20T17:00:00",
        },
    )
    responses = [
        _Response("tool_use", [tool_call]),
        _Response("end_turn", [_TextBlock("Scheduled 1 task.")]),
    ]

    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = responses

        agent = SchedulerAgent()
        agent.run("Schedule all triaged tasks")

    updated = temp_db.get_task(sample_triaged_task.id)
    assert updated is not None
    assert updated.assignee == "Alice Chen"
    assert updated.status == TaskStatus.SCHEDULED


def test_get_team_capacity_returns_all_members(temp_db: TaskStore) -> None:
    with patch("anthropic.Anthropic"):
        from agents.scheduler_agent import SchedulerAgent

        agent = SchedulerAgent()
        result = json.loads(agent._execute_tool("get_team_capacity", {}))

    assert len(result) == 5
    names = [m["name"] for m in result]
    assert "Alice Chen" in names
    assert "Carol Kim" in names
