"""tests/test_mcp_detect_interrupt.py — Unit tests for detect_user_interrupt().

All tests are pure in-memory; no disk I/O is performed.
"""

from mcp_server.tools.scratchpad import detect_user_interrupt


def test_stop_exact():
    result = detect_user_interrupt("STOP")
    assert result["interrupted"] is True
    assert result["signal"] == "STOP"
    assert result["ok"] is True
    assert result["errors"] == []


def test_do_not_continue():
    result = detect_user_interrupt("do not continue this task")
    assert result["interrupted"] is True
    assert result["signal"] == "DO NOT CONTINUE"


def test_abort_in_sentence():
    result = detect_user_interrupt("Please ABORT the current phase")
    assert result["interrupted"] is True
    assert result["signal"] == "ABORT"


def test_abort_this_task():
    result = detect_user_interrupt("ABORT THIS TASK immediately")
    assert result["interrupted"] is True
    assert result["signal"] == "ABORT THIS TASK"


def test_cancel():
    result = detect_user_interrupt("CANCEL")
    assert result["interrupted"] is True
    assert result["signal"] == "CANCEL"


def test_pause_execution():
    result = detect_user_interrupt("PAUSE EXECUTION please")
    assert result["interrupted"] is True
    assert result["signal"] == "PAUSE EXECUTION"


def test_hold():
    result = detect_user_interrupt("HOLD on a moment")
    assert result["interrupted"] is True
    assert result["signal"] == "HOLD"


def test_normal_message():
    result = detect_user_interrupt("what is the status?")
    assert result["interrupted"] is False
    assert result["signal"] is None
    assert result["ok"] is True
    assert result["errors"] == []


def test_empty_string():
    result = detect_user_interrupt("")
    assert result["interrupted"] is False
    assert result["signal"] is None


def test_case_insensitive_stop():
    result = detect_user_interrupt("stop")
    assert result["interrupted"] is True
    assert result["signal"] == "STOP"


def test_word_boundary_unstoppable():
    """'unstoppable' must NOT trigger the STOP keyword."""
    result = detect_user_interrupt("this is unstoppable progress")
    assert result["interrupted"] is False
    assert result["signal"] is None


def test_word_boundary_cancellation():
    """'cancellation' must NOT trigger the CANCEL keyword."""
    result = detect_user_interrupt("the cancellation notice was sent")
    assert result["interrupted"] is False
    assert result["signal"] is None


def test_multi_word_phrase_preferred():
    """'ABORT THIS TASK' matched before bare 'ABORT'."""
    result = detect_user_interrupt("ABORT THIS TASK now")
    assert result["signal"] == "ABORT THIS TASK"
