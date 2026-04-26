from pathlib import Path

from ccworkflow.app.runtime import get_collection_root
from ccworkflow.domain.common_schema import AppResult
from ccworkflow.repositories.install_record_repository import list_records, load_record


def list_install_records(input_data: dict | None = None) -> dict:
    records_dir = get_collection_root() / "install_records"
    return list_records({"records_dir": str(records_dir)})


def get_install_record_detail(input_data: dict) -> dict:
    record_id = input_data["install_record_id"]
    record_path = get_collection_root() / "install_records" / f"{record_id}.json"
    if not record_path.exists():
        return AppResult(success=False, message="安装记录不存在").model_dump()
    return load_record({"record_path": str(record_path)})
