from pydantic import BaseModel, Field


class InstallRecordDraft(BaseModel):
    install_record_id: str
    package_id: str
    scope: str
    project_root: str | None = None
    installed_at: str | None = None
    install_status: str = "success"
    uninstall_status: str = "not_uninstalled"
    installed_objects: list[str] = Field(default_factory=list)
    skipped_objects: list[str] = Field(default_factory=list)
    failed_objects: list[str] = Field(default_factory=list)
    written_files: list[str] = Field(default_factory=list)
    copied_scripts: list[str] = Field(default_factory=list)
    conflict_resolutions: list[dict] = Field(default_factory=list)
    entries: list[dict] = Field(default_factory=list)
