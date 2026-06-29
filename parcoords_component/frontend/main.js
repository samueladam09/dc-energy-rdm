// ── Streamlit message handler ─────────────────────────────────────────────
window.addEventListener("message", function (event) {
  if (
    event.data.type === "streamlit:render" &&
    event.data.args &&
    event.data.args.payload
  ) {
    const payload = event.data.args.payload;
    const height  = event.data.args.height || 720;
    render(payload, height);
  }
});

// ── Main render ───────────────────────────────────────────────────────────
function render(payload, height) {
  const { rows, irr_min, irr_max, lease_axis_range } = payload;

  d3.select("#chart").selectAll("*").remove();

  // ── Layout ───────────────────────────────────────────────────────────────
  const margin = { top: 130, right: 100, bottom: 50, left: 110 };
  const totalWidth  = Math.max(document.getElementById("chart").clientWidth || 1100, 900);
  const totalHeight = height;
  const W = totalWidth  - margin.left - margin.right;
  const H = totalHeight - margin.top  - margin.bottom;

  const SECTION_HEADER_Y = -90;
  const SECTION_LINE_Y   = -74;
  const AXIS_LABEL_Y     = -42;
  const AXIS_UNIT_Y      = -28;

  // ── Sections ─────────────────────────────────────────────────────────────
  const SECTIONS = {
    levers:      { label: "LEVERS",            color: "#3b82f6" },
    financial:   { label: "FINANCIAL METRICS", color: "#8b5cf6" },
    operational: { label: "OPS METRICS",       color: "#10b981" },
  };

  // ── Axes config ───────────────────────────────────────────────────────────
  const axesConfig = [
    {
      key: "Strategy", label: "Config", unit: "", type: "ordinal", section: "levers",
      values: ["Grid-Only","Grid-PV","Grid-Wind","Grid-PV-Wind","Grid-PV-BESS","Grid-Wind-BESS","Grid-PV-Wind-BESS"],
    },
    { key: "DC_Lease_Rate",         label: "Lease Rate",      unit: "£/kW/mo", type: "linear", section: "levers",      min: lease_axis_range[0], max: lease_axis_range[1] },
    { key: "Total_Investment_M",    label: "Total Investment", unit: "£M",      type: "linear", section: "financial",   min: 0,       max: 2000    },
    { key: "IRR_pct",               label: "IRR",              unit: "%",       type: "linear", section: "financial",   min: irr_min, max: irr_max },
    { key: "NPV_M",                 label: "NPV",              unit: "£M",      type: "linear", section: "financial",   min: -800,    max: 800     },
    { key: "Load_Served_by_RE_pct", label: "RE Load Served",  unit: "%",       type: "linear", section: "operational", min: 0,       max: 100     },
    { key: "RE_LCOE_per_MWh",       label: "RE LCOE",         unit: "£/MWh",   type: "linear", section: "operational", min: 0,       max: 300     },
    { key: "Lifetime_Carbon_tCO2e", label: "Lifetime Carbon", unit: "tCO₂e",   type: "linear", section: "operational", min: 0,       max: 1500000 },
  ];

  const axisKeys = axesConfig.map(a => a.key);

  // ── Scales ────────────────────────────────────────────────────────────────
  const xScale = d3.scalePoint().domain(axisKeys).range([0, W]).padding(0);

  const yScales = {};
  axesConfig.forEach(ax => {
    if (ax.type === "ordinal") {
      yScales[ax.key] = d3.scalePoint().domain(ax.values).range([H, 0]).padding(0.3);
    } else {
      yScales[ax.key] = d3.scaleLinear().domain([ax.min, ax.max]).range([H, 0]).clamp(true);
    }
  });

  const colorScale = d3.scaleSequential()
    .domain([irr_min, irr_max])
    .interpolator(d3.interpolateRgbBasis(["#d73027","#f46d43","#fee08b","#66bd63","#1a9850"]));

  // ── HiDPI canvas ──────────────────────────────────────────────────────────
  const dpr = window.devicePixelRatio || 1;
  const canvas = document.createElement("canvas");
  canvas.id = "pc-canvas";
  canvas.width  = totalWidth  * dpr;
  canvas.height = totalHeight * dpr;
  canvas.style.width    = totalWidth  + "px";
  canvas.style.height   = totalHeight + "px";
  canvas.style.position = "absolute";
  canvas.style.top      = "0";
  canvas.style.left     = "0";
  document.getElementById("chart").appendChild(canvas);

  const ctx = canvas.getContext("2d");
  ctx.scale(dpr, dpr);

  // ── SVG on top of canvas ──────────────────────────────────────────────────
  const svg = d3.select("#chart")
    .append("svg")
    .attr("id", "pc-svg")
    .attr("width",  totalWidth)
    .attr("height", totalHeight)
    .style("position", "absolute")
    .style("top",  "0")
    .style("left", "0");

  const g = svg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // ── State ─────────────────────────────────────────────────────────────────
  const brushExtents = {};
  axisKeys.forEach(k => { brushExtents[k] = null; });
  let hoveredRow = null;

  // ── Helpers ───────────────────────────────────────────────────────────────
  function getY(ax, row) {
    const val = row[ax.key];
    if (val === null || val === undefined) return null;
    return yScales[ax.key](val);
  }

  function isRowSelected(row) {
    return axisKeys.every(k => {
      const ext = brushExtents[k];
      if (!ext) return true;
      const ax = axesConfig.find(a => a.key === k);
      const y  = getY(ax, row);
      if (y === null) return false;
      return y >= Math.min(ext[0], ext[1]) && y <= Math.max(ext[0], ext[1]);
    });
  }

  // ── Draw lines ────────────────────────────────────────────────────────────
  function drawLines(highlightRow = null) {
    ctx.clearRect(0, 0, totalWidth, totalHeight);
    const anyBrush = axisKeys.some(k => brushExtents[k] !== null);

    // Pass 1 — all non-highlighted lines
    rows.forEach(row => {
      if (highlightRow && row === highlightRow) return;

      const selected = isRowSelected(row);
      let alpha;
      if (highlightRow)  alpha = selected ? 0.08 : 0.03;
      else if (anyBrush) alpha = selected ? 0.55 : 0.04;
      else               alpha = 0.15;

      const rgb = d3.color(colorScale(row["IRR_pct"]));
      ctx.beginPath();
      ctx.strokeStyle = `rgba(${rgb.r},${rgb.g},${rgb.b},${alpha})`;
      ctx.lineWidth   = 1.0;

      let started = false;
      axesConfig.forEach(ax => {
        const x    = xScale(ax.key) + margin.left;
        const y    = getY(ax, row);
        if (y === null) return;
        const yAbs = y + margin.top;
        if (!started) { ctx.moveTo(x, yAbs); started = true; }
        else            ctx.lineTo(x, yAbs);
      });
      ctx.stroke();
    });

    // Pass 2 — highlighted line drawn on top
    if (highlightRow) {
      const rgb = d3.color(colorScale(highlightRow["IRR_pct"]));
      ctx.beginPath();
      ctx.strokeStyle = `rgba(${rgb.r},${rgb.g},${rgb.b},1.0)`;
      ctx.lineWidth   = 2.5;

      let started = false;
      axesConfig.forEach(ax => {
        const x    = xScale(ax.key) + margin.left;
        const y    = getY(ax, highlightRow);
        if (y === null) return;
        const yAbs = y + margin.top;
        if (!started) { ctx.moveTo(x, yAbs); started = true; }
        else            ctx.lineTo(x, yAbs);
      });
      ctx.stroke();
    }
  }

  // ── Section headers ───────────────────────────────────────────────────────
  function drawSectionHeaders() {
    const groups = {};
    axesConfig.forEach(ax => {
      if (!groups[ax.section]) groups[ax.section] = [];
      groups[ax.section].push(ax.key);
    });
    Object.entries(groups).forEach(([section, keys]) => {
      const cfg    = SECTIONS[section];
      const xs     = keys.map(k => xScale(k));
      const xLeft  = Math.min(...xs);
      const xRight = Math.max(...xs);
      const xMid   = (xLeft + xRight) / 2;
      g.append("line")
        .attr("x1", xLeft - 18).attr("x2", xRight + 18)
        .attr("y1", SECTION_LINE_Y).attr("y2", SECTION_LINE_Y)
        .attr("stroke", cfg.color).attr("stroke-width", 2.5)
        .attr("stroke-linecap", "round");
      g.append("text")
        .attr("x", xMid).attr("y", SECTION_HEADER_Y)
        .attr("text-anchor", "middle").attr("fill", cfg.color)
        .attr("font-size", "11px").attr("font-weight", "700")
        .attr("letter-spacing", "0.07em").text(cfg.label);
    });
  }

  // ── Axes ──────────────────────────────────────────────────────────────────
  function formatTick(d, ax) {
    if (ax.key === "Lifetime_Carbon_tCO2e")
      return d >= 1000000 ? (d/1000000).toFixed(1)+"M"
           : d >= 1000    ? (d/1000).toFixed(0)+"k"
           : d;
    if (ax.key === "Total_Investment_M" || ax.key === "NPV_M")
      return d >= 1000 ? (d/1000).toFixed(1)+"k" : d;
    return d;
  }

  function drawAxes() {
    axesConfig.forEach(ax => {
      const x     = xScale(ax.key);
      const axisG = g.append("g").attr("class","axis").attr("transform",`translate(${x},0)`);
      const d3Axis = ax.type === "ordinal"
        ? d3.axisLeft(yScales[ax.key]).tickSize(4)
        : d3.axisLeft(yScales[ax.key]).ticks(6).tickSize(4).tickFormat(d => formatTick(d, ax));
      axisG.call(d3Axis);
      axisG.select(".domain").attr("stroke","#cbd5e1");
      axisG.selectAll(".tick line").attr("stroke","#cbd5e1");
      axisG.selectAll(".tick text").attr("font-size","10px").attr("fill","#64748b");
      axisG.append("text")
        .attr("y", AXIS_LABEL_Y).attr("x", 0)
        .attr("text-anchor","middle")
        .attr("fill","#1e293b")
        .attr("font-size","11.5px")
        .attr("font-weight","600")
        .text(ax.label);
      if (ax.unit) {
        axisG.append("text")
          .attr("y", AXIS_UNIT_Y).attr("x", 0)
          .attr("text-anchor","middle")
          .attr("fill","#64748b")
          .attr("font-size","10px")
          .text(ax.unit);
      }
    });
  }

  // ── Colourbar ─────────────────────────────────────────────────────────────
  function drawColourbar() {
    const cbX = W+36, cbY = 0, cbH = H*0.75, cbW = 12, steps = 120;
    for (let i = 0; i < steps; i++) {
      const t = i/steps;
      g.append("rect")
        .attr("x", cbX).attr("y", cbY + cbH*(1-t))
        .attr("width", cbW).attr("height", cbH/steps + 1)
        .attr("fill", colorScale(irr_min + t*(irr_max-irr_min)));
    }
    g.append("rect")
      .attr("x", cbX).attr("y", cbY)
      .attr("width", cbW).attr("height", cbH)
      .attr("fill","none").attr("stroke","#cbd5e1").attr("stroke-width",1);
    const cbScale = d3.scaleLinear()
      .domain([irr_min, irr_max])
      .range([cbY + cbH, cbY]);
    g.append("g")
      .attr("transform", `translate(${cbX + cbW},0)`)
      .call(d3.axisRight(cbScale).ticks(5).tickSize(4).tickFormat(d => d + "%"))
      .call(a => a.select(".domain").remove())
      .call(a => a.selectAll(".tick text")
        .attr("font-size","10px").attr("fill","#64748b"));
    g.append("text")
      .attr("x", cbX + cbW/2).attr("y", cbY - 10)
      .attr("text-anchor","middle")
      .attr("font-size","10px").attr("font-weight","700").attr("fill","#475569")
      .text("IRR");
  }

  // ── Brushes ───────────────────────────────────────────────────────────────
  function attachBrushes() {
    axesConfig.forEach(ax => {
      const brush = d3.brushY()
        .extent([[-10, 0], [10, H]])
        .on("brush end", function(event) {
          if (!event.sourceEvent) return;
          brushExtents[ax.key] = event.selection || null;
          drawLines(hoveredRow);
        });
      g.append("g")
        .attr("class", "brush")
        .attr("transform", `translate(${xScale(ax.key)},0)`)
        .call(brush);
    });
  }

  // ── Hover ─────────────────────────────────────────────────────────────────
  function attachHover() {
    const tooltip = document.getElementById("tooltip");

    svg.on("mousemove", function(event) {
      const target = event.target;

      // If hovering over a brush element, hide tooltip but don't redraw
      const isBrushElement =
        target.classList.contains("selection") ||
        target.classList.contains("handle")    ||
        target.classList.contains("overlay")   ||
        (target.parentNode && target.parentNode.classList.contains("brush"));

      if (isBrushElement) {
        tooltip.classList.add("hidden");
        return;
      }

      const [mouseX, mouseY] = d3.pointer(event, g.node());

      // Outside plot area — clear hover but only redraw if needed
      if (mouseX < -20 || mouseX > W + 20 || mouseY < 0 || mouseY > H) {
        tooltip.classList.add("hidden");
        if (hoveredRow !== null) {
          hoveredRow = null;
          drawLines(null);
        }
        return;
      }

      // Find nearest axis
      let nearestAxis = null;
      let minDist     = Infinity;
      axesConfig.forEach(ax => {
        const dist = Math.abs(mouseX - xScale(ax.key));
        if (dist < minDist) { minDist = dist; nearestAxis = ax; }
      });

      if (!nearestAxis || minDist > 80) {
        tooltip.classList.add("hidden");
        if (hoveredRow !== null) {
          hoveredRow = null;
          drawLines(null);
        }
        return;
      }

      // Find closest row on nearest axis
      let closestRow  = null;
      let closestDist = Infinity;
      const anyBrush  = axisKeys.some(k => brushExtents[k] !== null);

      rows.forEach(row => {
        if (anyBrush && !isRowSelected(row)) return;
        const y = getY(nearestAxis, row);
        if (y === null) return;
        const dist = Math.abs(y - mouseY);
        if (dist < closestDist) { closestDist = dist; closestRow = row; }
      });

      if (!closestRow || closestDist > 40) {
        tooltip.classList.add("hidden");
        if (hoveredRow !== null) {
          hoveredRow = null;
          drawLines(null);
        }
        return;
      }

      // Only redraw if hovered row actually changed
      if (closestRow !== hoveredRow) {
        hoveredRow = closestRow;
        drawLines(hoveredRow);
      }

      showTooltip(event, closestRow, tooltip);
    });

    svg.on("mouseleave", function() {
      tooltip.classList.add("hidden");
      if (hoveredRow !== null) {
        hoveredRow = null;
        drawLines(null);
      }
    });
  }

  // ── Tooltip ───────────────────────────────────────────────────────────────
  function showTooltip(event, row, tooltip) {
    const fmt = v => typeof v === "number"
      ? v.toLocaleString("en-GB", { maximumFractionDigits: 1 }) : (v ?? "—");

    tooltip.innerHTML = `
      <div class="tooltip-row">
        <span class="tooltip-label">Strategy</span>
        <span class="tooltip-value">${row.Strategy}</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">Config</span>
        <span class="tooltip-value">${row.Config_ID}</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">Lease Rate</span>
        <span class="tooltip-value">£${fmt(row.DC_Lease_Rate)} /kW/mo</span>
      </div>
      <hr class="tooltip-divider"/>
      <div class="tooltip-section">Uncertainties</div>
      <div class="tooltip-row">
        <span class="tooltip-label">DC Shell CAPEX</span>
        <span class="tooltip-value">£${fmt(row.DC_Shell_CAPEX)} /MW</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">Solar CAPEX</span>
        <span class="tooltip-value">£${fmt(row.Solar_PV_CAPEX)} /MW</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">Wind CAPEX</span>
        <span class="tooltip-value">£${fmt(row.Wind_CAPEX)} /MW</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">BESS Power CAPEX</span>
        <span class="tooltip-value">£${fmt(row.BESS_Power_CAPEX)} /MW</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">BESS Energy CAPEX</span>
        <span class="tooltip-value">£${fmt(row.BESS_Energy_CAPEX)} /MWh</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">Grid Buy Price</span>
        <span class="tooltip-value">£${fmt(row.Grid_Buy_Price)} /MWh</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">Grid Export Price</span>
        <span class="tooltip-value">£${fmt(row.Grid_Export_Price)} /MWh</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">Grid Carbon Intensity</span>
        <span class="tooltip-value">${row.Grid_Carbon_Intensity?.toFixed(3)} kgCO₂e/kWh</span>
      </div>
      <hr class="tooltip-divider"/>
      <div class="tooltip-section">Operational</div>
      <div class="tooltip-row">
        <span class="tooltip-label">RE Load Served</span>
        <span class="tooltip-value">${fmt(row.Load_Served_by_RE_pct)}%</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">RE LCOE</span>
        <span class="tooltip-value">£${fmt(row.RE_LCOE_per_MWh)} /MWh</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">Lifetime Carbon</span>
        <span class="tooltip-value">${fmt(row.Lifetime_Carbon_tCO2e)} tCO₂e</span>
      </div>
      <hr class="tooltip-divider"/>
      <div class="tooltip-section">Financial</div>
      <div class="tooltip-row">
        <span class="tooltip-label">Total Investment</span>
        <span class="tooltip-value">£${fmt(row.Total_Investment_M)}M</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">IRR</span>
        <span class="tooltip-value">${fmt(row.IRR_pct)}%</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">NPV</span>
        <span class="tooltip-value">£${fmt(row.NPV_M)}M</span>
      </div>
    `;

    tooltip.style.left = "-9999px";
    tooltip.style.top  = "-9999px";
    tooltip.classList.remove("hidden");

    requestAnimationFrame(() => {
      const TW = tooltip.offsetWidth  + 4;
      const TH = tooltip.offsetHeight + 4;
      const tx = (event.clientX + 20 + TW > window.innerWidth)
        ? event.clientX - TW - 10
        : event.clientX + 20;
      let ty = event.clientY;
      if (ty + TH > window.innerHeight) ty = window.innerHeight - TH - 8;
      if (ty < 4) ty = 4;
      tooltip.style.left = tx + "px";
      tooltip.style.top  = ty + "px";
    });
  }

  // ── Run ───────────────────────────────────────────────────────────────────
  drawLines();
  drawSectionHeaders();
  drawAxes();
  drawColourbar();
  attachBrushes();
  attachHover();

} // end render