from __future__ import annotations

import json
import logging

from core.models import Escalation
from core.task_store import get_store

logger = logging.getLogger(__name__)


def notify_owner(task_id: str, message: str) -> str:
    task = get_store().get_task(task_id)
    if not task:
        return json.dumps({"error": f"Task {task_id} not found"})

    assignee = task.assignee or "unassigned"
    log_msg = f"[NOTIFY] → {assignee} | task {task_id} ({task.title}): {message}"
    logger.info(log_msg)
    print(log_msg)
    return json.dumps({"success": True, "notified": assignee, "task_id": task_id})


def log_escalation(task_id: str, reason: str) -> str:
    task = get_store().get_task(task_id)
    if not task:
        return json.dumps({"error": f"Task {task_id} not found"})

    escalation = Escalation(task_id=task_id, reason=reason)
    get_store().create_escalation(escalation)
    get_store().update_task(task_id, status="escalated", escalation_notes=reason)

    log_msg = f"[ESCALATION] Task {task_id} ({task.title}): {reason}"
    logger.warning(log_msg)
    print(log_msg)
    return json.dumps({"success": True, "escalation_id": escalation.id})
