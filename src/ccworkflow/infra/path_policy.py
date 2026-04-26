from pathlib import Path

from ccworkflow.domain.common_schema import AppError, AppResult

TARGET_FILE_NAMES = {
    ".claude/settings.json",
    ".mcp.json",
    ".claude.json",
}

TARGET_DIR_MARKERS = {
    ".claude/skills",
    ".claude/scripts",
}


def validate_project_root(input_data: dict) -> dict:
    project_root = Path(input_data["project_root"])
    if not project_root.exists() or not project_root.is_dir():
        return AppResult(
            success=False,
            errors=[AppError(code="INVALID_PROJECT_ROOT", field="project_root", target="project", detail="项目根目录不存在或不是目录")],
        ).model_dump()
    return AppResult(success=True, data={"project_root": str(project_root.resolve())}).model_dump()


def validate_collection_root(input_data: dict) -> dict:
    target_root = Path(input_data["collection_root"])
    parent = target_root.parent
    if not parent.exists() or not parent.is_dir():
        return AppResult(
            success=False,
            errors=[AppError(code="INVALID_COLLECTION_ROOT", field="collection_root", target="settings", detail="收藏根目录的父目录不存在")],
        ).model_dump()
    return AppResult(success=True, data={"collection_root": str(target_root)}).model_dump()


def validate_target_path(input_data: dict) -> dict:
    target_path = Path(input_data["target_path"])
    normalized = target_path.as_posix()
    allowed = any(marker in normalized for marker in TARGET_DIR_MARKERS) or any(normalized.endswith(name) for name in TARGET_FILE_NAMES)
    if not allowed:
        return AppResult(
            success=False,
            errors=[AppError(code="TARGET_PATH_NOT_ALLOWED", field="target_path", target="install", detail="目标路径不在白名单范围内")],
        ).model_dump()
    return AppResult(success=True, data={"target_path": str(target_path)}).model_dump()
