---
title: "MCP Live Trace Capture — Design Decisions"
status: Final
closes_issue: 509
date: 2026-03-29
branch: feat/sprint-21-mcp-trace
recommendations:
  - id: rec-mcp-live-trace-design-001
    title: "ADOPT queue.Queue background writer for non-blocking JSONL append"
    status: accepted-for-adoption
    linked_issue: 509
  - id: rec-mcp-live-trace-design-002
    title: "Archive synthetic records to tool_calls.synthetic.bak.jsonl before enabling live capture"
    status: accepted-for-adoption
    linked_issue: 509
  - id: rec-mcp-live-trace-design-003
    title: "Add timestamp_utc, error_type, source fields to every live trace record"
    status: accepted-for-adoption
    linked_issue: 509
  - id: rec-mcp-live-trace-design-004
    title: "Omit quality fields from live trace records — not applicable at per-invocation level"
    status: accepted-for-adoption
    linked_issue: 509
  - id: rec-mcp-live-trace-design-005
    title: "Start with unbounded append; document 50 MB rotation trigger in capture_mcp_metrics.py docstring"
    status: accepted-for-adoption
    linked_issue: 509
  - id: rec-mcp-live-trace-design-006
    title: "Update data/mcp-metrics-schema.yml to add per_record_jsonl section for live-record fields"
    status: accepted-for-adoption
    linked_issue: 509
  - id: rec-mcp-live-trace-design-007
    title: "ADOPT importlib.metadata + branch counter for tool_version in live records"
    status: accepted-for-adoption
    linked_issue: 509
---

# MCP Live Trace Capture — Design Decisions

## Executive Summary

