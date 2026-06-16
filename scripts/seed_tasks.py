"""Seed the SmartOps database with realistic demo tasks."""
from __future__ import annotations

import sqlite3
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import Priority, Task, TaskStatus

_now = datetime.utcnow

SEED_TASKS = [
    # --- Pending triage (for the triage agent to process) ---
    Task(
        id="t001",
        title="Users cannot reset password via email",
        description=(
            "Multiple users reporting that the password reset email is not arriving. "
            "Affects both Gmail and corporate email domains. Started ~2 hours ago."
        ),
        status=TaskStatus.PENDING_TRIAGE,
        created_at=_now() - timedelta(hours=2),
        updated_at=_now() - timedelta(hours=2),
    ),
    Task(
        id="t002",
        title="Add CSV export to the analytics dashboard",
        description=(
            "Product request: users want to download their analytics data as CSV. "
            "Should cover last 30 days of metrics. Low-priority feature."
        ),
        status=TaskStatus.PENDING_TRIAGE,
        created_at=_now() - timedelta(hours=5),
        updated_at=_now() - timedelta(hours=5),
    ),
    Task(
        id="t003",
        title="Deploy auth service v2.1 to staging by Thursday",
        description=(
            "New auth service with OAuth2 improvements needs to be deployed to staging "
            "before the Friday demo. Requires a DB migration."
        ),
        status=TaskStatus.PENDING_TRIAGE,
        created_at=_now() - timedelta(hours=3),
        updated_at=_now() - timedelta(hours=3),
    ),
    Task(
        id="t004",
        title="Update API documentation for v3 endpoints",
        description=(
            "The v3 API was released last week but docs haven't been updated. "
            "Need to document all new endpoints with examples."
        ),
        status=TaskStatus.PENDING_TRIAGE,
        created_at=_now() - timedelta(hours=8),
        updated_at=_now() - timedelta(hours=8),
    ),
    Task(
        id="t005",
        title="Payment gateway returning 500 errors intermittently",
        description=(
            "Stripe webhook processing is failing ~15% of the time. "
            "We're losing payment confirmations. Started 30 min ago. Revenue impact confirmed."
        ),
        status=TaskStatus.PENDING_TRIAGE,
        created_at=_now() - timedelta(minutes=30),
        updated_at=_now() - timedelta(minutes=30),
    ),
    # --- Triaged (ready for scheduling) ---
    Task(
        id="t006",
        title="Migrate user table to new schema",
        description="Schema migration for users table to add soft-delete and audit fields.",
        priority=Priority.P1,
        status=TaskStatus.TRIAGED,
        category="deployment",
        tags=["database", "migration", "users"],
        estimated_effort="4h",
        deadline=_now() + timedelta(days=2),
        created_at=_now() - timedelta(days=1),
        updated_at=_now() - timedelta(hours=1),
    ),
    Task(
        id="t007",
        title="Add rate limiting to public API",
        description="Implement per-IP and per-key rate limiting on all public API endpoints.",
        priority=Priority.P2,
        status=TaskStatus.TRIAGED,
        category="feature",
        tags=["api", "security", "rate-limiting"],
        estimated_effort="1d",
        created_at=_now() - timedelta(days=2),
        updated_at=_now() - timedelta(hours=2),
    ),
    Task(
        id="t008",
        title="Fix broken search pagination",
        description="Search results page 2+ returning 0 results due to offset calculation bug.",
        priority=Priority.P1,
        status=TaskStatus.TRIAGED,
        category="bug",
        tags=["search", "pagination", "frontend"],
        estimated_effort="2h",
        created_at=_now() - timedelta(hours=6),
        updated_at=_now() - timedelta(hours=1),
    ),
    # --- Scheduled ---
    Task(
        id="t009",
        title="Upgrade Node.js from 18 to 20 LTS",
        description="EOL upgrade across all frontend services.",
        priority=Priority.P2,
        status=TaskStatus.SCHEDULED,
        category="chore",
        tags=["nodejs", "upgrade", "frontend"],
        estimated_effort="3h",
        assignee="Bob Martinez",
        deadline=_now() + timedelta(days=5),
        created_at=_now() - timedelta(days=4),
        updated_at=_now() - timedelta(hours=3),
    ),
    Task(
        id="t010",
        title="Set up staging environment monitoring",
        description="Add Datadog monitors for staging to catch regressions before prod.",
        priority=Priority.P2,
        status=TaskStatus.SCHEDULED,
        category="chore",
        tags=["monitoring", "staging", "devops"],
        estimated_effort="4h",
        assignee="Carol Kim",
        deadline=_now() + timedelta(days=3),
        created_at=_now() - timedelta(days=2),
        updated_at=_now() - timedelta(hours=4),
    ),
    # --- In progress ---
    Task(
        id="t011",
        title="Refactor authentication middleware",
        description="Extract auth logic into reusable middleware. Duplicated across 12 routes.",
        priority=Priority.P2,
        status=TaskStatus.IN_PROGRESS,
        category="chore",
        tags=["auth", "refactor", "backend"],
        estimated_effort="3h",
        assignee="Alice Chen",
        deadline=_now() + timedelta(days=1),
        created_at=_now() - timedelta(days=3),
        updated_at=_now() - timedelta(hours=1),
    ),
    Task(
        id="t012",
        title="Build in-app notification service",
        description="In-app notifications with read/unread state and email fallback.",
        priority=Priority.P1,
        status=TaskStatus.IN_PROGRESS,
        category="feature",
        tags=["notifications", "email", "backend"],
        estimated_effort="3d",
        assignee="David Okafor",
        deadline=_now() + timedelta(days=4),
        created_at=_now() - timedelta(days=6),
        updated_at=_now() - timedelta(hours=2),
    ),
    Task(
        id="t013",
        title="Write integration tests for checkout flow",
        description="End-to-end tests from add-to-cart through payment confirmation.",
        priority=Priority.P1,
        status=TaskStatus.IN_PROGRESS,
        category="chore",
        tags=["testing", "checkout", "e2e"],
        estimated_effort="2d",
        assignee="Eva Petrov",
        deadline=_now() + timedelta(days=2),
        created_at=_now() - timedelta(days=4),
        updated_at=_now() - timedelta(hours=3),
    ),
    # --- Blocked (will trigger escalation) ---
    Task(
        id="t014",
        title="Deploy recommendation engine",
        description="ML-powered product recommendations. Blocked on data team providing training dataset.",  # noqa: E501
        priority=Priority.P1,
        status=TaskStatus.BLOCKED,
        category="deployment",
        tags=["ml", "recommendations", "data"],
        estimated_effort="2d",
        assignee="Alice Chen",
        deadline=_now() - timedelta(days=1),  # OVERDUE
        created_at=_now() - timedelta(days=7),
        updated_at=_now() - timedelta(days=2),
        escalation_notes="Waiting on data team for training dataset",
    ),
    Task(
        id="t015",
        title="GDPR compliance audit",
        description="Quarterly GDPR audit blocked on legal team reviewing data retention policy.",
        priority=Priority.P1,
        status=TaskStatus.BLOCKED,
        category="chore",
        tags=["gdpr", "compliance", "legal"],
        estimated_effort="3d",
        assignee="Eva Petrov",
        deadline=_now() + timedelta(days=1),
        created_at=_now() - timedelta(days=10),
        updated_at=_now() - timedelta(days=3),
        escalation_notes="Waiting on legal team approval",
    ),
    # --- Completed ---
    Task(
        id="t016",
        title="Fix XSS vulnerability in comment field",
        description="Sanitize HTML in user comments to prevent script injection.",
        priority=Priority.P0,
        status=TaskStatus.COMPLETED,
        category="bug",
        tags=["security", "xss", "frontend"],
        estimated_effort="2h",
        assignee="Alice Chen",
        deadline=_now() - timedelta(days=2),
        created_at=_now() - timedelta(days=3),
        updated_at=_now() - timedelta(days=2),
    ),
    Task(
        id="t017",
        title="Add OpenTelemetry tracing",
        description="Distributed tracing across all microservices.",
        priority=Priority.P2,
        status=TaskStatus.COMPLETED,
        category="chore",
        tags=["observability", "tracing", "devops"],
        estimated_effort="1d",
        assignee="Carol Kim",
        deadline=_now() - timedelta(days=1),
        created_at=_now() - timedelta(days=5),
        updated_at=_now() - timedelta(days=1),
    ),
    Task(
        id="t018",
        title="Launch password strength meter",
        description="Visual password strength indicator on signup and change-password forms.",
        priority=Priority.P2,
        status=TaskStatus.COMPLETED,
        category="feature",
        tags=["auth", "ux", "frontend"],
        estimated_effort="4h",
        assignee="Bob Martinez",
        deadline=_now() - timedelta(days=3),
        created_at=_now() - timedelta(days=6),
        updated_at=_now() - timedelta(days=3),
    ),
    # --- Overdue active tasks (will trigger escalation) ---
    Task(
        id="t019",
        title="Renew SSL certificates",
        description="SSL certs expire in 3 days. Needs renewal across all production services.",
        priority=Priority.P0,
        status=TaskStatus.SCHEDULED,
        category="chore",
        tags=["ssl", "security", "devops", "production"],
        estimated_effort="1h",
        assignee="Carol Kim",
        deadline=_now() - timedelta(hours=12),  # OVERDUE
        created_at=_now() - timedelta(days=2),
        updated_at=_now() - timedelta(days=1),
    ),
    Task(
        id="t020",
        title="Rotate database credentials",
        description="Quarterly security rotation of all DB passwords and API keys.",
        priority=Priority.P1,
        status=TaskStatus.TRIAGED,
        category="chore",
        tags=["security", "database", "credentials"],
        estimated_effort="2h",
        deadline=_now() - timedelta(days=2),  # OVERDUE
        created_at=_now() - timedelta(days=5),
        updated_at=_now() - timedelta(days=3),
    ),
]


def seed() -> None:
    from core.task_store import get_store

    store = get_store()

    # Clear existing data for a fresh demo
    conn = sqlite3.connect(store.db_path)
    conn.execute("DELETE FROM escalations")
    conn.execute("DELETE FROM tasks")
    conn.commit()
    conn.close()

    for task in SEED_TASKS:
        store.create_task(task)


if __name__ == "__main__":
    seed()
    from core.task_store import get_store

    store = get_store()
    tasks = store.query_tasks()
    counts = Counter(t.status.value for t in tasks)
    print(f"Seeded {len(tasks)} tasks:")
    for status, count in sorted(counts.items()):
        print(f"  {status:<22} {count}")
