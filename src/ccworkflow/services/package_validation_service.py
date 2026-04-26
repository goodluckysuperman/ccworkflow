from ccworkflow.domain.common_schema import AppError, AppResult
from ccworkflow.domain.package_schema import PackageDraft
from ccworkflow.domain.enums import ObjectType, PackageCategory


def validate_package(input_data: dict) -> dict:
    package = PackageDraft.model_validate(input_data["package"])
    errors: list[AppError] = []
    object_summaries: list[dict] = []

    if not package.name.strip():
        errors.append(AppError(code="PACKAGE_NAME_REQUIRED", field="name", target="package", detail="配置包名称不能为空"))

    if not package.objects:
        errors.append(AppError(code="PACKAGE_OBJECTS_REQUIRED", field="objects", target="package", detail="配置包至少需要一个对象"))

    script_names = {script.name for script in package.scripts}
    object_types: set[str] = set()

    for obj in package.objects:
        object_errors: list[AppError] = []
        object_types.add(obj.type.value)

        if not obj.name.strip():
            object_errors.append(AppError(code="OBJECT_NAME_REQUIRED", field="name", target=obj.object_id or "object", detail="对象名称不能为空"))

        if obj.type == ObjectType.SKILL:
            if not isinstance(obj.body, str) or not obj.body.strip():
                object_errors.append(AppError(code="SKILL_BODY_REQUIRED", field="body", target=obj.object_id or "object", detail="skill 正文不能为空"))
        else:
            if not isinstance(obj.body, dict) or not obj.body:
                object_errors.append(AppError(code="OBJECT_BODY_REQUIRED", field="body", target=obj.object_id or "object", detail="对象正文不能为空"))

        if obj.type == ObjectType.HOOK and not obj.extra.get("hook_key", "").strip():
            object_errors.append(AppError(code="HOOK_KEY_REQUIRED", field="extra.hook_key", target=obj.object_id or "object", detail="hook_key 不能为空"))

        if obj.type == ObjectType.MCP and not obj.extra.get("server_name", "").strip():
            object_errors.append(AppError(code="MCP_SERVER_NAME_REQUIRED", field="extra.server_name", target=obj.object_id or "object", detail="server_name 不能为空"))

        missing_scripts: list[str] = []
        if isinstance(obj.body, str):
            parts = obj.body.split("{{script:")
            for part in parts[1:]:
                script_name = part.split("}}", 1)[0]
                if script_name and script_name not in script_names:
                    missing_scripts.append(script_name)
        elif isinstance(obj.body, dict):
            serialized = str(obj.body)
            parts = serialized.split("{{script:")
            for part in parts[1:]:
                script_name = part.split("}}", 1)[0]
                if script_name and script_name not in script_names:
                    missing_scripts.append(script_name)

        for script_name in missing_scripts:
            object_errors.append(AppError(code="SCRIPT_REFERENCE_MISSING", field="scripts", target=obj.object_id or "object", detail=f"缺少附加脚本: {script_name}"))

        object_summaries.append(
            {
                "object_id": obj.object_id,
                "valid": not object_errors,
                "errors": [error.model_dump() for error in object_errors],
            }
        )
        errors.extend(object_errors)

    category = _resolve_category(object_types)

    return AppResult(
        success=not errors,
        errors=errors,
        data={
            "valid": not errors,
            "category": category.value,
            "object_summaries": object_summaries,
        },
    ).model_dump()


def _resolve_category(object_types: set[str]) -> PackageCategory:
    if object_types == {ObjectType.SKILL.value}:
        return PackageCategory.SKILLS
    if object_types == {ObjectType.HOOK.value}:
        return PackageCategory.HOOKS
    if object_types == {ObjectType.MCP.value}:
        return PackageCategory.MCP
    return PackageCategory.MIXED
