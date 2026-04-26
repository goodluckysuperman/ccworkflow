from fastapi import APIRouter

from ccworkflow.services.generate_draft_service import generate_draft

router = APIRouter(prefix="/api/generate", tags=["generate"])


@router.post("/draft")
def api_generate_draft(payload: dict) -> dict:
    return generate_draft(payload)
