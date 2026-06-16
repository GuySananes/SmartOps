from __future__ import annotations

import json
from typing import Any

from agents.base_agent import BaseAgent
from tools.search_tools import get_team_capacity
from tools.task_tools import assign_task, get_task, query_tasks


class SchedulerAgent(BaseAgent):
    name = "scheduler"
    prompt_file = "scheduler_v1.md"

    def _get_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "get_triaged_tasks",
                "description": "Get all tasks with status 'triaged' that are ready to be scheduled.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "get_task",
                "description": "Get full details for a specific task by ID.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                    },
                    "required": ["task_id"],
                },
            },
            {
                "name": "get_team_capacity",
                "description": "Get all team members with their current task load and available slots.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "assign_task",
                "description": "Assign a task to a team member with a concrete deadline.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "assignee": {
                            "type": "string",
                            "description": "Full name of the team member (e.g. 'Alice Chen')",
                        },
                        "deadline": {
                            "type": "string",
                            "description": "ISO 8601 deadline (e.g. '2026-06-20T17:00:00')",
                        },
                    },
                    "required": ["task_id", "assignee", "deadline"],
                },
            },
        ]

    def _execute_tool(self, name: str, tool_input: dict[str, Any]) -> str:
        if name == "get_triaged_tasks":
            return query_tasks(status="triaged")
        if name == "get_task":
            return get_task(tool_input["task_id"])
        if name == "get_team_capacity":
            return get_team_capacity()
        if name == "assign_task":
            return assign_task(**tool_input)
        return json.dumps({"error": f"Unknown tool: {name}"})
