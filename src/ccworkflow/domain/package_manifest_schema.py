from pydantic import BaseModel, Field

from ccworkflow.domain.package_schema import PackageDraft


class ScriptMeta(BaseModel):
    script_id: str
    name: str
    stored_filename: str
    applies_to: list[str] = Field(default_factory=list)


class PackageManifest(BaseModel):
    package_id: str
    name: str
    summary: str = ""
    tags: list[str] = Field(default_factory=list)
    category: str
    object_types: list[str] = Field(default_factory=list)
    object_ids: list[str] = Field(default_factory=list)
    script_ids: list[str] = Field(default_factory=list)
    scripts_meta: list[ScriptMeta] = Field(default_factory=list)
    created_at: str
    updated_at: str
    status: str = "saved"


class PackageBundle(BaseModel):
    package: PackageDraft
    manifest: PackageManifest
    package_dir: str
