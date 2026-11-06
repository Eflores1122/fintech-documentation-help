"""Command line: fdh audit, fdh rules, fdh serve."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fdh import __version__
from fdh.catalog import (
    CatalogError,
    available_years,
    load_catalog,
    locate_rules_dir,
    validate_catalogs,
)
from fdh.diff import diff_catalogs, render_diff_json, render_diff_markdown
from fdh.disclaimer import DISCLAIMER_ES
from fdh.engine.audit import run_audit
from fdh.models import SEVERITY_RANK, canonical_entity
from fdh.report.render import write_reports


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except CatalogError as exc:
        print(DISCLAIMER_ES, file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fdh",
        description=(
            "Auditor de documentación para fintechs mexicanas (ITF). "
            "No es asesoría legal ni fiscal."
        ),
        epilog=DISCLAIMER_ES,
    )
    parser.add_argument("--version", action="version", version=f"fdh {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="Auditar un archivo o carpeta de documentos")
    audit.add_argument("path", type=Path, help="Archivo o directorio (PDF, DOCX, MD, TXT, HTML)")
    audit.add_argument("--year", type=int, default=2026, help="Año del catálogo regulatorio")
    audit.add_argument("--entity", default="IFPE", help="IFPE, IFC, ITF, fintech_general, …")
    audit.add_argument("--out", type=Path, default=Path("fdh-report"))
    audit.add_argument("--format", default="md,html,json", help="md,html,json separados por coma")
    audit.add_argument("--rules-dir", type=Path, default=None)
    audit.add_argument(
        "--llm",
        action="store_true",
        help="Enviar texto al revisor LLM (requiere FDH_LLM_API_KEY). Apagado por defecto.",
    )
    audit.add_argument("--operates-virtual-assets", action="store_true")
    audit.add_argument("--partial-payments", action="store_true")
    audit.add_argument("--transports-goods", action="store_true")
    audit.add_argument("--tech-platform", action="store_true")
    audit.add_argument("--digital-services", action="store_true")
    audit.add_argument(
        "--fail-on",
        choices=["critical", "high", "medium", "low", "info"],
        default=None,
        help="Código de salida 1 si hay un incumplimiento de esta severidad o peor",
    )
    audit.set_defaults(handler=_cmd_audit)

    rules = sub.add_parser("rules", help="Catálogo versionado")
    rules_sub = rules.add_subparsers(dest="rules_command", required=True)

    diff = rules_sub.add_parser("diff", help="Explicar qué cambió entre dos años")
    diff.add_argument("year_a", type=int)
    diff.add_argument("year_b", type=int)
    diff.add_argument("--format", choices=["md", "json"], default="md")
    diff.add_argument("--rules-dir", type=Path, default=None)
    diff.set_defaults(handler=_cmd_diff)

    listing = rules_sub.add_parser("list", help="Listar reglas de un año")
    listing.add_argument("--year", type=int, default=2026)
    listing.add_argument("--domain", default=None)
    listing.add_argument("--rules-dir", type=Path, default=None)
    listing.set_defaults(handler=_cmd_list)

    validate = rules_sub.add_parser("validate", help="Validar los YAML del catálogo")
    validate.add_argument("--rules-dir", type=Path, default=None)
    validate.set_defaults(handler=_cmd_validate)

    changed = sub.add_parser(
        "what-changed",
        help="Atajo de fdh rules diff (año-1 → año)",
    )
    changed.add_argument("--year", type=int, default=2026)
    changed.add_argument("--format", choices=["md", "json"], default="md")
    changed.add_argument("--rules-dir", type=Path, default=None)
    changed.set_defaults(handler=_cmd_what_changed)

    serve = sub.add_parser("serve", help="Interfaz web local para subir documentos")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.set_defaults(handler=_cmd_serve)
    return parser


def _cmd_audit(args: argparse.Namespace) -> int:
    from fdh.models import Profile

    if not args.path.exists():
        print(f"No existe la ruta: {args.path}", file=sys.stderr)
        return 2
    profile = Profile(
        entity_type=canonical_entity(args.entity),
        year=args.year,
        operates_virtual_assets=args.operates_virtual_assets,
        has_partial_or_deferred_payments=args.partial_payments,
        transports_goods=args.transports_goods,
        is_technological_platform_tax_regime=args.tech_platform,
        provides_digital_services_liva=args.digital_services,
    )
    report = run_audit(
        [args.path],
        profile,
        rules_dir=args.rules_dir,
        use_llm=args.llm,
    )
    formats = [item.strip() for item in str(args.format).split(",")]
    written = write_reports(report, args.out, formats)
    _print_summary(report, written)
    if args.fail_on is None:
        return 0
    threshold = SEVERITY_RANK[args.fail_on]
    for finding in report.findings:
        if finding.status == "fail" and SEVERITY_RANK[finding.severity] <= threshold:
            return 1
    return 0


def _print_summary(report, written: list[Path]) -> None:
    print(report.disclaimer)
    print()
    overall = "n/a" if report.scores.overall is None else f"{report.scores.overall:.1f}"
    print(
        f"{report.entity_type} · catálogo {report.catalog_year} · puntaje {overall}/100 · "
        f"incumplimientos {report.summary.get('fail', 0)} "
        f"(críticos {report.summary.get('fail_critical', 0)}, "
        f"altos {report.summary.get('fail_high', 0)}) · "
        f"UNVERIFIED {report.summary.get('unverified', 0)}"
    )
    if report.llm_note:
        print(report.llm_note)
    for path in written:
        print(f"reporte: {path}")


def _cmd_diff(args: argparse.Namespace) -> int:
    payload = diff_catalogs(args.year_a, args.year_b, args.rules_dir)
    rendered = render_diff_json(payload) if args.format == "json" else render_diff_markdown(payload)
    sys.stdout.write(rendered)
    return 0


def _cmd_what_changed(args: argparse.Namespace) -> int:
    args.year_a = args.year - 1
    args.year_b = args.year
    return _cmd_diff(args)


def _cmd_list(args: argparse.Namespace) -> int:
    rules = load_catalog(args.year, args.rules_dir)
    counts: dict[str, int] = {}
    unverified = 0
    for rule in rules:
        counts[rule.domain] = counts.get(rule.domain, 0) + 1
        if args.domain and rule.domain != args.domain:
            continue
        flag = " UNVERIFIED" if rule.unverified else ""
        print(f"[{rule.severity}{flag}] {rule.id}  {rule.title}")
        if rule.unverified:
            unverified += 1
    print()
    print(f"{len(rules)} reglas en {args.year}")
    for domain in sorted(counts):
        print(f"  {domain}: {counts[domain]}")
    total_unverified = sum(1 for rule in rules if rule.unverified)
    print(f"  UNVERIFIED: {total_unverified}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    root = locate_rules_dir(args.rules_dir)
    print(f"Catálogos en {root}")
    print("Años:", ", ".join(str(year) for year in available_years(root)))
    notes = validate_catalogs(root)
    # validate_catalogs returns notes on success (including UNVERIFIED lines) or errors.
    # Errors are raised as CatalogError by load_all_catalogs and caught in main...
    # except validate_catalogs swallows CatalogError and returns the error strings.
    problems = [line for line in notes if not _is_info(line)]
    for line in notes:
        print(line)
    if problems:
        return 1
    print("Catálogo válido. Las líneas UNVERIFIED son intencionales y deben permanecer visibles.")
    return 0


def _is_info(line: str) -> bool:
    if line.startswith("UNVERIFIED "):
        return True
    head, _, tail = line.partition(":")
    return head.isdigit() and tail.strip().endswith("reglas")


def _cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    print(DISCLAIMER_ES)
    print(
        f"Interfaz local en http://{args.host}:{args.port} "
        "(no envía documentos a un LLM salvo que lo active)"
    )
    uvicorn.run("fdh.web:app", host=args.host, port=args.port, reload=False)
    return 0
