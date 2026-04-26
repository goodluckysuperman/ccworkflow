from .generate_routes import router as generate_router
from .install_routes import router as install_router
from .package_routes import router as package_router
from .page_routes import router as page_router

__all__ = ["generate_router", "install_router", "package_router", "page_router"]
