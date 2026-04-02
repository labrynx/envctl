from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from envctl.cli.app import app


def test_json_string_value_survives_set_unset_rewrites(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)
    runner.invoke(app, ["init", "--contract", "starter"], catch_exceptions=False)

    runner.invoke(app, ["set", "APP_NAME", "demo"], catch_exceptions=False)
    runner.invoke(app, ["set", "DATABASE_URL", "https://db.example.com"], catch_exceptions=False)
    runner.invoke(
        app,
        ["add", "TEST_JSON", '["one","two"]', "--type", "string"],
        catch_exceptions=False,
    )

    before = runner.invoke(app, ["inspect"], catch_exceptions=False)
    assert before.exit_code == 0
    assert 'TEST_JSON = ["one","two"] (vault)' in before.stdout

    runner.invoke(app, ["set", "PORT", "1234"], catch_exceptions=False)
    runner.invoke(app, ["unset", "PORT"], catch_exceptions=False)

    after = runner.invoke(app, ["inspect"], catch_exceptions=False)
    assert after.exit_code == 0
    assert 'TEST_JSON = ["one","two"] (vault)' in after.stdout

    output_path = workspace / "roundtrip-json.txt"
    script = (
        "from pathlib import Path; "
        "import os; "
        f"Path({str(output_path)!r}).write_text(os.getenv('TEST_JSON', ''), encoding='utf-8')"
    )

    run = runner.invoke(app, ["run", "python3", "-c", script], catch_exceptions=False)
    assert run.exit_code == 0
    assert output_path.read_text(encoding="utf-8") == '["one","two"]'
