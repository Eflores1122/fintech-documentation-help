"""Command line: fdh audit, fdh rules, fdh serve."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fdh import __version__
from fdh.catalog import (
    CatalogError,
    available_years,
    load_all_catalogs,
    load_catalog,
    locate_rules_dir,
    validate_catalogs,
)
from fdh.citations import render_citation_report
from fdh.diff import diff_catalogs, render_diff_json, render_diff_markdown
from fdh.disclaimer import DISCLAIMER_EN, DISCLAIMER_ES
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
    audit.add_argument(
        "--year",
        type=int,
        default=None,
        help="Snapshot de un año. Si se omite y no hay --as-of, la fecha es hoy.",
    )
    audit.add_argument(
        "--as-of",
        default=None,
        help="Auditar a una fecha ISO (ejemplo 2031-03-15). Por defecto, hoy, si no hay --year.",
    )
    audit.add_argument("--entity", default="IFPE", help="IFPE, IFC, ITF, fintech_general, …")
    audit.add_argument("--out", type=Path, default=Path("fdh-report"))
    audit.add_argument(
        "--format",
        default="md,html,json",
        help="md,html,json,csv,xlsx,pdf,ics,diagrams separados por coma",
    )
    audit.add_argument(
        "--strictness",
        choices=["standard", "high", "max"],
        default="max",
        help="max es el auditor más exigente y es el default",
    )
    audit.add_argument("--compare", type=Path, default=None, help="JSON de una auditoría anterior")
    audit.add_argument(
        "--evidence", type=Path, default=None, help="JSON rule_id -> presente|ausente|parcial"
    )
    audit.add_argument(
        "--adversarial",
        action="store_true",
        help="Pide al LLM local más fallas, sin bajar severidad",
    )
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
    audit.add_argument("--processes-cards", action="store_true")
    audit.add_argument("--participates-spei", action="store_true")
    audit.add_argument("--specialized-services", action="store_true")
    audit.add_argument("--offers-credit", action="store_true")
    audit.add_argument("--offers-yield", action="store_true")
    audit.add_argument("--related-parties-abroad", action="store_true")
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
    diff.add_argument("year_a", type=int, nargs="?")
    diff.add_argument("year_b", type=int, nargs="?")
    diff.add_argument("--from", dest="date_from", default=None, help="Fecha ISO inicial")
    diff.add_argument("--to", dest="date_to", default=None, help="Fecha ISO final")
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

    citations = rules_sub.add_parser(
        "citations",
        help="Listar reglas sin fuente oficial o sin fecha. No inventa URLs.",
    )
    citations.add_argument("--rules-dir", type=Path, default=None)
    citations.set_defaults(handler=_cmd_citations)

    new_year = rules_sub.add_parser(
        "new-year", help="Clonar un catálogo al año siguiente y abrir checklist"
    )
    new_year.add_argument("year", type=int)
    new_year.add_argument("--rules-dir", type=Path, default=None)
    new_year.set_defaults(handler=_cmd_new_year)

    watch = rules_sub.add_parser("watch", help="Comparar fuentes oficiales contra el candado local")
    watch.add_argument("--rules-dir", type=Path, default=None)
    watch.add_argument("--lock", type=Path, default=None)
    watch.set_defaults(handler=_cmd_watch)

    changed = sub.add_parser(
        "what-changed",
        help="Atajo de fdh rules diff (año-1 → año)",
    )
    changed.add_argument("--year", type=int, default=2026)
    changed.add_argument("--format", choices=["md", "json"], default="md")
    changed.add_argument("--rules-dir", type=Path, default=None)
    changed.set_defaults(handler=_cmd_what_changed)

    diagrams = sub.add_parser("diagrams", help="Generar diagramas Mermaid y SVG")
    diagrams.add_argument("--out", type=Path, default=Path("fdh-diagramas"))
    diagrams.set_defaults(handler=_cmd_diagrams)

    templates = sub.add_parser(
        "templates", help="Borradores de políticas para que los revise un abogado"
    )
    templates.add_argument("--out", type=Path, default=Path("fdh-plantillas"))
    templates.add_argument("--only", default=None)
    templates.set_defaults(handler=_cmd_templates)

    calendar = sub.add_parser("calendar", help="Recordatorios .ics")
    calendar.add_argument("--year", type=int, default=2026)
    calendar.add_argument("--entity", default="IFPE")
    calendar.add_argument("--out", type=Path, default=Path("obligaciones.ics"))
    calendar.set_defaults(handler=_cmd_calendar)

    ask = sub.add_parser(
        "ask", help="Preguntar al catálogo (léxico local; embeddings solo en Ollama)"
    )
    ask.add_argument("question")
    ask.add_argument("--year", type=int, default=2026)
    ask.add_argument("--rules-dir", type=Path, default=None)
    ask.set_defaults(handler=_cmd_ask)

    doctor = sub.add_parser("llm", help="IA local")
    doctor_sub = doctor.add_subparsers(dest="llm_command", required=True)
    doctor_cmd = doctor_sub.add_parser("doctor", help="Ver proveedor local y modelos sugeridos")
    doctor_cmd.set_defaults(handler=_cmd_doctor)

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
    from datetime import date

    as_of = None
    year = args.year
    if args.as_of:
        as_of = date.today() if args.as_of == "today" else date.fromisoformat(args.as_of)
        year = as_of.year
    elif year is None:
        as_of = date.today()
        year = as_of.year
    profile = Profile(
        entity_type=canonical_entity(args.entity),
        year=year,
        as_of=as_of,
        operates_virtual_assets=args.operates_virtual_assets,
        has_partial_or_deferred_payments=args.partial_payments,
        transports_goods=args.transports_goods,
        is_technological_platform_tax_regime=args.tech_platform,
        provides_digital_services_liva=args.digital_services,
        processes_cards=args.processes_cards,
        participates_spei=args.participates_spei,
        uses_specialized_services=args.specialized_services,
        offers_credit=args.offers_credit,
        offers_yield=args.offers_yield,
        has_related_parties_abroad=args.related_parties_abroad,
        strictness=args.strictness,
    )
    previous = None
    if args.compare is not None:
        import json

        previous = json.loads(args.compare.read_text(encoding="utf-8"))
    evidence = None
    if args.evidence is not None:
        import json

        raw_marks = json.loads(args.evidence.read_text(encoding="utf-8"))
        evidence = {str(key): str(value) for key, value in raw_marks.items()}
    report = run_audit(
        [args.path],
        profile,
        rules_dir=args.rules_dir,
        use_llm=args.llm or args.adversarial,
        evidence=evidence,
        previous=previous,
        adversarial=args.adversarial,
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
    if report.disclaimer_en:
        print(report.disclaimer_en)
    print()
    overall = "n/a" if report.scores.overall is None else f"{report.scores.overall:.1f}"
    print(
        f"{report.entity_type} · catálogo {report.catalog_year} · puntaje {overall}/100 · "
        f"incumplimientos {report.summary.get('fail', 0)} "
        f"(críticos {report.summary.get('fail_critical', 0)}, "
        f"altos {report.summary.get('fail_high', 0)}) · "
        f"UNVERIFIED {report.summary.get('unverified', 0)} · "
        f"dictamen {report.opinion.get('label', '')}"
    )
    if report.llm_note:
        print(report.llm_note)
    for path in written:
        print(f"reporte: {path}")


def _cmd_diff(args: argparse.Namespace) -> int:
    from datetime import date

    from fdh.diff import diff_as_of

    date_from = getattr(args, "date_from", None)
    date_to = getattr(args, "date_to", None)
    if date_from or date_to:
        if not date_from or not date_to:
            print("Indique --from y --to con fechas ISO.", file=sys.stderr)
            return 2
        payload = diff_as_of(
            date.fromisoformat(date_from),
            date.fromisoformat(date_to),
            args.rules_dir,
        )
    elif args.year_a is None or args.year_b is None:
        print("Indique dos años o --from y --to.", file=sys.stderr)
        return 2
    else:
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


def _cmd_citations(args: argparse.Namespace) -> int:
    from pydantic import ValidationError

    from fdh.parameters import load_parameters

    try:
        catalogs = load_all_catalogs(args.rules_dir)
        parameters = load_parameters(args.rules_dir)
    except (CatalogError, ValidationError) as exc:
        print(DISCLAIMER_EN)
        print(DISCLAIMER_ES)
        print()
        print("MISSING SOURCE")
        print(exc)
        print("No se inventó una URL.")
        return 1
    text, missing = render_citation_report(catalogs, parameters)
    sys.stdout.write(text)
    return 1 if missing else 0


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


def _cmd_new_year(args: argparse.Namespace) -> int:
    from fdh.rules_admin import start_new_year

    target = start_new_year(args.year, args.rules_dir)
    print(f"Catálogo clonado en {target}")
    print(f"Checklist: {target / 'CHECKLIST.md'}")
    print("Revise las fuentes oficiales antes de tratar el año nuevo como cerrado.")
    return 0


def _cmd_watch(args: argparse.Namespace) -> int:
    from fdh.watch import run_watch

    code, text = run_watch(args.rules_dir, args.lock)
    sys.stdout.write(text)
    return code


def _cmd_diagrams(args: argparse.Namespace) -> int:
    from fdh.diagrams import write_diagrams

    written = write_diagrams(args.out)
    for path in written:
        print(path)
    return 0


def _cmd_templates(args: argparse.Namespace) -> int:
    from fdh.templates_lib import write_templates

    for path in write_templates(args.out, args.only):
        print(path)
    return 0


def _cmd_calendar(args: argparse.Namespace) -> int:
    from fdh.calendar_data import render_ics
    from fdh.models import canonical_entity

    entity = canonical_entity(args.entity)
    args.out.write_text(render_ics(entity, args.year), encoding="utf-8")
    print(args.out)
    return 0


def _cmd_ask(args: argparse.Namespace) -> int:
    from fdh.llm.rag import answer_question

    rules = load_catalog(args.year, args.rules_dir)
    sys.stdout.write(answer_question(args.question, rules))
    sys.stdout.write("\n")
    return 0


def _cmd_doctor(_args: argparse.Namespace) -> int:
    from fdh.llm.reviewer import SUGGESTED_MODELS, build_client

    _client, note = build_client()
    print(note)
    print("Modelos sugeridos para Ollama o un endpoint local compatible:")
    for model in SUGGESTED_MODELS:
        print(f"  - {model}")
    print("Proveedor local: FDH_LLM_PROVIDER=ollama y, si hace falta, FDH_LLM_MODEL.")
    print("Por defecto el texto no sale de la máquina. FDH_LLM_ALLOW_REMOTE=1 lo permite.")
    print(DISCLAIMER_ES)
    print(DISCLAIMER_EN)
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    print(DISCLAIMER_ES)
    print(DISCLAIMER_EN)
    print(
        f"Interfaz local en http://{args.host}:{args.port} "
        "(no envía documentos a un LLM salvo que lo active)"
    )
    uvicorn.run("fdh.web:app", host=args.host, port=args.port, reload=False)
    return 0
