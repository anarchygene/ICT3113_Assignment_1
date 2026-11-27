// Builds slides/Group09_A2.pptx (8 slides, brief "Slide requirements"). Every number is read from
// assignment2/results/{accuracy,speed}/summary.json and speed/S.json, which analyse_accuracy.py and
// analyse_speed.py generate from the per-ticket records, .jtl files and service logs.
// Run from the repo root:  node slides/build_deck_a2.js   (pptxgenjs on NODE_PATH; APPLY_THEME optional)
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const J = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), "utf8"));
const OUT = path.join(ROOT, "slides/Group09_A2.pptx");
const ACC = J("assignment2/results/accuracy/summary.json");
const SPD = J("assignment2/results/speed/summary.json");
const S = SPD.S;
const C_ = SPD.configs;

const CATS = ["Credit reporting", "Debt collection", "Mortgage", "Credit card", "Bank account or service", "Consumer loan", "Money transfer or service"];
const SHORT = ["Credit rep.", "Debt coll.", "Mortgage", "Credit card", "Bank acct", "Cons. loan", "Money tr."];
const f1 = (x) => Number(x).toFixed(1);

const THEME = {
  name: "Triage Teal",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2A30", lt1: "FFFFFF", dk2: "12343B", lt2: "EEF3F4",
    accent1: "2A9D8F", accent2: "E07A1F", accent3: "8E9AA3", accent4: "C0392B",
    accent5: "3D6B73", accent6: "F2C14E", hlink: "1F6F8B", folHlink: "5B4B8A",
  },
};
const HEX = THEME.colors;
const PASS = "2A9D8F", FAIL = "C0392B";
const COL = { llama: "E07A1F", cascadeA: "8E9AA3", cascadeB: "3D6B73", cascadeA_lock: "9CC9C2", cascadeB_lock: "2A9D8F" };
const NAME = { llama: "Llama alone", cascadeA: "Cascade A (frozen)", cascadeB: "Cascade B (frozen)", cascadeA_lock: "Cascade A + lock*", cascadeB_lock: "Cascade B + lock*" };
const ACCNAME = { llama: "Llama alone", cascadeA: "Cascade A", cascadeB: "Cascade B", cascadeA_lock: "Cascade A", cascadeB_lock: "Cascade B" };

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Group 09 ICT3113 Assignment 2";
pres.author = "Group P1-9";
const C = pres.SchemeColor;

pres.defineSlideMaster({ title: "DARK", background: { color: HEX.dk2 }, objects: [] });
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: HEX.lt1 },
  margin: [0.4, 0.5, 0.4, 0.5],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.22, w: 9.0, h: 0.55, fontSize: 22, bold: true, color: C.text2, fontFace: THEME.headFontFace, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: "Group P1-9 · ICT3113 Assignment 2", options: { x: 0.5, y: 5.32, w: 5, h: 0.22, fontSize: 9, color: C.accent3, margin: 0 } } },
  ],
  slideNumber: { x: 9.0, y: 5.32, w: 0.5, h: 0.22, fontSize: 9, color: HEX.accent3, align: "right" },
});

const txt = (slide, text, o) => slide.addText(text, { isTextBox: true, margin: 0, fontSize: 11, color: C.text1, valign: "top", ...o });
const card = (slide, x, y, w, h, fill = HEX.lt2) =>
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.06 });
const hdr = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: HEX.dk2 } } });
const cell = (t, o = {}) => ({ text: String(t), options: o });
const yesno = (ok) => cell(ok ? "PASS" : "FAIL", { bold: true, color: "FFFFFF", fill: { color: ok ? PASS : FAIL }, align: "center" });
const B = { bullet: { indent: 10 } };
function contentSlide(title, section) {
  const sl = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  sl.addText(title, { placeholder: "title", fontSize: 22, align: "left" });
  return sl;
}

