import shutil
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ccworkflow.app import runtime
from ccworkflow.services.root_init_service import ensure_root_ready


@pytest.fixture(autouse=True)
def collection_root_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "collection"
    ensure_root_ready({"default_root": str(root)})
    monkeypatch.setattr(runtime, "DEFAULT_COLLECTION_ROOT", root)
    yield root
    shutil.rmtree(root, ignore_errors=True)
