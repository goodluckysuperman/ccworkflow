from fastapi import APIRouter

from ccworkflow.services.record_query_service import get_install_record_detail, list_install_records

router = APIRouter(prefix="/api/install-records", tags=["install-records"])


@router.get("")
def api_list_install_records() -> dict:
    return list_install_records({})


@router.get("/{install_record_id}")
def api_get_install_record_detail(install_record_id: str) -> dict:
    return get_install_record_detail({"install_record_id": install_record_id})
