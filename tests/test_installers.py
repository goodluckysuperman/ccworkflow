import json
from pathlib import Path

from ccworkflow.installers.skill_installer import install_skill
from ccworkflow.installers.hook_installer import install_hook
from ccworkflow.installers.mcp_installer import install_mcp


def test_install_skill_writes_skill_file(tmp_path: Path) -> None:
    target = tmp_path / ".claude" / "skills" / "demo-skill" / "SKILL.md"

    result = install_skill(
        {
            "object": {
                "object_id": "obj1",
                "type": "skill",
                "name": "demo-skill",
                "body": "# Skill",
            },
            "target_file": target.as_posix(),
            "resolution": "replace",
        }
    )

    assert result["success"] is True
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "# Skill"


def test_install_hook_merges_generated_hooks(tmp_path: Path) -> None:
    target = tmp_path / ".claude" / "settings.json"

    result = install_hook(
        {
            "object": {
                "object_id": "obj2",
                "type": "hook",
                "name": "demo-hook",
                "body": {"event": "PostToolUse", "matcher": "Write", "hooks": []},
                "extra": {"hook_key": "demo-hook-key"},
            },
            "target_file": target.as_posix(),
            "resolution": "replace",
        }
    )

    payload = json.loads(target.read_text(encoding="utf-8"))
    assert result["success"] is True
    assert "demo-hook-key" in payload["generatedHooks"]


def test_install_mcp_merges_server_entry(tmp_path: Path) -> None:
    target = tmp_path / ".mcp.json"

    result = install_mcp(
        {
            "object": {
                "object_id": "obj3",
                "type": "mcp",
                "name": "docs",
                "body": {"command": "python", "args": [], "env": {}},
                "extra": {"server_name": "docs"},
            },
            "target_file": target.as_posix(),
            "resolution": "replace",
        }
    )

    payload = json.loads(target.read_text(encoding="utf-8"))
    assert result["success"] is True
    assert "docs" in payload["mcpServers"]
