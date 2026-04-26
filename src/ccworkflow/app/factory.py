from pathlib import Path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from ccworkflow.web.routes.generate_routes import router as generate_router
from ccworkflow.web.routes.install_routes import router as install_router
from ccworkflow.web.routes.package_routes import router as package_router
from ccworkflow.web.routes.page_routes import router as page_router


def create_app() -> FastAPI:
    app = FastAPI(title="ccworkflow")
    template_dir = Path(__file__).resolve().parent.parent / "web" / "templates"
    app.state.templates = Jinja2Templates(directory=str(template_dir))
    app.include_router(page_router)
    app.include_router(package_router)
    app.include_router(generate_router)
    app.include_router(install_router)
    return app
