import socket
import threading
import webbrowser
from pathlib import Path

import uvicorn

from ccworkflow.app.factory import create_app
from ccworkflow.infra.time_gateway import now_iso
from ccworkflow.services.root_init_service import ensure_root_ready


def _pick_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_app(host: str = "127.0.0.1", port: int | None = None, open_browser: bool = True) -> dict:
    root_result = ensure_root_ready({"default_root": "D:/Programming_tools/.ccworkflow"})
    actual_port = port or _pick_port()
    url = f"http://{host}:{actual_port}/"

    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    app = create_app()
    app.state.started_at = now_iso()
    app.state.collection_root = root_result["data"]["collection_root"]
    uvicorn.run(app, host=host, port=actual_port)

    return {
        "success": True,
        "data": {
            "host": host,
            "port": actual_port,
            "url": url,
            "collection_root": root_result["data"]["collection_root"],
        },
    }