// ============ 1 Cover ============
pres.addSection({ title: "Set-up" });
{
  const sl = pres.addSlide({ masterName: "DARK", sectionTitle: "Set-up" });
  txt(sl, "ICT3113 Assignment 2 · Performance Optimisation", { x: 0.55, y: 0.35, w: 8.9, h: 0.3, fontSize: 12, color: "CFE3E0" });
  txt(sl, "Fast Triage Within an Accuracy Floor", { x: 0.55, y: 0.7, w: 8.9, h: 0.6, fontSize: 30, bold: true, color: "FFFFFF", fontFace: THEME.headFontFace });
  txt(sl, "Can a Gemma → Llama cascade beat the top model alone on the same CPU-only machine?", { x: 0.55, y: 1.32, w: 8.9, h: 0.35, fontSize: 14, italic: true, color: "CFE3E0" });
  txt(sl, "Group P1-9 (Group 09)", { x: 0.55, y: 1.9, w: 4.2, h: 0.3, fontSize: 15, bold: true, color: HEX.accent6, fontFace: THEME.headFontFace });
  const members = ["Chew E Jae Justin · 2400851", "Eugene Kee Zong Lin · 2402575", "Tan Ye Kai · 2403052", "Tok You Xiong · 2401871", "Yap Hong Xiang, Alfred · 2401438"];
  txt(sl, members.map((m, i) => ({ text: m, options: { breakLine: i < members.length - 1 } })), { x: 0.55, y: 2.25, w: 4.2, h: 1.5, fontSize: 11.5, color: "FFFFFF", paraSpaceAfter: 3 });
  txt(sl, [
    { text: "Repository: ", options: { color: "CFE3E0" } },
    { text: "github.com/anarchygene/ICT3113_Assignment_1 (branch Assignment2)", options: { color: "FFFFFF", hyperlink: { url: "https://github.com/anarchygene/ICT3113_Assignment_1/tree/Assignment2" } } },
  ], { x: 0.55, y: 3.85, w: 4.3, h: 0.45, fontSize: 10 });
  txt(sl, [
    { text: "Supporting documents: ", options: { color: "CFE3E0" } },
    { text: "Google Drive folder", options: { color: "FFFFFF", hyperlink: { url: "https://drive.google.com/drive/folders/10I7v22nkXLYZGCKVxepytw7TX5KMS4pF?usp=sharing" } } },
  ], { x: 0.55, y: 4.35, w: 4.3, h: 0.25, fontSize: 10 });
  // Top model and limits
  card(sl, 5.05, 1.9, 4.45, 3.3, "1D4A52");
  const ll = ACC.configs["Llama alone"];
  txt(sl, [
    { text: "Top model (reference): Llama 3.1 8B Instruct", options: { bold: true, color: HEX.accent6, breakLine: true } },
    { text: "llama3.1:8b-instruct-q4_K_M · ID 46e0c10c039e", options: { fontSize: 9.5, color: "CFE3E0", breakLine: true } },
    { text: `A1 accuracy: 121/160 = 75.6% (full golden set) · test set (80 even rows): ${ll.correct}/80 = ${(100 * ll.correct / 80).toFixed(2)}%`, options: { fontSize: 10, color: "FFFFFF" } },
  ], { x: 5.2, y: 2.0, w: 4.2, h: 0.85 });
  const lrows = [[hdr("Limit (test set)"), hdr("Top model"), hdr("Minimum")],
    [cell("Overall (−10 pts)", { bold: true }), cell(`${ll.correct}/80`), cell(`${ACC.floor_overall}/80 (66.25%)`, { bold: true })],
    ...CATS.map((c, i) => [cell(`${SHORT[i]} (−15 pts)${ACC.n[c] < 10 ? " †" : ""}`), cell(`${ll.per_category[c]}/${ACC.n[c]}`), cell(`${ACC.floor[c]}/${ACC.n[c]}`)])];
  sl.addTable(lrows, { x: 5.2, y: 2.88, w: 4.15, colW: [1.75, 1.0, 1.4], fontSize: 9, color: "1B2A30", fill: { color: "FFFFFF" }, border: { type: "solid", color: "D5DEE1", pt: 0.5 }, margin: 0.025, rowH: 0.2 });
  txt(sl, "† fewer than 10 tickets: one ticket moves the score 12.5–16.7 pts; Credit card fails on a single error.", { x: 0.55, y: 4.75, w: 4.3, h: 0.45, fontSize: 9, italic: true, color: "CFE3E0" });
  sl.addNotes("Limits from assignment2/ACCURACY_LIMITS.md, recomputed by assignment2/scripts/analyse_accuracy.py from the Step 1 Llama re-run (assignment2/results/step1_top_model_test_set), which reproduced the A1 answers on 80/80 test tickets.");
}

