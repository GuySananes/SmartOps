from __future__ import annotations

from typing import Any

AGENT_REGISTRY: dict[str, type] = {}


def register_agent(name: str, cls: type) -> None:
    AGENT_REGISTRY[name] = cls


def get_agent(name: str) -> Any:
    if name not in AGENT_REGISTRY:
        raise ValueError(
            f"Unknown agent: '{name}'. Available: {list(AGENT_REGISTRY)}"
        )
    return AGENT_REGISTRY[name]()


def list_agents() -> list[dict[str, str]]:
    return [
        {"name": name, "class": cls.__name__}
        for name, cls in AGENT_REGISTRY.items()
    ]


def _bootstrap() -> None:
    """Lazily import and register all agents to avoid circular imports."""
    from agents.escalation_agent import EscalationAgent
    from agents.reporter_agent import ReporterAgent
    from agents.scheduler_agent import SchedulerAgent
    from agents.triage_agent import TriageAgent

    register_agent("triage", TriageAgent)
    register_agent("scheduler", SchedulerAgent)
    register_agent("reporter", ReporterAgent)
    register_agent("escalation", EscalationAgent)
