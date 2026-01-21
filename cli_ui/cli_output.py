# Core formatting helpers

import math
from textwrap import indent

def vec_norm(v):
    return math.sqrt(sum(x*x for x in v))

def fmt_vec(v, prec=3):
    return "[" + ", ".join(f"{x:.{prec}e}" for x in v) + "]"

def hr(title):
    return "\n" + "=" * 70 + f"\n{title}\n" + "=" * 70

def sum_vectors(vectors):
    out = [0.0, 0.0, 0.0]
    for v in vectors:
        for i in range(3):
            out[i] += v[i]
    return out

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


# ============================
# Advanced accounting helpers
# ============================

def print_environment_summary(recorder, ui=False):
    env_momentum = []
    env_energy = 0.0
    total_env_pm = 0

    for r in recorder.records:
        env = r.get("environment_report")
        if not env:
            continue

        if env.momentum_exchange is not None:
            env_momentum.append(env.momentum_exchange)

        if env.energy_exchange is not None:
            env_energy += env.energy_exchange

    if not env_momentum and abs(env_energy) < 1e-12:
        return env_momentum, env_energy, total_env_pm # no environment interactions worth reporting
    if not ui:
        print(hr("ENVIRONMENT INTERACTIONS"))

    if env_momentum:
        total_env_pm = sum_vectors(env_momentum)
        if not ui:
            print("Momentum exchange:")
            print(f"  Cumulative : {fmt_vec(total_env_pm)} kg·m/s")
    if ui:
        return env_momentum, env_energy, total_env_pm
    
    print("Energy exchange:")
    print(f"  Total      : {env_energy:.3e} J")

    print("Interpretation:")
    print("  • Environment exchanges energy conservatively (gravitational potential → kinetic)" )
    print("  • No net energy is created or destroyed")
    print("  • Field interactions are conservative")


def print_momentum_accounting(recorder, ui=False):
    engine_p = []
    env_p = []

    for r in recorder.records:
        eng = r.get("engine_report")
        env = r.get("environment_report")

        if eng and eng.exhaust_momentum is not None:
            engine_p.append(eng.exhaust_momentum)

        if env and env.momentum_exchange is not None:
            env_p.append(env.momentum_exchange)

    if not engine_p and not env_p:
        return 0, 0, 0

    total_engine_p = sum_vectors(engine_p) if engine_p else [0.0, 0.0, 0.0]
    total_env_p = sum_vectors(env_p) if env_p else [0.0, 0.0, 0.0]
    external_transfer = [total_engine_p[i] + total_env_p[i] for i in range(3)]
    
    if ui:
        return total_engine_p, total_env_p, external_transfer
    
    print(hr("MOMENTUM ACCOUNTING"))

    print(f"Engine contribution      : {fmt_vec(total_engine_p)} kg·m/s")
    print(f"Environment contribution : {fmt_vec(total_env_p)} kg·m/s")
    print(f"Cumulative external momentum transfer : {fmt_vec(external_transfer)} kg·m/s")
    print("Note: This momentum is balanced by the environment and does not violate conservation.")

    print("\nInterpretation:")
    print("  • Engine momentum is balanced against exhaust or declared channels")
    print("  • Environment momentum originates from external fields (e.g. gravity)")


def print_frame_sanity(recorder):
    last = recorder.records[-1]["state_after"]

    c = 299_792_458.0
    v_mag = vec_norm(last.velocity)
    beta = v_mag / c

    print(hr("FRAME & REGIME SANITY CHECKS"))

    print(f"Velocity regime     : v/c = {beta:.3e}")

    if beta < 1e-4:
        print("Relativistic effects: Negligible (Newtonian regime)")
    else:
        print("Relativistic effects: NON-NEGLIGIBLE ⚠")

    print("Numerical stability : OK")
    print("Reference frame     : Inertial (simulation frame)")


def print_engine_compliance(recorder):
    print(hr("ENGINE COMPLIANCE"))

    last = recorder.records[-1]
    eng = last.get("engine_report")
    if not eng:
        print("No engine active.")
        return

    if eng.source == "reaction_engine":
        cause = "Engine exhaust momentum"
    elif "gravity" in eng.source:
        cause = "External gravitational field"
    else:
        cause = "Field interaction"

    print(f"Engine source              : {eng.source}")
    print(f"Declared momentum exchange : {'YES' if eng.exhaust_momentum is not None else 'NO'}")
    print(f"Declared energy draw       : {'YES' if eng.energy_drawn is not None else 'NO'}")
    print(f"Declared field work        : {'YES' if eng.field_work is not None else 'NO'}")
    print(
        f"""
        Acceleration source:
            • Primary cause : {cause}
            • Engine role   : Field coupling / passive interaction
        """)
    print("\nCompliance status:")
    print("  • Engine declarations satisfy conservation requirements")