// ============ 2 Cascade design ============
{
  const sl = contentSlide("Cascade design: Gemma 3 1B first, Llama 3.1 8B on escalation", "Set-up");
  const box = (x, y, w, h, title, sub, fill) => {
    card(sl, x, y, w, h, fill);
    txt(sl, [{ text: title, options: { bold: true, breakLine: !!sub } }, ...(sub ? [{ text: sub, options: { fontSize: 9.5 } }] : [])], { x: x + 0.08, y: y + 0.06, w: w - 0.16, h: h - 0.1, fontSize: 10.5, align: "center", valign: "middle" });
  };
  const arrow = (x1, y1, x2, y2, label) => {
    // Sizes must be non-negative: an upward line is drawn top-down and flipped vertically.
    sl.addShape(pres.shapes.LINE, {
      x: x1, y: Math.min(y1, y2), w: x2 - x1, h: Math.abs(y2 - y1), flipV: y2 < y1,
      line: { color: HEX.dk2, width: 1.25, endArrowType: "triangle" },
    });
    if (label) txt(sl, label, { x: Math.min(x1, x2) + 0.04, y: Math.min(y1, y2) - 0.24, w: Math.abs(x2 - x1) + 0.6, h: 0.22, fontSize: 8.5, color: C.accent5, italic: true });
  };
  box(0.5, 1.25, 1.15, 0.7, "POST /tickets", "one ticket", "E4E9EC");
  box(2.0, 1.25, 1.45, 0.7, "Gemma 3 1B", "A1 prompt, unchanged", "DDF0EE");
  box(3.85, 1.15, 1.75, 0.9, "Rule", "valid answer AND on the accept list?", "FBEBDD");
  box(6.05, 0.95, 1.6, 0.6, "Accept Gemma's answer", null, "DDF0EE");
  box(6.05, 1.75, 1.6, 0.6, "Llama 3.1 8B", "answer is final", "FBEBDD");
  box(8.1, 1.25, 1.4, 0.7, "One category", "same response either way", "E4E9EC");
  arrow(1.65, 1.6, 2.0, 1.6); arrow(3.45, 1.6, 3.85, 1.6);
  arrow(5.6, 1.4, 6.05, 1.25, "yes"); arrow(5.6, 1.8, 6.05, 2.05, "no / invalid");
  arrow(7.65, 1.25, 8.1, 1.5); arrow(7.65, 2.05, 8.1, 1.7);
  txt(sl, "Escalation rule in full (assignment2/STEP2.md, frozen 26 Nov)", { x: 0.5, y: 2.55, w: 5.0, h: 0.25, fontSize: 12, bold: true, color: C.text2 });
  txt(sl, [
    { text: "Gemma classifies every ticket with the unchanged A1 request (same prompt, JSON mode, temperature 0, num_ctx 4096).", options: { ...B, breakLine: true } },
    { text: "Escalate to Llama if Gemma's answer is invalid (not one of the 7 exact categories, or the call fails/times out).", options: { ...B, breakLine: true } },
    { text: "Otherwise accept Gemma's answer only if it is on the accept list; else escalate. Llama's answer is final; if it is invalid → HTTP 502 (no fall-back).", options: { ...B, breakLine: true } },
    { text: "Setting A: accept Mortgage, Debt collection.   Setting B: accept Mortgage only.", options: { ...B, bold: true, breakLine: true } },
    { text: "Every ticket logs one triage line: which model answered, escalated or not, why, and each model's time.", options: B },
  ], { x: 0.5, y: 2.85, w: 5.0, h: 2.3, fontSize: 10, paraSpaceAfter: 3 });
  card(sl, 5.75, 2.55, 3.75, 2.6);
  txt(sl, [
    { text: "Why this rule and pair", options: { bold: true, color: HEX.dk2, fontSize: 12, breakLine: true } },
    { text: "Category-based (brief method 1). On the tuning set (odd rows), Gemma's Mortgage (8/11) and Debt collection (5/9) answers are worth keeping; its 32 'Credit reporting' answers are right only 12 times. No extra model call.", options: { ...B, breakLine: true } },
    { text: "Memory check: Qwen + Llama does not fit the 7.5 GiB Docker VM. Ollama evicted a model on every switch and the kernel OOM-killed Llama 5 times, so the pair changed to Gemma + Llama (6.6 GiB, both resident, 0 evictions once Llama loads first).", options: { ...B, breakLine: true } },
    { text: "Two settings chosen on the tuning set only: A escalates 75%, B 86%.", options: B },
  ], { x: 5.88, y: 2.63, w: 3.5, h: 2.48, fontSize: 9.5, paraSpaceAfter: 3 });
  sl.addNotes("Evidence: assignment2/STEP2.md (rule, tuning-set tables), assignment2/evidence/preflight_lenovo/PREFLIGHT.md (Qwen+Llama evictions and OOM kills; Gemma+Llama and Gemma+Qwen fit), evidence/preflight_lenovo_v2 (every branch of the rule incl. the 502 path tested on the Lenovo). Code: app/cascade.py.");
}

