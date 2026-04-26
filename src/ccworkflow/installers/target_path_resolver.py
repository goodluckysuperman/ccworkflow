from pathlib import Path

from ccworkflow.domain.common_schema import AppResult
from ccworkflow.domain.enums import ObjectType
from ccworkflow.infra.path_policy import validate_project_root, validate_target_path


def resolve_targets(input_data: dict) -> dict:
    scope = input_data["scope"]
    project_root = input_data.get("project_root")
    objects = input_data.get("objects", [])

    if scope == "project":
        project_result = validate_project_root({"project_root": project_root})
        if not project_result["success"]:
            return project_result
        base_root = Path(project_result["data"]["project_root"])
    else:
        base_root = Path.home()

    targets: list[dict] = []
    for obj in objects:
        object_type = ObjectType(obj["type"])
        object_name = obj["name"]

        if object_type == ObjectType.SKILL:
            target_file = _build_skill_target(base_root, object_name)
            target_kind = "skill_file"
        elif object_type == ObjectType.HOOK:
            target_file = _build_hook_target(base_root)
            target_kind = "settings_json"
        else:
            target_file = _build_mcp_target(base_root, scope)
            target_kind = "mcp_json"

        target_result = validate_target_path({"target_path": str(target_file)})
        if not target_result["success"]:
            return target_result

        targets.append(
            {
                "object_id": obj["object_id"],
                "type": obj["type"],
                "object_name": object_name,
                "target_file": target_file.as_posix(),
                "target_kind": target_kind,
            }
        )

    return AppResult(success=True, data={"targets": targets}).model_dump()


def _build_skill_target(base_root: Path, object_name: str) -> Path:
    return base_root / ".claude" / "skills" / object_name / "SKILL.md"


def _build_hook_target(base_root: Path) -> Path:
    return base_root / ".claude" / "settings.json"


def _build_mcp_target(base_root: Path, scope: str) -> Path:
    if scope == "project":
        return base_root / ".mcp.json"
    return base_root / ".claude.json"
