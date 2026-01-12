# Core formatting helpers

import math
from textwrap import indent

def vec_norm(v):
    return math.sqrt(sum(x*x for x in v))

def fmt_vec(v, prec=3):
    return "[" + ", ".join(f"{x:.{prec}e}" for x in v) + "]"

def hr(title):
    return "\n" + "=" * 70 + f"\n{title}\n" + "=" * 70

# Simulation summary output
def print_simulation_summary(recorder, final_verdict):
    last = recorder.records[-1]
    sa = last["state_after"]

    print(hr("SIMULATION SUMMARY"))

    print(f"Steps executed        : {len(recorder.records)}")
    print(f"Final simulation time : {sa.time:.3f} s")
    print(f"Final verdict         : {final_verdict['fraud verdict']['verdict']}")

    print("\nFinal State:")
    print(f"  Position  : {fmt_vec(sa.position)} m")
    print(f"  Velocity  : {fmt_vec(sa.velocity)} m/s")
    print(f"  |v|       : {vec_norm(sa.velocity):.3e} m/s")
    print(f"  Mass      : {sa.mass:.6f} kg")
    print(f"  Energy    : {sa.energy:.6e} J")

# Conservation drift summary
def print_conservation_summary(recorder):
    drift = recorder.analyze_drift()

    print(hr("CONSERVATION DRIFT ANALYSIS"))

    print(f"Total energy residual   : {drift['energy_drift']:.3e} J")
    print(f"Total mass residual     : {drift['mass_drift']:.3e} kg")
    print(f"Total momentum residual : {fmt_vec(drift['momentum_drift'])}")

    print("\nMechanical energy drift due to fields:")
    print(f"  Max   : {drift['max_mechanical_energy_drift']:.3e} J")
    print(f"  Min   : {drift['min_mechanical_energy_drift']:.3e} J")
    print(f"  Final : {drift['final_mechanical_energy_drift']:.3e} J")

# Compact per-step table
def print_step_table(recorder, max_steps=10):
    print(hr("STEP EVOLUTION (COMPACT VIEW)"))

    header = (
        f"{'Step':>4} | {'Δ|v| (m/s)':>12} | {'ΔE (J)':>12} | "
        f"{'Δm (kg)':>10} | {'Engine':>10} | {'OK':>4}"
    )
    print(header)
    print("-" * len(header))

    for r in recorder.records[:max_steps]:
        sb = r["state_before_snapshot"]
        sa = r["state_after_snapshot"]

        dv = vec_norm(sa["velocity"]) - vec_norm(sb["velocity"])
        dE = sa["stored_energy"] - sb["stored_energy"]
        dm = sa["mass"] - sb["mass"]

        engine = r["engine_report"].source
        ok = "YES" if r["conservation"]["valid"] else "NO"

        print(
            f"{r['step']:>4} | "
            f"{dv:>12.3e} | "
            f"{dE:>12.3e} | "
            f"{dm:>10.3e} | "
            f"{engine:>10} | "
            f"{ok:>4}"
        )

    if len(recorder.records) > max_steps:
        print(f"... ({len(recorder.records) - max_steps} more steps)")

# Deep per-step inspection (forensic mode)
def print_step_details(step_record):
    print(hr(f"STEP {step_record['step']} — DETAILED ANALYSIS"))

    cons = step_record["conservation"]

    print("Conservation verdict:", "VALID" if cons["valid"] else "INVALID")
    print("\nResiduals:")
    print(f"  Energy   : {cons['energy_residual']:.3e}")
    print(f"  Mass     : {cons['mass_residual']:.3e}")
    print(f"  Momentum : {fmt_vec(cons['momentum_residual'])}")

    print("\nExplanation:")
    for k, v in cons["explain"].items():
        print(f"  {k}:")
        print(indent(str(v), "    "))

# Fraud verdict output
def print_fraud_verdict(fraud):
    print(hr("FRAUD AUDIT"))

    print("Verdict:", fraud["verdict"])

    if fraud["flags"]:
        print("\nFlags raised:")
        for f in fraud["flags"]:
            print(f"  - {f}")

    if fraud["reasons"]:
        print("\nReasons:")
        for r in fraud["reasons"]:
            print(f"  • {r}")
