from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src" / "envctl"


class LegacyLoggingVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "logging":
                self.violations.append("import logging")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module == "logging":
            imported_names = ", ".join(alias.name for alias in node.names)
            self.violations.append(f"from logging import {imported_names}")
        if node.module == "envctl.utils.logging":
            self.violations.append("from envctl.utils.logging import ...")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "logging"
            and func.attr == "getLogger"
        ):
            self.violations.append("logging.getLogger(...)")
        self.generic_visit(node)

    def visit_arg(self, node: ast.arg) -> None:
        annotation = node.annotation
        if isinstance(annotation, ast.Name) and annotation.id == "Logger":
            self.violations.append(f"Logger annotation on argument {node.arg}")
        self.generic_visit(node)


def test_production_code_outside_observability_has_no_legacy_logging() -> None:
    violations: list[str] = []

    for path in sorted(SRC_ROOT.rglob("*.py")):
        relative = path.relative_to(SRC_ROOT)
        if relative.parts[0] == "observability":
            continue

        visitor = LegacyLoggingVisitor()
        visitor.visit(ast.parse(path.read_text(encoding="utf-8"), filename=str(path)))
        violations.extend(f"{relative}: {message}" for message in visitor.violations)

    assert violations == []
