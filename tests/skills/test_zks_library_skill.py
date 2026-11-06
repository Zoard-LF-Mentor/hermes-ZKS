"""Offline smoke checks for optional ZKS skill; no private library data needed."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "optional-skills" / "research" / "zks-library" / "scripts" / "zks.py"


def fixture(tmp_path):
    folder = tmp_path / "zks"
    folder.mkdir()
    parts = {
        "KNOWLEDGE/KNOW-ORBIT.md": ("KNOW-ORBIT", "# Orbital mechanics\n\nGravity, elliptical orbits, and angular momentum.\n"),
        "SYSTEM/CORE.md": ("SYS-CORE", "# Operating core\n\nSystem operations.\n"),
    }
    entries = []
    for rel, (ident, data) in parts.items():
        path = folder / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")
        entries.append({"id": ident, "path": rel, "sha256": hashlib.sha256(data.encode()).hexdigest()})
    (folder / "manifest.json").write_text(json.dumps({"system": "ZKS", "system_version": "0.1.0", "modules": entries, "integrity_files": []}))
    return folder


def invoke(root, *args):
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), *args], capture_output=True, text=True)


def test_verification_and_read(tmp_path):
    root = fixture(tmp_path)
    assert invoke(root, "verify").returncode == 0
    p = invoke(root, "read", "know-orbit")
    assert p.returncode == 0 and "elliptical orbits" in p.stdout


def test_lexical_search_and_system_gate(tmp_path):
    root = fixture(tmp_path)
    assert "KNOW-ORBIT" in invoke(root, "search", "orbital momentum").stdout
    assert "SYS-CORE" not in invoke(root, "search", "system operations").stdout
    assert "SYS-CORE" in invoke(root, "search", "system operations", "--all").stdout


def test_unknown_id(tmp_path):
    assert invoke(fixture(tmp_path), "read", "NOPE").returncode == 2


def test_corruption_detected(tmp_path):
    root = fixture(tmp_path)
    (root / "KNOWLEDGE/KNOW-ORBIT.md").write_text("tampered", encoding="utf-8")
    assert invoke(root, "verify").returncode != 0


def test_escaped_path_rejected(tmp_path):
    root = fixture(tmp_path)
    m = json.loads((root / "manifest.json").read_text())
    m["modules"][0]["path"] = "../../outside.md"
    (root / "manifest.json").write_text(json.dumps(m))
    assert invoke(root, "verify").returncode != 0
