import json
import subprocess

from ccworkflow.domain.common_schema import AppError, AppResult


def check_available(input_data: dict | None = None) -> dict:
    try:
        completed = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except FileNotFoundError:
        return AppResult(success=True, data={"available": False, "version": ""}).model_dump()
    except Exception as exc:
        return AppResult(
            success=False,
            errors=[AppError(code="CLAUDE_CHECK_FAILED", detail=str(exc), target="claude_cli")],
        ).model_dump()

    version_text = (completed.stdout or completed.stderr or "").strip()
    return AppResult(
        success=True,
        data={
            "available": completed.returncode == 0,
            "version": version_text,
        },
    ).model_dump()


def run_generate(input_data: dict) -> dict:
    prompt = input_data["prompt"]
    timeout_seconds = int(input_data.get("timeout_seconds", 60))

    try:
        completed = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError:
        return AppResult(
            success=False,
            errors=[AppError(code="CLAUDE_NOT_INSTALLED", detail="未检测到 Claude Code", target="claude_cli")],
        ).model_dump()
    except subprocess.TimeoutExpired:
        return AppResult(
            success=False,
            errors=[AppError(code="CLAUDE_GENERATE_TIMEOUT", detail="Claude Code 调用超时", target="claude_cli")],
        ).model_dump()
    except Exception as exc:
        return AppResult(
            success=False,
            errors=[AppError(code="CLAUDE_GENERATE_FAILED", detail=str(exc), target="claude_cli")],
        ).model_dump()

    raw_text = (completed.stdout or "").strip()
    if completed.returncode != 0:
        return AppResult(
            success=False,
            errors=[AppError(code="CLAUDE_GENERATE_FAILED", detail=(completed.stderr or raw_text or "Claude Code 调用失败"), target="claude_cli")],
        ).model_dump()

    return AppResult(success=True, data={"raw_text": raw_text}).model_dump()


def parse_generate_json(input_data: dict) -> dict:
    raw_text = input_data["raw_text"]
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        return AppResult(
            success=False,
            errors=[AppError(code="CLAUDE_OUTPUT_NOT_JSON", detail=str(exc), target="claude_cli")],
        ).model_dump()
    return AppResult(success=True, data={"payload": payload}).model_dump()
