# RESEARCH — fintech-documentation-help

**Proyecto:** auditor open-source de documentación regulatoria para fintechs mexicanas (ITF: IFPE / IFC y sujetos relacionados).  
**Autor del brief:** investigación para Edgar Flores (Eflores1122).  
**Fecha de verificación de fuentes:** 2026-11-05 (America/Mexico_City).  
**Disclaimer (obligatorio en producto y README):** esta herramienta **no es asesoría legal ni fiscal**. Es un checklist asistido con citas a fuentes públicas. Toda decisión de cumplimiento debe validarse con abogado/contador autorizado y contra el texto vigente en el DOF / portales oficiales.

---

## 1. Resumen ejecutivo (ES)

Edgar quiere un repo `fintech-documentation-help`: un “auditor” que revise políticas, manuales, avisos, contratos, procesos CFDI/SAT y documentación PLD/FT de una fintech mexicana y diga **qué está mal, qué falta y qué está desactualizado** frente a la regulación vigente — especialmente la que **cambia cada año** (RMF, LIF, anexos SAT) y la que cambió fuerte en **2025** (nueva LFPDPPP, reforma LFPIORPI, LIF 2026 con retenciones para IFC).

**Hallazgos clave 2025–2026**

| Área | Cambio | Fecha / fuente |
|------|--------|----------------|
| SAT / RMF | RMF 2026 publicada; varias resoluciones de modificaciones a lo largo de 2026 | DOF 28-dic-2025; portal SAT Normatividad RMF 2026 |
| SAT / LIF | LIF 2026: IFC deben retener ISR (20% / 35% extranjeros) e IVA 16% sobre intereses nominales; obligaciones de CFDI/constancias | LIF 2026 art. 25 fr. VIII; análisis Deloitte oct-2025; PDF Diputados |
| Datos personales | Nueva LFPDPPP; **INAI desaparece**; autoridad = **Secretaría Anticorrupción y Buen Gobierno** | DOF 20-mar-2025; vigente 21-mar-2025; PDF Diputados |
| Aviso de privacidad | Art. 15: 6 elementos mínimos; finalidades que requieren consentimiento; ya no se exige listar transferencias como en la ley 2010 | LFPDPPP 2025 art. 15 |
| PLD (actividades vulnerables) | Reforma LFPIORPI: Beneficiario Controlador, UMA, retención 10 años, manual, RBA, monitoreo automatizado, auditoría, PEP | DOF 16-jul-2025 |
| ITF PLD | Art. 58 LRITF + DCG 10-sep-2018: manual PLD, KYC, reportes relevantes/inusuales/preocupantes, oficial de cumplimiento certificado, auditoría anual | LRITF; SIDOF nota 5537449 |
| CNBV/Banxico | Manuales de riesgos, seguridad, continuidad, segregación, divulgación de riesgos; IFPE: política estratégica continuidad/seguridad (disposiciones 28-ene-2021) | CNBV Normatividad Fintech; Banxico reglas conjuntas |
| CONDUSEF | RECA previo a uso; consentimiento **expreso** (no tácito); UNE; REUS; leyendas de no garantía gubernamental; carátulas | Disposiciones CONDUSEF ITF (DOF ~2019; texto SIDOF 5565233) |
| LRITF | Última reforma publicada citada en texto vigente: 14-nov-2025 | PDF Diputados LRITF |

**Cadencia de actualización recomendada para el producto**

- **Anual (dic–ene):** recarga RMF + anexos + LIF del ejercicio.  
- **Trimestral:** resoluciones de modificaciones RMF/RGCE.  
- **Event-driven:** DOF alerts (LFPIORPI, LRITF, LFPDPPP, Banxico/CNBV/CONDUSEF).  
- Cada regla en el catálogo debe llevar `effective_date`, `supersedes`, `source_url`, `last_verified`.

---

## 2. Mapa de documentos que una fintech mexicana suele (o debe) tener

### 2.1 Autorización / gobierno (LRITF art. 39–40, 48)

