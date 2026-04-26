from pathlib import Path

from ccworkflow.app.bootstrap import read_startup_options, start_app


def test_start_app_can_build_startup_result_without_running_server(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("ccworkflow.app.bootstrap.DEFAULT_COLLECTION_ROOT", tmp_path / "collection")

    result = start_app(open_browser=False, run_server=False, port=8123)

    assert result["success"] is True
    assert result["data"]["port"] == 8123
    assert result["data"]["url"] == "http://127.0.0.1:8123/"


def test_read_startup_options_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("CCWORKFLOW_HOST", "127.0.0.1")
    monkeypatch.setenv("CCWORKFLOW_PORT", "9001")
    monkeypatch.setenv("CCWORKFLOW_OPEN_BROWSER", "0")
    monkeypatch.setenv("CCWORKFLOW_RUN_SERVER", "0")

    options = read_startup_options()

    assert options == {
        "host": "127.0.0.1",
        "port": 9001,
        "open_browser": False,
        "run_server": False,
    }


def test_read_startup_options_defaults(monkeypatch) -> None:
    monkeypatch.delenv("CCWORKFLOW_HOST", raising=False)
    monkeypatch.delenv("CCWORKFLOW_PORT", raising=False)
    monkeypatch.delenv("CCWORKFLOW_OPEN_BROWSER", raising=False)
    monkeypatch.delenv("CCWORKFLOW_RUN_SERVER", raising=False)

    options = read_startup_options()

    assert options["host"] == "127.0.0.1"
    assert options["port"] is None
    assert options["open_browser"] is True
    assert options["run_server"] is True
