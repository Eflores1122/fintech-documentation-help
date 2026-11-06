"""Load and validate the versioned YAML rule catalogs."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import ValidationError

from fdh.models import CatalogFile, Rule


class CatalogError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("\n".join(errors))


def locate_rules_dir(explicit: Path | None = None) -> Path:
    if explicit is not None:
        path = explicit.expanduser().resolve()
        if not path.is_dir():
            raise CatalogError([f"No existe el directorio de reglas: {path}"])
        return path
    env = os.environ.get("FDH_RULES_DIR")
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env).expanduser())
    candidates.append(Path.cwd() / "rules")
    here = Path(__file__).resolve()
    candidates.extend(parent / "rules" for parent in here.parents)
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if (resolved / "2026").is_dir() or (resolved / "2025").is_dir():
            return resolved
    raise CatalogError(
        [
            "No se encontró el catálogo de reglas. Ejecute fdh desde el repositorio "
            "o defina FDH_RULES_DIR."
        ]
    )


def available_years(rules_dir: Path | None = None) -> list[int]:
    root = locate_rules_dir(rules_dir)
    years = []
    for child in root.iterdir():
        if child.is_dir() and child.name.isdigit():
            years.append(int(child.name))
    return sorted(years)


def load_catalog(year: int, rules_dir: Path | None = None) -> list[Rule]:
    root = locate_rules_dir(rules_dir)
    folder = root / str(year)
    if not folder.is_dir():
        known = ", ".join(str(item) for item in available_years(root)) or "(ninguno)"
        raise CatalogError(
            [f"No existe el catálogo para el año {year} en {root}. Años disponibles: {known}."]
        )
    files = sorted(folder.glob("*.yaml")) + sorted(folder.glob("*.yml"))
    if not files:
        raise CatalogError([f"El catálogo {year} no contiene archivos YAML."])
    errors: list[str] = []
    rules: list[Rule] = []
    for path in files:
        loaded = _load_file(path, year, errors)
        rules.extend(loaded)
    seen: dict[str, str] = {}
    for rule in rules:
        if rule.id in seen:
            errors.append(f"id duplicado {rule.id!r} en {seen[rule.id]} y en el catálogo {year}")
        else:
            seen[rule.id] = str(year)
    if errors:
        raise CatalogError(errors)
    return rules


def load_all_catalogs(rules_dir: Path | None = None) -> dict[int, list[Rule]]:
    root = locate_rules_dir(rules_dir)
    catalogs = {year: load_catalog(year, root) for year in available_years(root)}
    errors: list[str] = []
    known_ids = {rule.id for rules in catalogs.values() for rule in rules}
    for year, rules in catalogs.items():
        for rule in rules:
            if rule.supersedes and rule.supersedes not in known_ids:
                errors.append(
                    f"{year}/{rule.id}: supersedes={rule.supersedes!r} no existe en ningún año"
                )
    if errors:
        raise CatalogError(errors)
    return catalogs


def validate_catalogs(rules_dir: Path | None = None) -> list[str]:
    """Return a list of human-readable problems. Empty means the catalogs are valid."""
    try:
        catalogs = load_all_catalogs(rules_dir)
    except CatalogError as exc:
        return exc.errors
    notes = [f"{year}: {len(rules)} reglas" for year, rules in sorted(catalogs.items())]
    unverified = [
        f"UNVERIFIED {year}/{rule.id}: {rule.unverified_detail}"
        for year, rules in sorted(catalogs.items())
        for rule in rules
        if rule.unverified
    ]
    return notes + unverified


def _load_file(path: Path, year: int, errors: list[str]) -> list[Rule]:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        errors.append(f"{path.name}: YAML inválido: {exc}")
        return []
    if not isinstance(raw, dict):
        errors.append(f"{path.name}: se esperaba un mapa con catalog_year y rules")
        return []
    try:
        parsed = CatalogFile.model_validate(raw)
    except ValidationError as exc:
        for item in exc.errors():
            loc = ".".join(str(part) for part in item["loc"])
            errors.append(f"{path.name}: {loc}: {item['msg']}")
        return []
    if parsed.catalog_year != year:
        errors.append(
            f"{path.name}: catalog_year={parsed.catalog_year} no coincide con la carpeta {year}"
        )
    return parsed.rules
