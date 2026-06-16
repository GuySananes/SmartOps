# Agent Design — Architecture Decision Records

Design decisions behind the SmartOps agent architecture.

---

## ADR-001: Thin Orchestrator Pattern

**Decision:** The `OrchestratorAgent` has zero domain logic. It only routes intent to sub-agents.

**Rationale:** If the orchestrator contained triage or scheduling logic, it would become a bottleneck for changes and untestable as a unit. Keeping it thin means:
- Each sub-agent is independently testable
- Adding a new agent requires no orchestrator changes
- Swapping an agent implementation is a one-line registry change

**Consequence:** The orchestrator prompt must be explicit about routing boundaries. See `orchestrator_v1.md`.

---

## ADR-002: Versioned Prompt Files

**Decision:** All agent system prompts live in `.claude/prompts/` as versioned markdown files (e.g. `triage_v1.md`). Prompts are never hardcoded in Python.

**Rationale:**
- Prompts change frequently. Inline strings make diffs unreadable.
- Versioned files allow `git diff` on prompt changes, the same as code.
- A new version (`triage_v2.md`) can be tested independently before replacing v1.
- Evals can be tied to a specific prompt version.

**Convention:** When a prompt changes significantly, create a new version file and update `prompt_file` in the agent class. Don't edit in place unless the change is trivially safe (typo fix, clarification).

---

## ADR-003: SQLite for the Task Store

**Decision:** Use SQLite via the stdlib `sqlite3` module. No ORM.

**Rationale:**
- Zero external dependencies for the persistence layer
- SQLite files are portable — anyone can inspect `smartops.db` with any SQLite client
- For a demo/interview project, simplicity beats scalability
- The `TaskStore` class abstracts the storage — swapping to Postgres is a matter of replacing `_conn()` and the SQL dialect

**What would change for production:** Replace the `TaskStore` with a Postgres-backed implementation. The tool layer doesn't change; only `core/task_store.py` does.

---

## ADR-004: Eval-Gated CI

**Decision:** CI blocks merges on changes to `agents/` or `.claude/prompts/` if any eval regresses below 90% accuracy.

**Rationale:** LLM behavior is non-deterministic. A prompt change that looks innocuous can break classification accuracy. Evals catch this before it reaches main. The 90% threshold was chosen as a balance between strictness and tolerance for variance.

**Tradeoff:** Evals make real API calls, which costs money and adds ~60s to CI. This is acceptable for a project where agent correctness is the core value.

---

## ADR-005: Pluggable Agent Registry

**Decision:** Agents are registered in a dictionary (`AGENT_REGISTRY`), not wired directly.

**Rationale:**
```python
# Adding an agent = one line
register_agent("summarizer", SummarizerAgent)
```

No other files change. The orchestrator looks up agents by name at runtime. This makes the system open to extension without modification — a direct application of the Open/Closed Principle.

**Lazy bootstrap:** The registry is populated via `_bootstrap()` inside the orchestrator's tool execution, not at import time. This avoids circular imports between the orchestrator and sub-agents.

---

## ADR-006: Tool Schema Follows MCP Convention

**Decision:** Tools are defined with `name`, `description`, and `input_schema` — the same structure used by the MCP (Model Context Protocol) standard.

**Rationale:**
- Consistent with the broader Claude ecosystem
- Self-documenting: the schema doubles as API documentation
- Future migration to actual MCP servers requires only moving function bodies, not restructuring schemas

---

## ADR-007: Tests Mock the Anthropic Client

**Decision:** Unit tests patch `anthropic.Anthropic` and provide canned `_Response` objects. No API calls in the test suite.

**Rationale:**
- Tests must be fast, free, and deterministic
- Real API calls belong in evals, which are run on a separate CI job
- The mock pattern tests the tool-call dispatch and tool execution logic — which is the actually risky code

**What the tests don't cover:** Whether Claude's actual responses are sensible. That's what evals are for.
