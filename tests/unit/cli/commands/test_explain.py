from __future__ import annotations

from envctl.cli.commands.explain import explain_command
from envctl.domain.resolution import ResolvedValue
from envctl.utils.masking import mask_value


def test_explain_command_outputs_detail_when_present(monkeypatch, capsys) -> None:
    item = ResolvedValue(
        key="PORT",
        value="abc",
        source="vault",
        masked=False,
        valid=False,
        detail="Expected an integer",
    )

    monkeypatch.setattr(
        "envctl.cli.commands.explain.run_explain",
        lambda key: ("context", item),
    )

    explain_command("PORT")

    captured = capsys.readouterr()
    output = captured.out

    assert "key: PORT" in output
    assert "source: vault" in output
    assert "value: abc" in output
    assert "valid: no" in output
    assert "detail: Expected an integer" in output


def test_explain_command_masks_sensitive_values(monkeypatch, capsys) -> None:
    item = ResolvedValue(
        key="API_KEY",
        value="super-secret",
        source="vault",
        masked=True,
        valid=True,
        detail=None,
    )

    monkeypatch.setattr(
        "envctl.cli.commands.explain.run_explain",
        lambda key: ("context", item),
    )

    explain_command("API_KEY")

    captured = capsys.readouterr()
    output = captured.out

    assert "key: API_KEY" in output
    assert f"value: {mask_value('super-secret')}" in output
    assert "valid: yes" in output
    assert "detail:" not in output
