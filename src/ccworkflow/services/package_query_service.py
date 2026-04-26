from pathlib import Path

from ccworkflow.app.runtime import get_collection_root
from ccworkflow.domain.common_schema import AppResult
from ccworkflow.repositories.package_repository import list_manifests, load_bundle


def list_packages(input_data: dict) -> dict:
    collection_root = get_collection_root()
    manifests = list_manifests({"collection_root": str(collection_root)})["data"]["items"]

    keyword = input_data.get("keyword", "").strip().lower()
    tags = set(input_data.get("tags", []))
    target_type = input_data.get("type", "all")

    filtered: list[dict] = []
    for item in manifests:
        haystack = " ".join([item["name"], item.get("summary", ""), " ".join(item.get("tags", []))]).lower()
        if keyword and keyword not in haystack:
            continue
        if tags and not tags.issubset(set(item.get("tags", []))):
            continue
        if target_type != "all" and target_type != item.get("category") and target_type not in item.get("object_types", []):
            continue
        filtered.append(item)

    return AppResult(
        success=True,
        data={
            "items": filtered,
            "total": len(filtered),
            "filters": {
                "keyword": input_data.get("keyword", ""),
                "tags": input_data.get("tags", []),
                "type": target_type,
            },
        },
    ).model_dump()


def get_package_detail(input_data: dict) -> dict:
    package_id = input_data["package_id"]
    collection_root = get_collection_root()

    for category in ["skills", "hooks", "mcp", "mixed"]:
        package_dir = Path(collection_root) / category / package_id
        if package_dir.exists():
            bundle = load_bundle({"package_dir": str(package_dir)})["data"]["bundle"]
            return AppResult(success=True, data={"package": bundle["package"], "manifest": bundle["manifest"]}).model_dump()

    return AppResult(success=False, message="配置包不存在").model_dump()
