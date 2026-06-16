from __future__ import annotations

import json
from typing import Any

from agents.base_agent import BaseAgent


class OrchestratorAgent(BaseAgent):
    """Entry point. Routes natural language intent to the appropriate sub-agent."""

    name = "orchestrator"
    prompt_file = "orchestrator_v1.md"

    def _get_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "get_agent_registry",
                "description": "List all available sub-agents and their responsibilities.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "route_to_agent",
                "description": "Delegate a task to the appropriate sub-agent.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "enum": ["triage", "scheduler", "reporter", "escalation"],
                            "description": "Which agent to route to",
                        },
                        "payload": {
                            "type": "string",
                            "description": "The full instruction to pass to the sub-agent",
                        },
                    },
                    "required": ["agent_name", "payload"],
                },
            },
        ]

    def _execute_tool(self, name: str, tool_input: dict[str, Any]) -> str:
        from core.agent_registry import _bootstrap, get_agent, list_agents

        _bootstrap()

        if name == "get_agent_registry":
            return json.dumps(list_agents(), indent=2)

        if name == "route_to_agent":
            agent = get_agent(tool_input["agent_name"])
            result = agent.run(tool_input["payload"])
            return json.dumps(
                {"agent": tool_input["agent_name"], "result": result}, indent=2
            )

        return json.dumps({"error": f"Unknown tool: {name}"})
