from pathlib import Path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from ccworkflow.web.routes.page_routes import router as page_router


def create_app() -> FastAPI:
    app = FastAPI(title="ccworkflow")
    template_dir = Path(__file__).resolve().parent.parent / "web" / "templates"
    app.state.templates = Jinja2Templates(directory=str(template_dir))
    app.include_router(page_router)
    return app
