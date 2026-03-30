"""Contract tests for browser MCP inspector source.

Why contract tests instead of runtime unit tests:
- The browser inspector server lives in TypeScript under web/src/lib.
- The repository test harness is Python-first and does not ship a JS/TS test runner.
- These tests enforce the public tool surface and safety contracts from source text.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.io

REPO_ROOT = Path(__file__).resolve().parent.parent
BROWSER_SERVER_PATH = REPO_ROOT / "web" / "src" / "lib" / "mcp-server.ts"

EXPECTED_TOOLS = {
    "ping",
    "query_dom",
    "get_console_logs",
    "get_component_state",
    "trigger_action",
}


def _source() -> str:
    return BROWSER_SERVER_PATH.read_text(encoding="utf-8")


def test_browser_mcp_server_source_exists() -> None:
    assert BROWSER_SERVER_PATH.exists()


def test_registers_expected_tool_set() -> None:
    source = _source()
    registered = set(re.findall(r"registerTool\('([^']+)'", source))
    assert registered == EXPECTED_TOOLS


def test_exposes_calltool_overloads_for_all_tools() -> None:
    source = _source()

    for tool_name in EXPECTED_TOOLS:
        # Overload signatures may wrap lines, so match name declarations flexibly.
        pattern = rf"async\s+callTool\(\s*name:\s*'{tool_name}'"
        assert re.search(pattern, source)


def test_ping_and_handshake_contracts_remain_present() -> None:
    source = _source()

    assert "registerTool('ping', async () => ({ status: 'ok' }))" in source
    assert "this.endpoint = options.endpoint ?? 'http://localhost:8000/mcp';" in source
    assert "fetch(`${this.endpoint}/handshake`" in source


def test_browser_bridge_contracts_remain_present() -> None:
    source = _source()

    assert "fetch(`${this.endpoint}/browser/session`" in source
    assert "`${this.endpoint}/browser/poll?session_id=${encodeURIComponent(sessionId)}`" in source
    assert "fetch(`${this.endpoint}/browser/respond`" in source
    assert "sessionId: this.bridgeSessionId" in source
    assert "requestId: request.requestId" in source
    assert "signal.removeEventListener('abort', onAbort)" in source


def test_sse_transport_probe_is_opt_in() -> None:
    source = _source()

    assert "this.enableSseProbe = options.enableSseProbe ?? false;" in source
    assert "if (!this.enableSseProbe) return;" in source
    assert "new EventSource(`${this.endpoint}/events`)" in source


def test_selector_and_input_safety_limits_are_encoded() -> None:
    source = _source()

    assert "const MAX_SELECTOR_LENGTH = 256;" in source
    assert "const MAX_QUERY_RESULTS = 100;" in source
    assert "const MAX_INPUT_VALUE_LENGTH = 5000;" in source
    assert "selector contains invalid control characters" in source
    assert "invalid CSS selector" in source
