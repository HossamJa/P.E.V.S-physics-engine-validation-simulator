/* =========================
   SIMULATION PAGE
========================= */

async function rerun_sim(form) {

    /* To rerun simulation from history */
    function getQueryParam(name) {
        return new URLSearchParams(window.location.search).get(name);
    }
    async function loadRerunSetup(simId) {
        const res = await fetch(`/api/simulation/rerun/${simId}`);
        if (!res.ok) {
            alert("Failed to load simulation setup.");
            return;
        }

        const setup = await res.json();

        populateSimulationForm(setup);
    }

    const rerunId = getQueryParam("rerun");

    /* Auto Submit */
    if (rerunId) {
        await loadRerunSetup(rerunId);
        setTimeout(() => {
            form.requestSubmit();
        }, 300);;
        return;
    }

    /* Functions for Reruning the Simulations From History */

    function populateSimulationForm(params) {

        /* ======================
        ENVIRONMENT (RADIO)
        ====================== */

        document
            .querySelector(`input[name="environment"][value="${params.env_type}"]`)
            ?.click();

        /* ======================
        ENGINE (RADIO)
        ====================== */

        document
            .querySelector(`input[name="engine_type"][value="${params.eng_type}"]`)
            ?.click();

        /* ======================
        TIME CONTROL
        ====================== */
        document.getElementById("dt").value = params.setup.dt;
        document.getElementById("steps").value = params.setup.steps;

        /* ======================
        MASS / ENERGY
        ====================== */
        document.getElementById("mass").value = params.setup.mass;
        document.getElementById("energy").value = params.setup.energy;

        /* ======================
        POSITION
        ====================== */
        document.querySelector("[name='position_x']").value = params.setup.position_x;
        document.querySelector("[name='position_y']").value = params.setup.position_y;
        document.querySelector("[name='position_z']").value = params.setup.position_z;

        /* ======================
        VELOCITY
        ====================== */
        document.querySelector("[name='iv_direction_x']").value = params.setup.iv_direction_x;
        document.querySelector("[name='iv_direction_y']").value = params.setup.iv_direction_y;
        document.querySelector("[name='iv_direction_z']").value = params.setup.iv_direction_z;

        /* Initial speed */
        document.querySelector("[name='speed']").value = params.setup.speed;

        /* ======================
        ENGINE PARAMS
        ====================== */
        if (params.eng_type === "1") {
            document.getElementById("exhaust_velocity").value = params.setup.exhaust_velocity;
            document.getElementById("mass_flow_rate").value = params.setup.mass_flow_rate;

            document.querySelector("[name='thrust_direction_x']").value = params.setup.thrust_direction_x;
            document.querySelector("[name='thrust_direction_y']").value = params.setup.thrust_direction_y;
            document.querySelector("[name='thrust_direction_z']").value = params.setup.thrust_direction_z;
        }

        if (params.eng_type === "2") {
            document.getElementById("power").value = params.setup.power;
        }

        if (params.eng_type === "3") {
            document.getElementById("efficiency").value = params.setup.efficiency;
        }

        /* ======================
        CUSTOM ENV
        ====================== */
        if (params.env_type === "3") {
            document.getElementById("gravity_mass").value = params.setup.gravity_mass;
            document.getElementById("G").value = params.setup.G;

            document.querySelector("[name='gravity_source_x']").value = params.setup.gravity_source_x;
            document.querySelector("[name='gravity_source_y']").value = params.setup.gravity_source_y;
            document.querySelector("[name='gravity_source_z']").value = params.setup.gravity_source_z;
        }
    }
}