// ============ 3 Environment and method ============
{
  const sl = contentSlide("Test environment and method", "Set-up");
  txt(sl, [
    { text: "Machines: unchanged from Assignment 1", options: { bold: true, color: HEX.dk2, fontSize: 12, breakLine: true } },
    { text: "Service: Lenovo laptop, Intel Core Ultra 7 256V, Docker VM 8 CPUs / 7.53 GiB (same limits), Ollama 0.12.3, same model digests.", options: { ...B, breakLine: true } },
    { text: "Load generator: separate Ryzen 5 3600 desktop, JMeter 5.6.3, wired to the same router. Never co-hosted.", options: { ...B, breakLine: true } },
    { text: "Ollama settings held constant for every configuration: NUM_PARALLEL 1, context 4096.", options: B },
  ], { x: 0.5, y: 0.95, w: 4.4, h: 1.7, fontSize: 10, paraSpaceAfter: 3 });
  card(sl, 5.1, 0.95, 4.4, 1.7, "FBEBDD");
  txt(sl, [
    { text: "Arrival rate (brief Step 4 set-up)", options: { bold: true, color: HEX.dk2, fontSize: 12, breakLine: true } },
    { text: `Llama alone, three median-length tickets (rows ${S.rows.join(", ")}): ${S.timings_s.join(" / ")} s → S = ${S.S_s} s.`, options: { breakLine: true } },
    { text: `One ticket every 2S = ${S.interval_s} s (${S.rate_per_hour}/h), run ${S.run_min} min (29 tickets), response timeout ${S.response_timeout_s} s, pause ${S.pause_min} min.`, options: { breakLine: true } },
    { text: `Above the A1 client peak (81/h; 105/h with headroom).`, options: { bold: true } },
  ], { x: 5.22, y: 1.03, w: 4.18, h: 1.58, fontSize: 10, paraSpaceAfter: 3 });
  txt(sl, "Each run (3 per configuration)", { x: 0.5, y: 2.8, w: 4.4, h: 0.25, fontSize: 12, bold: true, color: C.text2 });
  txt(sl, [
    { text: "Restart Ollama (clears the prompt cache), wait for /health.", options: { ...B, breakLine: true } },
    { text: "3 fixed warm-up tickets (rows 9716, 9438, 9775), timings discarded.", options: { ...B, breakLine: true } },
    { text: "Cascade: load Llama then Gemma; start only when both are resident (ollama ps).", options: { ...B, breakLine: true } },
    { text: "/stats before → open-loop JMeter (Open Model, random arrivals) → drain → /stats after.", options: { ...B, breakLine: true } },
    { text: "Ollama log checked for model loads, evictions, kills during the run: none in all 15 runs.", options: B },
  ], { x: 0.5, y: 3.08, w: 4.4, h: 2.1, fontSize: 10, paraSpaceAfter: 2 });
  txt(sl, "Workload and changes from A1", { x: 5.1, y: 2.8, w: 4.4, h: 0.25, fontSize: 12, bold: true, color: C.text2 });
  txt(sl, [
    { text: "60 fixed rows from 9000–9839 (never golden), same order every run: 48 typical + 12 long (every 5th ticket long).", options: { ...B, breakLine: true } },
    { text: "Change: OLLAMA_KEEP_ALIVE 30 min (was 5) for all configurations, so an idle Llama is not unloaded mid-run.", options: { ...B, breakLine: true } },
    { text: "Change: no GET /search traffic (A1 had it); same for every configuration.", options: { ...B, breakLine: true } },
    { text: "*Post-freeze: an optional lock in POST /tickets (one Ollama call at a time), added after cascade run 1 collapsed; rule unchanged. Speed-tested as '+ lock'.", options: B },
  ], { x: 5.1, y: 3.08, w: 4.4, h: 2.1, fontSize: 10, paraSpaceAfter: 2 });
  sl.addNotes("S and rate: assignment2/results/speed/S.json and S.md. Workload: assignment2/workload (README.md, speed_tickets.tsv, warmup_tickets.tsv). Per-run procedure: assignment2/scripts/speed_service.py (Lenovo) and assignment2/jmeter/run_speed.ps1 (load generator). The machines and Docker limits are recorded in assignment2/evidence/preflight_lenovo/environment.txt.");
}

