from typing import Any

from pydantic import BaseModel, Field

from ccworkflow.domain.enums import ObjectType


class PackageObjectDraft(BaseModel):
    object_id: str | None = None
    type: ObjectType
    name: str
    description: str = ""
    body: str | dict[str, Any]
    extra: dict[str, Any] = Field(default_factory=dict)


class ScriptDraft(BaseModel):
    script_id: str | None = None
    name: str
    source_path: str
    applies_to: list[str] = Field(default_factory=list)


class PackageDraft(BaseModel):
    package_id: str | None = None
    name: str
    summary: str = ""
    tags: list[str] = Field(default_factory=list)
    objects: list[PackageObjectDraft] = Field(default_factory=list)
    scripts: list[ScriptDraft] = Field(default_factory=list)


class ConflictItem(BaseModel):
    object_id: str
    type: ObjectType
    object_name: str
    target_file: str
    conflict_key: str
    reason: str


class InstallResolution(BaseModel):
    object_id: str
    action: str
