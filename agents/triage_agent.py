from __future__ import annotations

import json
from typing import Any

from agents.base_agent import BaseAgent
from tools.search_tools import get_open_sprint, search_similar_tasks
from tools.task_tools import create_task, get_pending_tasks


class TriageAgent(BaseAgent):
    name = "triage"
    prompt_file = "triage_v1.md"

    def _get_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "get_pending_tasks",
                "description": "Retrieve all tasks with status 'pending_triage' that need classification.",  # noqa: E501
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "search_similar_tasks",
                "description": "Search existing tasks by keyword to inform priority and category decisions.",  # noqa: E501
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Keywords to search"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "get_open_sprint",
                "description": "Get the current sprint details to inform deadline hints.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "create_task",
                "description": "Create a classified, structured task from a raw description.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Concise task title"},
                        "description": {"type": "string", "description": "Full description"},
                        "priority": {
                            "type": "string",
                            "enum": ["P0", "P1", "P2", "P3"],
                            "description": "P0=critical incident, P1=high, P2=medium, P3=low",
                        },
                        "category": {
                            "type": "string",
                            "enum": ["incident", "deployment", "feature", "bug", "chore", "research"],  # noqa: E501
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Relevant labels (e.g. auth, mobile, backend)",
                        },
                        "estimated_effort": {
                            "type": "string",
                            "description": "Time estimate: '30m', '2h', '1d', etc.",
                        },
                        "deadline_hint": {
                            "type": "string",
                            "description": "Natural language deadline if mentioned",
                        },
                    },
                    "required": [
                        "title", "description", "priority",
                        "category", "tags", "estimated_effort",
                    ],
                },
            },
        ]

    def _execute_tool(self, name: str, tool_input: dict[str, Any]) -> str:
        if name == "get_pending_tasks":
            return get_pending_tasks()
        if name == "search_similar_tasks":
            return search_similar_tasks(tool_input["query"])
        if name == "get_open_sprint":
            return get_open_sprint()
        if name == "create_task":
            return create_task(**tool_input)
        return json.dumps({"error": f"Unknown tool: {name}"})