function initSimulationPage() {

    /* =====================================================
       FORM LOGIC
    ===================================================== */
    const form = document.getElementById("simulation-form");
    const submitBtn = form.querySelector("button[type='submit']");

    const engineRadios = document.querySelectorAll("input[name='engine_type']");
    const engineParams = document.querySelectorAll(".engine-params");

    const envRadios = document.querySelectorAll("input[name='environment']");
    const customEnv = document.querySelector(".custom-environment");

    submitBtn.disabled = true;

    const engineMap = {
        "1": "reaction-params",
        "2": "photon-params",
        "3": "field-params"
    };

    rerun_sim(form);

    function resetEngineParams() {
        engineParams.forEach(div => {
            div.style.display = "none";
            div.querySelectorAll("input").forEach(i => i.required = false);
        });
    }

    engineRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            resetEngineParams();

            const params = document.getElementById(engineMap[radio.value]);
            if (params) {
                params.style.display = "block";
                params.querySelectorAll("input").forEach(i => i.required = true);
            }

            validateForm();
        });
    });

    envRadios.forEach(radio => {
        radio.addEventListener("change", () => {

            if (radio.value === "3") {
                customEnv.style.display = "block";
                customEnv.querySelectorAll("input").forEach(i => i.required = true);
            } else {
                customEnv.style.display = "none";
                customEnv.querySelectorAll("input").forEach(i => {
                    i.required = false;
                    i.value = "";
                });
            }

            if (radio.value === "3") {
                document.getElementById("G").value = 6.6743e-11;
                document.getElementById("gravity_mass").value = 5.972e24;
            }

            validateForm();
        });
    });

    function validateForm() {
        const required = form.querySelectorAll("input[required]");
        submitBtn.disabled = [...required].some(
            i => i.offsetParent !== null && !i.value
        );
    }

    form.addEventListener("input", validateForm);
    resetEngineParams();
    customEnv.style.display = "none";

    /* =====================================================
       FORM SUBMISSION
    ===================================================== */
    form.addEventListener("submit", async e => {
        e.preventDefault();
        setLoading(true);

        try {
            const res = await fetch("/api/simulation/run", {
                method: "POST",
                body: new FormData(form)
            });

            const data = await res.json();
            if (!res.ok || data.error) throw new Error(data.error || "Simulation failed");

            renderResults(data);

        } catch (err) {
            alert(err.message);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(state) {
        submitBtn.disabled = state;
        submitBtn.textContent = state ? "Running..." : "Run Simulation";
    }
    /* INITIAL PLACEHOLDERS FOR GRAPHS (ON LOAD) */
    renderPlaceholderGraphs();
    /* =====================================================
       RENDER RESULTS
    ===================================================== */
    function renderResults(data) {

        /* --- Summary --- */
        setSummaryVerdict("verdict-status", data.summary.verdict);
        setText("steps-executed", data.summary.steps_executed);
        setText("final-time", data.summary.final_time);

        /* --- Final State --- */
        const fs = data.final_state;
        setText("final-position", vec(fs.position));
        setText("final-velocity", vec(fs.velocity));
        setText("final-speed", fs.speed.toFixed(6));
        setText("final-mass", fs.mass);
        setText("final-energy", fs.energy.total);

        setText("final-ke", fs.energy.kinetic);
        setText("final-gpe", fs.energy.potential);

        /* --- Conservation --- */
        renderExplain("energy-conservation", data.conservation.energy);
        renderExplain("momentum-conservation", data.conservation.momentum);
        renderExplain("mass-conservation", data.conservation.mass);
        renderExplain("field-energy-conservation", data.conservation.field_energy);

        /* --- Audit Verdicts --- */
        setVerdict("closed-system-verdict", data.audit.closed_system.verdict.includes("PASS"));
        renderFlagList("closed-system-flags", data.audit.closed_system.flags);
        
        setVerdict("field-verdict", data.audit.field.verdict.includes("PASS"));
        renderFlagList("field-flags", data.audit.field.flags);

        /* --- Engine / Environment --- */
        renderLedger(data.engine, "engine");
        renderLedger(data.environment, "env");

        /* --- Graphs --- */
        renderGraphs(data.timeseries);

        /* --- Tables (with slicing) --- */
        const ts = data.timeseries;
        const limit = document.getElementById("step-limit").value;
        const start = limit === "all" ? 0 : Math.max(0, ts.time.length - Number(limit));

        renderStateTable(ts, start);
        renderEnergyTable(ts, start);
        renderMomentumTable(ts, start);
        renderExchangeTable(data.reports, start);

        /* --- Raw --- */
        const rawEl = document.getElementById("raw-records");

        rawEl.textContent = JSON.stringify(data.raw_data, null, 2);
        enableScopedSelectAll(rawEl);

    }

    /* =====================================================
       HELPERS
    ===================================================== */
    function setText(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value ?? "—";
    }

    const vec = v => `[${v.map(x => x.toFixed(3)).join(", ")}]`;

    const norm = v => Math.sqrt(v.reduce((s, x) => s + x * x, 0));

    function renderExplain(id, obj) {
        const el = document.getElementById(id);
        el.innerHTML = "";
        Object.entries(obj || {}).forEach(([k, v]) => {
            el.insertAdjacentHTML("beforeend", `
                <div class="explain-row">
                    <span class="explain-key">${k}</span>
                    <span class="explain-value">${formatValue(v)}</span>
                </div>
            `);
        });
    }

    const formatValue = v =>
        typeof v === "number" ? v.toExponential(6) :
        typeof v === "boolean" ? (v ? "✔ Yes" : "✖ No") :
        JSON.stringify(v);

    function renderFlagList(id, flags = []) {
        const ul = document.getElementById(id);

        if (!flags.length) {
            ul.innerHTML = `<li>No flags raised.</li>`;
            return;
        }

        ul.innerHTML = flags.map(f => {
            const level =
                f.toLowerCase().includes("violation") ? "flag-critical" :
                f.toLowerCase().includes("warning") ? "flag-warning" :
                "";

            return `<li class="${level}">${f}</li>`;
        }).join("");
    }

    function setSummaryVerdict(id, verdictText) {
        const el = document.getElementById(id);
        const v = verdictText.toUpperCase();

        el.textContent = v;
        el.classList.remove("verdict-pass", "verdict-fail", "verdict-warn");

        if (v === "PASS") el.classList.add("verdict-pass");
        else if (v === "FAIL") el.classList.add("verdict-fail");
        else el.classList.add("verdict-warn");
    }

    function setVerdict(id, passed) {
        const el = document.getElementById(id);

        el.textContent = passed ? "PASS" : "FAIL";
        el.classList.remove("verdict-pass", "verdict-fail");
        el.classList.add(passed ? "verdict-pass" : "verdict-fail");
    }

    function renderLedger(obj, prefix) {
        Object.entries(obj || {}).forEach(([k, v]) =>
            setText(`${prefix}-${k.replaceAll("_", "-")}`, v)
        );
    }

    /* =====================================================
       GRAPHS
    ===================================================== */
    function renderPlaceholderGraphs() {
        const zero = Array(10).fill(0);
        const t = Array.from({ length: 10 }, (_, i) => i);

        ["position-graph", "velocity-graph", "energy-graph", "momentum-graph"]
            .forEach(id => {
                plotMultiLine({
                    id,
                    time: t,
                    title: "No Simulation Data",
                    yLabel: "",
                    series: [{ label: "—", data: zero }],
                    placeholder: true
                });
            });
    }

    function plotMultiLine({
        id,
        time,
        series,
        title,
        yLabel,
        logScale = false,
        placeholder = false
    }) {
        const c = document.getElementById(id);
        if (c.chart) c.chart.destroy();
        
        c.chart = new Chart(c, {
            type: "line",
            data: {
                labels: time,
                datasets: series.map(s => ({
                    label: s.label,
                    data: s.data,
                    borderWidth: 1.5,
                    pointRadius: 0,
                    tension: 0.1,
                    borderDash: placeholder ? [6, 4] : []
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: !placeholder,
                        position: "bottom"
                    },
                    title: {
                        display: true,
                        text: placeholder
                            ? "No simulation data yet"
                            : title
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: !placeholder,
                            text: "Time (s)"
                        }
                    },
                    y: {
                        type: logScale ? "logarithmic" : "linear",
                        title: {
                            display: !placeholder,
                            text: yLabel
                        },
                        ticks: {
                            maxTicksLimit: 6,
                            callback: v => {
                                if (v === 0) return "0";
                                const exp = Math.floor(Math.log10(Math.abs(v)));
                                if (Math.abs(exp) > 3) {
                                    return v.toExponential(2);
                                }
                                return Number(v).toPrecision(4);
                            }
                        },
                        afterBuildTicks: logScale
                            ? axis => {
                                axis.ticks = axis.ticks.filter(t =>
                                    Number.isInteger(Math.log10(t.value))
                                );
                            }
                            : undefined
                    }
                }
            }
        });
    }

    function renderGraphs(ts) {

        plotMultiLine({
            id: "position-graph",
            time: ts.time,
            title: "Position Components",
            yLabel: "Position (m)",
            series: [
                { label: "x", data: ts.position.map(p => p[0]) },
                { label: "y", data: ts.position.map(p => p[1]) },
                { label: "z", data: ts.position.map(p => p[2]) }
            ]
        });

        plotMultiLine({
            id: "velocity-graph",
            time: ts.time,
            title: "Velocity Components",
            yLabel: "Velocity (m/s)",
            series: [
                { label: "vx", data: ts.velocity.map(v => v[0]) },
                { label: "vy", data: ts.velocity.map(v => v[1]) },
                { label: "vz", data: ts.velocity.map(v => v[2]) }
            ]
        });

        plotMultiLine({
            id: "energy-graph",
            time: ts.time,
            title: "Energy Evolution",
            yLabel: "Energy (J)",
            logScale: true,
            series: [
                { label: "Stored", data: ts.energy.map(e => e.stored) },
                { label: "Kinetic", data: ts.energy.map(e => e.kinetic) },
                {
                    label: "Total",
                    data: ts.energy.map(e =>
                        e.stored + e.kinetic + e.potential
                    )
                }
            ]
        });

        plotMultiLine({
            id: "momentum-graph",
            time: ts.time,
            title: "Momentum Components",
            yLabel: "Momentum (kg·m/s)",
            logScale: true,
            series: [
                { label: "px", data: ts.momentum.map(p => Math.abs(p[0])) },
                { label: "py", data: ts.momentum.map(p => Math.abs(p[1])) },
                { label: "pz", data: ts.momentum.map(p => Math.abs(p[2])) }
            ]
        });
    }

    /* =====================================================
       TABLES (SLICED)
    ===================================================== */
    function renderStateTable(ts, s) {
        fillTable("#state-table tbody", ts.time, (i) => `
            <td>${i}</td>
            <td>${ts.time[i].toFixed(3)}</td>
            <td>${vec(ts.position[i])}</td>
            <td>${vec(ts.velocity[i])}</td>
            <td>${norm(ts.velocity[i]).toFixed(4)}</td>
            <td>${ts.mass[i]}</td>
        `, s);
    }

    function renderEnergyTable(ts, s) {
        fillTable("#energy-table tbody", ts.energy, (i) => {
            const e = ts.energy[i];
            const t = e.stored + e.kinetic + e.potential;
            return `<td>${i}</td>
                    <td>${e.stored.toFixed(6)}</td>
                    <td>${e.kinetic.toFixed(6)}</td>
                    <td>${e.potential.toFixed(6)}</td>
                    <td>${t.toFixed(6)}</td>`;
        }, s);
    }

    function renderMomentumTable(ts, s) {
        fillTable("#momentum-table tbody", ts.momentum, i =>
            `<td>${i}</td><td>${vec(ts.momentum[i])}</td><td>${norm(ts.momentum[i]).toFixed(6)}</td>`, s);
    }

    function renderExchangeTable(records, s) {
        fillTable("#exchange-table tbody", records, i => {
            const r = records[i];
            return `<td>${i}</td>
                <td>${r.engine_report_snapshot?.exhaust_momentum ? vec(r.engine_report_snapshot.exhaust_momentum) : "—"}</td>
                <td>${r.engine_report_snapshot?.energy_drawn ?? "—"}</td>
                <td>${r.engine_report_snapshot?.mass_spent ?? "—"}</td>
                <td>${r.environment_report_snapshot?.momentum_exchange ? vec(r.environment_report_snapshot.momentum_exchange) : "—"}</td>
                <td>${r.environment_report_snapshot?.energy_exchange ?? "—"}</td>
                <td>${r.environment_report_snapshot?.mass_exchange ?? "—"}</td>`;
        }, s);
    }

    function fillTable(sel, arr, rowFn, s) {
        const tb = document.querySelector(sel);
        tb.innerHTML = "";
        for (let i = s; i < arr.length; i++) {
            const tr = document.createElement("tr");
            tr.innerHTML = rowFn(i);
            tb.appendChild(tr);
        }
    }

    function enableScopedSelectAll(preEl) {
        preEl.setAttribute("tabindex", "0"); // make focusable

        preEl.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === "a") {
                e.preventDefault();

                const range = document.createRange();
                range.selectNodeContents(preEl);

                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
            }
        });
    }
}

document.getElementById("copy-raw").addEventListener("click", async () => {
    const text = document.getElementById("raw-records").textContent;

    try {
        await navigator.clipboard.writeText(text);
        alert("Raw data copied to clipboard");
    } catch {
        alert("Copy failed");
    }
});

document.getElementById("export-raw").addEventListener("click", () => {
    const data = document.getElementById("raw-records").textContent;

    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "simulation_raw_data.json";
    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});
