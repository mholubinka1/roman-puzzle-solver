# Review Criteria (repo-specific)

Review criteria this repository has accumulated from its own Copilot review rounds.

- The `address-copilot-comments` skill appends a generalised, one-line criterion here for
  every Copilot finding on a PR that resulted in a code change. Findings that were pushed
  back on ("Ignored.") are never recorded — this file only holds criteria the team accepted
  by changing code.
- The `code-review` skill feeds this file to its Standards sub-agent alongside the skill's
  own `REVIEW-CRITERIA.md`, and treats the entries here as documented repo standards (a
  breach may be blocking).
- Prune stale entries, and promote durable ones into a shared criteria file, by hand.

Each entry is a bold label plus a one-line imperative rule, tagged with the PR it came
from — for example:
`- **Partial checks for compound state**: flag a readiness check that inspects one artefact when the state it gates has several parts. (PR #58)`

## Criteria

- **Complete exception taxonomy for input parsers**: when a loader promises to turn every malformed input into one domain error type, check every conversion helper it calls (`int()`, `.upper()`, dict indexing, an enum lookup) and catch the full set each can raise — `AttributeError`, `TypeError`, `KeyError`, `ValueError` — not just the common one. (PR #8)
- **Deterministic collection order**: a function returning a list assembled from a dict, set, or JSON object must impose an explicit sort; output order must not depend on input key or insertion order. (PR #8)
- **Default only on `None`**: substitute a default for an optional argument with `x if x is None else default`, never `x or default` — the latter silently discards a falsy-but-valid value (empty collection, `0`, an object defining `__bool__`/`__len__`). (PR #8)
- **Validate bounded constructor arguments**: a class whose `__init__` stores a numeric or range-limited parameter must reject out-of-range values there with a clear error, even when a CLI or other caller already validates — the class is also constructed directly. (PR #8)
