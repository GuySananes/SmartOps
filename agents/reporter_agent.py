from __future__ import annotations

import json
from typing import Any

from agents.base_agent import BaseAgent
from tools.search_tools import check_blocked_tasks, compute_velocity
from tools.task_tools import query_tasks


class ReporterAgent(BaseAgent):
    name = "reporter"
    prompt_file = "reporter_v1.md"

    def _get_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "query_tasks",
                "description": "Query tasks with optional filters by status, priority, or date range.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Filter by status (e.g. 'completed', 'in_progress')",
                        },
                        "priority": {"type": "string", "description": "Filter by priority (P0-P3)"},
                        "date_from": {"type": "string", "description": "ISO 8601 start date"},
                        "date_to": {"type": "string", "description": "ISO 8601 end date"},
                    },
                    "required": [],
                },
            },
            {
                "name": "compute_velocity",
                "description": "Compute team velocity: completed task count, by assignee, sprint total.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "get_blocked_tasks",
                "description": "Get all currently blocked tasks.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
        ]

    def _execute_tool(self, name: str, tool_input: dict[str, Any]) -> str:
        if name == "query_tasks":
            return query_tasks(**tool_input)
        if name == "compute_velocity":
            return compute_velocity()
        if name == "get_blocked_tasks":
            return check_blocked_tasks()
        return json.dumps({"error": f"Unknown tool: {name}"})
