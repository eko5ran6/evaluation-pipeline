async function loadSummary() {
  const res = await fetch("/api/summary", { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to load summary.json: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

function fmtMaybe(x) {
  if (x === null || x === undefined) return "";
  if (typeof x === "number") return x.toFixed(3);
  return String(x);
}

function uniqueLabels(models) {
  return (models || []).map((m) => m.label);
}

function buildModelSelect(models) {
  const el = document.getElementById("modelSelect");
  el.innerHTML = "";
  const labels = uniqueLabels(models);

  for (const label of labels) {
    const opt = document.createElement("option");
    opt.value = label;
    opt.textContent = label;
    el.appendChild(opt);
  }
}

function setMeta(payload) {
  const meta = document.getElementById("meta");
  const models = payload?.models || [];
  meta.textContent = `Models: ${models.length}. Metrics: ${payload?.metrics?.join(", ") || ""}`;
}

function getMetricAvailability(payload) {
  const metricSet = new Set(payload?.metrics || []);
  return {
    hasEntityRecall: metricSet.has("entity_recall"),
    hasRougeL: metricSet.has("rouge_l"),
  };
}

function plotMeanBars(models, metricKey, chartDiv, options) {
  const x = [];
  const y = [];

  for (const m of models) {
    const val = m?.aggregate?.[metricKey];
    if (typeof val === "number") {
      x.push(m.label);
      y.push(val);
    }
  }

  const title = options?.title || "";
  const yLabel = options?.yLabel || metricKey;

  const data = [
    {
      type: "bar",
      x,
      y,
      text: y.map((v) => v.toFixed(3)),
      textposition: "auto",
    },
  ];

  const layout = {
    title,
    margin: { l: 40, r: 10, t: 40, b: 80 },
    xaxis: { tickangle: -35 },
    yaxis: { title: yLabel, rangemode: "tozero" },
  };

  Plotly.newPlot(chartDiv, data, layout, { responsive: true });
}

function renderPerCaseTable(payload) {
  const models = payload.models || [];
  const modelSelect = document.getElementById("modelSelect");
  const caseFilter = document.getElementById("caseFilter");
  const tableBody = document.querySelector("#perCaseTable tbody");
  tableBody.innerHTML = "";

  const selectedLabel = modelSelect.value;
  const selectedModel = models.find((m) => m.label === selectedLabel);
  const perCase = selectedModel?.per_case || [];

  const filterMode = caseFilter.value; // all|ok|missing

  const rows = perCase.filter((r) => {
    if (filterMode === "all") return true;
    if (filterMode === "ok") return r.status === "ok";
    if (filterMode === "missing") return r.status === "missing_prediction";
    return true;
  });

  for (const r of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.case_id}</td>
      <td>${r.status}</td>
      <td>${fmtMaybe(r.entity_recall)}</td>
      <td>${fmtMaybe(r.rouge_l_f1)}</td>
    `;
    tableBody.appendChild(tr);
  }
}

async function main() {
  const payload = await loadSummary();
  setMeta(payload);

  const { hasEntityRecall, hasRougeL } = getMetricAvailability(payload);
  buildModelSelect(payload.models || []);

  if (hasEntityRecall) {
    plotMeanBars(
      payload.models || [],
      "entity_recall_mean",
      "entityRecallChart",
      { title: "Entity Recall (mean)", yLabel: "Recall" },
    );
  }

  if (hasRougeL) {
    plotMeanBars(
      payload.models || [],
      "rouge_l_f1_mean",
      "rougeChart",
      { title: "ROUGE-L F1 (mean)", yLabel: "F1" },
    );
  }

  const modelSelect = document.getElementById("modelSelect");
  const caseFilter = document.getElementById("caseFilter");

  modelSelect.addEventListener("change", () => renderPerCaseTable(payload));
  caseFilter.addEventListener("change", () => renderPerCaseTable(payload));

  // initial render
  renderPerCaseTable(payload);
}

main().catch((err) => {
  console.error(err);
  const meta = document.getElementById("meta");
  meta.textContent = String(err?.message || err);
});

