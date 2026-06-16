from __future__ import annotations

import json
from typing import Any

from agents.base_agent import BaseAgent
from tools.notify_tools import log_escalation, notify_owner
from tools.search_tools import check_blocked_tasks, check_overdue_tasks, get_unassigned_p0s


class EscalationAgent(BaseAgent):
    name = "escalation"
    prompt_file = "escalation_v1.md"

    def _get_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "check_overdue_tasks",
                "description": "Find all active tasks that have passed their deadline.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "check_blocked_tasks",
                "description": "Find all tasks with status 'blocked'.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "get_unassigned_p0s",
                "description": "Find P0 priority tasks that have no assignee.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "log_escalation",
                "description": "Record an escalation for a task and mark it as escalated.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "reason": {"type": "string", "description": "Why this task is being escalated"},  # noqa: E501
                    },
                    "required": ["task_id", "reason"],
                },
            },
            {
                "name": "notify_owner",
                "description": "Send a notification to the task's assigned owner.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "message": {"type": "string"},
                    },
                    "required": ["task_id", "message"],
                },
            },
        ]

    def _execute_tool(self, name: str, tool_input: dict[str, Any]) -> str:
        if name == "check_overdue_tasks":
            return check_overdue_tasks()
        if name == "check_blocked_tasks":
            return check_blocked_tasks()
        if name == "get_unassigned_p0s":
            return get_unassigned_p0s()
        if name == "log_escalation":
            return log_escalation(**tool_input)
        if name == "notify_owner":
            return notify_owner(**tool_input)
        return json.dumps({"error": f"Unknown tool: {name}"})