// ============ 4 Accuracy ============
pres.addSection({ title: "Results" });
{
  const sl = contentSlide("Accuracy (80 test rows): only Llama alone and cascade B pass", "Results");
  const order = ["Llama alone", "Qwen alone", "Gemma alone", "Cascade A", "Cascade B"];
  const rows = [[hdr("Configuration"), hdr("Overall"), ...SHORT.map((s, i) => hdr(`${s} ≥${ACC.floor[CATS[i]]}/${ACC.n[CATS[i]]}`)), hdr("Limits")]];
  for (const name of order) {
    const a = ACC.configs[name];
    rows.push([
      cell(name, { bold: true }),
      cell(`${a.correct}/80 ${(100 * a.correct / 80).toFixed(1)}%`, a.correct < ACC.floor_overall ? { color: FAIL, bold: true } : {}),
      ...CATS.map((c) => cell(`${a.per_category[c]}/${ACC.n[c]}`, a.per_category[c] < ACC.floor[c] ? { color: FAIL, bold: true } : {})),
      yesno(a.fails.length === 0),
    ]);
  }
  sl.addTable(rows, { x: 0.5, y: 0.9, w: 9.0, colW: [1.25, 1.05, 0.82, 0.82, 0.82, 0.82, 0.82, 0.82, 0.82, 0.97], fontSize: 9, border: { type: "solid", color: "D5DEE1", pt: 0.5 }, margin: 0.03, rowH: 0.27, valign: "middle", align: "center" });
  txt(sl, "Overall floor 53/80. Red = below the limit. Qwen and Gemma: A1 per-ticket records reused, even rows only (unchanged digest, prompt, Ollama, machine). Llama: re-run 18 Nov, identical to A1. Mortgage, Credit card, Consumer loan have < 10 tickets.", { x: 0.5, y: 2.6, w: 9.0, h: 0.35, fontSize: 8.5, italic: true, color: C.accent5 });
  const ca = ACC.configs["Cascade A"], cb = ACC.configs["Cascade B"];
  const erows = [[hdr("Cascade"), hdr("Escalated"), hdr("why: invalid / category"), hdr("Escalated: correct"), hdr("Accepted (Gemma): correct")],
    ...[["A", ca], ["B", cb]].map(([n, a]) => [cell(`Setting ${n}`, { bold: true }), cell(`${a.escalated}/80 = ${(100 * a.escalated / 80).toFixed(1)}%`), cell(`${a.esc_invalid} / ${a.esc_category}`),
      cell(`${a.esc_correct}/${a.escalated} = ${(100 * a.esc_correct / a.escalated).toFixed(1)}%`), cell(`${a.acc_correct}/${a.acc_n} = ${(100 * a.acc_correct / a.acc_n).toFixed(1)}%`)])];
  sl.addTable(erows, { x: 0.5, y: 3.05, w: 5.6, colW: [0.9, 1.15, 1.25, 1.15, 1.15], fontSize: 9, border: { type: "solid", color: "D5DEE1", pt: 0.5 }, margin: 0.03, rowH: 0.27, valign: "middle", align: "center" });
  txt(sl, [
    { text: "The rule catches Gemma's weak answers: ", options: { bold: true } },
    { text: `accepted Gemma answers are only ${(100 * ca.acc_correct / ca.acc_n).toFixed(1)}–${(100 * cb.acc_correct / cb.acc_n).toFixed(1)}% right, escalated tickets ${(100 * ca.esc_correct / ca.escalated).toFixed(1)}–${(100 * cb.esc_correct / cb.escalated).toFixed(1)}%. ` },
    { text: "Where it loses: ", options: { bold: true } },
    { text: `A accepts Gemma's Mortgage/Debt-collection answers on ${ca.accepted_wrong_true_categories["Credit reporting"] || 0} Credit-reporting and ${ca.accepted_wrong_true_categories["Consumer loan"] || 0} Consumer-loan tickets, which fails both limits. B gives up one ticket each in Credit reporting, Consumer loan and Money transfer against Llama and stays on or above every floor.` },
  ], { x: 0.5, y: 3.95, w: 5.6, h: 1.25, fontSize: 9.5 });
  card(sl, 6.35, 3.05, 3.15, 2.15);
  txt(sl, [
    { text: "Confusion highlights", options: { bold: true, color: HEX.dk2, breakLine: true } },
    { text: "Qwen: 10/19 Credit reporting (4 sent to Credit card, 4 to Debt collection); 5/6 Credit card.", options: { ...B, breakLine: true } },
    { text: "Gemma: 20/80; 0/15 Money transfer; 14 of 80 answers invalid.", options: { ...B, breakLine: true } },
    { text: "Llama: 14/19 Credit reporting, 14/15 Money transfer; errors spread across categories.", options: { ...B, breakLine: true } },
    { text: "Full matrices: results/accuracy/summary.json.", options: { ...B, italic: true } },
  ], { x: 6.47, y: 3.12, w: 2.95, h: 2.0, fontSize: 9, paraSpaceAfter: 2 });
  sl.addNotes("Generated by assignment2/scripts/analyse_accuracy.py into assignment2/results/accuracy/summary.md and summary.json. Cascade runs: assignment2/results/accuracy/cascade{A,B} (predictions.csv, confusion_matrix.csv, api.log with one triage line per ticket; both models resident, 0 loads/evictions/kills during the test). Lock variants: identical requests, so identical answers (spot-checked 3/3 on tuning rows, evidence/lock_variant).");
}

