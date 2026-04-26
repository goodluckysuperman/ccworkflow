from ccworkflow.domain.common_schema import AppResult
from ccworkflow.domain.settings_schema import SettingsDraft
from ccworkflow.infra.json_gateway import read_json, write_json


def load_settings(input_data: dict) -> dict:
    payload = read_json(input_data["settings_path"])
    settings = SettingsDraft.model_validate(payload)
    return AppResult(success=True, data={"settings": settings.model_dump()}).model_dump()


def save_settings(input_data: dict) -> dict:
    settings = SettingsDraft.model_validate(input_data["settings"])
    write_json(input_data["settings_path"], settings.model_dump())
    return AppResult(success=True, data={"settings": settings.model_dump()}).model_dump()