| Documento | Quién | Notas |
|-----------|-------|-------|
| Políticas de separación / segregación de cuentas | ITF | Art. 39-IV, 46 |
| Políticas de divulgación de riesgos, comisiones, advertencias en interfaz | ITF | Art. 39-V; art. 11 (no garantía gobierno) |
| Políticas de riesgos operativos + seguridad de la información + confidencialidad | ITF | Art. 39-VI; IFPE: disposiciones conjuntas Banxico-CNBV |
| Procesos KYC / identificación de clientes | ITF | Art. 39-VII; art. 58 |
| Políticas de conflictos de interés | ITF | Art. 39-VIII |
| Políticas prevención de fraude + PLD/FT | ITF | Art. 39-IX; art. 58 |
| Manual de controles internos / administración de riesgos | ITF | Art. 48 |
| Plan / política de continuidad operativa | ITF (esp. IFPE) | Art. 48; Banxico 28-ene-2021 |
| Contratos con proveedores tecnológicos (procesos clave) | ITF | Art. 39-X, 54 |
| Estados financieros dictaminados | ITF | Art. 49 |
| Conservación de comprobantes ≥ 10 años | ITF | Art. 48 |

### 2.2 PLD/FT (LRITF art. 58 + DCG art. 58 + UIF vía CNBV SITI)

| Documento / artefacto | Checkable |
|-----------------------|-----------|
| Manual / documento de medidas y procedimientos PLD/FT presentado a CNBV | Existe; versión; fecha; alcance productos/tecnologías |
| Metodología de evaluación de riesgos (RBA) | Documentada; resultados disponibles a SHCP/CNBV |
| KYC: criterios por tipo de cliente, zona, actividad; documentación de identidad | Matrices / checklists |
| Oficial de cumplimiento + comité de comunicación y control | Designación; **certificación** CNBV (art. 4 fr. X Ley CNBV) |
| Capacitación interna | Programa y evidencia |
| Sistemas automatizados de monitoreo | Descripción en manual |
| Reportes: relevantes, inusuales, internas preocupantes, transferencias internacionales, efectivo MXN extranjera | Procedimientos y plazos |
| Lista de personas bloqueadas SHCP | Procedimiento de suspensión inmediata |
| Conservación identificación + reportes ≥ 10 años | Política de retención |
| Revisión anual auditoría interna o tercero independiente | Informe anual |

### 2.3 CONDUSEF (transparencia ITF)

| Documento | Checkable |
|-----------|-----------|
| Contratos de adhesión + anexos inscritos en **RECA** antes de uso | Número RECA vigente en contrato y carátula |
| Carátula por producto (Anexos 1–3) | Leyendas obligatorias (no garantía; rendimientos estimados; AV) |
| Términos y condiciones de la plataforma | Usos, claves, horarios, continuidad |
| UNE | Datos de contacto en contrato/plataforma; registro en directorio |
| Consulta **REUS** antes de publicidad | Procedimiento + consentimiento expreso independiente |
| Estados de cuenta / operación; comprobantes; listado de comisiones en plataforma | Contenidos mínimos arts. 33–43 |
| Consentimiento **expreso** (FEA / firma digitalizada / autenticación art. 56) — **prohibido tácito** | Art. 8 disposiciones |

### 2.4 Protección de datos (LFPDPPP 2025)

| Documento | Checkable (art. 15) |
|-----------|---------------------|
| Aviso de privacidad (integral + simplificado) | I identidad/domicilio; II datos (sensibles); III finalidades (distinguir las que requieren consentimiento); IV opciones limitar uso; V ARCO; VI cómo se comunican cambios |
| Procedimiento ARCO (plazos 20+15 días) | Art. 31 |
| Persona / departamento de datos personales | Art. 29 |
| Medidas de seguridad admin/técnicas/físicas | Art. 18 |
| Protocolo de vulneraciones (aviso inmediato a titulares) | Art. 19 |
| Consentimiento expreso datos financieros/patrimoniales y sensibles | Arts. 7–8 |
| **No** referir al INAI como autoridad vigente | Sustituir por Secretaría Anticorrupción y Buen Gobierno |

### 2.5 SAT / fiscal (anual)

