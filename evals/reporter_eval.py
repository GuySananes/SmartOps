"""
Eval for ReporterAgent.

Checks that generated reports contain the required sections
and basic structural validity.

Usage:
    python -m evals.reporter_eval
    python -m evals.reporter_eval --verbose
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "reporter_cases.json"
ACCURACY_THRESHOLD = 0.90


def run_eval(verbose: bool = False) -> float:
    import core.task_store as ts_module
    from agents.reporter_agent import ReporterAgent
    from core.task_store import TaskStore
    from scripts.seed_tasks import SEED_TASKS

    cases = json.loads(FIXTURE_PATH.read_text())

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    original = ts_module._store
    ts_module._store = TaskStore(db_path)

    try:
        store = ts_module.get_store()
        for task in SEED_TASKS:
            store.create_task(task)

        agent = ReporterAgent()
        results = []

        for case in cases:
            report = agent.run(case["prompt"])

            section_hits = sum(1 for s in case["expected_sections"] if s in report)
            keyword_hits = sum(1 for k in case["expected_contains"] if k in report)
            passed = (
                section_hits == len(case["expected_sections"])
                and keyword_hits == len(case["expected_contains"])
            )

            if verbose:
                label = "PASS" if passed else "FAIL"
                print(f"[{label}] {case['scenario']}")
                if not passed:
                    missing_sections = [
                        s for s in case["expected_sections"] if s not in report
                    ]
                    missing_keywords = [
                        k for k in case["expected_contains"] if k not in report
                    ]
                    if missing_sections:
                        print(f"       Missing sections: {missing_sections}")
                    if missing_keywords:
                        print(f"       Missing keywords: {missing_keywords}")

            results.append({"scenario": case["scenario"], "pass": passed})

    finally:
        ts_module._store = original
        try:
            os.unlink(db_path)
        except OSError:
            pass

    n_pass = sum(r["pass"] for r in results)
    accuracy = n_pass / len(results)
    print(f"\nReporter eval: {accuracy:.1%} ({n_pass}/{len(results)} passed)")

    assert accuracy >= ACCURACY_THRESHOLD, (
        f"Eval regression: {accuracy:.1%} < {ACCURACY_THRESHOLD:.0%} threshold"
    )
    return accuracy


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    run_eval(verbose=verbose)
