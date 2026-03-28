from __future__ import annotations

from envctl.utils.output import print_error, print_kv, print_success, print_warning


def test_print_success_outputs_ok_prefix(capsys) -> None:
    print_success("done")

    captured = capsys.readouterr()
    assert captured.out.strip() == "[OK] done"


def test_print_warning_outputs_warn_prefix(capsys) -> None:
    print_warning("careful")

    captured = capsys.readouterr()
    assert captured.out.strip() == "[WARN] careful"


def test_print_error_outputs_to_stderr(capsys) -> None:
    print_error("boom")

    captured = capsys.readouterr()
    assert captured.err.strip() == "boom"
    assert captured.out == ""


def test_print_kv_outputs_key_value_pair(capsys) -> None:
    print_kv("key", "value")

    captured = capsys.readouterr()
    assert captured.out.strip() == "key: value"
