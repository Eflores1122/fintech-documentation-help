"""Citation checks for the rule catalog.

A rule without an official https source, a source name, or a date is reported.
This module does not invent a URL, an article number, or a date.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from fdh.disclaimer import DISCLAIMER_EN, DISCLAIMER_ES

if TYPE_CHECKING:
    from fdh.models import Rule
    from fdh.parameters import Parameter

# Publishers of the Mexican instruments this catalog cites, plus INEGI (UMA).
OFFICIAL_HOSTS = frozenset(
    {
        "dof.gob.mx",
        "www.dof.gob.mx",
        "sidof.segob.gob.mx",
        "www.diputados.gob.mx",
        "www.sat.gob.mx",
        "wwwmat.sat.gob.mx",
        "www.cnbv.gob.mx",
        "www.banxico.org.mx",
        "www.gob.mx",
        "www.condusef.gob.mx",
        "uif.gob.mx",
        "www.uif.gob.mx",
        "www.inegi.org.mx",
    }
)

# Reference frameworks. They are not Mexican law.
REFERENCE_HOSTS = frozenset(
    {
        "www.iso.org",
        "www.nist.gov",
        "www.pcisecuritystandards.org",
        "www.aicpa-cima.com",
        "www.coso.org",
        "www.fatf-gafi.org",
    }
)

ALLOWED_HOSTS = OFFICIAL_HOSTS | REFERENCE_HOSTS


def source_host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def source_url_problem(url: str) -> str | None:
    """Return a Spanish error when the URL is not an allowed https citation."""
    if not url.startswith("https://"):
        return "source_url debe usar https. No se inventa una URL."
    host = source_host(url)
    if host not in ALLOWED_HOSTS:
        return (
            f"source_url usa el sitio {host!r}, que no está en la lista de fuentes "
            "oficiales ni de marcos de referencia. No se inventa otra URL."
        )
    return None


def citation_problem(url: str, source_name: str, label: str) -> str | None:
    url_problem = source_url_problem(url)
    if url_problem:
        return f"{label}: {url_problem}"
    if not source_name or not source_name.strip():
        return f"{label}: source_name está vacío. No se inventa el nombre de la fuente."
    return None


def _iso(value: date | None) -> str:
    if value is None:
        return "missing"
    return value.isoformat()


def render_citation_report(
    catalogs: dict[int, list[Rule]],
    parameters: list[Parameter],
) -> tuple[str, int]:
    """Text report and the count of rules or parameters that lack a citation."""
    lines = [
        DISCLAIMER_EN,
        "",
        DISCLAIMER_ES,
        "",
        "Citation check. Rules without an official https source, a source name, or a date "
        "are listed below. Nothing is invented to fill a gap.",
        "UNVERIFIED means the official URL and the dates are present and the unread "
        "article, rule number, or amount was left blank.",
        "",
    ]
    missing: list[str] = []
    unverified: list[str] = []
    for year, rules in sorted(catalogs.items()):
        year_missing = 0
        year_unverified = 0
        for rule in rules:
            rule_id = str(getattr(rule, "id", "?"))
            label = f"{year}/{rule_id}"
            problem = citation_problem(
                str(getattr(rule, "source_url", "")),
                str(getattr(rule, "source_name", "")),
                label,
            )
            effective = getattr(rule, "effective_date", None)
            verified_on = getattr(rule, "last_verified", None)
            if effective is None or verified_on is None:
                extra = (
                    f"{label}: falta effective_date ({_iso(effective)}) o "
                    f"last_verified ({_iso(verified_on)}). No se inventa la fecha."
                )
                problem = extra if problem is None else f"{problem} {extra}"
            if problem:
                missing.append(problem)
                year_missing += 1
                continue
            if getattr(rule, "unverified", False):
                year_unverified += 1
                unverified.append(
                    f"{label}  effective {_iso(effective)}  "
                    f"verified {_iso(verified_on)}  {rule.source_url}"
                )
        lines.append(
            f"{year}: {len(rules)} rules, {year_missing} missing source or date, "
            f"{year_unverified} UNVERIFIED"
        )
    param_missing = 0
    param_unverified: list[str] = []
    for item in parameters:
        label = f"parameter/{getattr(item, 'id', '?')}"
        problem = citation_problem(
            str(getattr(item, "source_url", "")),
            str(getattr(item, "source_name", "")),
            label,
        )
        if problem:
            missing.append(problem)
            param_missing += 1
            continue
        if getattr(item, "verified", True) is False:
            param_unverified.append(f"{label}  {item.source_url}")
    lines.append(f"parameters: {len(parameters)}, {param_missing} missing source")
    lines.append("")
    lines.append("MISSING SOURCE")
    lines.extend(missing or ["(none)"])
    lines.append("")
    lines.append(
        "UNVERIFIED (official source and dates are present; the article was not fully read)"
    )
    lines.extend(unverified or ["(none)"])
    lines.append("")
    lines.append("PARAMETERS UNVERIFIED (source present; numeric value not copied)")
    lines.extend(param_unverified or ["(none)"])
    lines.append("")
    return "\n".join(lines) + "\n", len(missing)
