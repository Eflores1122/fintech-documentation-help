"""Select the rule snapshot in force on a date. Years are derived views."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fdh.catalog import available_years, load_catalog
from fdh.models import Rule


def snapshot_year(on: date, rules_dir: Path | None = None) -> int | None:
    """Latest catalog year whose 1 January is on or before ``on``."""
    eligible = [year for year in available_years(rules_dir) if date(year, 1, 1) <= on]
    if not eligible:
        return None
    return max(eligible)


def rules_as_of(on: date, rules_dir: Path | None = None) -> tuple[list[Rule], list[str]]:
    """Rules from the snapshot in force, filtered by each rule's own window.

    A later date with no newer snapshot reuses the latest one. It does not
    invent reforms. Rules whose ``effective_from`` is still in the future, or
    whose ``effective_to`` has passed, drop out. If another active rule lists
    this id in ``supersedes``, this id drops out too.
    """
    year = snapshot_year(on, rules_dir)
    if year is None:
        known = ", ".join(str(item) for item in available_years(rules_dir)) or "(ninguno)"
        return [], [
            f"No hay snapshot de catálogo con inicio en o antes del {on.isoformat()}. "
            f"Años publicados: {known}. No se inventó un catálogo."
        ]
    rules = load_catalog(year, rules_dir)
    notes = [
        f"Fecha de auditoría {on.isoformat()}. Snapshot usado: {year}. "
        "Los años posteriores a esa fecha no se anticipan."
    ]
    if year < on.year:
        notes.append(
            f"No hay snapshot {on.year}. Se reutiliza {year} solo en las reglas que siguen "
            "vigentes. Los parámetros sin fila para esta fecha se listan aparte."
        )
    active = [rule for rule in rules if rule.in_force(on)]
    superseded = {rule.supersedes for rule in active if rule.supersedes and rule.in_force(on)}
    kept: list[Rule] = []
    for rule in active:
        if rule.id in superseded:
            notes.append(
                f"{rule.id} no aplica el {on.isoformat()}: la sustituye una regla vigente."
            )
            continue
        if rule.superseded_by:
            notes.append(
                f"{rule.id} está marcada superseded_by={rule.superseded_by} "
                f"y no aplica el {on.isoformat()}."
            )
            continue
        kept.append(rule)
    dropped = len(rules) - len(kept)
    if dropped:
        notes.append(f"{dropped} reglas del snapshot {year} no están vigentes en esa fecha.")
    return kept, notes


def explain_applicability(
    rules: list[Rule],
    findings_status: dict[str, str],
    omitted: list[dict[str, str]],
    entity: str,
    on: date | None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    omitted_ids = {item["id"]: item["reason"] for item in omitted}
    for rule in rules:
        if rule.id in omitted_ids:
            rows.append(
                {
                    "rule_id": rule.id,
                    "applies": False,
                    "reason": omitted_ids[rule.id],
                }
            )
            continue
        status = findings_status.get(rule.id)
        if status == "not_applicable":
            rows.append(
                {
                    "rule_id": rule.id,
                    "applies": False,
                    "reason": (
                        f"El perfil no activó `{rule.applies_if}`. "
                        "La regla existe, pero este negocio no declaró ese supuesto."
                    ),
                }
            )
            continue
        start = rule.effective_from or rule.effective_date
        window = f"desde {start.isoformat()}"
        if rule.effective_to:
            window += f" hasta {rule.effective_to.isoformat()}"
        when = f" el {on.isoformat()}" if on else ""
        rows.append(
            {
                "rule_id": rule.id,
                "applies": True,
                "reason": (
                    f"Aplica a {entity}{when} ({window}) porque la regla lista "
                    + ", ".join(rule.entity_types)
                    + "."
                ),
            }
        )
    for rule_id, reason in omitted_ids.items():
        if any(row["rule_id"] == rule_id for row in rows):
            continue
        rows.append({"rule_id": rule_id, "applies": False, "reason": reason})
    return rows