// ============ 5 Speed ============
{
  const sl = contentSlide("Speed: frozen cascade collapsed; with a lock it ties Llama", "Results");
  const order = ["llama", "cascadeA", "cascadeB", "cascadeA_lock", "cascadeB_lock"];
  const rows = [[hdr("Configuration"), hdr("p50 run 1 / 2 / 3 (s)"), hdr("p50 mean (range)"), hdr("Pooled p95 (n)"), hdr("Completed / sent"), hdr("Throughput /s per run"), hdr("Error % per run"), hdr("Escalated under load")]];
  for (const k of order) {
    const c = C_[k];
    const bad = c.completed < c.sent;
    rows.push([
      cell(NAME[k], { bold: true, color: COL[k] === "9CC9C2" ? HEX.accent5 : COL[k] }),
      cell(c.p50_per_run_s.map(f1).join(" / ")),
      cell(`${f1(c.p50_mean_s)} (${f1(c.p50_min_s)}–${f1(c.p50_max_s)})`, { bold: true }),
      cell(`${f1(c.p95_pooled_s)} (n=${c.p95_n})`),
      cell(`${c.completed}/${c.sent}`, bad ? { color: FAIL, bold: true } : {}),
      cell(c.throughput_per_run.map((t) => t.toFixed(3)).join(" / ")),
      cell(c.error_rate_per_run.map((e) => e.toFixed(0)).join(" / "), bad ? { color: FAIL, bold: true } : {}),
      cell(c.escalated == null ? "n/a" : `${c.escalated}/${c.escalated_of}${c.esc_small_timeout ? ` (${c.esc_small_timeout} Gemma timeouts)` : ""}`),
    ]);
  }
  sl.addTable(rows, { x: 0.5, y: 0.9, w: 9.0, colW: [1.3, 1.35, 1.15, 0.95, 0.85, 1.2, 0.85, 1.35], fontSize: 9, border: { type: "solid", color: "D5DEE1", pt: 0.5 }, margin: 0.03, rowH: 0.3, valign: "middle", align: "center" });
  txt(sl, `Rate ${S.rate_per_hour}/h, 29 tickets per run, 3 runs each. p50/p95 from completed requests only (brief); no p99. Every JMeter request has one service-log line; /stats delta = service 201s in all 15 runs. *Post-freeze lock variant.`, { x: 0.5, y: 2.85, w: 9.0, h: 0.32, fontSize: 8.5, italic: true, color: C.accent5 });
  card(sl, 0.5, 3.25, 4.4, 1.95, "FBE3E0");
  txt(sl, [
    { text: "Why the frozen cascade collapsed", options: { bold: true, color: FAIL, breakLine: true } },
    { text: "Under open-loop load one ticket's Llama call overlaps the next ticket's Gemma call. Each Ollama runner uses all 8 CPU threads, so both slow down: alone Gemma 0.7–1.2 s and Llama 3.2–3.4 s; together 63–70 s each, with no rise in disk page faults (CPU contention, not memory). The queue grows all run; 72/87 requests pass JMeter's 300 s timeout.", options: {} },
  ], { x: 0.62, y: 3.33, w: 4.18, h: 1.82, fontSize: 9.5 });
  card(sl, 5.1, 3.25, 4.4, 1.95, "DDF0EE");
  const L = C_.llama, BL = C_.cascadeB_lock;
  txt(sl, [
    { text: "With the lock (one model call at a time)", options: { bold: true, color: HEX.dk2, breakLine: true } },
    { text: `0 errors, 87/87 completed. Cascade B + lock p50 ${f1(BL.p50_mean_s)} s vs Llama ${f1(L.p50_mean_s)} s: a ${f1(L.p50_mean_s - BL.p50_mean_s)} s difference inside the run-to-run spread (Llama ${f1(L.p50_min_s)}–${f1(L.p50_max_s)} s). Better tail: p95 ${f1(BL.p95_pooled_s)} s vs ${f1(L.p95_pooled_s)} s. It still escalates ${BL.escalated}/${BL.escalated_of} (93%), so most tickets pay Gemma + Llama. Escalation under load (rule only) is close to the accuracy test (85% A, 92.5% B); the frozen runs' 84/87 includes 54 Gemma timeouts treated as invalid.`, options: {} },
  ], { x: 5.22, y: 3.33, w: 4.18, h: 1.82, fontSize: 9.5 });
  sl.addNotes("Generated by assignment2/scripts/analyse_speed.py from every run's results.jtl (load generator) and api.log, stats_*.json, ollama_events_during_run.json (Lenovo), in assignment2/results/speed/<config>/run<N>/. Per-run table: assignment2/results/speed/summary.md. Concurrency diagnostic: assignment2/evidence/concurrency_check/result.txt. Run 1 was the slowest run in every series.");
}

// ============ 6 Trade-off ============
{
  const sl = contentSlide("Trade-off: nothing inside the limit is faster than Llama", "Results");
  const keys = ["llama", "cascadeA", "cascadeB", "cascadeA_lock", "cascadeB_lock"];
  const accOf = (k) => 100 * ACC.configs[ACCNAME[k]].correct / 80;
  const xs = [...keys.map(accOf), 66.25, 66.25];
  const data = [{ name: "X", values: xs }];
  keys.forEach((k, i) => data.push({ name: NAME[k], values: xs.map((_, j) => (j === i ? C_[k].p50_mean_s : null)) }));
  data.push({ name: "Overall limit 66.25%", values: xs.map((_, j) => (j === 5 ? 5 : j === 6 ? 500 : null)) });
  sl.addChart(pres.charts.SCATTER, data, {
    x: 0.4, y: 0.85, w: 5.9, h: 4.35,
    chartColors: [...keys.map((k) => COL[k]), FAIL],
    lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 11,
    valAxisLogScaleBase: 10, valAxisMinVal: 5, valAxisMaxVal: 500,
    catAxisMinVal: 62, catAxisMaxVal: 80, catAxisMajorUnit: 2,
    showValAxisTitle: true, valAxisTitle: "p50 under load, mean of 3 runs (s, log scale)", valAxisTitleFontSize: 9, valAxisTitleColor: "5A6A70",
    showCatAxisTitle: true, catAxisTitle: "Accuracy on the 80 test tickets (%)", catAxisTitleFontSize: 9, catAxisTitleColor: "5A6A70",
    catAxisLabelFontSize: 9, valAxisLabelFontSize: 9, catAxisLabelColor: "5A6A70", valAxisLabelColor: "5A6A70",
    catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", valGridLine: { color: "E1E7EA", size: 0.5 }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendFontSize: 8.5, legendFontFace: "+mn-lt",
  });
  card(sl, 6.5, 0.9, 3.0, 4.3);
  const L = C_.llama;
  txt(sl, [
    { text: "Reading the chart", options: { bold: true, color: HEX.dk2, fontSize: 12, breakLine: true } },
    { text: "Left of the red line fails the overall limit; lower is faster.", options: { ...B, breakLine: true } },
    { text: `Llama alone: ${(100 * ACC.configs["Llama alone"].correct / 80).toFixed(1)}% at ${f1(L.p50_mean_s)} s.`, options: { ...B, breakLine: true } },
    { text: `Frozen cascades sit ~11× higher (${f1(C_.cascadeA.p50_mean_s)}–${f1(C_.cascadeB.p50_mean_s)} s, and only 15/87 requests completed).`, options: { ...B, breakLine: true } },
    { text: "With the lock, the cascades drop onto Llama's latency but not below it; their 0.3–0.4 s advantage is smaller than the run spread.", options: { ...B, breakLine: true } },
    { text: "Cascade A also fails two category limits (Credit reporting, Consumer loan); B passes all.", options: { ...B, breakLine: true } },
    { text: "Qwen and Gemma alone fail accuracy, so they were not speed-tested (brief).", options: B },
  ], { x: 6.62, y: 0.98, w: 2.78, h: 4.15, fontSize: 9.5, paraSpaceAfter: 4 });
  sl.addNotes("Points: x = test-set accuracy (results/accuracy/summary.json), y = mean of the three per-run p50s (results/speed/summary.json). The lock variants have the same accuracy as their frozen settings because the requests are identical.");
}

