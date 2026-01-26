/* =========================
   HISTORY PAGE
========================= */

function initHistoryPage() {
    loadHistory();

    ["filter-verdict", "filter-engine", "filter-env"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("change", loadHistory);
    });
}

async function loadHistory() {
    try {
        const params = new URLSearchParams();

        const verdict = document.getElementById("filter-verdict")?.value;
        const engine = document.getElementById("filter-engine")?.value;
        const env = document.getElementById("filter-env")?.value;

        if (verdict) params.append("verdict", verdict);
        if (engine) params.append("engine", engine);
        if (env) params.append("environment", env);

        const res = await fetch(`/api/history?${params.toString()}`);

        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        renderHistory(data);

    } catch (err) {
        console.error("History load failed:", err);
        document.getElementById("history-body").innerHTML = `
            <tr>
                <td colspan="10" class="mono text-danger">
                    Failed to load history.
                </td>
            </tr>
        `;
    }
}

function renderHistory(data) {
    const tbody = document.getElementById("history-body");
    tbody.innerHTML = "";

    if (!data.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="mono">No simulations found.</td>
            </tr>
        `;
        return;
    }

    for (const sim of data) {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${sim.created_at.slice(0, 10)}</td>
            <td>${capitalize(sim.engine)}</td>
            <td>${capitalize(sim.environment)}</td>
            <td>${sim.steps ?? "-"}</td>
            <td>${sim.final_time ?? "-"} s</td>

            <td>
                <span class="badge ${sim.verdict === "PASS" ? "pass" : "fail"}">
                    ${sim.verdict}
                </span>
            </td>

            <td class="mono">${formatDrift(sim.energy_drift, "J")}</td>
            <td class="mono">${vec(sim.momentum_drift)} kg·m/s</td>

            <td>
                <span class="badge ${sim.audit_ok ? "ok" : "warn"}">
                    ${sim.audit_ok ? "OK" : "CHECK"}
                </span>
            </td>

            <td>
                <button class="btn-view" data-id="${sim.id}">
                    Rerun
                </button>

                <button class="btn-delete" data-id="${sim.id}">
                    Delete
                </button>
            </td>
        `;

        tr.querySelector(".btn-view").addEventListener("click", () => {
            rerunSimulation(sim.id);
        });
        
        tr.querySelector(".btn-delete").addEventListener("click", () => {
            deleteSimulation(sim.id);
        });

        tbody.appendChild(tr);
    }
}

async function deleteSimulation(simId) {
    if (!confirm("Delete this simulation permanently?")) return;

    try {
        const res = await fetch(`/api/history/${simId}`, {
            method: "DELETE"
        });

        if (!res.ok) throw new Error("Delete failed");

        loadHistory(); // refresh table

    } catch (err) {
        alert("Failed to delete simulation.");
        console.error(err);
    }
}

function formatDrift(value, unit) {
    if (value === null || value === undefined) return "-";
    return `${value > 0 ? "+" : ""}${Number(value).toExponential(2)} ${unit}`;
}

const vec = v => `[${v.map(x => x.toFixed(3)).join(", ")}]`;

function rerunSimulation(simId) {
    window.location.href = `/simulation?rerun=${simId}`;
}

function capitalize(str) {
    if (!str || typeof str !== "string") return "-";
    return str.charAt(0).toUpperCase() + str.slice(1);
}

