import os
import socket
import threading
import webbrowser

import uvicorn

from ccworkflow.app.factory import create_app
from ccworkflow.app.runtime import DEFAULT_COLLECTION_ROOT
from ccworkflow.infra.time_gateway import now_iso
from ccworkflow.services.root_init_service import ensure_root_ready


def _pick_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_app(
    host: str = "127.0.0.1",
    port: int | None = None,
    open_browser: bool = True,
    run_server: bool = True,
) -> dict:
    root_result = ensure_root_ready({"default_root": str(DEFAULT_COLLECTION_ROOT)})
    actual_port = port or _pick_port()
    url = f"http://{host}:{actual_port}/"

    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    app = create_app()
    app.state.started_at = now_iso()
    app.state.collection_root = root_result["data"]["collection_root"]

    result = {
        "success": True,
        "data": {
            "host": host,
            "port": actual_port,
            "url": url,
            "collection_root": root_result["data"]["collection_root"],
        },
    }

    if run_server:
        uvicorn.run(app, host=host, port=actual_port)

    return result


def read_startup_options() -> dict:
    open_browser = os.environ.get("CCWORKFLOW_OPEN_BROWSER", "1") != "0"
    run_server = os.environ.get("CCWORKFLOW_RUN_SERVER", "1") != "0"
    port_value = os.environ.get("CCWORKFLOW_PORT")
    port = int(port_value) if port_value else None
    return {
        "host": os.environ.get("CCWORKFLOW_HOST", "127.0.0.1"),
        "port": port,
        "open_browser": open_browser,
        "run_server": run_server,
    }
