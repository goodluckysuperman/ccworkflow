from ccworkflow.domain.common_schema import AppError, AppResult
from ccworkflow.domain.package_schema import PackageDraft
from ccworkflow.integrations.claude_cli_adapter import check_available, parse_generate_json, run_generate

PROMPT_TEMPLATE = """你是 Claude Code 配置生成器。
请根据输入生成一个 JSON 对象，且只能输出 JSON。
输出结构必须为：
{json_shape}

输入信息：
- 配置包名称：{name}
- 简介：{summary}
- 标签：{tags}
- 目标类型：{target_types}
- 用户描述：{prompt}

要求：
1. 只输出 JSON。
2. 若没有脚本，scripts 输出空数组。
3. hook 必须带 extra.hook_key。
4. mcp 必须带 extra.server_name。
5. 不要自动保存，不要输出解释文字。
"""

JSON_SHAPE = """{
  \"name\": string,
  \"summary\": string,
  \"tags\": string[],
  \"objects\": [
    {
      \"type\": \"skill\" | \"hook\" | \"mcp\",
      \"name\": string,
      \"description\": string,
      \"body\": string | object,
      \"extra\": object
    }
  ],
  \"scripts\": [
    {
      \"name\": string,
      \"source_path\": string,
      \"applies_to\": string[]
    }
  ],
  \"warnings\": string[]
}"""


def generate_draft(input_data: dict) -> dict:
    availability = check_available({})
    if not availability["success"]:
        return availability
    if not availability["data"]["available"]:
        return AppResult(
            success=False,
            errors=[AppError(code="CLAUDE_NOT_AVAILABLE", detail="本机未安装或不可用 Claude Code", target="generate")],
        ).model_dump()

    prompt = PROMPT_TEMPLATE.format(
        json_shape=JSON_SHAPE,
        name=input_data.get("name", ""),
        summary=input_data.get("summary", ""),
        tags=", ".join(input_data.get("tags", [])),
        target_types=", ".join(input_data.get("target_types", [])),
        prompt=input_data.get("prompt", ""),
    )

    generated = run_generate({"prompt": prompt, "timeout_seconds": input_data.get("timeout_seconds", 60)})
    if not generated["success"]:
        return generated

    parsed = parse_generate_json({"raw_text": generated["data"]["raw_text"]})
    if not parsed["success"]:
        return parsed

    payload = parsed["data"]["payload"]
    try:
        draft = PackageDraft.model_validate(
            {
                "package_id": None,
                "name": payload.get("name") or input_data.get("name", ""),
                "summary": payload.get("summary") or input_data.get("summary", ""),
                "tags": payload.get("tags", input_data.get("tags", [])),
                "objects": payload.get("objects", []),
                "scripts": payload.get("scripts", []),
            }
        )
    except Exception as exc:
        return AppResult(
            success=False,
            errors=[AppError(code="GENERATE_DRAFT_INVALID", detail=str(exc), target="generate")],
        ).model_dump()

    return AppResult(
        success=True,
        data={
            "draft": draft.model_dump(mode="json"),
            "warnings": payload.get("warnings", []),
            "claude_version": availability["data"]["version"],
        },
    ).model_dump()
