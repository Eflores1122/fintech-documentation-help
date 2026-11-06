"""Shared data model for catalogs, audits and reports."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Severity = Literal["critical", "high", "medium", "low", "info"]
Status = Literal["pass", "fail", "not_applicable", "unclear"]
CheckType = Literal[
    "contains_all_groups",
    "contains_any",
    "forbidden_phrases",
    "regex",
    "each_document_contains_any",
    "each_document_forbidden",
]
Strictness = Literal["standard", "high", "max"]

SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
SEVERITY_WEIGHT = {"critical": 5, "high": 3, "medium": 2, "low": 1, "info": 0}
STRICTNESS_RANK = {"standard": 0, "high": 1, "max": 2}

PROFILE_FLAGS = (
    "operates_virtual_assets",
    "has_partial_or_deferred_payments",
    "transports_goods",
    "is_technological_platform_tax_regime",
    "provides_digital_services_liva",
    "processes_cards",
    "participates_spei",
    "uses_specialized_services",
    "offers_credit",
    "offers_yield",
    "has_related_parties_abroad",
)

AREAS = (
    "legal",
    "regulatorio",
    "financiero",
    "fiscal",
    "pld",
    "ciberseguridad",
    "privacidad",
    "condusef",
    "riesgos",
    "operacion",
    "laboral",
    "metodologia",
    "meta",
)

DOMAIN_AREA = {
    "privacy": "privacidad",
    "lritf": "regulatorio",
    "banxico": "regulatorio",
    "cnbv": "regulatorio",
    "pld": "pld",
    "condusef": "condusef",
    "sat": "fiscal",
    "meta": "meta",
    "legal": "legal",
    "regulatorio": "regulatorio",
    "financiero": "financiero",
    "fiscal": "fiscal",
    "ciberseguridad": "ciberseguridad",
    "privacidad": "privacidad",
    "riesgos": "riesgos",
    "operacion": "operacion",
    "laboral": "laboral",
    "metodologia": "metodologia",
}

# Entity implications: auditing an IFPE also runs rules aimed at ITF and
# fintech_general. IFC-only rules (LIF 2026 retenciones) stay out of an IFPE run.
ENTITY_IMPLIES: dict[str, set[str]] = {
    "IFPE": {"IFPE", "ITF", "fintech_general"},
    "IFC": {"IFC", "ITF", "fintech_general"},
    "ITF": {"ITF", "fintech_general"},
    "fintech_general": {"fintech_general"},
    "AV_exchange_non_ef": {"AV_exchange_non_ef", "fintech_general"},
    "plataforma_tecnologica": {"plataforma_tecnologica", "fintech_general"},
    "servicios_digitales": {"servicios_digitales", "fintech_general"},
    "SOFOM_ENR": {"SOFOM_ENR", "fintech_general"},
    "transmisor_dinero": {"transmisor_dinero", "fintech_general"},
    "asesor_inversion": {"asesor_inversion", "fintech_general"},
    "modelo_novedoso": {"modelo_novedoso", "fintech_general"},
    "tool": {"tool"},
}

ENTITY_ALIASES = {
    "ifpe": "IFPE",
    "ifc": "IFC",
    "itf": "ITF",
    "fintech_general": "fintech_general",
    "fintech": "fintech_general",
    "av_exchange_non_ef": "AV_exchange_non_ef",
    "av": "AV_exchange_non_ef",
    "plataforma_tecnologica": "plataforma_tecnologica",
    "plataforma": "plataforma_tecnologica",
    "servicios_digitales": "servicios_digitales",
    "sofom_enr": "SOFOM_ENR",
    "sofom": "SOFOM_ENR",
    "transmisor_dinero": "transmisor_dinero",
    "transmisor": "transmisor_dinero",
    "asesor_inversion": "asesor_inversion",
    "asesor": "asesor_inversion",
    "modelo_novedoso": "modelo_novedoso",
    "modelo": "modelo_novedoso",
    "tool": "tool",
}


def canonical_entity(value: str) -> str:
    key = value.strip()
    mapped = ENTITY_ALIASES.get(key.casefold())
    if mapped is None:
        known = ", ".join(sorted(ENTITY_IMPLIES))
        raise ValueError(f"Tipo de entidad desconocido: {value!r}. Use uno de: {known}.")
    return mapped


class Group(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    all: list[str] = Field(default_factory=list)
    any: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def not_empty(self) -> Group:
        if not self.all and not self.any:
            raise ValueError(f"El grupo {self.name!r} no tiene términos")
        return self


class Check(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: CheckType
    label: str | None = None
    groups: list[Group] = Field(default_factory=list)
    any: list[str] = Field(default_factory=list)
    pattern: str | None = None
    expect: Literal["match", "no_match"] = "match"

    @model_validator(mode="after")
    def shape(self) -> Check:
        if self.type == "contains_all_groups" and not self.groups:
            raise ValueError("contains_all_groups requiere groups")
        needs_any = {
            "contains_any",
            "forbidden_phrases",
            "each_document_contains_any",
            "each_document_forbidden",
        }
        if self.type in needs_any and not self.any:
            raise ValueError(f"{self.type} requiere any")
        if self.type == "regex":
            if not self.pattern:
                raise ValueError("regex requiere pattern")
            try:
                re.compile(self.pattern)
            except re.error as exc:
                raise ValueError(f"regex inválida: {exc}") from exc
        return self


class Matcher(BaseModel):
    model_config = ConfigDict(extra="forbid")
    require_document: bool = True
    checks: list[Check] = Field(default_factory=list)


class Rule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    domain: str
    title: str
    requirement: str
    check_hint: str
    fix_suggestion: str
    entity_types: list[str]
    documents: list[str]
    source_url: str
    source_name: str
    effective_date: date
    effective_from: date | None = None
    effective_to: date | None = None
    last_verified: date
    severity: Severity
    unverified: bool = False
    verified: bool | None = None
    unverified_detail: str | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    parameter_ids: list[str] = Field(default_factory=list)
    applies_if: str | None = None
    notes: str | None = None
    diff_note: str | None = None
    area: str | None = None
    min_strictness: Strictness = "standard"
    binding: bool = True
    owner_role: str = "Responsable de cumplimiento"
    remediation_days: int = 30
    evidence_expected: list[str] = Field(default_factory=list)
    procedure: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    matcher: Matcher

    @field_validator("id")
    @classmethod
    def slug(cls, value: str) -> str:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
            raise ValueError(f"id inválido: {value}")
        return value

    @field_validator("source_url")
    @classmethod
    def https_url(cls, value: str) -> str:
        if not value.startswith("https://"):
            raise ValueError("source_url debe usar https y apuntar a una fuente oficial")
        return value

    @field_validator("entity_types")
    @classmethod
    def known_entities(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("entity_types no puede estar vacío")
        unknown = [item for item in value if item not in ENTITY_IMPLIES]
        if unknown:
            raise ValueError(f"entity_type desconocido: {', '.join(unknown)}")
        return value

    @field_validator("documents")
    @classmethod
    def documents_present(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("documents no puede estar vacío")
        return value

    @field_validator("fix_suggestion")
    @classmethod
    def fix_len(cls, value: str) -> str:
        if len(value.strip()) < 15:
            raise ValueError("fix_suggestion debe ser concreto")
        return value.strip()

    @field_validator("area")
    @classmethod
    def known_area(cls, value: str | None) -> str | None:
        if value is not None and value not in AREAS:
            raise ValueError(f"area desconocida: {value}")
        return value

    @field_validator("domain")
    @classmethod
    def known_domain(cls, value: str) -> str:
        if value not in DOMAIN_AREA:
            raise ValueError(f"domain desconocido: {value}")
        return value

    @model_validator(mode="after")
    def flags(self) -> Rule:
        if self.verified is False:
            self.unverified = True
        elif self.verified is True:
            self.unverified = False
        self.verified = not self.unverified
        if self.unverified and not (self.unverified_detail and self.unverified_detail.strip()):
            raise ValueError(f"{self.id}: unverified requiere unverified_detail")
        if self.applies_if and self.applies_if not in PROFILE_FLAGS:
            raise ValueError(f"{self.id}: applies_if desconocido: {self.applies_if}")
        if self.area is None:
            self.area = DOMAIN_AREA[self.domain]
        if self.effective_from is None:
            self.effective_from = self.effective_date
        if self.effective_to is not None and self.effective_to < self.effective_from:
            raise ValueError(f"{self.id}: effective_to es anterior a effective_from")
        if self.remediation_days < 1:
            raise ValueError(f"{self.id}: remediation_days debe ser positivo")
        return self

    def in_force(self, on: date) -> bool:
        start = self.effective_from or self.effective_date
        ended = self.effective_to is not None and on > self.effective_to
        return on >= start and not ended

    def applies_to_entity(self, entity: str) -> bool:
        implied = ENTITY_IMPLIES.get(entity, {entity})
        return bool(set(self.entity_types) & implied)

    def enabled_at(self, strictness: str) -> bool:
        return STRICTNESS_RANK[strictness] >= STRICTNESS_RANK[self.min_strictness]


class CatalogFile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    catalog_year: int
    disclaimer: str
    rules: list[Rule]
    last_verified: date | None = None

    @field_validator("disclaimer")
    @classmethod
    def disclaimer_text(cls, value: str) -> str:
        folded = value.casefold()
        if "asesor" not in folded and "asesoría" not in folded and "asesoria" not in folded:
            raise ValueError("El disclaimer del catálogo debe decir que no es asesoría")
        return value


class Document(BaseModel):
    path: str
    filename: str
    media_type: str
    text: str
    types: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Finding(BaseModel):
    rule_id: str
    status: Status
    severity: Severity
    domain: str
    title: str
    requirement: str
    message: str
    evidence: str | None = None
    document: str | None = None
    fix_suggestion: str
    source_name: str
    source_url: str
    effective_date: date
    last_verified: date
    unverified: bool = False
    unverified_detail: str | None = None
    notes: str | None = None
    origin: list[str] = Field(default_factory=lambda: ["deterministic"])
    area: str = ""
    binding: bool = True
    verified: bool = True
    condition: str = ""
    criterion: str = ""
    cause: str = ""
    effect: str = ""
    recommendation: str = ""
    evidence_required: list[str] = Field(default_factory=list)
    suggested_owner: str = ""
    suggested_deadline: str = ""
    confidence: float | None = None
    source: Literal["deterministic", "llm", "mixed"] = "deterministic"


class ScoreCard(BaseModel):
    overall: float | None
    by_domain: dict[str, float | None]
    by_area: dict[str, float | None] = Field(default_factory=dict)
    weights: dict[str, int]


class AuditReport(BaseModel):
    tool: str
    version: str
    disclaimer: str
    disclaimer_en: str
    generated_at: datetime
    entity_type: str
    catalog_year: int
    llm_used: bool
    llm_note: str | None = None
    profile: dict[str, object]
    documents: list[Document]
    scores: ScoreCard
    summary: dict[str, int]
    findings: list[Finding]
    rejected_llm_findings: list[dict[str, str]] = Field(default_factory=list)
    omitted_rules: list[dict[str, str]] = Field(default_factory=list)
    strictness: Strictness = "max"
    phases: list[dict[str, str]] = Field(default_factory=list)
    inventory: list[dict[str, object]] = Field(default_factory=list)
    remediation: list[dict[str, object]] = Field(default_factory=list)
    opinion: dict[str, object] = Field(default_factory=dict)
    comparison: list[dict[str, object]] = Field(default_factory=list)
    heatmap: dict[str, dict[str, object]] = Field(default_factory=dict)
    as_of: str | None = None
    business_profile: dict[str, object] = Field(default_factory=dict)
    coherence: list[dict[str, object]] = Field(default_factory=list)
    applicability: list[dict[str, object]] = Field(default_factory=list)
    parameter_gaps: list[dict[str, object]] = Field(default_factory=list)
    parameter_values: list[dict[str, object]] = Field(default_factory=list)


class Profile(BaseModel):
    entity_type: str
    year: int
    operates_virtual_assets: bool = False
    has_partial_or_deferred_payments: bool = False
    transports_goods: bool = False
    is_technological_platform_tax_regime: bool = False
    provides_digital_services_liva: bool = False
    processes_cards: bool = False
    participates_spei: bool = False
    uses_specialized_services: bool = False
    offers_credit: bool = False
    offers_yield: bool = False
    has_related_parties_abroad: bool = False
    strictness: Strictness = "max"
    as_of: date | None = None

    @field_validator("entity_type")
    @classmethod
    def norm_entity(cls, value: str) -> str:
        return canonical_entity(value)

    def flag(self, name: str) -> bool:
        return bool(getattr(self, name))
