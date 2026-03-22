#!/usr/bin/env python3
import sys
from pathlib import Path

import pytest
import yaml

# Add scripts to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from substrate_distiller import RegistryError, get_substrate_files, load_registry, main


def test_load_registry_not_found(tmp_path):
    registry = tmp_path / "missing.yml"
    with pytest.raises(RegistryError, match="Registry not found"):
        load_registry(registry)


def test_load_registry_valid(tmp_path):
    registry = tmp_path / "recommendations-registry.yml"
    data = {
        "recommendations": [
            {"id": "rec-1", "status": "accepted", "title": "Test 1"},
            {"id": "rec-2", "status": "deferred", "title": "Test 2"},
        ]
    }
    registry.write_text(yaml.dump(data), encoding="utf-8")
    recs = load_registry(registry)
    assert len(recs) == 2
    assert recs[0]["id"] == "rec-1"


def test_get_substrate_files_structure(tmp_path):
    root = tmp_path
    (root / ".github/agents").mkdir(parents=True)
    (root / ".github/skills/test-skill").mkdir(parents=True)
    (root / "docs/guides").mkdir(parents=True)

    agent = root / ".github/agents/test.agent.md"
    skill = root / ".github/skills/test-skill/SKILL.md"
    guide = root / "docs/guides/test-guide.md"
    other = root / "other.txt"

    agent.write_text("content", encoding="utf-8")
    skill.write_text("content", encoding="utf-8")
    guide.write_text("content", encoding="utf-8")
    other.write_text("content", encoding="utf-8")

    files = get_substrate_files(root)
    file_names = {f.name for f in files}
    assert "test.agent.md" in file_names
    assert "SKILL.md" in file_names
    assert "test-guide.md" in file_names
    assert "other.txt" not in file_names


def test_substrate_distiller_main_success(tmp_path, monkeypatch, capsys):
    root = tmp_path
    monkeypatch.chdir(root)

    registry = root / "data/recommendations-registry.yml"
    registry.parent.mkdir()
    data = {"recommendations": [{"id": "rec-accepted", "status": "accepted", "title": "Accepted Title"}]}
    registry.write_text(yaml.dump(data), encoding="utf-8")

    guide = root / "docs/guides/distilled.md"
    guide.parent.mkdir(parents=True)
    guide.write_text("Implementing rec-accepted here.", encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["substrate_distiller.py", "--check"])

    main()
    out, _ = capsys.readouterr()
    assert "✅ DISTILLED: rec-accepted" in out


def test_substrate_distiller_main_missing_check(tmp_path, monkeypatch, capsys):
    root = tmp_path
    monkeypatch.chdir(root)

    registry = root / "data/recommendations-registry.yml"
    registry.parent.mkdir()
    data = {"recommendations": [{"id": "rec-missing", "status": "accepted", "title": "Missing Title"}]}
    registry.write_text(yaml.dump(data), encoding="utf-8")

    # Create empty substrate
    (root / "docs/guides/").mkdir(parents=True)

    monkeypatch.setattr("sys.argv", ["substrate_distiller.py", "--check"])

    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    out, _ = capsys.readouterr()
    assert "❌ MISSING: rec-missing" in out


def test_substrate_distiller_invalid_status_ignored(tmp_path, monkeypatch, capsys):
    root = tmp_path
    monkeypatch.chdir(root)

    registry = root / "data/recommendations-registry.yml"
    registry.parent.mkdir()
    data = {"recommendations": [{"id": "rec-deferred", "status": "deferred", "title": "Deferred Title"}]}
    registry.write_text(yaml.dump(data), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["substrate_distiller.py", "--check"])

    main()
    out, _ = capsys.readouterr()
    assert "No accepted recommendations to audit." in out
