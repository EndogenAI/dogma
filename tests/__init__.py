"""tests/__init__.py

Test suite for EndogenAI Workflows scripts.

Run all tests with:
    uv run pytest tests/

Run with coverage:
    uv run pytest tests/ --cov=scripts

Run only fast tests:
    uv run pytest tests/ -m "not slow and not integration"

Run only unit tests (no I/O):
    uv run pytest tests/ -m "not io"
"""