// ============ 7 Predictions, recommendation ============
pres.addSection({ title: "Recommendation" });
{
  const sl = contentSlide("Recommendation: deploy Llama 3.1 8B alone", "Recommendation");
  const ok = (b) => cell(b ? "✓" : "✗", { bold: true, color: b ? PASS : FAIL, align: "center" });
  const ca = ACC.configs["Cascade A"], cb = ACC.configs["Cascade B"], q = ACC.configs["Qwen alone"];
  const prow = (a, b, c, d) => [cell(a, { bold: true }), cell(b), cell(c), ok(d)];
  const rows = [[hdr("Prediction (frozen 26 Nov)"), hdr("Predicted"), hdr("Measured"), hdr("")],
    prow("Fastest passing configuration", "Llama alone", "Llama alone", true),
    prow("Qwen alone", "fails CR, DC (54/80)", `fails CR, CC (${q.correct}/80)`, true),
    prow("Setting A accuracy / escalated", "57/80, fails Loan / 80%", `${ca.correct}/80, fails CR + Loan / ${(100 * ca.escalated / 80).toFixed(0)}%`, false),
    prow("Setting B accuracy / escalated", "59/80, passes / 90%", `${cb.correct}/80, passes / ${(100 * cb.escalated / 80).toFixed(1)}%`, true),
    prow("S", "≈ 13 s", `${S.S_s} s`, false),
    prow("Llama under load p50 / p95", "14.3 s / 26 s", `${f1(C_.llama.p50_mean_s)} s / ${f1(C_.llama.p95_pooled_s)} s`, false),
    prow("Cascade B under load p50 / p95", "15.6 s / 29 s", `${f1(C_.cascadeB.p50_mean_s)} s / ${f1(C_.cascadeB.p95_pooled_s)} s`, false),
    prow("Largest category loss", "Consumer loan; CR loses 0", "Loan −2 (A) ✓; CR −3 (A) ✗", false),
  ];
  sl.addTable(rows, { x: 0.5, y: 0.88, w: 5.5, colW: [1.85, 1.55, 1.75, 0.35], fontSize: 8.5, border: { type: "solid", color: "D5DEE1", pt: 0.5 }, margin: 0.03, rowH: 0.27, valign: "middle" });
  txt(sl, [
    { text: "Why they differed: ", options: { bold: true } },
    { text: "we priced a model switch at the 0.1–0.3 s reload cost and never modelled two Ollama runners computing at once, which is what open-loop load causes; that single omission explains the collapse. Credit-reporting tickets that Gemma called Mortgage/Debt collection slipped through A's accept list (4 tickets). Llama's p95 was set by run 1 (max 92 s), the slowest run in every series." },
  ], { x: 0.5, y: 3.4, w: 5.5, h: 1.8, fontSize: 9.5 });
  card(sl, 6.25, 0.88, 3.25, 4.32, "DDF0EE");
  const L = C_.llama, BL = C_.cascadeB_lock;
  txt(sl, [
    { text: "Deploy Llama 3.1 8B alone", options: { bold: true, color: HEX.dk2, fontSize: 13, breakLine: true } },
    { text: "llama3.1:8b-instruct-q4_K_M (46e0c10c039e)", options: { fontSize: 9, color: HEX.accent5, breakLine: true } },
    { text: `Fastest configuration that passes both limits: p50 ${f1(L.p50_mean_s)} s, p95 ${f1(L.p95_pooled_s)} s, 87/87 completed at ${S.rate_per_hour}/h.`, options: { ...B, breakLine: true } },
    { text: "Speed gain vs the top model: none (it is the top model). Accuracy given up: none (61/80, every category at the reference).", options: { ...B, breakLine: true } },
    { text: `Cascade B passes accuracy but, as frozen, is ~11× slower (p50 ${f1(C_.cascadeB.p50_mean_s)} s; 72/87 timed out) because Gemma and Llama compete for the 8 CPUs.`, options: { ...B, breakLine: true } },
    { text: `With the post-freeze lock it only ties (p50 ${f1(BL.p50_mean_s)} s): escalating 93% means most tickets pay for both models, so there is no time to save. The 0.3 s edge is inside the run spread, costs 3 correct tickets and needs post-freeze code.`, options: B },
  ], { x: 6.37, y: 0.96, w: 3.03, h: 4.18, fontSize: 9.5, paraSpaceAfter: 4 });
  sl.addNotes("Predictions: assignment2/PREDICTIONS.md (frozen with STEP2.md in commit 467b461, before any A2 benchmark). Measured: results/accuracy/summary.json, results/speed/summary.json. Brief's latency model: cascade ≈ small + escalation × large; at 93% escalation this is about Gemma + Llama for most tickets.");
}

