/* charts.js - small hand-written SVG charts with hover tooltips (no external libraries). */
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const tip = () => document.getElementById("tooltip");

  function el(tag, attrs, parent) {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs || {}) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function text(parent, x, y, str, attrs) {
    const t = el("text", Object.assign({ x, y }, attrs || {}), parent);
    t.textContent = str;
    return t;
  }
  function showTip(evt, html) {
    const t = tip(); t.innerHTML = html; t.hidden = false;
    const pad = 14, w = t.offsetWidth, h = t.offsetHeight;
    let x = evt.clientX + pad, y = evt.clientY + pad;
    if (x + w > window.innerWidth - 8) x = evt.clientX - w - pad;
    if (y + h > window.innerHeight - 8) y = evt.clientY - h - pad;
    t.style.left = x + "px"; t.style.top = y + "px";
  }
  function hideTip() { tip().hidden = true; }
  function niceMax(v) {
    if (v <= 0) return 1;
    const p = Math.pow(10, Math.floor(Math.log10(v))), m = v / p;
    return (m <= 1 ? 1 : m <= 2 ? 2 : m <= 2.5 ? 2.5 : m <= 5 ? 5 : 10) * p;
  }
  function niceTicks(max, n) {
    const step = niceMax(max / n) || 1, top = Math.max(step, Math.ceil(max / step - 1e-9) * step), out = [];
    for (let v = 0; v <= top + 1e-9; v += step) out.push(+v.toFixed(6));
    return { top, ticks: out };
  }
  const width = (host) => Math.max(300, Math.round(host.getBoundingClientRect().width) || 640);
  function ticks(max, n) { const out = [], step = max / n; for (let i = 0; i <= n; i++) out.push(+(i * step).toFixed(6)); return out; }
  const fmt = (v) => (Math.abs(v) >= 100 ? Math.round(v).toLocaleString() : +v.toFixed(v < 1 && v !== 0 ? 2 : 1) + "");
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function frame(host, W, H, m) {
    host.innerHTML = "";
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img" }, host);
    return { svg, iw: W - m.l - m.r, ih: H - m.t - m.b, g: el("g", { transform: `translate(${m.l},${m.t})` }, svg) };
  }
  function yAxis(g, iw, ih, max, label, fmtT) {
    const grid = el("g", { class: "grid" }, g);
    ticks(max, 4).forEach((v) => {
      const y = ih - (v / max) * ih;
      el("line", { x1: 0, x2: iw, y1: y, y2: y }, grid);
      text(g, -8, y + 4, fmtT ? fmtT(v) : fmt(v), { "text-anchor": "end" });
    });
    if (label) text(g, -44, ih / 2, label, { transform: `rotate(-90,-44,${ih / 2})`, "text-anchor": "middle" });
  }

  /* ---------- line chart: series[{name,color,points:[{x,y,tip}]}] ---------- */
  function line(host, o) {
    const m = { l: 56, r: 16, t: 12, b: 36 }, W = width(host), H = o.height || 260;
    const { g, iw, ih } = frame(host, W, H, m);
    const all = o.series.flatMap((s) => s.points);
    if (!all.length) { host.innerHTML = '<p class="empty">No data</p>'; return; }
    const xMax = Math.max(...all.map((p) => p.x)), xMin = Math.min(...all.map((p) => p.x));
    const yMax = niceMax(Math.max(...all.map((p) => p.y)) * 1.05);
    const X = (v) => (xMax === xMin ? iw / 2 : ((v - xMin) / (xMax - xMin)) * iw), Y = (v) => ih - (v / yMax) * ih;
    yAxis(g, iw, ih, yMax, o.yLabel);
    const xt = o.xTicks || ticks(xMax - xMin, 5).map((v) => v + xMin);
    xt.forEach((v) => text(g, X(v), ih + 18, o.xFmt ? o.xFmt(v) : fmt(v), { "text-anchor": "middle" }));
    if (o.xLabel) text(g, iw / 2, ih + 33, o.xLabel, { "text-anchor": "middle" });
    o.series.forEach((s) => {
      let d = "", pen = false;
      s.points.forEach((p) => {
        if (p.y == null) { pen = false; return; }
        d += (pen ? "L" : "M") + X(p.x).toFixed(1) + "," + Y(p.y).toFixed(1); pen = true;
      });
      el("path", { d, fill: "none", stroke: s.color, "stroke-width": 2, "stroke-linejoin": "round" }, g);
      const last = [...s.points].reverse().find((p) => p.y != null);
      if (last) el("circle", { cx: X(last.x), cy: Y(last.y), r: 4, fill: s.color, stroke: "var(--surface)", "stroke-width": 2 }, g);
    });
    // hover crosshair
    const cross = el("line", { y1: 0, y2: ih, stroke: "var(--ink-3)", "stroke-dasharray": "3 3", visibility: "hidden" }, g);
    const hit = el("rect", { x: 0, y: 0, width: iw, height: ih, fill: "transparent" }, g);
    hit.addEventListener("mousemove", (e) => {
      const r = hit.getBoundingClientRect(), fx = ((e.clientX - r.left) / r.width) * (xMax - xMin) + xMin;
      let html = "";
      o.series.forEach((s) => {
        const p = s.points.reduce((a, b) => (Math.abs(b.x - fx) < Math.abs(a.x - fx) ? b : a));
        cross.setAttribute("x1", X(p.x)); cross.setAttribute("x2", X(p.x));
        html += `<div><b style="color:${s.color}">●</b> ${esc(s.name)}: ${p.tip || fmt(p.y)}</div>`;
      });
      cross.setAttribute("visibility", "visible"); showTip(e, html);
    });
    hit.addEventListener("mouseleave", () => { cross.setAttribute("visibility", "hidden"); hideTip(); });
  }

  /* ---------- Kaplan-Meier step chart: series[{name,color,curve:[[t,s,n]]}] ---------- */
  function km(host, o) {
    const m = { l: 56, r: 18, t: 12, b: 38 }, W = width(host), H = o.height || 280;
    const { g, iw, ih } = frame(host, W, H, m);
    const series = o.series.filter((s) => s.curve && s.curve.length);
    if (!series.length) { host.innerHTML = '<p class="empty">No issues introduced inside the observation window for this selection.</p>'; return; }
    const nt = niceTicks(Math.max(...series.map((s) => s.curve[s.curve.length - 1][0]), 1), 5), xMax = nt.top;
    const X = (v) => (v / xMax) * iw, Y = (v) => ih - v * ih;
    yAxis(g, iw, ih, 1, "Share still present", (v) => Math.round(v * 100) + "%");
    nt.ticks.forEach((v) => text(g, X(v), ih + 18, fmt(v), { "text-anchor": "middle" }));
    text(g, iw / 2, ih + 34, o.xLabel || "", { "text-anchor": "middle" });
    el("line", { x1: 0, x2: iw, y1: Y(0.5), y2: Y(0.5), stroke: "var(--ink-3)", "stroke-dasharray": "4 4", opacity: 0.6 }, g);
    text(g, iw - 2, Y(0.5) - 5, "median", { "text-anchor": "end", opacity: 0.8 });
    series.forEach((s) => {
      let d = `M0,${Y(1)}`; let prevS = 1;
      s.curve.forEach(([t, sv]) => { d += `H${X(t).toFixed(1)}V${Y(sv).toFixed(1)}`; prevS = sv; });
      el("path", { d, fill: "none", stroke: s.color, "stroke-width": 2 }, g);
    });
    const cross = el("line", { y1: 0, y2: ih, stroke: "var(--ink-3)", "stroke-dasharray": "3 3", visibility: "hidden" }, g);
    const hit = el("rect", { x: 0, y: 0, width: iw, height: ih, fill: "transparent" }, g);
    hit.addEventListener("mousemove", (e) => {
      const r = hit.getBoundingClientRect(), ft = ((e.clientX - r.left) / r.width) * xMax;
      cross.setAttribute("x1", X(ft)); cross.setAttribute("x2", X(ft)); cross.setAttribute("visibility", "visible");
      let html = `<div class="mono">${o.unitLabel || "t"} = ${fmt(ft)}</div>`;
      series.forEach((s) => {
        let sv = 1, n = s.curve[0][2];
        for (const [t, v, at] of s.curve) { if (t <= ft) { sv = v; n = at; } else break; }
        html += `<div><b style="color:${s.color}">●</b> ${esc(s.name)}: ${Math.round(sv * 100)}% still present</div>`;
      });
      showTip(e, html);
    });
    hit.addEventListener("mouseleave", () => { cross.setAttribute("visibility", "hidden"); hideTip(); });
  }

  /* ---------- grouped bars: groups[labels], series[{name,color,values[]}] ---------- */
  function bars(host, o) {
    const m = { l: 56, r: 12, t: 16, b: 34 }, W = width(host), H = o.height || 240;
    const { g, iw, ih } = frame(host, W, H, m);
    const vals = o.series.flatMap((s) => s.values).filter((v) => v != null);
    const yMax = niceMax(Math.max(...vals, 0.001) * 1.1);
    yAxis(g, iw, ih, yMax, o.yLabel);
    const gw = iw / o.groups.length, bw = Math.min(46, (gw - 24) / o.series.length);
    o.groups.forEach((lab, gi) => {
      const cx = gi * gw + gw / 2;
      text(g, cx, ih + 20, lab, { "text-anchor": "middle" });
      o.series.forEach((s, si) => {
        const v = s.values[gi]; if (v == null) return;
        const x = cx - (o.series.length * (bw + 2)) / 2 + si * (bw + 2), h = (v / yMax) * ih;
        const r = Math.min(4, h / 2);
        const path = `M${x},${ih}V${ih - h + r}Q${x},${ih - h} ${x + r},${ih - h}H${x + bw - r}Q${x + bw},${ih - h} ${x + bw},${ih - h + r}V${ih}Z`;
        const b = el("path", { d: path, fill: s.color }, g);
        text(g, x + bw / 2, ih - h - 5, fmt(v), { "text-anchor": "middle", "font-size": 10 });
        b.addEventListener("mousemove", (e) => showTip(e, `<b>${esc(s.name)}</b> · ${esc(lab)}<br>${fmt(v)} ${o.unit || ""}`));
        b.addEventListener("mouseleave", hideTip);
      });
    });
  }

  /* ---------- dot strip: one row per group, one dot per project ---------- */
  function dots(host, o) {
    const m = { l: 60, r: 20, t: 10, b: 38 }, W = width(host), H = 48 + o.rows.length * 50;
    const { g, iw, ih } = frame(host, W, H, m);
    const all = o.rows.flatMap((r) => r.points.map((p) => p.v)).filter((v) => v != null);
    const nt = niceTicks(Math.max(...all, 1), 4), xMax = nt.top, X = (v) => (v / xMax) * iw;
    const grid = el("g", { class: "grid" }, g);
    nt.ticks.forEach((v) => { el("line", { x1: X(v), x2: X(v), y1: 0, y2: ih }, grid); text(g, X(v), ih + 18, fmt(v), { "text-anchor": "middle" }); });
    text(g, iw / 2, ih + 33, o.xLabel || "", { "text-anchor": "middle" });
    const rh = ih / o.rows.length;
    o.rows.forEach((r, ri) => {
      const cy = ri * rh + rh / 2;
      text(g, -10, cy + 4, r.label, { "text-anchor": "end", class: "title" });
      const vs = r.points.map((p) => p.v).filter((v) => v != null).sort((a, b) => a - b);
      if (vs.length) {
        const med = vs.length % 2 ? vs[(vs.length - 1) / 2] : (vs[vs.length / 2 - 1] + vs[vs.length / 2]) / 2;
        el("line", { x1: X(med), x2: X(med), y1: cy - 14, y2: cy + 14, stroke: r.color, "stroke-width": 3, "stroke-linecap": "round" }, g);
      }
      r.points.forEach((p, i) => {
        if (p.v == null) return;
        const c = el("circle", { cx: X(p.v), cy: cy + ((i % 3) - 1) * 6, r: 6, fill: r.color, "fill-opacity": 0.85, stroke: "var(--surface)", "stroke-width": 2 }, g);
        c.addEventListener("mousemove", (e) => showTip(e, `<b>${esc(p.name)}</b><br>${fmt(p.v)} ${o.unit || ""}`));
        c.addEventListener("mouseleave", hideTip);
      });
    });
  }

  /* ---------- 100% stacked horizontal bars ---------- */
  function stack(host, o) {
    const m = { l: 80, r: 12, t: 6, b: 8 }, W = width(host), H = 20 + o.rows.length * 40;
    const { g, iw } = frame(host, W, H, m);
    o.rows.forEach((r, ri) => {
      const y = ri * 40 + 4, tot = r.parts.reduce((a, p) => a + p.value, 0) || 1;
      text(g, -10, y + 17, r.label, { "text-anchor": "end", class: "title" });
      let x = 0;
      r.parts.forEach((p) => {
        const w = (p.value / tot) * iw; if (w <= 0) return;
        const rect = el("rect", { x: x + 1, y, width: Math.max(0, w - 2), height: 26, rx: 4, fill: p.color }, g);
        if (w > 60) text(g, x + 8, y + 17, Math.round((p.value / tot) * 100) + "%", { fill: "#fff", style: "fill:#fff;font-weight:600" });
        rect.addEventListener("mousemove", (e) => showTip(e, `<b>${esc(p.name)}</b><br>${p.value.toLocaleString()} (${Math.round((p.value / tot) * 100)}%)`));
        rect.addEventListener("mouseleave", hideTip);
        x += w;
      });
    });
  }

  window.Charts = { line, km, bars, dots, stack, esc, fmt };
})();
