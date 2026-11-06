/* Browser port of the deterministic matcher. Documents stay in this page. */
const WEIGHT = { critical: 5, high: 3, medium: 2, low: 1, info: 0 };
const RANK = { standard: 0, high: 1, max: 2 };
const IMPLIES = {
  IFPE: ["IFPE", "ITF", "fintech_general"],
  IFC: ["IFC", "ITF", "fintech_general"],
  ITF: ["ITF", "fintech_general"],
  fintech_general: ["fintech_general"],
  SOFOM_ENR: ["SOFOM_ENR", "fintech_general"],
  transmisor_dinero: ["transmisor_dinero", "fintech_general"],
  asesor_inversion: ["asesor_inversion", "fintech_general"],
  modelo_novedoso: ["modelo_novedoso", "fintech_general"],
};

let CATALOG = null;
let SAMPLES = null;
let LAST = null;

function fold(value) {
  return value.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();
}

function hasPhrase(text, phrase) {
  const hay = fold(text);
  const needle = fold(phrase);
  if (!needle) return false;
  if (/^[a-z0-9]{2,8}$/.test(needle) && phrase === phrase.toUpperCase()) {
    return new RegExp(`\\b${needle}\\b`).test(hay);
  }
  return hay.includes(needle);
}

function classify(name, text, vocabulary) {
  const types = [];
  const stem = name.replace(/\.[^.]+$/, "").toLowerCase().replaceAll("-", "_");
  if (vocabulary.has(stem)) types.push(stem);
  const folded = fold(text);
  if (folded.includes("aviso de privacidad")) types.push("aviso_privacidad");
  if (folded.includes("contrato de adhesion")) types.push("contrato_adhesion");
  if (folded.includes("manual pld") || folded.includes("prevencion de lavado")) types.push("manual_pld_ft");
  if (name.includes("kyc")) types.push("politica_kyc");
  return [...new Set(types)];
}

function inForce(rule, on) {
  if (on < rule.effective_from) return false;
  if (rule.effective_to && on > rule.effective_to) return false;
  return true;
}

function selectRules(asOf) {
  const year = Number(asOf.slice(0, 4));
  const years = [...new Set(CATALOG.rules.map((rule) => rule.catalog_year))].filter((item) => item <= year);
  if (!years.length) return { rules: [], note: "No hay snapshot para esa fecha." };
  const snapshot = Math.max(...years);
  let rules = CATALOG.rules.filter((rule) => rule.catalog_year === snapshot && inForce(rule, asOf));
  const superseded = new Set(rules.map((rule) => rule.supersedes).filter(Boolean));
  rules = rules.filter((rule) => !superseded.has(rule.id) && !rule.superseded_by);
  const note = snapshot < year
    ? `Sin snapshot ${year}. Se reutiliza ${snapshot} y no se inventan reformas.`
    : `Snapshot ${snapshot}.`;
  return { rules, note };
}

function applies(rule, entity, flags, strictness) {
  const implied = new Set(IMPLIES[entity] || [entity]);
  if (!rule.entity_types.some((item) => implied.has(item))) {
    return { ok: false, reason: `No aplica a ${entity}.` };
  }
  if (RANK[strictness] < RANK[rule.min_strictness]) {
    return { ok: false, reason: `Pide estrictez ${rule.min_strictness}.` };
  }
  if (rule.applies_if && !flags[rule.applies_if]) {
    return { ok: false, reason: `El perfil no activó ${rule.applies_if}.` };
  }
  return { ok: true, reason: `Aplica a ${entity} desde ${rule.effective_from}.` };
}

