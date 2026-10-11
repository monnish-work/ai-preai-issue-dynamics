/* app.js - Issue Lifelines front end (vanilla JS, hash routing). */
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = Charts.esc, fmt = Charts.fmt;
  const main = $("#main");
  const CAT = { maintainability: "m", reliability: "r", security: "s" };
  const CATS = ["maintainability", "reliability", "security"];
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const col = { ai: () => css("--ai"), human: () => css("--human") };
  const MECH = { code_changed: "Code changed", file_deleted: "File deleted", code_still_present: "Code still present (context changed)" };
  const S = { me: null, meta: null, phase: "phaseC", cmp: {}, iss: { page: 1 }, unit: "commits", cat: "all" };

  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
  };
  async function api(path, opts) {
    const r = await fetch(path, opts ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(opts) } : undefined);
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.error || `Request failed (${r.status})`);
    return j;
  }
  const short = (repo) => repo.split("/")[1];
  const gh = (repo) => `https://github.com/${repo}`;
  const date = (d) => (d || "").slice(0, 10);
  const pct = (v) => (v == null ? "–" : Math.round(v * 100) + "%");
  const pvs = (p) => (p == null || p === "" ? "p = –" : p < 0.001 ? "p < 0.001" : "p = " + (+p).toFixed(3));
  const pval = (p) => (p == null ? "–" : p < 0.001 ? "< 0.001" : p.toFixed(3));
  const chip = (grp) => grp === "AI" ? '<span class="chip ai"><span class="dot"></span>AI-assisted</span>' : '<span class="chip human"><span class="dot"></span>Pre-AI</span>';
  const catTag = (c) => `<span class="cat-tag cat-${CAT[c]}">${c}</span>`;
  const seg = (name, opts, cur) => `<div class="seg" role="group" data-seg="${name}">${opts.map(([v, l]) => `<button type="button" data-v="${v}" aria-pressed="${v === cur}">${l}</button>`).join("")}</div>`;
  const phaseObj = () => S.meta.phases.find((p) => p.id === S.phase) || S.meta.phases[0];

  /* ================= theme ================= */
  const savedTheme = store.get("theme");
  if (savedTheme) document.documentElement.setAttribute("data-theme", savedTheme);
  $("#theme-toggle").addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme") || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next); store.set("theme", next); route();
  });

  /* ================= welcome art ================= */
  function drawArt() {
    const svg = $("#lifeline-art"); const n = 16, x0 = 30, x1 = 490, step = (x1 - x0) / (n - 1);
    let h = `<line x1="${x0}" y1="70" x2="${x1}" y2="70" stroke="var(--line)" stroke-width="2"/>`;
    for (let i = 0; i < n; i++) {
      const x = x0 + i * step;
      h += `<circle cx="${x}" cy="70" r="6" fill="var(--surface)" stroke="var(--ink-3)" stroke-width="2"/>`;
      if (i % 3 === 0) h += `<text x="${x}" y="50" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="10" fill="var(--ink-3)">c${String(i + 1).padStart(2, "0")}</text>`;
    }
    const rows = [
      { y: 125, a: 4, b: 12, c: "var(--ai)", l: "AI-assisted · complex function" },
      { y: 170, a: 2, b: 15, c: "var(--ai)", l: "AI-assisted · unused variable", open: true },
      { y: 215, a: 6, b: 9, c: "var(--human)", l: "Pre-AI · duplicated literal" },
      { y: 260, a: 1, b: 13, c: "var(--human)", l: "Pre-AI · insecure SHA-1", sec: true },
    ];
    rows.forEach((r, k) => {
      const xa = x0 + r.a * step, xb = x0 + r.b * step;
      h += `<line x1="${x0}" y1="${r.y}" x2="${x1}" y2="${r.y}" stroke="var(--surface-2)" stroke-width="10" stroke-linecap="round"/>`;
      h += `<line class="art-life" style="animation-delay:${0.3 + k * 0.25}s" x1="${xa}" y1="${r.y}" x2="${xb}" y2="${r.y}" stroke="${r.c}" stroke-width="10" stroke-linecap="round"/>`;
      h += `<circle cx="${xa}" cy="${r.y}" r="7" fill="var(--surface)" stroke="${r.c}" stroke-width="3"/>`;
      h += r.open ? `<path d="M${xb + 8},${r.y - 6}l8,6l-8,6" fill="none" stroke="${r.c}" stroke-width="2.5"/>` : `<line x1="${xb + 9}" y1="${r.y - 8}" x2="${xb + 9}" y2="${r.y + 8}" stroke="var(--ink)" stroke-width="2.5"/>`;
      h += `<text x="${x0}" y="${r.y - 12}" font-size="11" fill="var(--ink-2)" font-family="IBM Plex Sans, sans-serif">${r.l}${r.open ? " · still open" : ""}</text>`;
    });
    svg.innerHTML = h;
  }

  /* ================= auth ================= */
  async function boot() {
    S.me = await api("/api/me");
    if (!S.me.name) { showWelcome(); return; }
    await enter();
  }
  function showWelcome() {
    $("#shell").hidden = true; $("#welcome").hidden = false; drawArt();
    const last = store.get("lastName"); if (last) $("#login-name").value = last;
    $("#login-name").focus();
  }
  $("#login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = $("#login-name").value.trim();
    $("#login-error").textContent = "";
    try { S.me = await api("/api/login", { name }); store.set("lastName", name); await enter(); }
    catch (err) { $("#login-error").textContent = err.message; }
  });
  $("#logout").addEventListener("click", async () => { await api("/api/logout", {}); S.me = { name: null }; showWelcome(); });

  async function enter() {
    $("#welcome").hidden = true; $("#shell").hidden = false;
    $("#user-name").textContent = S.me.name; $("#user-avatar").textContent = S.me.name.slice(0, 1).toUpperCase();
    if (!S.meta) S.meta = await api("/api/meta");
    const saved = store.get("phase");
    if (saved && S.meta.phases.some((p) => p.id === saved)) S.phase = saved;
    else if (!S.meta.phases.some((p) => p.id === S.phase)) S.phase = S.meta.phases[0].id;
    $("#phase-select").innerHTML = S.meta.phases.map((p) => `<option value="${p.id}" ${p.id === S.phase ? "selected" : ""}>${esc(p.label)}</option>`).join("");
    if (!location.hash) location.hash = "#about"; else route();
  }
  $("#phase-select").addEventListener("change", (e) => { S.phase = e.target.value; store.set("phase", S.phase); S.cmp = {}; S.iss = { page: 1 }; route(); });

  /* ================= router ================= */
  const views = { about, results, compare, issues, validation, dataset, limits };
  function route() {
    if ($("#shell").hidden) return;
    const v = (location.hash || "#about").slice(1);
    const fn = views[v] || about;
    $$(".nav a").forEach((a) => a.classList.toggle("active", a.dataset.view === (views[v] ? v : "about")));
    main.innerHTML = '<p class="loading">Loading…</p>';
    fn().catch((err) => { main.innerHTML = `<div class="panel empty">Could not load this page: ${esc(err.message)}</div>`; });
    main.focus({ preventScroll: true }); window.scrollTo(0, 0);
  }
  window.addEventListener("hashchange", route);
  function onSeg(root, name, cb) {
    const s = $(`[data-seg="${name}"]`, root); if (!s) return;
    s.addEventListener("click", (e) => {
      const b = e.target.closest("button"); if (!b) return;
      $$("button", s).forEach((x) => x.setAttribute("aria-pressed", x === b)); cb(b.dataset.v);
    });
  }

  /* ================= ABOUT ================= */
  async function about() {
    const ph = S.meta.phases, main5 = ph.find((p) => p.id === "phaseC");
    const nIss = null;
    main.innerHTML = `
    <header class="page-head">
      <p class="eyebrow">Individual Study · Software Engineering · 2026</p>
      <h1>Issue Dynamics in AI-Assisted vs. Pre-AI Software</h1>
      <p>A longitudinal study of Python repositories using Git history and free static-analysis tools. It asks how many quality issues projects have, and also when each issue is introduced, how long it survives, and how it is removed.</p>
      <p class="small muted">Student: <b>Monnish Sayi Reddy Peta</b> · Signed in as <b>${esc(S.me.name)}</b></p>
    </header>

    <section class="section">
      <div class="section-head"><h2>Research questions</h2></div>
      <div class="grid g3">
        <div class="panel rq"><span class="tag">RQ1 · Introduction</span><b>Are maintainability, reliability and security issues introduced at different rates in AI-assisted repositories than in matched pre-AI repositories?</b></div>
        <div class="panel rq"><span class="tag">RQ2 · Persistence</span><b>Do issues survive for different lengths of time in AI-assisted versus pre-AI repositories?</b></div>
        <div class="panel rq"><span class="tag">RQ3 · Remediation</span><b>Are security issues removed faster than maintainability and reliability issues, and does that differ between the two groups?</b></div>
      </div>
    </section>

    <section class="section">
      <div class="section-head"><h2>How the study works</h2><p>Every step is scripted, so the whole study can be re-run from the raw data.</p></div>
      <ol class="steps">
        <li><b>Find candidates</b><span>GitHub code search for explicit attribution comments such as “generated by ChatGPT” (AI), and repositories whose last commit is before 2022 (pre-AI).</span></li>
        <li><b>Validate and match</b><span>Each AI declaration is checked by hand; a repository needs ≥ 2 % declared files. Each AI repository is paired with a pre-AI one of similar size and popularity.</span></li>
        <li><b>Sample commits</b><span>30 non-merge commits per repository, chosen by the same rule in both groups (pilot: the last 30; main study: evenly spaced over the whole history).</span></li>
        <li><b>Scan every commit</b><span>SonarQube Community Build (maintainability, reliability) and Semgrep CE (security) with frozen versions and rules. Raw output is archived.</span></li>
        <li><b>Track issues</b><span>A tracker links each warning across consecutive commits using rule, file (with rename detection), flagged code and a diff-based line mapping.</span></li>
        <li><b>Measure and compare</b><span>Introduction and removal rates per KLOC, issue lifetimes with Kaplan–Meier curves, log-rank tests, and repository-level Mann–Whitney tests.</span></li>
      </ol>
    </section>

    <section class="section grid g2">
      <div class="panel">
        <h3>Data sets in this app</h3>
        <div class="table-wrap" style="margin-top:12px"><table><thead><tr><th>Data set</th><th class="n">Projects</th><th>Sampling</th></tr></thead><tbody>
        ${ph.map((p) => `<tr><td>${esc(p.label)}</td><td class="n">${p.projects.length}</td><td class="small">${esc(p.sampling)}</td></tr>`).join("")}
        </tbody></table></div>
        <p class="small muted" style="margin-top:10px">Switch between them with <b>Data set</b> in the sidebar.</p>
      </div>
      <div class="panel">
        <h3>Tools and exact versions</h3>
        <div class="table-wrap" style="margin-top:12px"><table><tbody>
        ${S.meta.versions.filter((v) => v.includes(":")).slice(1).map((v) => { const i = v.indexOf(":"); return `<tr><td>${esc(v.slice(0, i))}</td><td class="mono">${esc(v.slice(i + 1).trim())}</td></tr>`; }).join("")}
        </tbody></table></div>
      </div>
    </section>

    <section class="section">
      <div class="panel">
        <h3>Terms used in this app</h3>
        <dl class="gloss" style="margin-top:12px">
          <dt>Issue</dt><dd>One static-analysis warning (a rule firing on a piece of code), followed across commits.</dd>
          <dt>Introduced / removed</dt><dd>The analysed commit where the issue first appears / the first analysed commit where it is gone.</dd>
          <dt>Lifetime</dt><dd>Analysed commits (or days) from introduction to removal.</dd>
          <dt>Censored</dt><dd>Still present at the last analysed commit, so its full lifetime is unknown. Survival curves handle this correctly.</dd>
          <dt>Baseline issue</dt><dd>Already present at the first analysed commit; its introduction time is unknown, so it is excluded from introduction rates and survival curves.</dd>
          <dt>KLOC</dt><dd>1,000 non-blank lines of Python (generated folders such as <code>build/</code> and <code>vendor/</code> excluded).</dd>
        </dl>
      </div>
    </section>`;
  }

  /* ================= RESULTS ================= */
  async function results() {
    const r = await api(`/api/results?phase=${S.phase}&unit=${S.unit}`);
    const ph = phaseObj();
    const all = r.rates.filter((x) => x.category === "all");
    const tot = (k) => all.reduce((a, x) => a + (+x[k] || 0), 0);
    const commits = ph.projects.reduce((a, p) => a + p.snapshots, 0);
    const isPilot = S.phase === "pilot";
    const med = (g, c) => r.km[g][c].median;
    const unitLabel = S.unit === "commits" ? "analysed commits" : "days";
    const rt = (m) => r.repo_tests.find((t) => t.measure === m);
    const t1 = rt("intro_per_kloc"), t2 = rt("removed_per_kloc"), tk = rt("km_median_snapshots");
    const mech = (g) => { const m = r.mechanisms[g] || {}; const t = Object.values(m).reduce((a, b) => a + b, 0) || 1; return { m, t }; };
    const fdAI = mech("AI"), fdPre = mech("PreAI");

    main.innerHTML = `
    <header class="page-head">
      <p class="eyebrow">${esc(ph.label)}</p>
      <h1>What the data says</h1>
      <p>${isPilot ? "The pilot compares one AI-assisted and one pre-AI repository. It was built to test the tracking method, so treat these numbers as a check of the method rather than as findings." : "Five AI-assisted repositories compared with five matched pre-AI repositories, 30 analysed commits each, spread over each project's whole history."}</p>
    </header>
    <div class="grid g4">
      <div class="panel stat"><span class="v">${ph.projects.length}</span><span class="k">repositories (${ph.projects.filter((p) => p.grp === "AI").length} AI · ${ph.projects.filter((p) => p.grp !== "AI").length} pre-AI)</span></div>
      <div class="panel stat"><span class="v">${commits}</span><span class="k">commits scanned with both tools</span></div>
      <div class="panel stat"><span class="v">${(tot("baseline_issues") + tot("introduced")).toLocaleString()}</span><span class="k">issues tracked across commits</span></div>
      <div class="panel stat"><span class="v">${tot("removed").toLocaleString()}</span><span class="k">removals observed</span></div>
    </div>

    <section class="section">
      <div class="section-head"><div><p class="eyebrow">RQ1 · Introduction</p><h2>How fast do new issues appear?</h2></div>${seg("rq1cat", [["all", "All"], ...CATS.map((c) => [c, c[0].toUpperCase() + c.slice(1)])], S.cat)}</div>
      <div class="grid g2">
        <div class="panel"><h3>Introduced per KLOC</h3><p class="small muted">Each dot is one repository; the bar marks the group median.</p><div class="chart" id="rq1a"></div></div>
        <div class="panel"><h3>Removed per KLOC</h3><p class="small muted">Removals counted over the same window.</p><div class="chart" id="rq1b"></div></div>
      </div>
      ${t1 ? `<p class="takeaway"><strong>Repository-level test:</strong> median introductions per KLOC are ${fmt(t1.AI_median)} (AI) vs ${fmt(t1.PreAI_median)} (pre-AI), Mann–Whitney ${pvs(t1.p_value)}, Cliff's δ = ${t1.cliffs_delta}. Removals: ${fmt(t2.AI_median)} vs ${fmt(t2.PreAI_median)}, ${pvs(t2.p_value)}. With five repositories per group, differences of this size are not statistically distinguishable from chance.</p>` : `<p class="takeaway">A repository-level test needs at least two repositories per group; see the main study.</p>`}
    </section>

    <section class="section">
      <div class="section-head"><div><p class="eyebrow">RQ2 · Persistence</p><h2>How long do issues survive?</h2></div>
        <div class="toolbar">${seg("rq2cat", [["all", "All"], ...CATS.map((c) => [c, c[0].toUpperCase() + c.slice(1)])], S.cat)}${seg("unit", [["commits", "Commits"], ["days", "Days"]], S.unit)}</div></div>
      <div class="panel"><div class="legend"><span><i style="background:var(--ai)"></i>AI-assisted</span><span><i style="background:var(--human)"></i>Pre-AI</span></div><div class="chart" id="rq2"></div></div>
      <div class="table-wrap"><table><thead><tr><th>Category</th><th class="n">AI issues</th><th class="n">AI median</th><th class="n">Pre-AI issues</th><th class="n">Pre-AI median</th><th class="n">Log-rank χ²</th><th class="n">p (issue level)</th></tr></thead><tbody>
        ${["all", ...CATS].map((c) => `<tr><td>${c === "all" ? "All" : catTag(c)}</td><td class="n">${r.km.AI[c].n}</td><td class="n">${med("AI", c) == null ? "not reached" : fmt(med("AI", c))}</td><td class="n">${r.km.PreAI[c].n}</td><td class="n">${med("PreAI", c) == null ? "not reached" : fmt(med("PreAI", c))}</td><td class="n">${r.tests[c] ? r.tests[c].chi2 ?? "–" : "–"}</td><td class="n">${r.tests[c] ? pval(r.tests[c].p) : "–"}</td></tr>`).join("")}
      </tbody></table></div>
      <p class="takeaway"><strong>Reading this:</strong> medians are in ${unitLabel}. Pooled over all issues, AI-assisted issues ${(med("AI", "all") ?? 0) > (med("PreAI", "all") ?? 0) ? "tend to survive longer" : "do not survive longer"} than pre-AI issues (log-rank ${pvs(r.tests.all && r.tests.all.p)}). Issues in one repository are not independent, so this p-value overstates certainty.${tk ? ` At repository level the median lifetime is ${fmt(tk.AI_median)} vs ${fmt(tk.PreAI_median)} commits (Mann–Whitney ${pvs(tk.p_value)}).` : ""}</p>
    </section>

    <section class="section">
      <div class="section-head"><div><p class="eyebrow">RQ3 · Remediation</p><h2>Are security issues removed faster?</h2></div></div>
      ${r.rq3.length ? `<div class="table-wrap"><table><thead><tr><th>Group</th><th>Unit</th><th class="n">Security issues</th><th class="n">Other issues</th><th class="n">Security removed</th><th class="n">Other removed</th><th class="n">p (log-rank)</th></tr></thead><tbody>
        ${r.rq3.map((x) => `<tr><td>${chip(x.group)}</td><td>${x.unit}</td><td class="n">${x.n_security}</td><td class="n">${x.n_other}</td><td class="n">${pct(x.security_removed_share)}</td><td class="n">${pct(x.other_removed_share)}</td><td class="n">${pval(x.p_value === "" ? null : x.p_value)}</td></tr>`).join("")}
      </tbody></table></div>
      <p class="takeaway">Security issues are rare (${r.km.AI.security.n} AI, ${r.km.PreAI.security.n} pre-AI introduced), so the difference between security and other issues is not measurable with this sample in either group.</p>` : '<p class="panel empty">Not enough security issues in this data set.</p>'}
    </section>

    <section class="section">
      <div class="section-head"><div><p class="eyebrow">How issues disappear</p><h2>A disappearing warning is not always a fix</h2></div></div>
      <div class="panel"><div class="legend"><span><i style="background:var(--good)"></i>Code changed</span><span><i style="background:var(--ink-3)"></i>File deleted</span><span><i style="background:var(--warn)"></i>Code still present</span></div><div class="chart" id="mech"></div></div>
      <p class="takeaway">${Math.round(((fdAI.m.file_deleted || 0) / fdAI.t) * 100)}% of AI removals and ${Math.round(((fdPre.m.file_deleted || 0) / fdPre.t) * 100)}% of pre-AI removals happened because the whole file was deleted, not because the flagged code was edited.</p>
    </section>`;

    const drawRQ1 = () => {
      const rows = r.rates.filter((x) => x.category === S.cat);
      const mk = (key) => [["AI", "AI", col.ai()], ["PreAI", "Pre-AI", col.human()]].map(([g, l, c]) => ({ label: l, color: c, points: rows.filter((x) => x.group === g).map((x) => ({ name: short(x.repo), v: x[key] === "" ? null : +x[key] })) }));
      Charts.dots($("#rq1a"), { rows: mk("intro_per_kloc"), xLabel: "issues introduced per 1,000 lines", unit: "per KLOC" });
      Charts.dots($("#rq1b"), { rows: mk("removed_per_kloc"), xLabel: "issues removed per 1,000 lines", unit: "per KLOC" });
    };
    const drawRQ2 = () => Charts.km($("#rq2"), { series: [{ name: "AI-assisted", color: col.ai(), curve: r.km.AI[S.cat].curve }, { name: "Pre-AI", color: col.human(), curve: r.km.PreAI[S.cat].curve }], xLabel: S.unit === "commits" ? "analysed commits since introduction" : "days since introduction", unitLabel: S.unit });
    drawRQ1(); drawRQ2();
    Charts.stack($("#mech"), { rows: ["AI", "PreAI"].map((g) => ({ label: g === "AI" ? "AI" : "Pre-AI", parts: [["code_changed", css("--good")], ["file_deleted", css("--ink-3")], ["code_still_present", css("--warn")]].map(([k, c]) => ({ name: MECH[k], value: (r.mechanisms[g] || {})[k] || 0, color: c })) })) });
    onSeg(main, "rq1cat", (v) => { S.cat = v; drawRQ1(); });
    onSeg(main, "rq2cat", (v) => { S.cat = v; drawRQ2(); });
    onSeg(main, "unit", (v) => { S.unit = v; results(); });
  }

  /* ================= COMPARE ================= */
  async function compare() {
    const ph = phaseObj();
    const ais = ph.projects.filter((p) => p.grp === "AI"), hus = ph.projects.filter((p) => p.grp !== "AI");
    if (!S.cmp.ai || !ais.some((p) => p.repo === S.cmp.ai)) S.cmp.ai = ais[0].repo;
    if (!S.cmp.human || !hus.some((p) => p.repo === S.cmp.human)) S.cmp.human = (hus.find((h) => h.match_id === ais[0].match_id) || hus[0]).repo;
    const opt = (list, cur) => list.map((p) => `<option value="${p.repo}" ${p.repo === cur ? "selected" : ""}>${esc(short(p.repo))}${p.match_id && p.match_id !== "P1" ? " · pair " + p.match_id : ""}</option>`).join("");
    main.innerHTML = `
    <header class="page-head"><p class="eyebrow">${esc(ph.label)}</p><h1>Compare two projects</h1>
      <p>Pick one AI-assisted project and one pre-AI project. The matched pair is suggested, but any combination works.</p></header>
    <div class="panel toolbar">
      <div class="field"><label for="pick-ai">AI-assisted project</label><select id="pick-ai">${opt(ais, S.cmp.ai)}</select></div>
      <div class="field"><label for="pick-hu">Pre-AI project</label><select id="pick-hu">${opt(hus, S.cmp.human)}</select></div>
      <button class="btn" id="use-pair" type="button">Use matched pair</button>
    </div>
    <div id="cmp-body"><p class="loading">Loading…</p></div>`;
    $("#pick-ai").addEventListener("change", (e) => { S.cmp.ai = e.target.value; drawCompare(); });
    $("#pick-hu").addEventListener("change", (e) => { S.cmp.human = e.target.value; drawCompare(); });
    $("#use-pair").addEventListener("click", () => {
      const a = ais.find((p) => p.repo === S.cmp.ai), h = hus.find((p) => p.match_id === a.match_id);
      if (h) { S.cmp.human = h.repo; $("#pick-hu").value = h.repo; drawCompare(); }
    });
    await drawCompare();
  }

  async function drawCompare() {
    const body = $("#cmp-body"); if (!body) return;
    const d = await api(`/api/compare?phase=${S.phase}&ai=${encodeURIComponent(S.cmp.ai)}&human=${encodeURIComponent(S.cmp.human)}&unit=${S.unit}`);
    const card = (p, k) => `
      <div class="panel proj ${k}">
        <div style="display:flex;justify-content:space-between;gap:8px;align-items:start;flex-wrap:wrap">${chip(p.grp)}<a class="small" href="${gh(p.repo)}" target="_blank" rel="noopener">GitHub ↗</a></div>
        <h3 style="margin-top:8px">${esc(p.repo)}</h3><p class="desc">${esc(p.description)}</p>
        <div class="kv">
          <div><span class="k">Python lines</span><span class="v">${p.loc_first.toLocaleString()} → ${p.loc_last.toLocaleString()}</span></div>
          <div><span class="k">Period</span><span class="v small">${p.first_date} → ${p.last_date}</span></div>
          <div><span class="k">Stars</span><span class="v">${p.stars ?? "–"}</span></div>
          <div><span class="k">Introduced</span><span class="v">${p.rates.all.introduced}</span></div>
          <div><span class="k">Removed</span><span class="v">${p.rates.all.removed}</span></div>
          <div><span class="k">Open at end</span><span class="v">${p.rates.all.open_end}</span></div>
        </div>
        <p class="evidence"><b>${p.grp === "AI" ? "AI evidence" : "Pre-AI basis"}:</b> ${esc(p.evidence)}</p>
      </div>`;
    body.innerHTML = `
    <div class="vs" style="margin-top:16px">${card(d.ai, "ai")}<div class="vs-mid">vs</div>${card(d.human, "human")}</div>

    <section class="section">
      <div class="section-head"><h2>Open issues over time</h2>${seg("dens", [["kloc", "Per KLOC"], ["abs", "Count"]], S.cmp.dens || "kloc")}</div>
      <div class="panel"><div class="legend"><span><i style="background:var(--ai)"></i>${esc(short(d.ai.repo))}</span><span><i style="background:var(--human)"></i>${esc(short(d.human.repo))}</span></div><div class="chart" id="c-dens"></div>
      <p class="small muted">x-axis: analysed commit 1–30. Commits where SonarQube failed are left as gaps.</p></div>
    </section>

    <section class="section">
      <div class="section-head"><h2>Rates by category</h2><p>Introductions and removals per 1,000 lines of Python.</p></div>
      <div class="grid g2"><div class="panel"><h3>Introduced per KLOC</h3><div class="chart" id="c-in"></div></div><div class="panel"><h3>Removed per KLOC</h3><div class="chart" id="c-out"></div></div></div>
    </section>

    <section class="section">
      <div class="section-head"><h2>Issue survival</h2><div class="toolbar">${seg("ccat", [["all", "All"], ...CATS.map((c) => [c, c[0].toUpperCase() + c.slice(1)])], S.cat)}${seg("cunit", [["commits", "Commits"], ["days", "Days"]], S.unit)}</div></div>
      <div class="panel"><div class="legend"><span><i style="background:var(--ai)"></i>${esc(short(d.ai.repo))}</span><span><i style="background:var(--human)"></i>${esc(short(d.human.repo))}</span></div><div class="chart" id="c-km"></div><p class="small muted" id="c-km-note"></p></div>
    </section>

    <section class="section grid g2">
      <div class="panel"><h3>How issues were removed</h3><div class="chart" id="c-mech"></div></div>
      <div class="panel"><h3>At a glance</h3><div class="table-wrap" style="margin-top:10px"><table><thead><tr><th></th><th class="n">${esc(short(d.ai.repo))}</th><th class="n">${esc(short(d.human.repo))}</th></tr></thead><tbody>
        ${[["Baseline issues", "baseline"], ["Introduced", "introduced"], ["Removed", "removed"], ["Introduced / KLOC", "intro_per_kloc"], ["Removed / KLOC", "removed_per_kloc"], ["Share removed", "remediation_share"]].map(([l, k]) => `<tr><td>${l}</td><td class="n">${k === "remediation_share" ? pct(d.ai.rates.all[k]) : d.ai.rates.all[k] ?? "–"}</td><td class="n">${k === "remediation_share" ? pct(d.human.rates.all[k]) : d.human.rates.all[k] ?? "–"}</td></tr>`).join("")}
      </tbody></table></div></div>
    </section>

    <section class="section grid g2">
      ${[d.ai, d.human].map((p) => `<div class="panel"><h3>Most frequent rules · ${esc(short(p.repo))}</h3><div class="table-wrap" style="margin-top:10px"><table><thead><tr><th>Rule</th><th class="n">Issues</th></tr></thead><tbody>
        ${p.top_rules.map((t) => `<tr><td><span class="mono">${esc(t.rule.split(".").pop())}</span> ${catTag(t.category)}<div class="small muted">${esc(t.example)}</div></td><td class="n">${t.n}</td></tr>`).join("")}
      </tbody></table></div></div>`).join("")}
    </section>`;

    const densMode = S.cmp.dens || "kloc";
    const series = (p, c) => ({ name: short(p.repo), color: c, points: p.series.map((s) => { const n = s.maint + s.rel + s.sec, miss = (s.missing || "").includes("sonarqube"); const y = miss ? null : densMode === "kloc" ? (s.loc ? n / (s.loc / 1000) : 0) : n; return { x: s.idx, y, tip: miss ? "scan failed" : `${fmt(y)} ${densMode === "kloc" ? "per KLOC" : "issues"} · ${date(s.date)} · <span class="mono">${s.sha.slice(0, 8)}</span>` }; }) });
    const drawDens = () => Charts.line($("#c-dens"), { xTicks: [1, 5, 10, 15, 20, 25, 30].filter((t) => t <= d.ai.series.length || t <= d.human.series.length), series: [series(d.ai, col.ai()), series(d.human, col.human())], yLabel: densMode === "kloc" ? "open issues / KLOC" : "open issues", xLabel: "analysed commit" });
    drawDens();
    const lab = CATS.map((c) => c[0].toUpperCase() + c.slice(1));
    Charts.bars($("#c-in"), { groups: lab, series: [{ name: short(d.ai.repo), color: col.ai(), values: CATS.map((c) => d.ai.rates[c].intro_per_kloc) }, { name: short(d.human.repo), color: col.human(), values: CATS.map((c) => d.human.rates[c].intro_per_kloc) }], unit: "per KLOC" });
    Charts.bars($("#c-out"), { groups: lab, series: [{ name: short(d.ai.repo), color: col.ai(), values: CATS.map((c) => d.ai.rates[c].removed_per_kloc) }, { name: short(d.human.repo), color: col.human(), values: CATS.map((c) => d.human.rates[c].removed_per_kloc) }], unit: "per KLOC" });
    const drawKM = () => {
      Charts.km($("#c-km"), { series: [{ name: short(d.ai.repo), color: col.ai(), curve: d.ai.km[S.cat].curve }, { name: short(d.human.repo), color: col.human(), curve: d.human.km[S.cat].curve }], xLabel: S.unit === "commits" ? "analysed commits since introduction" : "days since introduction", unitLabel: S.unit });
      const t = d.tests[S.cat]; const a = d.ai.km[S.cat], h = d.human.km[S.cat];
      $("#c-km-note").textContent = `${short(d.ai.repo)}: ${a.n} issues, ${a.events} removed, median ${a.median == null ? "not reached" : fmt(a.median)}. ${short(d.human.repo)}: ${h.n} issues, ${h.events} removed, median ${h.median == null ? "not reached" : fmt(h.median)}. Log-rank ${t ? pvs(t.p) : "p = –"}.`;
    };
    drawKM();
    Charts.stack($("#c-mech"), { rows: [d.ai, d.human].map((p) => ({ label: short(p.repo).slice(0, 10), parts: [["code_changed", css("--good")], ["file_deleted", css("--ink-3")], ["code_still_present", css("--warn")]].map(([k, c]) => ({ name: MECH[k], value: p.mechanisms[k] || 0, color: c })) })) });
    onSeg(body, "dens", (v) => { S.cmp.dens = v; drawCompare(); });
    onSeg(body, "ccat", (v) => { S.cat = v; drawKM(); });
    onSeg(body, "cunit", (v) => { S.unit = v; drawCompare(); });
  }

  /* ================= ISSUES ================= */
  async function issues() {
    const ph = phaseObj(), f = S.iss;
    main.innerHTML = `
    <header class="page-head"><p class="eyebrow">${esc(ph.label)}</p><h1>Issue explorer</h1><p>Every tracked warning with its life story. Click a row to see where it appeared, how it moved and how it disappeared.</p></header>
    <form class="panel toolbar" id="iss-form">
      <div class="field" style="flex:1 1 220px"><label for="f-q">Search rule, message or file</label><input id="f-q" type="search" value="${esc(f.q || "")}" placeholder="e.g. complexity, pickle, cluster.py"></div>
      <div class="field"><label for="f-repo">Project</label><select id="f-repo"><option value="">All projects</option>${ph.projects.map((p) => `<option value="${p.repo}" ${f.repo === p.repo ? "selected" : ""}>${esc(short(p.repo))} (${p.grp === "AI" ? "AI" : "pre-AI"})</option>`).join("")}</select></div>
      <div class="field"><label for="f-cat">Category</label><select id="f-cat"><option value="">All</option>${CATS.map((c) => `<option ${f.category === c ? "selected" : ""}>${c}</option>`).join("")}</select></div>
      <div class="field"><label for="f-st">Status</label><select id="f-st">${[["", "Any"], ["open", "Still open"], ["removed", "Removed"], ["code_changed", "Removed · code changed"], ["file_deleted", "Removed · file deleted"]].map(([v, l]) => `<option value="${v}" ${f.status === v ? "selected" : ""}>${l}</option>`).join("")}</select></div>
      <div class="field"><label for="f-sort">Sort</label><select id="f-sort">${[["", "Project"], ["longest", "Longest-lived"], ["newest", "Newest"], ["oldest", "Oldest"]].map(([v, l]) => `<option value="${v}" ${f.sort === v ? "selected" : ""}>${l}</option>`).join("")}</select></div>
    </form>
    <div id="iss-list"><p class="loading">Loading…</p></div>`;
    const form = $("#iss-form");
    const upd = () => { Object.assign(S.iss, { q: $("#f-q").value.trim(), repo: $("#f-repo").value, category: $("#f-cat").value, status: $("#f-st").value, sort: $("#f-sort").value, page: 1 }); loadIssues(); };
    form.addEventListener("submit", (e) => { e.preventDefault(); upd(); });
    $$("select", form).forEach((s) => s.addEventListener("change", upd));
    let t; $("#f-q").addEventListener("input", () => { clearTimeout(t); t = setTimeout(upd, 300); });
    await loadIssues();
  }
  async function loadIssues() {
    const f = S.iss, q = new URLSearchParams({ phase: S.phase, page: f.page || 1 });
    ["q", "repo", "category", "status", "sort"].forEach((k) => f[k] && q.set(k, f[k]));
    const d = await api("/api/issues?" + q);
    const list = $("#iss-list"); if (!list) return;
    if (!d.items.length) { list.innerHTML = '<div class="panel empty">No issues match these filters. Clear the search or pick another project.</div>'; return; }
    const status = (i) => i.removed_idx == null ? '<span class="chip open">Open</span>' : i.mechanism === "file_deleted" ? '<span class="chip del">File deleted</span>' : '<span class="chip gone">Removed</span>';
    list.innerHTML = `<p class="small muted" style="margin:14px 0 8px">${d.total.toLocaleString()} issues</p>
    <div class="table-wrap"><table><thead><tr><th>Project</th><th>Rule & message</th><th>Category</th><th class="n">Born</th><th class="n">Lifetime</th><th>Status</th></tr></thead><tbody>
    ${d.items.map((i) => `<tr class="click" data-id="${i.id}" tabindex="0"><td>${chip(i.grp)}<div class="small" style="margin-top:4px">${esc(short(i.repo))}</div></td>
      <td><span class="mono">${esc(i.rule.split(".").pop())}</span><div class="small muted">${esc(i.message.slice(0, 120))}</div><div class="small mono muted">${esc(i.path_last)}</div></td>
      <td>${catTag(i.category)}</td><td class="n mono">${i.baseline ? "≤ c01" : "c" + String(i.intro_idx).padStart(2, "0")}</td>
      <td class="n">${i.life_commits} commits<div class="small muted">${fmt(i.life_days)} days</div></td><td>${status(i)}</td></tr>`).join("")}
    </tbody></table></div>
    <div class="pager"><button class="btn" id="pg-prev" ${d.page <= 1 ? "disabled" : ""}>Previous</button><span>Page ${d.page} of ${d.pages}</span><button class="btn" id="pg-next" ${d.page >= d.pages ? "disabled" : ""}>Next</button></div>`;
    $$("tr.click", list).forEach((tr) => { const open = () => openIssue(+tr.dataset.id); tr.addEventListener("click", open); tr.addEventListener("keydown", (e) => e.key === "Enter" && open()); });
    $("#pg-prev").addEventListener("click", () => { S.iss.page--; loadIssues(); });
    $("#pg-next").addEventListener("click", () => { S.iss.page++; loadIssues(); });
  }

  async function openIssue(id) {
    const i = await api(`/api/issue/${S.phase}/${id}`);
    const n = i.snapshots.length, color = i.grp === "AI" ? "var(--ai)" : "var(--human)";
    const on = (k) => k >= i.intro_idx && k <= i.last_idx;
    const lineAt = Object.fromEntries(i.lines.map(([s, l]) => [s, l]));
    const snap = (k) => i.snapshots.find((s) => s.idx === k);
    const blob = (k, p, l) => { const s = snap(k); return s ? `https://github.com/${i.repo}/blob/${s.sha}/${p}${l ? "#L" + l : ""}` : "#"; };
    const events = [];
    events.push([i.intro_idx, i.baseline ? "Already present at the first analysed commit" : "Introduced", `${i.path_first}:${lineAt[i.intro_idx] ?? ""}`, blob(i.intro_idx, i.path_first, lineAt[i.intro_idx])]);
    let prevL = lineAt[i.intro_idx];
    i.lines.forEach(([s, l]) => { if (prevL != null && l !== prevL) events.push([s, `Moved from line ${prevL} to ${l}`, "", blob(s, i.path_last, l)]); prevL = l; });
    if (i.paths.length > 1) events.push([i.last_idx, `File renamed: ${i.paths.join(" → ")}`, "", ""]);
    if (i.removed_idx) events.push([i.removed_idx, `Removed · ${MECH[i.mechanism] || i.mechanism}`, "", `https://github.com/${i.repo}/commit/${snap(i.removed_idx).sha}`]);
    else events.push([i.last_idx, "Still present at the last analysed commit (censored)", "", blob(i.last_idx, i.path_last, lineAt[i.last_idx])]);
    events.sort((a, b) => a[0] - b[0]);
    $("#drawer-body").innerHTML = `
      <p class="eyebrow">${esc(i.repo)} · issue #${i.id}</p>
      <h2 id="drawer-title" style="margin:6px 0 4px;font-size:1.3rem" class="mono">${esc(i.rule)}</h2>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin:8px 0">${chip(i.grp)}${catTag(i.category)}<span class="chip">${esc(i.tool)}</span>${i.severity ? `<span class="chip">${esc(i.severity)}</span>` : ""}${i.cwe ? `<span class="chip">${esc(i.cwe.slice(0, 40))}</span>` : ""}</div>
      <p>${esc(i.message)}</p>
      <div class="panel" style="margin-top:16px"><h3>Lifeline across the ${n} analysed commits</h3>
        <div class="strip" style="--n:${n};--c:${color}">${i.snapshots.map((s) => `<i class="${on(s.idx) ? "on" : ""} ${s.idx === i.intro_idx && !i.baseline ? "born" : ""} ${(s.missing || "").includes(i.tool) ? "miss" : ""}" title="c${String(s.idx).padStart(2, "0")} · ${date(s.date)}${on(s.idx) ? " · present" : ""}"></i>`).join("")}</div>
        <div class="strip-axis"><span>c01 · ${date(i.snapshots[0].date)}</span><span>c${n} · ${date(i.snapshots[n - 1].date)}</span></div>
        <p class="small muted" style="margin-top:8px">Lifetime: <b>${i.life_commits}</b> analysed commits, <b>${fmt(i.life_days)}</b> days${i.removed_idx ? "" : " so far (censored)"}.</p>
      </div>
      <div class="panel" style="margin-top:12px"><h3>Timeline</h3><ul class="timeline" style="margin-top:8px">
        ${events.map(([k, what, where, link]) => `<li><b>c${String(k).padStart(2, "0")}</b><div>${esc(what)}${where ? `<div class="small mono muted">${esc(where)}</div>` : ""}<div class="small muted">${date((snap(k) || {}).date)} · <span class="mono">${((snap(k) || {}).sha || "").slice(0, 10)}</span>${link ? ` · <a href="${link}" target="_blank" rel="noopener">view on GitHub ↗</a>` : ""}</div></div></li>`).join("")}
      </ul></div>`;
    $("#drawer").hidden = false; $(".drawer-close").focus();
  }
  $("#drawer").addEventListener("click", (e) => { if (e.target.closest("[data-close]")) $("#drawer").hidden = true; });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") $("#drawer").hidden = true; });

  /* ================= VALIDATION ================= */
  async function validation() {
    const v = await api(`/api/validation?phase=${S.phase}`), ph = phaseObj();
    const reasons = {}; v.reasons.forEach((r) => (reasons[r.reason] = (reasons[r.reason] || 0) + r.n));
    const methods = {}; v.methods.forEach((m) => (methods[m.method] = (methods[m.method] || 0) + m.n));
    const mTot = Object.values(methods).reduce((a, b) => a + b, 0) || 1;
    main.innerHTML = `
    <header class="page-head"><p class="eyebrow">${esc(ph.label)}</p><h1>Can the tracker be trusted?</h1>
      <p>Two independent checks: comparison with SonarQube's own issue tracking, and a manual check of ten sampled issue histories.</p></header>

    <section class="section">
      <div class="section-head"><h2>Agreement with SonarQube</h2><p>Event agreement compares how many new issues each method sees at every commit. Identity agreement checks that both follow the same issue.</p></div>
      <div class="table-wrap"><table><thead><tr><th>Project</th><th class="n">SonarQube new issues</th><th class="n">Tracker introductions</th><th class="n">Event agreement</th><th class="n">Identity agreement</th></tr></thead><tbody>
        ${v.agreement.map((a) => { const e = v.events.find((x) => x.repo === a.repo) || {}; return `<tr><td>${esc(a.repo)}</td><td class="n">${e.sonar_new_keys ?? "–"}</td><td class="n">${e.tracker_introductions ?? "–"}</td><td class="n">${e.event_agreement_pct ?? "–"}%</td><td class="n">${a.agreement_pct}%</td></tr>`; }).join("")}
      </tbody></table></div>
      ${Object.keys(reasons).length ? `<div class="panel"><h3>Why the two methods disagree</h3><div class="legend" style="margin-top:8px">${Object.keys(reasons).map((k, i) => `<span><i style="background:${["var(--accent)", "var(--warn)", "var(--ink-3)"][i % 3]}"></i>${esc(k)} (${reasons[k]})</span>`).join("")}</div><div class="chart" id="v-why"></div></div>
      <p class="takeaway">Most disagreements come from <strong>renamed or moved files</strong>: the tracker follows Git's rename detection, while SonarQube starts a new issue. Where the flagged line itself was edited, either answer is defensible, and these cases are counted as ambiguous.</p>` : ""}
    </section>

    <section class="section">
      <div class="section-head"><h2>How issues were matched between commits</h2></div>
      <div class="grid g3">
        ${[["exact", "Exact", "Same rule, same file and identical flagged code"], ["context", "Context", "Same rule and code, line moved"], ["message", "Message", "Same rule and message, nearest line after diff mapping (≤ 15 lines)"]].map(([k, l, d]) => `<div class="panel stat"><span class="v">${Math.round(((methods[k] || 0) / mTot) * 100)}%</span><span class="k"><b>${l}.</b> ${d}</span></div>`).join("")}
      </div>
      <p class="takeaway"><strong>Failure case found in the pilot:</strong> when code was inserted above an issue, the nearest-line rule paired it with the wrong warning. Adding a diff-based line mapping fixed it, and identity agreement for dhSegment rose from 91.6% to 97.5%. A committed <code>build/</code> folder also produced 146 fake issues, so generated folders are now excluded in both groups.</p>
    </section>

    <section class="section">
      <div class="section-head"><h2>Manual check of ten issue histories</h2><p>Click <b>Show code</b> on a card to see the flagged line before, during and after the issue's life, then mark each claim and save. Your answers are stored in the app's database under your name.</p></div>
      <div class="grid g2" id="checks">
        ${v.sample.map((s) => { const c = s.check || {}; const yn = (k) => `<span class="yn" data-k="${k}"><button type="button" class="y" aria-pressed="${c[k] === "Y"}">Correct</button><button type="button" class="n" aria-pressed="${c[k] === "N"}">Wrong</button></span>`;
          return `<div class="panel check-card" data-id="${s.issue_id}">
            <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">${chip(s.group)}${catTag(s.category)}<span class="small muted">#${s.issue_id} · ${esc(short(s.repo))}</span></div>
            <b class="mono small">${esc(s.rule)}</b><span class="small">${esc(s.message)}</span>
            <span class="small muted">Seen in commits ${esc(s.seen_in_snapshots)} · lines ${esc(s.lines_seen)} · ${esc(s.removal_mechanism)}</span>
            <span class="small"><a href="${s.link_introduced}" target="_blank" rel="noopener">code at introduction ↗</a> · <a href="${s.link_last_seen}" target="_blank" rel="noopener">last seen ↗</a>${s.link_removal_diff ? ` · <a href="${s.link_removal_diff}" target="_blank" rel="noopener">removal commit ↗</a>` : ""}</span>
            <button class="btn show-code" type="button">Show code</button><div class="code-views" hidden></div>
            <div class="check-row"><span>Introduction ${yn("intro")}</span><span>Persistence ${yn("persist")}</span><span>Removal ${yn("removal")}</span></div>
            <textarea id="note-${s.issue_id}" placeholder="Notes (optional)">${esc(c.notes || "")}</textarea>
            <div style="display:flex;gap:10px;align-items:center"><button class="btn primary save" type="button">Save check</button><span class="saved">${c.updated ? `Saved by ${esc(c.checked_by)} · ${c.updated.replace("T", " ")}` : ""}</span></div>
          </div>`; }).join("")}
      </div>
    </section>`;
    if (Object.keys(reasons).length) Charts.stack($("#v-why"), { rows: [{ label: "All", parts: Object.entries(reasons).map(([k, n], i) => ({ name: k, value: n, color: [css("--accent"), css("--warn"), css("--ink-3")][i % 3] })) }] });
    const parse = (u) => { const m = /github\.com\/([^/]+\/[^/]+)\/blob\/([0-9a-f]+)\/(.+?)(?:#L(\d+))?$/.exec(u || ""); return m ? { repo: m[1], sha: m[2], path: m[3], line: +(m[4] || 1) } : null; };
    const codeBox = (title, hint, d) => {
      if (d.error) return `<div class="code-box"><div class="code-title">${title}</div><p class="small muted">${esc(d.error)}</p></div>`;
      if (d.missing) return `<div class="code-box"><div class="code-title">${title}</div><p class="code-missing">The file <span class="mono">${esc(d.path)}</span> does not exist in this version (deleted or renamed).</p></div>`;
      return `<div class="code-box"><div class="code-title">${title}<span class="small muted"> · ${esc(d.path)}</span></div>${hint ? `<p class="small code-hint">${hint}</p>` : ""}<pre class="code">${d.lines.map((t, k) => { const n = d.start + k; return `<span class="${n === d.focus ? "hl" : ""}"><i>${n}</i>${esc(t) || " "}</span>`; }).join("")}</pre></div>`;
    };
    v.sample.forEach((s) => {
      const card = $(`.check-card[data-id="${s.issue_id}"]`); if (!card) return;
      $(".show-code", card).addEventListener("click", async (e) => {
        const box = $(".code-views", card);
        if (!box.hidden) { box.hidden = true; e.target.textContent = "Show code"; return; }
        box.hidden = false; e.target.textContent = "Hide code"; box.innerHTML = '<p class="loading">Loading code…</p>';
        const a = parse(s.link_introduced), b = parse(s.link_last_seen);
        const q = (o, extra) => api(`/api/code?repo=${encodeURIComponent(o.repo)}&sha=${o.sha}&path=${encodeURIComponent(o.path)}&line=${o.line}${extra || ""}`);
        const parts = [];
        const intro = await q(a);
        parts.push(codeBox(`① Introduced · commit ${a.sha.slice(0, 8)}`, "Does the highlighted line match the warning?", intro));
        let lastLine = "";
        if (b && b.sha !== a.sha) { const last = await q(b); lastLine = last.lines ? last.lines[last.focus - last.start] : ""; parts.push(codeBox(`② Last seen · commit ${b.sha.slice(0, 8)}`, "Is this the same code as in ①, maybe on another line?", last)); }
        else { lastLine = intro.lines ? intro.lines[intro.focus - intro.start] : ""; parts.push(`<p class="small muted">② Seen in only one analysed commit, so ① is also the last sighting.</p>`); }
        if (s.removed_commit) {
          const after = await q({ repo: s.repo, sha: s.removed_commit, path: b ? b.path : a.path, line: b ? b.line : a.line }, `&find=${encodeURIComponent(lastLine || "")}`);
          const hint = after.missing ? "" : after.found ? `The flagged line still exists here (line ${after.found}). If the app says “code changed”, look for edits around it.` : "The flagged line no longer exists in this form, so the code was changed.";
          parts.push(codeBox(`③ After removal · commit ${s.removed_commit.slice(0, 8)} · app says: ${esc(s.removal_mechanism)}`, hint, after));
        } else parts.push(`<p class="small muted">③ Still open at the last analysed commit, so there is no removal to check. Leave Removal empty.</p>`);
        box.innerHTML = parts.join("");
      });
    });
    $$(".check-card").forEach((card) => {
      $$(".yn", card).forEach((g) => g.addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b) return; const was = b.getAttribute("aria-pressed") === "true"; $$("button", g).forEach((x) => x.setAttribute("aria-pressed", "false")); b.setAttribute("aria-pressed", String(!was)); }));
      $(".save", card).addEventListener("click", async () => {
        const val = (k) => { const b = $(`.yn[data-k="${k}"] button[aria-pressed="true"]`, card); return b ? (b.classList.contains("y") ? "Y" : "N") : ""; };
        try { const r = await api(`/api/manual/${S.phase}/${card.dataset.id}`, { intro: val("intro"), persist: val("persist"), removal: val("removal"), notes: $("textarea", card).value });
          $(".saved", card).textContent = `Saved by ${S.me.name} · ${r.saved.replace("T", " ")}`; }
        catch (err) { $(".saved", card).textContent = err.message; }
      });
    });
  }

  /* ================= DATASET ================= */
  async function dataset() {
    const ph = phaseObj();
    const pairs = [...new Set(ph.projects.map((p) => p.match_id))].sort();
    main.innerHTML = `
    <header class="page-head"><p class="eyebrow">${esc(ph.label)}</p><h1>Dataset</h1><p>Every repository in this data set, how it was classified, and the variables used for matching. Sampling rule: ${esc(ph.sampling)}.</p></header>
    <div class="table-wrap"><table><thead><tr><th>Pair</th><th>Group</th><th>Repository</th><th>Evidence / basis</th><th class="n">Stars</th><th class="n">Python lines</th><th>Period analysed</th></tr></thead><tbody>
      ${pairs.map((m) => ph.projects.filter((p) => p.match_id === m).sort((a) => (a.grp === "AI" ? -1 : 1)).map((p, k) => `<tr>${k === 0 ? `<td rowspan="2" class="mono"><b>${m}</b></td>` : ""}<td>${chip(p.grp)}</td><td><a href="${gh(p.repo)}" target="_blank" rel="noopener">${esc(p.repo)}</a><div class="small muted">${esc(p.description)}</div></td><td class="small">${esc(p.evidence)}</td><td class="n">${p.stars ?? "–"}</td><td class="n">${p.loc_first.toLocaleString()} → ${p.loc_last.toLocaleString()}</td><td class="small">${p.first_date} → ${p.last_date}</td></tr>`).join("")).join("")}
    </tbody></table></div>
    <section class="section grid g2">
      <div class="panel"><h3>Inclusion rules</h3><ul class="small" style="margin:10px 0 0;padding-left:18px;display:grid;gap:6px">
        <li><b>AI-assisted:</b> explicit comments in source files attributing the code to an AI tool, checked by hand; at least 2 % of .py files declared (or ≥ 2 files).</li>
        <li><b>Pre-AI:</b> last push before 1 January 2022; not a fork, not archived, at least 10 stars, has a licence.</li>
        <li>Excluded: tutorials, homework, examples, benchmarks, paper-only code dumps.</li>
        <li>At least 60 non-merge commits, so 30 commits can be sampled.</li></ul></div>
      <div class="panel"><h3>Search funnel</h3><ul class="small" style="margin:10px 0 0;padding-left:18px;display:grid;gap:6px">
        <li>15 attribution phrases → 3,644 file hits in 1,636 repositories.</li>
        <li>After filters: 151 AI candidates meet the 2 % rule; one checked candidate (vibe-security-radar) was a false positive: the phrase appeared only inside test strings.</li>
        <li>Pre-AI: 2,014 candidates in 9 popularity × size strata; 250 profiled from their Git history.</li></ul></div>
    </section>`;
  }

  /* ================= LIMITATIONS ================= */
  async function limits() {
    const L = [
      ["Small sample", "Five repositories per group give low statistical power. Repository-level tests are the honest unit; issue-level tests overstate certainty because issues inside one repository are related."],
      ["AI evidence is partial", "A declaration proves some AI involvement but not how much of the code is AI-written. Undeclared AI use is invisible, which is why the baseline is pre-AI rather than 'non-AI'."],
      ["Time periods differ", "Pre-AI projects are older by design. Language versions, libraries and analyzer rules written for modern Python can treat old code differently."],
      ["Warnings are a proxy", "Static-analysis warnings stand in for quality problems. Some are false positives and real defects can be missed."],
      ["Sampling hides short lives", "Only 30 commits per project are analysed. An issue introduced and removed between two sampled commits is never seen, and lifetimes are measured in analysed commits."],
      ["Disappearance is not a fix", "A warning can vanish because its file was deleted or its code was refactored. The app separates these mechanisms, but intent cannot be proven."],
      ["Matching is approximate", "Pairs are matched on language, size and popularity. Domain, team size and project maturity still differ within pairs."],
      ["Tracker ambiguity", "Identical warnings on identical code can swap identities, and edited lines can be matched either way. These cases are logged and quantified on the validation page."],
      ["A few failed scans", `SonarQube failed on 7 of 360 analysed commits. Those commits are skipped for SonarQube and the issue histories continue across the gap.`],
    ];
    main.innerHTML = `<header class="page-head"><h1>Limitations and threats to validity</h1><p>What these results can and cannot show.</p></header><ul class="limits">${L.map(([b, s]) => `<li><b>${b}</b><span>${s}</span></li>`).join("")}</ul>`;
  }

  boot().catch((e) => { document.body.innerHTML = `<p style="padding:24px">The app could not start: ${esc(e.message)}. Is the server running?</p>`; });
})();