The `_run_with_mcp_telemetry()` function in `mcp_server/dogma_server.py` is the confirmed
single injection point for live JSONL trace capture: all 12 MCP tools already route through
it, it already measures wall-clock latency and catches exceptions, and adding JSONL append
there requires no per-tool changes. The four design questions resolve as follows: **ADOPT a
`queue.Queue` background writer** for atomicity (same pattern as Python's `QueueHandler`
and OTel's `BatchSpanProcessor`); **ADOPT archival of synthetic records** to a `.bak.jsonl`
file and start a fresh baseline (the rolling `window_calls=100` reader makes natural aging
insufficient for a clean Phase 2 baseline without the marker field overhead); **ADOPT
unbounded append** for rotation (the reader's window already caps meaningful data and `.cache/`
is gitignored); and **ADOPT a `"source": "live"` marker with quality fields omitted** from
live records (`mcp-metrics-schema.yml` `required: true` constraints apply to aggregated
`measurement_surfaces` outputs, not to individual JSONL rows).

---

## Injection Point

`_run_with_mcp_telemetry(tool_name, call)` at `mcp_server/dogma_server.py` lines 100–131 is
the correct and only place to inject JSONL append. Evidence:

- Every `@mcp.tool()` decorator wraps its implementation with a call to this function via a
  lambda (e.g. `lambda: _validate_agent_file(file_path)`).
- The function already captures `started = time.perf_counter()`, computes `duration_s`,
  sets OTel error attributes, and records the histogram — the latency and error values
  needed for each JSONL record are already present as local variables.
- Both branches (with OTel tracer and without) converge on `finally:` blocks that report
  duration, so a JSONL append in the same `finally:` block will capture every call regardless
  of OTel availability.
- Injecting into individual tool functions instead would require 12 separate edits and would
  miss any future tool additions.

**Caveat**: The `_run_with_mcp_telemetry` tracer branch raises exceptions after the `finally:`
block rather than swallowing them. The JSONL writer must not add latency to this hot path —
confirmed reason to use the queue strategy (Q1).

---

## Q1 — Atomicity Approach

**Verdict: ADOPT `queue.Queue` + background writer thread (option c).**

### Rationale

Three options were evaluated:

| Option | Thread-safe | Cross-platform | Hot-path latency | Crash safety |
|--------|------------|---------------|-----------------|--------------|
| `open('a')` inline | ❌ (interleaved bytes possible) | ✅ | Adds file I/O on every call | Partial lines possible |
| `fcntl.flock` | ✅ (multi-process) | ❌ (Unix only) | Blocking syscall on contention | Good |
| `queue.Queue` + background thread | ✅ (stdlib GIL-protected put) | ✅ | O(1) enqueue only | Power-loss risk; acceptable |

The stdlib `queue.Queue` is the exact pattern used by:
- `logging.handlers.QueueHandler` / `QueueListener` — the Python stdlib's own production
  solution for thread-safe log file writing (docs.python.org/3/library/logging.handlers.html).
  `QueueHandler.enqueue()` calls `queue.put_nowait()` from the hot path; a background
  `QueueListener` drains to the file handler.
- OTel `BatchSpanProcessor` — Python OTel SDK uses an internal `queue.SimpleQueue` and a
  background thread to batch-drain to `SpanExporter.export()`. The `on_end()` callback
  (called on the tool-execution thread) only does `queue.put_nowait()`.

Windows lacks `fcntl` entirely (`AttributeError` at import time), making option (b) a
hard blocker for cross-platform use. The MCP server already runs on macOS and will run
on Windows dev machines.

For a local-dev telemetry JSONL file (not a financial ledger), the residual risk of
losing in-flight records on a kill-9 is acceptable. The `queue.Queue` approach uses
`queue.put_nowait()` to stay non-blocking on the hot path; the background thread performs
actual `f.write()` + `f.flush()` in a daemon thread.

**Canonical example**:

```python
# At module level in dogma_server.py — initialised once on server start
import queue, threading, json, pathlib
from datetime import UTC, datetime

_JSONL_QUEUE: queue.Queue = queue.Queue(maxsize=0)   # unbounded
_JSONL_PATH = pathlib.Path(".cache/mcp-metrics/tool_calls.jsonl")

def _jsonl_writer() -> None:
    """Background daemon: drain queue → append to JSONL file."""
    _JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    while True:
        record = _JSONL_QUEUE.get()
        if record is None:          # sentinel — shut down
            break
        try:
            with _JSONL_PATH.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            pass                    # local telemetry; swallow write errors

_writer_thread = threading.Thread(target=_jsonl_writer, daemon=True, name="mcp-jsonl-writer")
_writer_thread.start()

# Inside _run_with_mcp_telemetry, in both finally: blocks:
_JSONL_QUEUE.put_nowait({
    "tool_name": tool_name,
    "timestamp_utc": datetime.now(UTC).isoformat(),
    "latency_ms": round(duration_s * 1000, 3),
    "is_error": is_error,
    "error_type": error_type,   # None if no error
    "source": "live",
})
```

**Anti-pattern**: Calling `open().write()` directly inside `_run_with_mcp_telemetry` for
every tool invocation — this adds file-system I/O to the hot path, blocks concurrent MCP
sessions on file lock contention, and produces partial JSONL lines if the process is
interrupted mid-write on non-atomic OS file-append operations (Linux `O_APPEND` is atomic
only for writes ≤ `PIPE_BUF`; Python `json.dumps()` of a typical record exceeds 512 bytes).

---

## Q2 — Data Transition Strategy

**Verdict: ADOPT archival to `.synthetic.bak.jsonl` and start a fresh `tool_calls.jsonl`
(option b).**

### Rationale

`capture_mcp_metrics.py` uses a rolling window via `tool_obs = tool_obs[-window_calls:]`
(default `window_calls=100`). With 800 synthetic records (100 per tool across 8 canonical
tools), synthetic records would be naturally aged out once 100 live records per tool
accumulate. However:

1. **Baseline skew during ramp-up**: Until each tool accrues 100+ live records, aggregated
   metrics (P95 latency, error rate, faithfulness) will be averaged against synthetic values
   that have known artificial distributions (uniform random in the seed script). A `latency_ms`
   of 938 ms for `check_substrate` in the synthetic data will inflate P95 until real data
   dominates. This makes Phase 2 dashboard graphs untrustworthy for the entire ramp-up
   period.
2. **Source field overhead**: Adding `"source": "live"` / `"source": "synthetic"` to the
   schema and filtering by it in `capture_mcp_metrics.py` adds complexity to every downstream
   consumer. It's more encoding than the problem warrants.
3. **Prometheus precedent**: Prometheus' own instrumentation docs recommend against mixing
   historical synthetic baselines with live counters — the resulting time series produces
   misleading rate calculations across the transition boundary. The clean pattern is a fresh
   scrape target.

Archiving to `.cache/mcp-metrics/tool_calls.synthetic.bak.jsonl` preserves the synthetic
seed data for regression reference without polluting the live ingestion path. The archive
file is also gitignored, so it costs nothing in repository terms.

**Canonical example**:

```bash
# One-time migration before Phase 2 instrumentation is enabled
mv .cache/mcp-metrics/tool_calls.jsonl \
   .cache/mcp-metrics/tool_calls.synthetic.bak.jsonl
touch .cache/mcp-metrics/tool_calls.jsonl
# Verify
wc -l .cache/mcp-metrics/tool_calls.jsonl   # → 0
```

**Anti-pattern**: Deleting the synthetic records by running `rm tool_calls.jsonl` and
recreating an empty file without preserving the bak copy. If the Phase 2 implementation
reveals a regression in quality metrics, having the synthetic baseline available as a
reference prevents having to re-run the seed script. Always archive, never discard.

**Anti-pattern**: Keeping both synthetic and live records in the same file and relying on
the `window_calls=100` rolling window to age out synthetics. With 8 tools × 100 records
= 800 synthetic entries, a tool that receives only 10 live calls will still be dominated
by synthetic data in its 100-record window. Dashboard graphs will silently misrepresent
real latencies for low-traffic tools.

---

## Q3 — File Rotation Policy

**Verdict: ADOPT unbounded append for initial implementation (option d), with a documented
trigger condition for adding size-based rotation.**

### Rationale

The effective disk growth rate for `tool_calls.jsonl` with live traces is bounded:

- Each live record is approximately 180–250 bytes (no quality fields, just `tool_name`,
  `timestamp_utc`, `latency_ms`, `is_error`, `error_type`, `source`).
- An MCP server handling 100 tool calls/day generates ~22 KB/day, reaching 10 MB after
  ~450 days.
- `capture_mcp_metrics.py` only reads the last `window_calls=100` records per tool — so
  at any point, only 800 lines (8 tools × 100 calls) actually matter for metric
  computation. The rest is archival history useful for debugging.

`.cache/` is gitignored and not committed, so file size does not affect repository weight.

The Python stdlib `RotatingFileHandler` supports size-based rotation with named backup
files (`app.log`, `app.log.1`, `app.log.2`, …). For a local dev system with `window_calls=100`,
this overhead is not yet warranted. The `TimedRotatingFileHandler` (daily rotation) would
split records mid-window and complicate the path computation in `capture_mcp_metrics.py`
which currently expects a single file path argument.

**Canonical example** (rotation pattern to adopt if file exceeds 50 MB):

```python
# Future drop-in: replace the inline open() in _jsonl_writer with:
from logging.handlers import RotatingFileHandler

_handler = RotatingFileHandler(
    _JSONL_PATH, mode="a", maxBytes=50 * 1024 * 1024,
    backupCount=3, encoding="utf-8"
)

def _jsonl_writer() -> None:
    while True:
        record = _JSONL_QUEUE.get()
        if record is None:
            break
        _handler.stream.write(json.dumps(record) + "\n")
        _handler.stream.flush()
        _handler.doRollover() if _handler.shouldRollover(record) else None
```

**Trigger condition for rotation adoption**: Add `RotatingFileHandler` when
`.cache/mcp-metrics/tool_calls.jsonl` exceeds 50 MB, or when the MCP server is deployed
in a CI/CD context where multiple agents interact concurrently and the 100-call window
per tool turns over faster than once per hour.

---

## Q4 — Quality Metrics Schema for Live Records

**Verdict: ADOPT `"source": "live"` marker with quality fields omitted from live trace
records (option c).**

### Rationale

The `mcp-metrics-schema.yml` `required: true` constraints for quality fields
(`faithfulness`, `answer_relevance`, `context_precision`, etc.) appear **only** under
the `measurement_surfaces` section — which defines the schema for *aggregated output
JSON artifacts* produced by `capture_mcp_metrics.py`, not for individual JSONL rows.

The per-record section is `measurement_record`, and every field there is
`required: false`. The per-record JSONL rows are observation inputs; the aggregated
artifacts are the governed outputs. Including quality fields as `null` in every live
trace record would:

1. Double record size with no downstream benefit (`capture_mcp_metrics.py` uses
   `r.get("faithfulness")` which already handles `None` and absent keys identically).
2. Create a semantic mismatch — a live MCP trace does not have an evaluated faithfulness
   score; `null` signals "was measured but absent" whereas the correct meaning is
   "not applicable to this record type".
3. Pollute future evaluation runs that distinguish live-plus-evaluation records from
   pure latency/error traces.

OTel's log data model (OTLP spec) is instructive here: optional fields that are not
applicable to a specific observation type are omitted rather than set to `null` —
`Attributes` are sparse by design precisely to avoid semantic inflation of inapplicable
fields (opentelemetry.io/docs/specs/otel/logs/data-model).

JSON Schema's own type specification distinguishes `null` (field present with null value,
meaning "measured but missing") from absent (field not present, meaning "not applicable").
For live trace records, absence is the correct semantic (json-schema.org/understanding-json-schema/reference/type.html).

