from pathlib import Path

from ccworkflow.domain.common_schema import AppResult
from ccworkflow.domain.record_schema import InstallRecordDraft
from ccworkflow.infra.fs_gateway import ensure_dir
from ccworkflow.infra.json_gateway import read_json, write_json


def save_record(input_data: dict) -> dict:
    record = InstallRecordDraft.model_validate(input_data["record"])
    record_path = Path(input_data["record_path"])
    write_json(record_path, record.model_dump(mode="json"))
    return AppResult(success=True, data={"record": record.model_dump(mode="json"), "record_path": record_path.as_posix()}).model_dump()


def load_record(input_data: dict) -> dict:
    record = InstallRecordDraft.model_validate(read_json(input_data["record_path"]))
    return AppResult(success=True, data={"record": record.model_dump(mode="json")}).model_dump()


def list_records(input_data: dict) -> dict:
    records_dir = ensure_dir(input_data["records_dir"])
    items: list[dict] = []
    for path in records_dir.glob("*.json"):
        items.append(read_json(path))
    items.sort(key=lambda item: item.get("installed_at") or "", reverse=True)
    return AppResult(success=True, data={"items": items}).model_dump()


def mark_uninstall_result(input_data: dict) -> dict:
    record = InstallRecordDraft.model_validate(read_json(input_data["record_path"]))
    record.uninstall_status = input_data["uninstall_status"]
    write_json(input_data["record_path"], record.model_dump(mode="json"))
    return AppResult(success=True, data={"record": record.model_dump(mode="json")}).model_dump()
