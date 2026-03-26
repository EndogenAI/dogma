"""
test_health_check_services.py — Unit tests for service health check orchestrator.

Tests healthy/degraded/unreachable scenarios with mocked HTTP.
"""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add scripts/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from health_check_services import (
    check_service_health,
    extract_services_with_health_endpoints,
    load_substrate_atlas,
)


@pytest.mark.io
def test_load_substrate_atlas_reads_yaml(tmp_path):
    """Verify load_substrate_atlas reads and parses YAML file correctly."""
    atlas_file = tmp_path / "atlas.yml"
    atlas_file.write_text("""
substrates:
  - id: 1
    name: "test-service"
    health_endpoint: "http://localhost:8000/health"
""")

    atlas = load_substrate_atlas(atlas_file)
    assert "substrates" in atlas
    assert len(atlas["substrates"]) == 1
    assert atlas["substrates"][0]["name"] == "test-service"


@pytest.mark.io
def test_load_substrate_atlas_raises_on_missing_file(tmp_path):
    """Verify FileNotFoundError is raised when atlas file doesn't exist."""
    missing_file = tmp_path / "nonexistent.yml"
    with pytest.raises(FileNotFoundError, match="Substrate atlas not found"):
        load_substrate_atlas(missing_file)


def test_extract_services_with_health_endpoints():
    """Verify extract_services_with_health_endpoints filters correctly."""
    atlas = {
        "substrates": [
            {"name": "service-with-health", "health_endpoint": "http://localhost:8000/health"},
            {"name": "service-without-health", "path_pattern": "*.py"},
            {"name": "another-with-health", "health_endpoint": "http://localhost:9000/health"},
        ]
    }

    services = extract_services_with_health_endpoints(atlas)
    assert len(services) == 2
    assert services[0]["name"] == "service-with-health"
    assert services[1]["name"] == "another-with-health"


@patch("health_check_services.requests.get")
def test_check_service_health_returns_healthy_on_200(mock_get):
    """Verify check_service_health returns 'healthy' for HTTP 200."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.elapsed.total_seconds.return_value = 0.15
    mock_get.return_value = mock_response

    result = check_service_health("test-service", "http://localhost:8000/health")

    assert result["status"] == "healthy"
    assert result["name"] == "test-service"
    assert "0.15s" in result["message"]


@patch("health_check_services.requests.get")
def test_check_service_health_returns_degraded_on_non_200(mock_get):
    """Verify check_service_health returns 'degraded' for non-200 status."""
    mock_response = Mock()
    mock_response.status_code = 503
    mock_get.return_value = mock_response

    result = check_service_health("test-service", "http://localhost:8000/health")

    assert result["status"] == "degraded"
    assert "503" in result["message"]


@patch("health_check_services.requests.get")
def test_check_service_health_returns_unreachable_on_timeout(mock_get):
    """Verify check_service_health returns 'unreachable' on timeout."""
    import requests

    mock_get.side_effect = requests.Timeout()

    result = check_service_health("test-service", "http://localhost:8000/health", timeout=2)

    assert result["status"] == "unreachable"
    assert "Timeout" in result["message"]


@patch("health_check_services.requests.get")
def test_check_service_health_returns_unreachable_on_connection_error(mock_get):
    """Verify check_service_health returns 'unreachable' on connection error."""
    import requests

    mock_get.side_effect = requests.ConnectionError("Connection refused")

    result = check_service_health("test-service", "http://localhost:8000/health")

    assert result["status"] == "unreachable"
    assert "Connection error" in result["message"]


@pytest.mark.io
def test_main_exits_0_when_all_healthy(tmp_path, capsys):
    """Verify main exits 0 when all services are healthy."""
    atlas_file = tmp_path / "atlas.yml"
    atlas_file.write_text("""
substrates:
  - name: "healthy-service"
    health_endpoint: "http://localhost:8000/health"
""")

    with patch("sys.argv", ["health_check_services.py", "--atlas", str(atlas_file)]):
        with patch("health_check_services.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.elapsed.total_seconds.return_value = 0.1
            mock_get.return_value = mock_response

            from health_check_services import main

            exit_code = main()

            assert exit_code == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert "healthy-service" in output["healthy"]


@pytest.mark.io
def test_main_exits_1_when_service_degraded(tmp_path, capsys):
    """Verify main exits 1 when a service is degraded."""
    atlas_file = tmp_path / "atlas.yml"
    atlas_file.write_text("""
substrates:
  - name: "degraded-service"
    health_endpoint: "http://localhost:8000/health"
""")

    with patch("sys.argv", ["health_check_services.py", "--atlas", str(atlas_file)]):
        with patch("health_check_services.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 503
            mock_get.return_value = mock_response

            from health_check_services import main

            exit_code = main()

            assert exit_code == 1
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert len(output["degraded"]) == 1


@pytest.mark.io
def test_main_exits_2_when_service_unreachable(tmp_path, capsys):
    """Verify main exits 2 when a service is unreachable."""
    atlas_file = tmp_path / "atlas.yml"
    atlas_file.write_text("""
substrates:
  - name: "unreachable-service"
    health_endpoint: "http://localhost:8000/health"
""")

    with patch("sys.argv", ["health_check_services.py", "--atlas", str(atlas_file)]):
        with patch("health_check_services.requests.get") as mock_get:
            import requests

            mock_get.side_effect = requests.Timeout()

            from health_check_services import main

            exit_code = main()

            assert exit_code == 2
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert len(output["unreachable"]) == 1


@pytest.mark.io
def test_main_dry_run_lists_services(tmp_path, capsys):
    """Verify --dry-run lists services without checking health."""
    atlas_file = tmp_path / "atlas.yml"
    atlas_file.write_text("""
substrates:
  - name: "service-1"
    health_endpoint: "http://localhost:8000/health"
  - name: "service-2"
    health_endpoint: "http://localhost:9000/health"
""")

    with patch("sys.argv", ["health_check_services.py", "--atlas", str(atlas_file), "--dry-run"]):
        from health_check_services import main

        exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["count"] == 2
        assert "service-1" in output["services"]
        assert "service-2" in output["services"]