**Canonical example** — live trace record shape:

```json
{
  "tool_name": "check_substrate",
  "timestamp_utc": "2026-03-29T14:32:01.123456+00:00",
  "latency_ms": 412.7,
  "is_error": false,
  "error_type": null,
  "source": "live"
}
```

**Schema contract update required**: `data/mcp-metrics-schema.yml` should add a
`per_record_jsonl` section that explicitly marks `timestamp_utc`, `tool_name`,
`latency_ms`, `is_error`, and `source` as required for live records, while marking
quality fields as `required: false, applicable_to: ["evaluation"]`. This separates the
per-record governance constraint from the aggregated surface constraint.

---

## 2. Hypothesis Validation

The central hypothesis entering Phase 1 was: **a single injection point exists in `dogma_server.py` that can capture all tool calls without per-tool changes, and a non-blocking writer can be added without impacting tool response latency.**

| Hypothesis | Verdict | Evidence |
|------------|---------|----------|
| Single injection point exists (`_run_with_mcp_telemetry`) | ✅ Confirmed | All 12 tools route through this function; latency and error state already captured as local variables |
| Non-blocking write is achievable | ✅ Confirmed | `queue.Queue.put_nowait()` is O(1) and GIL-protected; background thread handles all file I/O |
| Synthetic records can be cleanly separated from live | ✅ Confirmed | Archive strategy eliminates mixed-baseline skew; rolling window would not age synthetics fast enough for low-traffic tools |
| Quality fields safe to omit from live records | ✅ Confirmed | `mcp-metrics-schema.yml` `required: true` constraints apply only to `measurement_surfaces` (aggregated outputs), not `measurement_record` (JSONL rows) |
| Unbounded append is safe for local dev | ✅ Confirmed | ~22 KB/day at 100 calls/day; reader already caps at `window_calls=100`; `.cache/` is gitignored |

