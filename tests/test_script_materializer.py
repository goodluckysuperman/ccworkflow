from ccworkflow.installers.script_materializer import materialize_scripts


def test_materialize_scripts_replaces_placeholders(tmp_path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()

    result = materialize_scripts(
        {
            "scope": "project",
            "project_root": str(project_root),
            "objects": [
                {
                    "object_id": "obj1",
                    "type": "skill",
                    "name": "demo-skill",
                    "body": "# Skill\nrun {{script:helper.py}}",
                    "extra": {},
                }
            ],
            "scripts": [
                {
                    "script_id": "script1",
                    "name": "helper.py",
                    "source_path": "D:/tmp/helper.py",
                    "applies_to": [],
                }
            ],
        }
    )

    assert result["success"] is True
    assert ".claude/scripts/helper.py" in result["data"]["resolved_objects"][0]["body"]
    assert result["data"]["copied_scripts"][0]["target_path"].endswith(".claude/scripts/helper.py")


def test_materialize_scripts_reports_missing_script(tmp_path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()

    result = materialize_scripts(
        {
            "scope": "project",
            "project_root": str(project_root),
            "objects": [
                {
                    "object_id": "obj1",
                    "type": "skill",
                    "name": "demo-skill",
                    "body": "# Skill\nrun {{script:missing.py}}",
                    "extra": {},
                }
            ],
            "scripts": [],
        }
    )

    assert result["success"] is False
    assert result["errors"][0]["code"] == "SCRIPT_REFERENCE_MISSING"
