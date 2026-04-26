import json
from pathlib import Path
from typing import Any

from ccworkflow.domain.common_schema import AppError, AppResult


SCRIPT_PLACEHOLDER_PREFIX = "{{script:"
SCRIPT_PLACEHOLDER_SUFFIX = "}}"


def materialize_scripts(input_data: dict) -> dict:
    scope = input_data["scope"]
    project_root = input_data.get("project_root")
    objects = input_data.get("objects", [])
    scripts = input_data.get("scripts", [])

    script_name_to_target: dict[str, str] = {}
    copied_scripts: list[dict[str, Any]] = []
    missing_scripts: list[str] = []

    script_dir = _resolve_script_dir(scope, project_root)
    for script in scripts:
        target_path = (script_dir / script["name"]).as_posix()
        script_name_to_target[script["name"]] = target_path
        copied_scripts.append(
            {
                "script_id": script["script_id"],
                "name": script["name"],
                "target_path": target_path,
                "source_path": script["source_path"],
            }
        )

    resolved_objects: list[dict[str, Any]] = []
    for obj in objects:
        resolved_body, object_missing_scripts = _resolve_body_placeholders(obj["body"], script_name_to_target)
        missing_scripts.extend(object_missing_scripts)
        resolved_object = dict(obj)
        resolved_object["body"] = resolved_body
        resolved_objects.append(resolved_object)

    if missing_scripts:
        unique_missing = sorted(set(missing_scripts))
        return AppResult(
            success=False,
            errors=[
                AppError(
                    code="SCRIPT_REFERENCE_MISSING",
                    field="scripts",
                    target="install_preview",
                    detail=f"缺少附加脚本: {', '.join(unique_missing)}",
                )
            ],
            data={"missing_scripts": unique_missing},
        ).model_dump()

    return AppResult(
        success=True,
        data={
            "resolved_objects": resolved_objects,
            "copied_scripts": copied_scripts,
            "missing_scripts": [],
        },
    ).model_dump()


def _resolve_script_dir(scope: str, project_root: str | None) -> Path:
    if scope == "project":
        return Path(project_root) / ".claude" / "scripts"
    return Path.home() / ".claude" / "scripts"


def _resolve_body_placeholders(body: Any, script_name_to_target: dict[str, str]) -> tuple[Any, list[str]]:
    if isinstance(body, str):
        return _replace_in_string(body, script_name_to_target)

    if isinstance(body, dict):
        body_text = json.dumps(body, ensure_ascii=False)
        resolved_text, missing_scripts = _replace_in_string(body_text, script_name_to_target)
        return json.loads(resolved_text), missing_scripts

    return body, []


def _replace_in_string(text: str, script_name_to_target: dict[str, str]) -> tuple[str, list[str]]:
    result_parts: list[str] = []
    missing_scripts: list[str] = []
    cursor = 0

    while True:
        start = text.find(SCRIPT_PLACEHOLDER_PREFIX, cursor)
        if start == -1:
            result_parts.append(text[cursor:])
            break

        end = text.find(SCRIPT_PLACEHOLDER_SUFFIX, start)
        if end == -1:
            result_parts.append(text[cursor:])
            break

        result_parts.append(text[cursor:start])
        script_name = text[start + len(SCRIPT_PLACEHOLDER_PREFIX) : end]
        replacement = script_name_to_target.get(script_name)
        if replacement is None:
            missing_scripts.append(script_name)
            result_parts.append(text[start : end + len(SCRIPT_PLACEHOLDER_SUFFIX)])
        else:
            result_parts.append(replacement)
        cursor = end + len(SCRIPT_PLACEHOLDER_SUFFIX)

    return "".join(result_parts), missing_scripts