| Documento / proceso | Checkable |
|---------------------|-----------|
| Política / procedimiento CFDI 4.0 (emisión, cancelación, complemento de pagos / REP) | Versión catálogo; plazos |
| Complemento Carta Porte (si hay transporte de mercancías) | Aplica solo si el modelo lo requiere |
| Retenciones plataformas tecnológicas / IVA servicios digitales (si aplica al modelo) | Complemento SPT; CFDI retenciones |
| Para **IFC (2026):** retención ISR e IVA sobre intereses + CFDI/constancias | LIF 2026 art. 25-VIII |
| CFF art. 32-B (si la entidad entra en el supuesto de “entidades financieras” / auxiliares reportables al SAT) | Procedimientos de entrega de información a autoridad |
| Contabilidad electrónica / Anexo 24 RMF | Si aplica |
| Calendario de actualización ante nueva RMF (cada dic/ene) | Owner + checklist anual |

---

## 3. Detalle por dominio (con URLs oficiales consultadas)

### 3.1 SAT — RMF, CFDI, plataformas, LIF

**RMF 2025:** publicada DOF **30-dic-2024**  
- https://www.dof.gob.mx/nota_detalle.php?codigo=5746354&fecha=30%2F12%2F2024  
- PDF SAT: http://omawww.sat.gob.mx/normatividad_RMF_RGCE/Paginas/documentos2025/rmf/rmf/RMF_2025-30122024.pdf  
- Hub: https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/normatividad_rmf_rgce2025.html  

**RMF 2026:** publicada **28-dic-2025**  
- PDF DOF SHCP: https://dof.gob.mx/2025/SHCP/SHCP_281225_01.pdf  
- Hub SAT 2026 (incluye 1ª–4ª modificaciones hasta oct-2026 y versiones anticipadas): https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/normatividad_rmf_rgce2026.html  

**LIF 2026:** texto Diputados  
- https://www.diputados.gob.mx/LeyesBiblio/pdf/LIF_2026.pdf  
- SIDOF nota asociada: https://sidof.segob.gob.mx/notas/5772357  
- Impacto IFC (retención ISR 20%/35% + IVA 16% sobre intereses; CFDI/constancias): resumen Deloitte 31-oct-2025 (secundario, no DOF): https://www.deloitte.com/content/dam/assets-zone4/latam/es/docs/services/tax/2025/Sector-financiero-fintech.pdf  

**CFDI / plataformas (portales SAT, verificar contra RMF vigente):**  
- Complemento plataformas tecnológicas: https://wwwmat.sat.gob.mx/consulta/52846/complemento-servicios-de-plataformas-tecnologicas  
- Plataformas / servicios digitales: https://www.sat.gob.mx/minisitio/PlataformasTecnologicas/PlataformasTecnologicas_ServiciosDigitales/pt_sd_comprobantes.html  
- Carta Porte: https://wwwmat.sat.gob.mx/consultas/68823/complemento-carta-porte-  

**CFF art. 32-B:** obligaciones de entidades del sistema financiero de proporcionar información al SAT y de identificar cuentahabientes (texto compilado en sitios jurídicos; validar siempre contra CFF vigente en Diputados/DOF).  

**Cadencia:** RMF anual (CFF art. 33-I-g); modificaciones múltiples por año; LIF anual.

**UNVERIFIED / partial:** el detalle línea-por-línea de reglas RMF 2026 específicas a fintechs (p.ej. números de regla exactos sustitutos de 3.16.13 / 4.1.12) debe extraerse del PDF RMF 2026 completo en una pasada de parsing posterior — no se inventan aquí números de regla no leídos íntegramente.

### 3.2 LRITF + CNBV + Banxico

**Ley:** https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf (texto vigente; última reforma citada 14-nov-2025)  
Publicación original DOF 9-mar-2018.

**Art. 39 — documentación de autorización (checklist duro para el auditor):**  
políticas segregación; divulgación riesgos/comisiones/advertencias; riesgos operativos + seguridad + confidencialidad; KYC; conflictos; fraude+PLD; convenios tecnología; etc.

**Art. 58 — PLD/FT:** documento de medidas; metodología de riesgos; reportes a Secretaría vía CNBV (relevantes, inusuales, preocupantes, etc.); KYC; resguardo; capacitación; sistemas automatizados; comité + oficial de cumplimiento certificado; auditoría anual; lista bloqueados; conservación 10 años.

