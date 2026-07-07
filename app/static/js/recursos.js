async function loadRecursosCharts() {
  const params = new URLSearchParams(window.recursosParams);
  const response = await fetch(`/api/recursos-charts?${params.toString()}`);
  const data = await response.json();

  const config = {responsive: true, displaylogo: false};
  const chartMap = {
    "chart-recursos-total": data.recursos_total,
    "chart-recursos-composicion": data.recursos_composicion,
    "chart-transferencias": data.transferencias,
    "chart-recaudacion-nacional": data.recaudacion_nacional,
    "chart-variaciones": data.variaciones
  };

  Object.entries(chartMap).forEach(([id, figJson]) => {
    const element = document.getElementById(id);
    if (!element || !figJson) return;
    const fig = JSON.parse(figJson);
    Plotly.newPlot(element, fig.data, fig.layout, config);
  });
}

document.addEventListener("DOMContentLoaded", loadRecursosCharts);