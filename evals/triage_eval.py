"""
Eval for TriageAgent.

Measures priority and category accuracy against fixture cases.
Makes real API calls — run before merging changes to agents/ or .claude/prompts/.

Usage:
    python -m evals.triage_eval
    python -m evals.triage_eval --verbose
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "triage_cases.json"
ACCURACY_THRESHOLD = 0.90


def run_eval(verbose: bool = False) -> float:
    import core.task_store as ts_module
    from agents.triage_agent import TriageAgent
    from core.models import Task
    from core.task_store import TaskStore

    cases = json.loads(FIXTURE_PATH.read_text())

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    original = ts_module._store
    ts_module._store = TaskStore(db_path)

    try:
        store = ts_module.get_store()
        task_id_to_case: dict[str, dict] = {}

        for i, case in enumerate(cases):
            task = Task(
                id=f"eval{i:03d}",
                title=case["input_title"],
                description=case["input_description"],
            )
            store.create_task(task)
            task_id_to_case[task.id] = case

        agent = TriageAgent()
        agent.run("Triage all pending tasks in the system.")

        results = []
        for tid, case in task_id_to_case.items():
            updated = store.get_task(tid)
            if not updated:
                passed = False
                got_priority, got_category = None, None
            else:
                p_match = (
                    updated.priority is not None
                    and updated.priority.value == case["expected_priority"]
                )
                c_match = updated.category == case["expected_category"]
                passed = p_match and c_match
                got_priority = updated.priority.value if updated.priority else None
                got_category = updated.category

            if verbose:
                status = "PASS" if passed else "FAIL"
                print(f"[{status}] {case['input_title'][:55]}")
                if not passed:
                    print(
                        f"       priority: expected={case['expected_priority']}, got={got_priority}"
                    )
                    print(
                        f"       category: expected={case['expected_category']}, got={got_category}"
                    )

            results.append({"input": case["input_title"], "pass": passed})

    finally:
        ts_module._store = original
        try:
            os.unlink(db_path)
        except OSError:
            pass

    n_pass = sum(r["pass"] for r in results)
    accuracy = n_pass / len(results)
    print(f"\nTriage eval: {accuracy:.1%} ({n_pass}/{len(results)} passed)")

    assert accuracy >= ACCURACY_THRESHOLD, (
        f"Eval regression: {accuracy:.1%} < {ACCURACY_THRESHOLD:.0%} threshold"
    )
    return accuracy


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    run_eval(verbose=verbose)
