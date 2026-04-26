from fastapi import APIRouter, Query

from ccworkflow.services.package_copy_service import copy_package
from ccworkflow.services.package_delete_service import delete_package
from ccworkflow.services.package_query_service import get_package_detail, list_packages
from ccworkflow.services.package_save_service import save_package

router = APIRouter(prefix="/api/packages", tags=["packages"])


@router.get("")
def api_list_packages(keyword: str = "", tags: list[str] | None = Query(default=None), type: str = "all") -> dict:
    return list_packages({"keyword": keyword, "tags": tags or [], "type": type})


@router.get("/{package_id}")
def api_get_package_detail(package_id: str) -> dict:
    return get_package_detail({"package_id": package_id})


@router.post("")
def api_create_package(payload: dict) -> dict:
    return save_package({"package": payload, "save_mode": "create"})


@router.put("/{package_id}")
def api_update_package(package_id: str, payload: dict) -> dict:
    payload["package_id"] = package_id
    return save_package({"package": payload, "save_mode": "update"})


@router.delete("/{package_id}")
def api_delete_package(package_id: str) -> dict:
    return delete_package({"package_id": package_id})


@router.post("/{package_id}/copy")
def api_copy_package(package_id: str, payload: dict) -> dict:
    return copy_package({"package_id": package_id, "new_name": payload["new_name"]})
