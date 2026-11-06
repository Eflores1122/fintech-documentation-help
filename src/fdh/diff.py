"""Explain what changed between two regulatory-year catalogs."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from fdh.catalog import load_catalog
from fdh.disclaimer import DISCLAIMER_ES
from fdh.models import Rule

# Fields that matter for an annual regulatory update. last_verified is reported
# separately so a re-read of the same obligation is not mistaken for a reform.
MATERIAL_FIELDS = (
    "title",
    "requirement",
    "check_hint",
    "fix_suggestion",
    "entity_types",
    "documents",
    "source_url",
    "source_name",
    "effective_date",
    "severity",
    "unverified",
    "unverified_detail",
    "supersedes",
    "superseded_by",
    "effective_from",
    "effective_to",
    "parameter_ids",
    "applies_if",
    "notes",
    "diff_note",
    "area",
    "min_strictness",
    "binding",
    "owner_role",
    "remediation_days",
    "evidence_expected",
    "procedure",
    "frameworks",
    "verified",
    "matcher",
)

FIELD_LABELS = {
    "title": "Título",
    "requirement": "Requisito",
    "check_hint": "Pista de revisión",
    "fix_suggestion": "Sugerencia de corrección",
    "entity_types": "Tipos de entidad",
    "documents": "Documentos esperados",
    "source_url": "URL oficial",
    "source_name": "Fuente",
    "effective_date": "Fecha de vigencia",
    "severity": "Severidad",
    "unverified": "Bandera UNVERIFIED",
    "unverified_detail": "Detalle UNVERIFIED",
    "supersedes": "Sustituye a",
    "superseded_by": "Sustituida por",
    "effective_from": "Vigencia desde",
    "effective_to": "Vigencia hasta",
    "parameter_ids": "Parámetros",
    "applies_if": "Condición de aplicación",
    "notes": "Notas",
    "diff_note": "Nota de cambio",
    "area": "Área",
    "min_strictness": "Estrictez mínima",
    "binding": "Vinculante en México",
    "owner_role": "Responsable sugerido",
    "remediation_days": "Plazo sugerido (días)",
    "evidence_expected": "Evidencia esperada",
    "procedure": "Procedimiento",
    "frameworks": "Marcos de referencia",
    "verified": "Verificada",
    "matcher": "Criterio determinístico",
}


def _canon(rule: Rule) -> dict[str, Any]:
    data = rule.model_dump(mode="json")
    data["entity_types"] = sorted(data["entity_types"])
    data["documents"] = sorted(data["documents"])
    return data


def diff_catalogs(year_a: int, year_b: int, rules_dir: Path | None = None) -> dict[str, Any]:
    return diff_rule_maps(
        {rule.id: rule for rule in load_catalog(year_a, rules_dir)},
        {rule.id: rule for rule in load_catalog(year_b, rules_dir)},
        year_a,
        year_b,
    )


def diff_as_of(start: date, end: date, rules_dir: Path | None = None) -> dict[str, Any]:
    from fdh.temporal import rules_as_of

    before, _notes_a = rules_as_of(start, rules_dir)
    after, _notes_b = rules_as_of(end, rules_dir)
    payload = diff_rule_maps(
        {rule.id: rule for rule in before},
        {rule.id: rule for rule in after},
        start.isoformat(),
        end.isoformat(),
    )
    payload["from_date"] = start.isoformat()
    payload["to_date"] = end.isoformat()
    return payload


def diff_rule_maps(
    before: dict[str, Rule],
    after: dict[str, Rule],
    year_a: int | str,
    year_b: int | str,
) -> dict[str, Any]:
    added_ids = sorted(set(after) - set(before))
    removed_ids = sorted(set(before) - set(after))
    modified: list[dict[str, Any]] = []
    revalidated: list[dict[str, str]] = []
    unchanged = 0
    for rule_id in sorted(set(before) & set(after)):
        old = _canon(before[rule_id])
        new = _canon(after[rule_id])
        changes = []
        for field in MATERIAL_FIELDS:
            if old.get(field) != new.get(field):
                changes.append(
                    {
                        "field": field,
                        "label": FIELD_LABELS.get(field, field),
                        "before": old.get(field),
                        "after": new.get(field),
                    }
                )
        if changes:
            modified.append(
                {
                    "id": rule_id,
                    "domain": after[rule_id].domain,
                    "title": after[rule_id].title,
                    "severity": after[rule_id].severity,
                    "diff_note": after[rule_id].diff_note,
                    "changes": changes,
                }
            )
        elif old.get("last_verified") != new.get("last_verified"):
            revalidated.append(
                {
                    "id": rule_id,
                    "before": str(old.get("last_verified")),
                    "after": str(new.get("last_verified")),
                }
            )
        else:
            unchanged += 1
    superseded_by = {rule.supersedes: rule.id for rule in after.values() if rule.supersedes}
    added = [_describe_added(after[rule_id]) for rule_id in added_ids]
    removed = [
        _describe_removed(before[rule_id], superseded_by.get(rule_id)) for rule_id in removed_ids
    ]
    return {
        "from_year": year_a,
        "to_year": year_b,
        "disclaimer": DISCLAIMER_ES,
        "summary": {
            "added": len(added),
            "removed": len(removed),
            "modified": len(modified),
            "revalidated": len(revalidated),
            "unchanged": unchanged,
            "rules_before": len(before),
            "rules_after": len(after),
        },
        "added": added,
        "removed": removed,
        "modified": modified,
        "revalidated": revalidated,
    }


def _describe_added(rule: Rule) -> dict[str, Any]:
    return {
        "id": rule.id,
        "domain": rule.domain,
        "title": rule.title,
        "severity": rule.severity,
        "effective_date": rule.effective_date.isoformat(),
        "source_name": rule.source_name,
        "source_url": rule.source_url,
        "requirement": rule.requirement,
        "supersedes": rule.supersedes,
        "diff_note": rule.diff_note,
        "unverified": rule.unverified,
        "explanation": _added_sentence(rule),
    }


def _added_sentence(rule: Rule) -> str:
    bits = [
        f"Nueva regla {rule.id} ({rule.severity}) en el dominio {rule.domain}, "
        f"vigente desde {rule.effective_date.isoformat()}.",
        f"Fuente: {rule.source_name}.",
    ]
    if rule.supersedes:
        bits.append(f"Sustituye a {rule.supersedes}.")
    if rule.diff_note:
        bits.append(rule.diff_note)
    elif rule.unverified:
        bits.append(f"Sigue marcada UNVERIFIED: {rule.unverified_detail}")
    return " ".join(bits)


def _describe_removed(rule: Rule, replaced_by: str | None) -> dict[str, Any]:
    explanation = f"La regla {rule.id} ({rule.title}) ya no está en el catálogo destino."
    if replaced_by:
        explanation += f" Fue sustituida por {replaced_by}."
    if rule.diff_note:
        explanation += " " + rule.diff_note
    return {
        "id": rule.id,
        "domain": rule.domain,
        "title": rule.title,
        "severity": rule.severity,
        "source_url": rule.source_url,
        "replaced_by": replaced_by,
        "diff_note": rule.diff_note,
        "explanation": explanation,
    }


def render_diff_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        f"# Diferencias del catálogo {payload['from_year']} → {payload['to_year']}",
        "",
        f"> {payload['disclaimer']}",
        "",
        (
            f"De {payload['from_year']} a {payload['to_year']}: "
            f"**{summary['added']}** reglas nuevas, **{summary['removed']}** eliminadas, "
            f"**{summary['modified']}** modificadas, **{summary['revalidated']}** solo "
            f"revalidadas (cambió `last_verified`) y **{summary['unchanged']}** sin cambio "
            f"material. El catálogo pasa de {summary['rules_before']} a "
            f"{summary['rules_after']} reglas."
        ),
        "",
        "## Qué cambió y por qué importa",
        "",
    ]
    if not payload["added"] and not payload["removed"] and not payload["modified"]:
        lines.append("No hay cambios materiales entre estos catálogos.")
        lines.append("")
    for item in payload["added"]:
        lines.extend(_added_md(item))
    for item in payload["removed"]:
        lines.extend(
            [
                f"### Eliminada: `{item['id']}`",
                "",
                item["explanation"],
                "",
                f"- Fuente que deja de usarse como ancla de esta regla: {item['source_url']}",
                "",
            ]
        )
    for item in payload["modified"]:
        lines.extend(_modified_md(item))
    if payload["revalidated"]:
        lines.append("## Solo cambió la fecha de verificación")
        lines.append("")
        for item in payload["revalidated"]:
            lines.append(f"- `{item['id']}`: {item['before']} → {item['after']}")
        lines.append("")
    lines.append(
        "Las reglas sin cambio material se conservan porque la obligación sigue vigente; "
        "un diff vacío en privacidad o PLD no significa que esos documentos dejen de revisarse."
    )
    lines.append("")
    return "\n".join(lines)


def _added_md(item: dict[str, Any]) -> list[str]:
    flag = " · UNVERIFIED" if item["unverified"] else ""
    rows = [
        f"### Añadida: `{item['id']}` ({item['severity']}{flag})",
        "",
        item["explanation"],
        "",
        f"- Dominio: `{item['domain']}`",
        f"- Vigencia: {item['effective_date']}",
        f"- Fuente: [{item['source_name']}]({item['source_url']})",
        f"- Requisito: {item['requirement']}",
        "",
    ]
    return rows


def _modified_md(item: dict[str, Any]) -> list[str]:
    rows = [
        f"### Modificada: `{item['id']}` ({item['severity']})",
        "",
        item["title"],
        "",
    ]
    if item.get("diff_note"):
        rows.append(item["diff_note"])
        rows.append("")
    for change in item["changes"]:
        before = _short(change["before"])
        after = _short(change["after"])
        rows.append(f"- **{change['label']}**: {before} → {after}")
    rows.append("")
    return rows


def _short(value: Any, limit: int = 280) -> str:
    if value is None:
        rendered = "—"
    elif isinstance(value, (dict, list)):
        rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        rendered = str(value)
    rendered = rendered.replace("\n", " ")
    if len(rendered) > limit:
        return rendered[: limit - 1] + "…"
    return rendered


def render_diff_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
