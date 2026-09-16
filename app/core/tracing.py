"""
Request-scoped trace IDs for end-to-end log correlation.

Every log line carries a `trace_id` (injected via a log-record factory), so all
logs for one request can be filtered by that id.

The trace-id STRUCTURE lives here in code — intentionally NOT in settings/env —
so its shape is a code-level decision. Change `generate_trace_id()` (or the
constants it uses) to alter the format anytime; nothing else needs to change.
"""
import contextvars
import logging
import secrets
import time
from typing import Optional

# ── Trace-ID structure (edit freely) ───────────────────────────────────────
TRACE_ID_PREFIX = "TONIK"          # leading tag
TRACE_ID_TIME_FMT = "%Y%m%d%H%M%S"  # timestamp component
TRACE_ID_RAND_BYTES = 4             # -> 8 hex chars of randomness


def generate_trace_id() -> str:
    """
    Build a fresh trace id. This is the single place that defines the format —
    e.g. 'TONIK-20260916T... '. Change the pieces above or the f-string below to
    restructure the id; callers never assume a particular shape.
    """
    ts = time.strftime(TRACE_ID_TIME_FMT)
    rand = secrets.token_hex(TRACE_ID_RAND_BYTES)
    return f"{TRACE_ID_PREFIX}-{ts}-{rand}"


# ── Context propagation ─────────────────────────────────────────────────────
_TRACE_ID: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")


def set_trace_id(trace_id: str) -> str:
    _TRACE_ID.set(trace_id or "-")
    return _TRACE_ID.get()


def get_trace_id() -> str:
    return _TRACE_ID.get()


def resolve_trace_id(incoming: Optional[str]) -> str:
    """Use an upstream-provided id (cross-service correlation) or mint a new one."""
    trace_id = incoming.strip() if incoming and incoming.strip() else generate_trace_id()
    return set_trace_id(trace_id)


def bind_trace_id_from_state(state) -> str:
    """
    Re-bind the trace id inside a graph node. LangGraph may run sync nodes in a
    worker thread where the request's context var isn't set, so each node
    re-binds from the trace id carried in the graph state.
    """
    trace_id = "-"
    try:
        trace_id = state.get("trace_id") or "-"
    except AttributeError:
        pass
    return set_trace_id(trace_id)


# ── Logging integration ─────────────────────────────────────────────────────
def install_log_record_factory() -> None:
    """Make every LogRecord carry the current trace id as `record.trace_id`."""
    base_factory = logging.getLogRecordFactory()

    def factory(*args, **kwargs):
        record = base_factory(*args, **kwargs)
        record.trace_id = get_trace_id()
        return record

    logging.setLogRecordFactory(factory)