function runCheck(check, docs) {
  const texts = docs.map((doc) => doc.text);
  if (check.type === "contains_any" || check.type === "forbidden_phrases") {
    for (const phrase of check.any || []) {
      const hit = docs.find((doc) => hasPhrase(doc.text, phrase));
      if (hit && check.type === "contains_any") return { ok: true };
      if (hit && check.type === "forbidden_phrases") {
        return { ok: false, message: `Se encontró «${phrase}».` };
      }
    }
    if (check.type === "contains_any") return { ok: false, message: `No aparece ${check.label || "el término"}.` };
    return { ok: true };
  }
  if (check.type === "contains_all_groups") {
    const missing = [];
    for (const group of check.groups || []) {
      const allOk = (group.all || []).every((phrase) => texts.some((text) => hasPhrase(text, phrase)));
      const anyOk = !(group.any || []).length || (group.any || []).some((phrase) => texts.some((text) => hasPhrase(text, phrase)));
      if (!allOk || !anyOk) missing.push(group.name);
    }
    return missing.length ? { ok: false, message: `Faltan elementos: ${missing.join("; ")}.` } : { ok: true };
  }
  if (check.type === "regex") {
    let source = String(check.pattern || "").replace(/^\(\?i\)/, "");
    let pattern;
    try {
      pattern = new RegExp(source, "i");
    } catch (_err) {
      return { ok: false, message: "El patrón no se evaluó en la demo." };
    }
    const hit = texts.some((text) => pattern.test(text));
    if (check.expect === "no_match") return { ok: !hit, message: hit ? `Se encontró ${check.label}.` : "" };
    return { ok: hit, message: hit ? "" : `No coincide ${check.label}.` };
  }
  if (check.type === "each_document_contains_any" || check.type === "each_document_forbidden") {
    for (const doc of docs) {
      const phrases = check.any || [];
      const present = phrases.filter((phrase) => hasPhrase(doc.text, phrase));
      if (check.type === "each_document_contains_any" && !present.length) {
        return { ok: false, message: `No aparece ${check.label || "el elemento"} en ${doc.name}.` };
      }
      if (check.type === "each_document_forbidden" && present.length) {
        return { ok: false, message: `Se encontró «${present[0]}» en ${doc.name}.` };
      }
    }
    return { ok: true };
  }
  return { ok: false, message: "Chequeo no soportado en la demo." };
}

function evaluate(rule, docs) {
  const expected = new Set(rule.documents);
  const candidates = docs.filter((doc) => doc.types.some((type) => expected.has(type)));
  if (rule.matcher.require_document && !candidates.length) {
    return { status: "fail", message: "No se encontró el documento esperado." };
  }
  if (!candidates.length) return { status: "pass", message: "Sin documentos en alcance." };
  for (const check of rule.matcher.checks || []) {
    const result = runCheck(check, candidates);
    if (!result.ok) return { status: "fail", message: result.message || "Incumplimiento." };
  }
  return { status: "pass", message: "Cubre el criterio." };
}

function infer(docs) {
  const products = [];
  const joined = docs.map((doc) => fold(doc.text)).join("\n");
  const add = (id, label, phrases) => {
    if (phrases.some((phrase) => joined.includes(fold(phrase)))) products.push({ id, label });
  };
  add("wallet", "Cuenta de dinero electrónico", ["dinero electronico", "fondos de pago electronico"]);
  add("crowdfunding", "Financiamiento colectivo", ["financiamiento colectivo", "crowdfunding"]);
  add("credito", "Crédito", ["riesgo de credito"]);
  add("cripto", "Activos virtuales", ["activo virtual"]);
  const custody = joined.includes("dinero electronico");
  const lines = ["flowchart LR", "  cliente[Cliente] --> entidad[Entidad]"];
  products.forEach((item, index) => lines.push(`  entidad --> p${index}[${item.label}]`));
  if (custody) lines.push("  entidad --> fondos[Recursos de clientes]");
  const coherence = [];
  if (products.some((item) => item.id === "wallet") && !joined.includes("segregacion de")) {
    coherence.push("Hay dinero electrónico y no hay política de segregación de recursos de clientes.");
  }
  return { products, custody, coherence, diagram: lines.join("\n") };
}

function score(findings) {
  const areas = {};
  let got = 0;
  let total = 0;
  for (const finding of findings) {
    if (finding.status === "not_applicable") continue;
    const weight = WEIGHT[finding.severity] || 0;
    if (!weight) continue;
    total += weight;
    const credit = finding.status === "pass" ? 1 : finding.status === "unclear" ? 0.5 : 0;
    got += weight * credit;
    const bucket = areas[finding.area] || { got: 0, total: 0 };
    bucket.total += weight;
    bucket.got += weight * credit;
    areas[finding.area] = bucket;
  }
  const byArea = {};
  for (const [area, bucket] of Object.entries(areas)) {
    byArea[area] = bucket.total ? Math.round((1000 * bucket.got) / bucket.total) / 10 : null;
  }
  return { overall: total ? Math.round((1000 * got) / total) / 10 : null, byArea };
}