**CNBV Normatividad Fintech:** https://www.cnbv.gob.mx/SECTORES-SUPERVISADOS/Fintech/Paginas/NORMATIVIDAD-FINTECH.aspx  
Incluye (entre otras):  
- Disposiciones de carácter general aplicables a las ITF (10-sep-2018)  
- Disposiciones APIs (04-jun-2020)  
- Disposiciones IFPE arts. 48/54/56 (28-ene-2021)  
- Lineamientos informe auditoría PLD (18-oct-2021)  

**DCG art. 58 LRITF (PLD):** SIDOF https://sidof.segob.gob.mx/notas/5537449 (10-sep-2018)

**Resolución que modifica DCG ITF:** SIDOF https://sidofqa.segob.gob.mx/notas/5763700 (24-jul-2025) — **verificar en DOF producción** el texto completo al implementar reglas concretas de capital/manuales.

**Banxico IFPE:** https://www.banxico.org.mx/marco-normativo/normativa-emitida-por-el-banco-de-mexico/reglas-conjuntas-instituciones-de-fondos-de-pago-e/pagina-reglas-conjuntas-ins.html  
DOF 28-ene-2021: https://dof.gob.mx/nota_detalle.php?codigo=5610487&fecha=28/01/2021  

### 3.3 PLD/FT — LFPIORPI reforma 2025

**Decreto:** https://www.diputados.gob.mx/LeyesBiblio/ref/lfpiorpi/LFPIORPI_ref03_16jul25.pdf  
Publicado DOF **16-jul-2025**; vigencia día siguiente salvo transitorios.

**Relevante para fintechs / AV / actividades vulnerables:**  
- Art. 3: nueva definición Beneficiario Controlador; PEP; UMA; Entidades Financieras incluyen art. 58 LRITF.  
- Art. 17-XVI: intercambio de activos virtuales por no-EF (umbrales UMA; avisos).  
- Art. 18: conocer cliente **de forma directa**; BC; conservación **10 años**; padrón; avisos 24h por sospecha; **evaluación RBA**; **Manual de Políticas Internas**; capacitación anual; **monitoreo automatizado**; auditoría interna/externa según riesgo.  
- Cap. IV Bis: obligaciones de sociedades mercantiles sobre BC (33 Bis–Ter).  
- Transitorios: SHCP modifica reglas en 12 meses; fracciones VII–XI art. 18 entran según reglas secundarias.

**UIF:** https://uif.gob.mx/ — reportes de ITF canalizados vía CNBV (SITI); formatos .ITFI / .ITFR / .ITFP (fuentes secundarias Grant Thornton / DOF formatos — validar plantillas vigentes en CNBV SITI PLD).

### 3.4 CONDUSEF

**Disposiciones transparencia ITF:** https://sidof.segob.gob.mx/notas/docFuente/5565233  
También: https://dof.gob.mx/nota_detalle_popup.php?codigo=5565233  

**Checks de alto valor para el auditor de docs:**  
- Art. 3: Términos plataforma (usos, claves, horarios, continuidad; aviso fallas ≥24h a `suptech@condusef.gob.mx`).  
- Arts. 5–8: forma y contenido contrato; carátula; **consentimiento expreso**; prohibición tácito.  
- Art. 6-VIII-d / art. 7-IV: leyenda de **no garantía** del Gobierno Federal.  
- Art. 11: REUS + consentimiento publicidad independiente.  
- Art. 31: inscripción **RECA previa** a uso; número en contrato.  
- UNE en contrato y plataforma.  

**RECA:** https://registros.condusef.gob.mx/reca/reca.php  
**REUS:** https://registros.condusef.gob.mx/reus/  

### 3.5 Protección de datos — post-INAI

**LFPDPPP nueva:** https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf  
DOF 20-mar-2025; vigencia 21-mar-2025; reforma menor 14-nov-2025 (art. 4).  

**Autoridad:** **Secretaría Anticorrupción y Buen Gobierno** (art. 2-XV, Cap. VII).  
INAI extinguido por simplificación orgánica (DOF 20-dic-2024) + decreto 20-mar-2025.  

