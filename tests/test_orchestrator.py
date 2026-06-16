from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

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


def test_orchestrator_defines_routing_tools() -> None:
    with patch("anthropic.Anthropic"):
        from agents.orchestrator import OrchestratorAgent

        agent = OrchestratorAgent()
        tool_names = {t["name"] for t in agent._get_tools()}

    assert "route_to_agent" in tool_names
    assert "get_agent_registry" in tool_names


def test_orchestrator_get_agent_registry() -> None:
    with patch("anthropic.Anthropic"):
        from agents.orchestrator import OrchestratorAgent

        agent = OrchestratorAgent()
        result = json.loads(agent._execute_tool("get_agent_registry", {}))

    agent_names = [a["name"] for a in result]
    assert "triage" in agent_names
    assert "reporter" in agent_names
    assert "escalation" in agent_names
    assert "scheduler" in agent_names


def test_orchestrator_routes_to_triage(temp_db: TaskStore) -> None:
    """Orchestrator should delegate to the triage agent on request."""
    from agents.orchestrator import OrchestratorAgent

    triage_tool_call = _ToolUseBlock(
        "call_1",
        "route_to_agent",
        {"agent_name": "triage", "payload": "Triage all pending tasks"},
    )

    def fake_triage_run(message: str) -> str:
        return "Triaged 0 tasks."

    responses = [
        _Response("tool_use", [triage_tool_call]),
        _Response("end_turn", [_TextBlock("Routing to triage agent done.")]),
    ]

    with (
        patch("anthropic.Anthropic") as mock_anthropic,
        patch("agents.triage_agent.TriageAgent.run", side_effect=fake_triage_run),
    ):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = responses

        agent = OrchestratorAgent()
        result = agent.run("Triage all pending tasks")

    assert "triage" in result.lower() or "Routing" in result
