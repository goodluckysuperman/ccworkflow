import json
from pathlib import Path

from ccworkflow.services.root_init_service import ensure_root_ready


def test_ensure_root_ready_creates_expected_layout(tmp_path: Path) -> None:
    root = tmp_path / "collection"

    result = ensure_root_ready({"default_root": str(root)})

    assert result["success"] is True
    assert (root / "skills").exists()
    assert (root / "hooks").exists()
    assert (root / "mcp").exists()
    assert (root / "mixed").exists()
    assert (root / "install_records").exists()
    assert (root / "system" / "settings.json").exists()

    payload = json.loads((root / "system" / "settings.json").read_text(encoding="utf-8"))
    assert payload["collection_root"] == str(root)