**Aviso art. 15 — elementos mínimos (checklist determinístico):**  
1. Identidad y domicilio del responsable  
2. Datos tratados (marcar sensibles)  
3. Finalidades, **distinguiendo las que requieren consentimiento**  
4. Opciones/medios para limitar uso o divulgación  
5. Mecanismos ARCO  
6. Cómo se comunican cambios al aviso  

Nota: la ley 2025 **no** exige en el art. 15 listar transferencias como elemento mínimo (sí regula transferencias en Cap. V). Documentos que aún digan “INAI” o citen solo la ley 2010 → finding de severidad alta.

---

## 4. Diseño de producto propuesto — `fintech-documentation-help`

### 4.1 Objetivo

CLI (+ UI opcional Streamlit/FastAPI) que:

1. Ingesta documentos (PDF, DOCX, MD, TXT, HTML).  
2. Corre **checks determinísticos** (regex/keywords/estructura) contra un catálogo **rules-as-data** versionado por año.  
3. Opcionalmente invoca un **LLM reviewer** que **solo** puede citar reglas del catálogo (RAG restringido) y debe devolver `rule_id` + excerpt.  
4. Emite reporte Markdown/HTML: severity, hallazgo, evidencia, sugerencia de fix, `source_url`.  
5. Comando `what-changed --year 2026` que diffea el catálogo año N vs N-1.  
6. Incluye **documentos sintéticos** de una fintech ficticia (“Nube Pago, S.A. de C.V. IFPE”) con fallas intencionales (aviso con “INAI”, contrato sin RECA, manual PLD sin oficial certificado, etc.).  
7. Tests + CI; disclaimer fuerte.

### 4.2 Arquitectura

```
fintech-documentation-help/
  rules/
    catalog/2025/*.yaml
    catalog/2026/*.yaml          # effective_date, supersedes
    schemas/rule.schema.json
  src/fdh/
    ingest/   # pdfplumber / pypdf, python-docx, markdown
    extract/  # text + optional section headings
    engine/   # deterministic matchers (must_contain, must_not_contain, regex, any_of)
    llm/      # optional: OpenAI-compatible, grounded to rules only
    report/   # md + html
    cli.py
  samples/nube_pago/            # docs sintéticos
  tests/
  dashboard/app.py              # Streamlit opcional
  RESEARCH.md                   # este brief
  rules_seed.yaml               # semilla
  README.md                     # disclaimer + how to update rules each December
```

**Regla (YAML) — campos mínimos**

```yaml
id: sat-lif2026-ifc-isr-retention
domain: sat
title: "IFC: retención ISR sobre intereses (LIF 2026)"
requirement: "..."
check_hint: "Buscar política de retenciones / CFDI que mencione tasa 20% / 35%"
entity_types: [IFC]
source_url: "https://www.diputados.gob.mx/LeyesBiblio/pdf/LIF_2026.pdf"
source_name: "LIF 2026"
effective_date: "2026-01-01"
last_verified: "2026-11-05"
severity: high
matcher:
  type: document_presence_or_keyword
  any_keywords: ["retención", "ISR", "intereses"]
  # deterministic checks are hints; human/LLM confirms
```

### 4.3 Motor de auditoría

1. **Inventory:** ¿existen los documentos esperados por `entity_type` (IFPE/IFC/AV/plataforma)?  
2. **Deterministic:** keywords, secciones obligatorias, frases prohibidas (`INAI` como autoridad vigente, “garantizado por el gobierno”, consentimiento tácito en contratos CONDUSEF).  
3. **Structural:** aviso de privacidad tiene fracciones I–VI; contrato tiene número RECA; manual PLD menciona oficial de cumplimiento + reportes ROI/ROR/ROP.  
4. **LLM (opcional):** para cada regla `severity>=medium`, pedir JSON `{pass|fail|unclear, evidence_quote, fix}`. Rechazar output sin `rule_id` del catálogo.  
5. **Diff anual:** comparar `rules/catalog/2025` vs `2026` → sección “Qué cambió este año”.

### 4.4 Severities