function parametersAt(asOf, ruleIds) {
  const gaps = [];
  const values = [];
  for (const item of CATALOG.parameters || []) {
    if (item.used_by?.length && !item.used_by.some((id) => ruleIds.has(id))) continue;
    const hit = (item.values || []).filter((row) => row.effective_from <= asOf && (!row.effective_to || asOf <= row.effective_to)).pop();
    if (!hit) gaps.push(`${item.title}: no hay valor el ${asOf}. No se inventó el monto.`);
    else values.push(`${item.title}: ${hit.value} ${item.unit}`);
  }
  return { gaps, values };
}

function audit(docs, entity, asOf, strictness) {
  const vocabulary = new Set(CATALOG.rules.flatMap((rule) => rule.documents));
  const prepared = docs.map((doc) => ({ ...doc, types: classify(doc.name, doc.text, vocabulary) }));
  const selected = selectRules(asOf);
  const flags = {};
  const findings = [];
  const applicability = [];
  for (const rule of selected.rules) {
    const gate = applies(rule, entity, flags, strictness);
    applicability.push({ id: rule.id, applies: gate.ok, reason: gate.reason });
    if (!gate.ok) continue;
    const result = evaluate(rule, prepared);
    findings.push({ ...rule, status: result.status, message: result.message });
  }
  const profile = infer(prepared);
  const marks = score(findings);
  const params = parametersAt(asOf, new Set(selected.rules.map((rule) => rule.id)));
  return { findings, profile, marks, params, note: selected.note, prepared };
}