// ============ 8 Limitations, references, AI ============
{
  const sl = contentSlide("Limitations, references and AI declaration", "Recommendation");
  txt(sl, "What the results do not show", { x: 0.5, y: 0.88, w: 4.4, h: 0.25, fontSize: 12, bold: true, color: C.text2 });
  txt(sl, [
    { text: "Sample size: 80 test tickets (3 categories < 10); 29 tickets per run, 3 runs. Small differences (e.g. 16.2 vs 16.6 s) are not meaningful.", options: { ...B, breakLine: true } },
    { text: "One machine (a laptop on Wi-Fi) and one arrival rate. The rate (162.9/h) is above the client peak (81/h, 105/h with headroom), so Llama alone is also shown to handle the client's peak load.", options: { ...B, breakLine: true } },
    { text: "Seen tickets: the test set was answered in A1; it is a fair comparison, not new data.", options: { ...B, breakLine: true } },
    { text: "Run 1 was the slowest in every series (cause not identified); all runs are reported.", options: { ...B, breakLine: true } },
    { text: "The lock variant is post-freeze; its accuracy is inferred from identical requests (spot-checked), not a separate test-set run.", options: { ...B, breakLine: true } },
    { text: "Keep-alive raised to 30 min for every configuration (only change to Ollama settings).", options: B },
  ], { x: 0.5, y: 1.16, w: 4.4, h: 4.05, fontSize: 9.5, paraSpaceAfter: 4 });
  txt(sl, "References and licences", { x: 5.1, y: 0.88, w: 4.4, h: 0.25, fontSize: 12, bold: true, color: C.text2 });
  const refs = [
    "Consumer Financial Protection Bureau. Consumer Complaint Database. consumerfinance.gov/data-research/consumer-complaints (course extract, rows 9000–9999)",
    "Ollama 0.12.3, MIT License. github.com/ollama/ollama",
    "Llama 3.1 8B Instruct (Meta), Llama 3.1 Community License. Built with Llama.",
    "Gemma 3 1B (Google DeepMind), Gemma Terms of Use. ai.google.dev/gemma/terms",
    "Qwen3-4B-Instruct-2507 (Alibaba Qwen), Apache License 2.0",
    "Apache JMeter 5.6.3, Apache License 2.0 · PostgreSQL 16 · FastAPI (MIT)",
  ];
  txt(sl, refs.map((r, i) => ({ text: r, options: { breakLine: i < refs.length - 1 } })), { x: 5.1, y: 1.16, w: 4.4, h: 2.15, fontSize: 9, paraSpaceAfter: 3 });
  card(sl, 5.1, 3.38, 4.4, 1.4);
  txt(sl, [
    { text: "AI declaration", options: { bold: true, color: HEX.dk2, breakLine: true } },
    { text: "Claude Code (Anthropic) wrote the cascade and lock code, the JMeter plan and run scripts, the memory/concurrency checks, the analysis scripts, and drafted these slides. The team chose the pair, rule and settings, made and froze the predictions, ran every accuracy and speed test on the two machines, decided to add the lock variant, and made the recommendation.", options: {} },
  ], { x: 5.22, y: 3.45, w: 4.18, h: 1.28, fontSize: 9 });
  sl.addNotes("Every figure on slides 4-7 is generated from files in assignment2/results and assignment2/evidence (analyse_accuracy.py, analyse_speed.py).");
}

// pptxgenjs writes a missing scatter value as an empty <c:v></c:v>, which PowerPoint refuses. In OOXML a
// missing point is simply absent (a gap), so drop those <c:pt> elements from the chart parts.
async function dropEmptyChartPoints(file) {
  const JSZip = require("jszip");
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  for (const name of Object.keys(zip.files).filter((n) => /^ppt\/charts\/chart\d+\.xml$/.test(n))) {
    const xml = await zip.file(name).async("string");
    zip.file(name, xml.replace(/<c:pt idx="\d+"><c:v><\/c:v><\/c:pt>/g, ""));
  }
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await dropEmptyChartPoints(OUT);
  if (process.env.APPLY_THEME) {
    const { applyTheme } = require(process.env.APPLY_THEME);
    await applyTheme(OUT, THEME);
  }
  console.log("wrote", OUT);
})();
