from typing import Any

from pydantic import BaseModel, Field


class AppError(BaseModel):
    code: str
    field: str | None = None
    target: str | None = None
    detail: str


class AppResult(BaseModel):
    success: bool
    message: str = ""
    errors: list[AppError] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