- `critical` — incumplimiento claro de obligación legal/regulatoria con sanción o bloqueo operativo (p.ej. sin RECA, sin manual PLD, aviso sin elementos art. 15).  
- `high` — desactualización material (INAI, tasas LIF 2026 ausentes en IFC).  
- `medium` — documentación incompleta / ambigua.  
- `low` — buenas prácticas / claridad.  
- `info` — recordatorio de cadencia anual.

### 4.5 Roadmap de implementación sugerido

1. Repo + schema + `rules_seed.yaml` expandido a `rules/catalog/2026/`.  
2. CLI `fdh audit path/ --entity IFPE --year 2026`.  
3. Samples + tests golden.  
4. Streamlit viewer del reporte.  
5. Scraper/asistente “pull RMF index from SAT hub” (solo index + hashes; humanos confirman reglas nuevas).  
6. **No** scrapear DOF login walls; preferir PDFs Diputados/SAT/Banxico/CNBV.

---

## 5. Top 10 checks más importantes (prioridad producto)

1. **Aviso de privacidad cumple art. 15 LFPDPPP 2025** y **no cita INAI** como autoridad.  
2. **Contrato de adhesión inscrito en RECA** con número vigente visible + carátula con leyendas.  
3. **Consentimiento expreso** (no tácito) en contratos CONDUSEF.  
4. **Manual PLD/FT art. 58** presente: RBA, KYC, reportes relevantes/inusuales/preocupantes, oficial certificado, auditoría anual, retención 10 años.  
5. **Divulgación “el Gobierno Federal no garantiza recursos”** en contratos, publicidad y plataforma (LRITF art. 11 + CONDUSEF).  
6. **Políticas de seguridad de la información + continuidad** (LRITF 39-VI / 48; IFPE Banxico 2021).  
7. **Segregación de recursos de clientes** documentada (LRITF 46).  
8. **LIF 2026 IFC:** procedimiento de retención ISR/IVA sobre intereses + CFDI/constancias.  
9. **UNE + REUS** documentados (atención usuarios / no spam).  
10. **Calendario anual RMF:** owner, checklist post-publicación DOF (dic/ene) y seguimiento de modificaciones.

---

## 6. Items marcados UNVERIFIED / pendientes de lectura íntegra

- Números exactos de reglas RMF 2026 que sustituyen o detallan obligaciones IFC (leer PDF RMF 2026 completo).  
- Texto íntegro de la Resolución 24-jul-2025 que modifica DCG ITF (SIDOF 5763700) — confirmar qué secciones de capital/manuales cambian.  
- Plantillas XML SITI vigentes (.ITFI/.ITFR/.ITFP) — confirmar en portal CNBV SITI PLD, no solo guías secundarias.  
- Si IFPE específicas quedan **fuera** de la retención LIF 2026 art. 25-VIII (Deloitte indica impacto en IFC; no inventar extensión a IFPE).  
- Reglamento nuevo de LFPDPPP 2025 (plazo 90 días en transitorios del decreto — verificar si ya se publicó al momento de release).

---

## 7. Fuentes primarias (lista corta)

| Fuente | URL |
|--------|-----|
| LRITF | https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf |
| LFPDPPP 2025 | https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf |
| LFPIORPI reforma | https://www.diputados.gob.mx/LeyesBiblio/ref/lfpiorpi/LFPIORPI_ref03_16jul25.pdf |
| LIF 2026 | https://www.diputados.gob.mx/LeyesBiblio/pdf/LIF_2026.pdf |
| RMF 2026 hub SAT | https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/normatividad_rmf_rgce2026.html |
| RMF 2026 PDF DOF | https://dof.gob.mx/2025/SHCP/SHCP_281225_01.pdf |
| CNBV Fintech | https://www.cnbv.gob.mx/SECTORES-SUPERVISADOS/Fintech/Paginas/NORMATIVIDAD-FINTECH.aspx |
| DCG art. 58 | https://sidof.segob.gob.mx/notas/5537449 |
| CONDUSEF ITF | https://sidof.segob.gob.mx/notas/docFuente/5565233 |
| Banxico IFPE | https://dof.gob.mx/nota_detalle.php?codigo=5610487&fecha=28/01/2021 |
| UIF | https://uif.gob.mx/ |

---

*Fin del RESEARCH.md — seed rules en `rules_seed.yaml`.*
