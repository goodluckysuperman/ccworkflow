from typing import Any

from pydantic import BaseModel, Field


class SettingsDraft(BaseModel):
    collection_root: str
    last_generate_mode: str = "form"
    last_install_scope: str = "project"
    last_filters: dict[str, Any] = Field(default_factory=lambda: {
        "keyword": "",
        "tags": [],
        "type": "all",
    })