function render(result) {
  document.getElementById("out").hidden = false;
  const profile = document.getElementById("profile");
  const names = result.profile.products.map((item) => item.label).join(", ") || "sin producto identificado";
  profile.innerHTML = `<p>Productos: ${escapeHtml(names)}</p>` + result.profile.coherence.map((line) => `<p>${escapeHtml(line)}</p>`).join("");
  document.getElementById("overall").textContent = `${result.marks.overall ?? "n/a"} / 100`;
  const body = document.querySelector("#areas tbody");
  body.innerHTML = "";
  for (const [area, value] of Object.entries(result.marks.byArea).sort()) {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${escapeHtml(area)}</td><td>${value ?? "n/a"}</td>`;
    body.appendChild(row);
  }
  document.getElementById("params").innerHTML = result.params.gaps.map((line) => `<p>${escapeHtml(line)}</p>`).join("")
    || "<p>Los parámetros usados por estas reglas tienen fila en la fecha.</p>";
  document.getElementById("diagram").textContent = result.profile.diagram;
  document.getElementById("status").textContent = result.note;
  LAST = result;
  paintFindings();
}

function paintFindings() {
  if (!LAST) return;
  const mode = document.getElementById("filter").value;
  const host = document.getElementById("findings");
  host.innerHTML = "";
  const rows = LAST.findings.filter((item) => mode === "all" || item.status === mode).slice(0, 40);
  for (const item of rows) {
    const block = document.createElement("article");
    block.className = "finding";
    block.innerHTML = `<p class="${item.status === "fail" ? "fail" : ""}">${escapeHtml(item.status)} · ${escapeHtml(item.severity)} · ${escapeHtml(item.id)}</p><h2>${escapeHtml(item.title)}</h2><p>${escapeHtml(item.message)}</p><p class="meta">${escapeHtml(item.source_name)}</p>`;
    host.appendChild(block);
  }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
}

function download(name, content, type) {
  const blob = new Blob([content], { type });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = name;
  link.click();
}

function reportHtml(result) {
  const rows = result.findings.filter((item) => item.status === "fail").slice(0, 40).map((item) => `<li><strong>${escapeHtml(item.id)}</strong> ${escapeHtml(item.title)}. ${escapeHtml(item.source_name)}</li>`).join("");
  return `<!DOCTYPE html><meta charset="utf-8"><title>Informe</title><h1>${result.marks.overall} / 100</h1><p>No es asesoria legal ni fiscal.</p><ul>${rows}</ul>`;
}

function reportPdf(result) {
  const lines = [
    "fintech-documentation-help",
    "No es asesoria legal ni fiscal.",
    `Calificacion ${result.marks.overall} / 100`,
    result.note,
    ...result.findings.filter((item) => item.status === "fail").slice(0, 25).map((item) => `${item.severity} ${item.id} ${item.title}`),
  ];
  const commands = ["BT", "/F1 10 Tf", "40 780 Td", "14 TL"];
  for (const line of lines) {
    const safe = line.replace(/[^\x20-\x7E]/g, " ").replace(/[()\\]/g, " ");
    commands.push(`(${safe}) Tj`, "T*");
  }
  commands.push("ET");
  const stream = commands.join("\n");
  const objects = [
    "<< /Type /Catalog /Pages 2 0 R >>",
    "<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
    `<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`,
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
  ];
  let blob = "%PDF-1.4\n";
  const offsets = [0];
  objects.forEach((obj, index) => {
    offsets.push(blob.length);
    blob += `${index + 1} 0 obj\n${obj}\nendobj\n`;
  });
  const xref = blob.length;
  blob += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  for (const offset of offsets.slice(1)) blob += `${String(offset).padStart(10, "0")} 00000 n \n`;
  blob += `trailer << /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`;
  return blob;
}

async function loadData() {
  CATALOG = await (await fetch("data/catalog.json")).json();
  SAMPLES = await (await fetch("data/samples.json")).json();
}

function runNamed(name, entity) {
  const docs = SAMPLES[name];
  const asOf = document.getElementById("asof").value;
  document.getElementById("entity").value = entity;
  render(audit(docs, entity, asOf, document.getElementById("strictness").value));
}

async function readFiles(fileList) {
  const docs = [];
  for (const file of fileList) {
    if (/\.(png|jpe?g|tiff?)$/i.test(file.name)) {
      docs.push({ name: file.name, text: await ocrFile(file) });
    } else {
      docs.push({ name: file.name, text: await file.text() });
    }
  }
  const asOf = document.getElementById("asof").value;
  render(audit(docs, document.getElementById("entity").value, asOf, document.getElementById("strictness").value));
}

async function ocrFile(file) {
  document.getElementById("status").textContent = "OCR en el navegador…";
  const { createWorker } = await import("https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.esm.min.js");
  const worker = await createWorker("spa");
  const result = await worker.recognize(file);
  await worker.terminate();
  return result.data.text || "";
}

document.getElementById("nube").addEventListener("click", () => runNamed("nube_pago", "IFPE"));
document.getElementById("nube-en").addEventListener("click", () => runNamed("nube_pago", "IFPE"));
document.getElementById("ladrillo").addEventListener("click", () => runNamed("ladrillo_comun", "IFC"));
document.getElementById("files").addEventListener("change", (event) => readFiles(event.target.files));
document.getElementById("files-en").addEventListener("change", (event) => readFiles(event.target.files));
document.getElementById("filter").addEventListener("change", paintFindings);
document.getElementById("html").addEventListener("click", () => LAST && download("informe.html", reportHtml(LAST), "text/html"));
document.getElementById("html-en").addEventListener("click", () => LAST && download("informe.html", reportHtml(LAST), "text/html"));
document.getElementById("pdf").addEventListener("click", () => LAST && download("informe.pdf", reportPdf(LAST), "application/pdf"));
document.getElementById("pdf-en").addEventListener("click", () => LAST && download("informe.pdf", reportPdf(LAST), "application/pdf"));
document.getElementById("scan").addEventListener("click", scanSample);
document.getElementById("scan-en").addEventListener("click", scanSample);

async function scanSample() {
  const response = await fetch("samples/aviso_escaneado.png");
  const blob = await response.blob();
  const file = new File([blob], "aviso_escaneado.png", { type: "image/png" });
  await readFiles([file]);
}

loadData().then(() => {
  if (location.hash === "#nube") runNamed("nube_pago", "IFPE");
}).catch((error) => {
  document.getElementById("status").textContent = `No se cargó el catálogo: ${error}`;
});
