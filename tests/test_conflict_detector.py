import json
from pathlib import Path

from ccworkflow.installers.conflict_detector import detect_conflicts


def test_detect_conflicts_for_existing_skill_file(tmp_path: Path) -> None:
    target = tmp_path / ".claude" / "skills" / "demo-skill" / "SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_text("# Existing", encoding="utf-8")

    result = detect_conflicts(
        {
            "targets": [
                {
                    "object_id": "obj1",
                    "type": "skill",
                    "object_name": "demo-skill",
                    "target_file": str(target),
                    "target_kind": "skill_file",
                }
            ],
            "objects": [
                {
                    "object_id": "obj1",
                    "type": "skill",
                    "name": "demo-skill",
                    "extra": {},
                }
            ],
        }
    )

    assert result["success"] is True
    assert result["data"]["conflicts"][0]["reason"] == "same_name"


def test_detect_conflicts_for_existing_mcp_server(tmp_path: Path) -> None:
    target = tmp_path / ".mcp.json"
    target.write_text(json.dumps({"mcpServers": {"docs": {"command": "python"}}}), encoding="utf-8")

    result = detect_conflicts(
        {
            "targets": [
                {
                    "object_id": "obj1",
                    "type": "mcp",
                    "object_name": "docs",
                    "target_file": str(target),
                    "target_kind": "mcp_json",
                }
            ],
            "objects": [
                {
                    "object_id": "obj1",
                    "type": "mcp",
                    "name": "docs",
                    "extra": {"server_name": "docs"},
                }
            ],
        }
    )

    assert result["success"] is True
    assert result["data"]["conflicts"][0]["reason"] == "same_server_name"
