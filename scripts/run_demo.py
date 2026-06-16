"""
SmartOps end-to-end demo.

Demonstrates the full agent pipeline:
  1. Seed the database with 20 realistic tasks
  2. Triage Agent — classify all pending tasks
  3. Scheduler Agent — assign triaged tasks to team members
  4. Reporter Agent — generate daily status report
  5. Escalation Agent — detect overdue, blocked, and unassigned P0s

Usage:
    python scripts/run_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def _header(title: str) -> None:
    print(f"\n{'=' * 62}")
    print(f"  {title}")
    print("=" * 62 + "\n")


def main() -> None:
    _header("STEP 1 — Seeding the database")
    from scripts.seed_tasks import seed

    seed()
    print("Database seeded with 20 realistic tasks.\n")

    from core.task_store import get_store

    store = get_store()
    pending = store.query_tasks(status="pending_triage")
    print(f"  {len(pending)} tasks waiting for triage")

    _header("STEP 2 — Triage Agent: classifying pending tasks")
    from agents.triage_agent import TriageAgent

    triage = TriageAgent()
    result = triage.run(
        "Please triage all pending tasks in the system. "
        "Classify each one with priority, category, tags, and effort estimate."
    )
    print(result)

    _header("STEP 3 — Scheduler Agent: assigning tasks to team")
    from agents.scheduler_agent import SchedulerAgent

    scheduler = SchedulerAgent()
    result = scheduler.run(
        "Schedule all triaged tasks that haven't been assigned yet. "
        "Match each task to the best available team member based on role and capacity."
    )
    print(result)

    _header("STEP 4 — Reporter Agent: generating daily report")
    from agents.reporter_agent import ReporterAgent

    reporter = ReporterAgent()
    result = reporter.run("Generate a daily status report for today.")
    print(result)

    _header("STEP 5 — Escalation Agent: checking for issues")
    from agents.escalation_agent import EscalationAgent

    escalation = EscalationAgent()
    result = escalation.run(
        "Check all active tasks for overdue deadlines, blocked status, "
        "and unassigned P0s. Log escalations and notify owners."
    )
    print(result)

    _header("Demo complete")
    tasks = store.query_tasks()
    from collections import Counter

    counts = Counter(t.status.value for t in tasks)
    print("Final task status breakdown:")
    for status, count in sorted(counts.items()):
        print(f"  {status:<22} {count}")
    print("\nSmartOps pipeline ran successfully.")


if __name__ == "__main__":
    main()
