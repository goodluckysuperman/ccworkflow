from pathlib import Path

from ccworkflow.installers.target_path_resolver import resolve_targets


def test_resolve_targets_for_project_scope(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()

    result = resolve_targets(
        {
            "scope": "project",
            "project_root": str(project_root),
            "objects": [
                {"object_id": "obj1", "type": "skill", "name": "demo-skill"},
                {"object_id": "obj2", "type": "hook", "name": "demo-hook"},
                {"object_id": "obj3", "type": "mcp", "name": "demo-mcp"},
            ],
        }
    )

    assert result["success"] is True
    targets = result["data"]["targets"]
    assert any(target["target_file"].endswith(".claude/skills/demo-skill/SKILL.md") for target in targets)
    assert any(target["target_file"].endswith(".claude/settings.json") for target in targets)
    assert any(target["target_file"].endswith(".mcp.json") for target in targets)
