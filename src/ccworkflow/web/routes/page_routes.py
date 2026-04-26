from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ccworkflow.services.package_query_service import get_package_detail, list_packages

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    packages_result = list_packages({"keyword": "", "tags": [], "type": "all"})
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="packages_list.html",
        context={
            "title": "ccworkflow",
            "packages": packages_result["data"]["items"],
            "filters": packages_result["data"]["filters"],
        },
    )


@router.get("/packages", response_class=HTMLResponse)
def packages_page(request: Request, keyword: str = "", type: str = "all") -> HTMLResponse:
    packages_result = list_packages({"keyword": keyword, "tags": [], "type": type})
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="packages_list.html",
        context={
            "title": "配置包列表",
            "packages": packages_result["data"]["items"],
            "filters": packages_result["data"]["filters"],
        },
    )


@router.get("/packages/new", response_class=HTMLResponse)
def package_new_page(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="package_form.html",
        context={
            "title": "新建配置包",
            "mode": "create",
            "package": None,
            "manifest": None,
        },
    )


@router.get("/packages/{package_id}", response_class=HTMLResponse)
def package_detail_page(request: Request, package_id: str) -> HTMLResponse:
    detail_result = get_package_detail({"package_id": package_id})
    if not detail_result["success"]:
        return RedirectResponse(url="/packages", status_code=302)

    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="package_detail.html",
        context={
            "title": "配置包详情",
            "package": detail_result["data"]["package"],
            "manifest": detail_result["data"]["manifest"],
        },
    )


@router.get("/packages/{package_id}/edit", response_class=HTMLResponse)
def package_edit_page(request: Request, package_id: str) -> HTMLResponse:
    detail_result = get_package_detail({"package_id": package_id})
    if not detail_result["success"]:
        return RedirectResponse(url="/packages", status_code=302)

    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="package_form.html",
        context={
            "title": "编辑配置包",
            "mode": "edit",
            "package": detail_result["data"]["package"],
            "manifest": detail_result["data"]["manifest"],
        },
    )