---

## 3. Pattern Catalog

**Canonical example — Queue-based background writer (Q1)**:

```python
import queue, threading, json, pathlib
from datetime import UTC, datetime

_JSONL_QUEUE: queue.Queue = queue.Queue(maxsize=0)
_JSONL_PATH = pathlib.Path(".cache/mcp-metrics/tool_calls.jsonl")

def _jsonl_writer() -> None:
    _JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    while True:
        record = _JSONL_QUEUE.get()
        if record is None:
            break
        try:
            with _JSONL_PATH.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            pass  # local telemetry; swallow write errors

_writer_thread = threading.Thread(
    target=_jsonl_writer, daemon=True, name="mcp-jsonl-writer"
)
_writer_thread.start()
```

**Anti-pattern — inline file write on hot path**:
Calling `open().write()` inside `_run_with_mcp_telemetry` directly adds file I/O to every
tool invocation, blocks concurrent sessions, and risks partial JSONL lines on process
interruption (Python `json.dumps()` output typically exceeds 512 bytes — above Linux
`O_APPEND` atomicity guarantee).

**Canonical example — archive migration (Q2)**:

```bash
mv .cache/mcp-metrics/tool_calls.jsonl \
   .cache/mcp-metrics/tool_calls.synthetic.bak.jsonl
touch .cache/mcp-metrics/tool_calls.jsonl
```

**Anti-pattern — relying on rolling window to age out synthetics**:
With 8 tools × 100 synthetic records each, a tool receiving only 10 live calls still
has 90 synthetic rows in its 100-record window, producing misleading P95 and error-rate
figures on the dashboard during the entire ramp-up period.

**Canonical example — live record shape (Q4 + R7)**:

```json
{
  "tool_name": "check_substrate",
  "timestamp_utc": "2026-03-29T14:32:01.123456+00:00",
  "latency_ms": 412.7,
  "is_error": false,
  "error_type": null,
  "source": "live",
  "tool_version": "0.1.0.0"
}
```

