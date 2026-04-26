from pydantic import BaseModel, Field


class InstallRecordDraft(BaseModel):
    install_record_id: str
    package_id: str
    scope: str
    project_root: str | None = None
    installed_objects: list[str] = Field(default_factory=list)
    skipped_objects: list[str] = Field(default_factory=list)
    failed_objects: list[str] = Field(default_factory=list)
    written_files: list[str] = Field(default_factory=list)
    copied_scripts: list[str] = Field(default_factory=list)
