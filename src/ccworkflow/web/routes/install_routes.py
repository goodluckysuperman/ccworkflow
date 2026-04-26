from fastapi import APIRouter

from ccworkflow.services.install_preview_service import preview_install

router = APIRouter(prefix="/api/install", tags=["install"])


@router.post("/preview")
def api_preview_install(payload: dict) -> dict:
    return preview_install(payload)
