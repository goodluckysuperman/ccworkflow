from ccworkflow.domain.common_schema import AppResult
from ccworkflow.integrations import claude_cli_adapter
from ccworkflow.services.generate_draft_service import generate_draft


def test_check_available_handles_missing_claude(monkeypatch) -> None:
    def raise_file_not_found(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(claude_cli_adapter.subprocess, "run", raise_file_not_found)

    result = claude_cli_adapter.check_available({})

    assert result["success"] is True
    assert result["data"]["available"] is False


def test_generate_draft_returns_error_when_claude_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(
        "ccworkflow.services.generate_draft_service.check_available",
        lambda _: AppResult(success=True, data={"available": False, "version": ""}).model_dump(),
    )

    result = generate_draft(
        {
            "name": "draft package",
            "summary": "summary",
            "tags": ["ai"],
            "target_types": ["skill"],
            "prompt": "生成一个 Python review skill",
        }
    )

    assert result["success"] is False
    assert result["errors"][0]["code"] == "CLAUDE_NOT_AVAILABLE"


def test_generate_draft_parses_valid_json(monkeypatch) -> None:
    monkeypatch.setattr(
        "ccworkflow.services.generate_draft_service.check_available",
        lambda _: AppResult(success=True, data={"available": True, "version": "claude-test"}).model_dump(),
    )
    monkeypatch.setattr(
        "ccworkflow.services.generate_draft_service.run_generate",
        lambda _: AppResult(
            success=True,
            data={
                "raw_text": '{"name":"ai package","summary":"generated","tags":["ai"],"objects":[{"type":"skill","name":"ai-skill","description":"generated skill","body":"# Skill","extra":{}}],"scripts":[],"warnings":[]}'
            },
        ).model_dump(),
    )

    result = generate_draft(
        {
            "name": "draft package",
            "summary": "summary",
            "tags": ["ai"],
            "target_types": ["skill"],
            "prompt": "生成一个 Python review skill",
        }
    )

    assert result["success"] is True
    assert result["data"]["draft"]["name"] == "ai package"
    assert result["data"]["draft"]["objects"][0]["name"] == "ai-skill"
