from pathlib import Path

from ccworkflow.infra.path_policy import validate_project_root, validate_target_path


def test_validate_project_root_rejects_missing_dir(tmp_path: Path) -> None:
    result = validate_project_root({"project_root": str(tmp_path / "missing")})
    assert result["success"] is False
    assert result["errors"][0]["code"] == "INVALID_PROJECT_ROOT"


def test_validate_target_path_accepts_allowed_claude_paths() -> None:
    result = validate_target_path({"target_path": "D:/demo/.claude/settings.json"})
    assert result["success"] is True


def test_validate_target_path_rejects_other_paths() -> None:
    result = validate_target_path({"target_path": "D:/demo/random.txt"})
    assert result["success"] is False
    assert result["errors"][0]["code"] == "TARGET_PATH_NOT_ALLOWED"
