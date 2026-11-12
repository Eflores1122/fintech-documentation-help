"""Dated parameters. Missing rows are reported. They are never filled in."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator

from fdh.catalog import locate_rules_dir
from fdh.citations import source_url_problem


class ParameterValue(BaseModel):
    effective_from: date
    effective_to: date | None = None
    value: float | int | str
    note: str | None = None

    def covers(self, on: date) -> bool:
        ended = self.effective_to is not None and on > self.effective_to
        return on >= self.effective_from and not ended


class Parameter(BaseModel):
    id: str
    title: str
    unit: str
    source_url: str
    source_name: str
    verified: bool = False
    unverified_detail: str | None = None
    used_by: list[str] = Field(default_factory=list)
    values: list[ParameterValue] = Field(default_factory=list)

    @field_validator("source_url")
    @classmethod
    def https_url(cls, value: str) -> str:
        problem = source_url_problem(value)
        if problem:
            raise ValueError(problem)
        return value

    @field_validator("source_name")
    @classmethod
    def source_named(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("source_name no puede estar vacío. No se inventa el nombre.")
        return value.strip()

    def at(self, on: date) -> ParameterValue | None:
        hits = [item for item in self.values if item.covers(on)]
        if not hits:
            return None
        return max(hits, key=lambda item: item.effective_from)


class ParameterBook(BaseModel):
    disclaimer: str
    parameters: list[Parameter]


def load_parameters(rules_dir: Path | None = None) -> list[Parameter]:
    root = locate_rules_dir(rules_dir)
    path = root / "parameters.yaml"
    if not path.is_file():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    book = ParameterBook.model_validate(raw)
    return book.parameters


def resolve_parameters(
    on: date,
    active_rule_ids: set[str],
    rules_dir: Path | None = None,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Return (values in force, gaps). A gap is explicit. No number is invented."""
    values: list[dict[str, object]] = []
    gaps: list[dict[str, object]] = []
    for item in load_parameters(rules_dir):
        if item.used_by and not (set(item.used_by) & active_rule_ids):
            continue
        chosen = item.at(on)
        base = {
            "id": item.id,
            "title": item.title,
            "unit": item.unit,
            "source_name": item.source_name,
            "source_url": item.source_url,
            "verified": item.verified,
            "unverified_detail": item.unverified_detail,
        }
        if chosen is None:
            gaps.append(
                {
                    **base,
                    "as_of": on.isoformat(),
                    "message": (
                        f"No hay valor de «{item.title}» vigente el {on.isoformat()}. "
                        "No se usó un monto de otro año."
                    ),
                }
            )
            continue
        values.append(
            {
                **base,
                "as_of": on.isoformat(),
                "value": chosen.value,
                "effective_from": chosen.effective_from.isoformat(),
                "effective_to": chosen.effective_to.isoformat() if chosen.effective_to else None,
                "note": chosen.note,
            }
        )
    return values, gaps
