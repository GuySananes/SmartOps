## What changed

<!-- Summarize the change. What does this PR do and why? -->

## Agent / prompt changes

- [ ] System prompt updated? If yes, which agent and which version?
- [ ] Evals run? Results: **X% → Y%** (paste output of `python -m evals.triage_eval`)

## Testing

- [ ] Unit tests pass: `pytest tests/`
- [ ] Type check passes: `mypy agents/ core/ tools/`
- [ ] Lint passes: `ruff check .`

## Checklist

- [ ] `CLAUDE.md` updated if architecture changed
- [ ] `docs/feature-index.md` updated if new feature added
- [ ] `docs/adding-agents.md` updated if agent pattern changed
- [ ] `.env.example` updated if new env vars added
- [ ] New agent? Registered in `core/agent_registry.py`
