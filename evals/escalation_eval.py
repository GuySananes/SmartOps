"""
Eval for EscalationAgent.

Verifies the agent correctly identifies tasks that need escalation
and does not escalate healthy tasks.

Usage:
    python -m evals.escalation_eval
    python -m evals.escalation_eval --verbose
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "escalation_cases.json"
ACCURACY_THRESHOLD = 0.90


def run_eval(verbose: bool = False) -> float:
    import core.task_store as ts_module
    from agents.escalation_agent import EscalationAgent
    from core.models import Priority, Task, TaskStatus
    from core.task_store import TaskStore

    cases = json.loads(FIXTURE_PATH.read_text())

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    original = ts_module._store
    ts_module._store = TaskStore(db_path)

    try:
        store = ts_module.get_store()

        for case in cases:
            t = case["task"]
            deadline = None
            if t.get("deadline_offset_days") is not None:
                deadline = datetime.utcnow() + timedelta(days=t["deadline_offset_days"])
            task = Task(
                id=t["id"],
                title=t["title"],
                description=t["description"],
                priority=Priority(t["priority"]) if t.get("priority") else None,
                status=TaskStatus(t["status"]),
                assignee=t.get("assignee"),
                deadline=deadline,
            )
            store.create_task(task)

        agent = EscalationAgent()
        agent.run(
            "Check all active tasks for overdue deadlines, blocked status, "
            "and unassigned P0s. Log escalations where needed."
        )

        results = []
        for case in cases:
            updated = store.get_task(case["task"]["id"])
            was_escalated = updated and updated.status.value == "escalated"
            expected = case["expected_escalated"]
            passed = bool(was_escalated) == expected

            if verbose:
                label = "PASS" if passed else "FAIL"
                print(
                    f"[{label}] {case['scenario']}: "
                    f"expected_escalated={expected}, got={bool(was_escalated)}"
                )

            results.append({"scenario": case["scenario"], "pass": passed})

    finally:
        ts_module._store = original
        try:
            os.unlink(db_path)
        except OSError:
            pass

    n_pass = sum(r["pass"] for r in results)
    accuracy = n_pass / len(results)
    print(f"\nEscalation eval: {accuracy:.1%} ({n_pass}/{len(results)} passed)")

    assert accuracy >= ACCURACY_THRESHOLD, (
        f"Eval regression: {accuracy:.1%} < {ACCURACY_THRESHOLD:.0%} threshold"
    )
    return accuracy


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    run_eval(verbose=verbose)