`tool_version` format: `{importlib.metadata.version('dogma-governance')}.{BRANCH_COUNTER}` where
`BRANCH_COUNTER` is a module-level constant in `mcp_server/_version.py`, starting at `0` on every
branch from main, incremented manually when tool behaviour changes mid-branch, and reset to `0`
on merge. This gives per-release correlation (first 3 digits) and per-branch-change correlation
(last digit) without requiring a separate versioning system.

---

## Recommendations

1. **ADOPT queue.Queue background writer** — inject a `_JSONL_QUEUE.put_nowait(record)`
   call into both `finally:` blocks of `_run_with_mcp_telemetry()`. Start the daemon
   writer thread once at module load. This is the Phase 2 implementation entry point.

2. **Archive synthetic records before enabling live capture** — run
   `mv .cache/mcp-metrics/tool_calls.jsonl .cache/mcp-metrics/tool_calls.synthetic.bak.jsonl`
   as a one-time migration step in the Phase 2 setup script. Do not delete the original.

3. **Add the three missing fields** to every live trace record:
   `timestamp_utc` (ISO-8601 UTC), `error_type` (string or null), and `source: "live"`.
   These fields are present in `mcp-metrics-schema.yml` identity section as required.

4. **Omit quality fields from live trace records** — they are not applicable at the
   per-invocation level. `capture_mcp_metrics.py` already handles absent quality fields
   safely via `r.get("faithfulness")`.

5. **Start with unbounded append** for rotation — document the 50 MB trigger condition
   in `scripts/capture_mcp_metrics.py` docstring as a follow-up item.

6. **Update `data/mcp-metrics-schema.yml`** to add a `per_record_jsonl` section that
   formalises the live-record shape and explicitly annotates quality fields as
   `applicable_to: ["evaluation"]` only.

7. **ADOPT `tool_version` field** in live records using `importlib.metadata` + branch counter.
   Create `mcp_server/_version.py` with a single `BRANCH_COUNTER: int = 0` constant.
   In `dogma_server.py` at module load: `_TOOL_VERSION = f"{importlib.metadata.version('dogma-governance')}.{BRANCH_COUNTER}"`.
   Convention: increment `BRANCH_COUNTER` when tool behaviour changes mid-branch; reset to `0`
   before merging to main. A pre-push hook warns when `BRANCH_COUNTER != 0` on a merge-to-main
   push. This is the field that lets the dashboard correlate latency/error shifts with specific
   code changes — it answers "which version of `check_substrate` produced these metrics?".

---

## Sources

| URL | Description |
|-----|-------------|
| https://docs.python.org/3/library/queue.html | Python stdlib `queue.Queue` — thread-safe FIFO, used by logging.QueueHandler and OTel BatchSpanProcessor |
| https://docs.python.org/3/library/logging.handlers.html#logging.handlers.RotatingFileHandler | Python stdlib RotatingFileHandler — size-based log rotation with named backup sequence; reference pattern for unbounded-to-rotation upgrade path |
| https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.export.html | OTel Python SDK BatchSpanProcessor — canonical queue+background-thread telemetry export pattern |
| https://opentelemetry.io/docs/specs/otel/logs/data-model/ | OTLP Log Data Model — optional fields are omitted, not null; `Attributes` are sparse by design |
| https://prometheus.io/docs/practices/instrumentation/ | Prometheus instrumentation practices — advises against mixing synthetic and live counter series across a transition boundary |
| https://jsonlines.org/ | JSONL spec — each line is a valid JSON value; UTF-8 required; no guidance on nullable vs absent (absence is semantically distinct, defer to JSON Schema) |
| https://json-schema.org/understanding-json-schema/reference/type.html | JSON Schema type reference — `null` (field present, value null) vs absent field have distinct semantics; absence = "not applicable" |
| mcp_server/dogma_server.py | Endogenous — `_run_with_mcp_telemetry()` implementation confirming injection point and existing latency/error capture |
| scripts/capture_mcp_metrics.py | Endogenous — `window_calls=100` rolling window and `.get("faithfulness")` safe-access pattern confirming Q2 and Q4 design |
| data/mcp-metrics-schema.yml | Endogenous — `measurement_surfaces` (aggregated, quality required) vs `measurement_record` (per-record, all fields optional); confirms Q4 verdict |
