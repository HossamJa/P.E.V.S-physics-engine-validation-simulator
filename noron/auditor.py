"""
Central reasoning engine.
Aggregates diagnostic checks and issues verdicts.
This module NEVER interprets physics.
"""

from noron.diagnostics import (
    FraudFlags,

    check_momentum_sink,
    check_energy_payment,
    check_mass_energy_accounting,
    check_engine_agency,

    check_impulse_consistency,
    check_velocity_energy_consistency,
    check_work_energy_balance,
    check_relativistic_warning,
)

def detect_closed_system_fraud(step_record):
    flags = FraudFlags()
    reasons = []

    # -----------------------------
    # Required inputs
    # -----------------------------
    sb = step_record["state_before"]
    sa = step_record["state_after"]
    dt = step_record["dt"]

    engine = step_record["engine_report"]
    env = step_record.get("environment_report")

    # -----------------------------
    # Core conservation checks
    # -----------------------------

    bad, reason = check_momentum_sink(sb, sa, engine, env)
    if bad:
        flags.add("momentum_without_sink", reason)

    bad, reason = check_energy_payment(sb, sa, engine, env)
    if bad:
        flags.add("energy_without_work", reason)

    bad, reason = check_mass_energy_accounting(sb, sa, engine, env)
    if bad:
        flags.add("unpaid_mass_energy", reason)

    bad, reason = check_engine_agency(sb, sa, engine, env)
    if bad:
        flags.add("unjustified_engine_activity", reason)

    # -----------------------------
    # Frame sanity checks
    # -----------------------------

    bad, reason = check_impulse_consistency(sb, sa, engine, env, dt)
    if bad:
        flags.add("momentum_without_sink", reason)

    bad, reason = check_velocity_energy_consistency(sa)
    if bad:
        flags.add("energy_without_work", reason)

    bad, reason = check_work_energy_balance(sb, sa, engine, env)
    if bad:
        flags.add("energy_without_work", reason)

    # -----------------------------
    # Relativistic warning (non-fatal)
    # -----------------------------

    warn, note = check_relativistic_warning(sa)
    if warn:
        reasons.append(note)

    # -----------------------------
    # Final verdict
    # -----------------------------

    verdict = "FAIL" if flags.any() else "PASS"

    return {
        "verdict": verdict,
        "flags": flags.flags,
        "reasons": flags.explanations + reasons,
    }


# --------------------------------------------------
# Optional: Field-specific fraud detector (V2.3)
# --------------------------------------------------

def detect_field_fraud(step_record):
    """
    Specialized detector for illegal field propulsion.
    Delegates logic to diagnostics via engine/environment ledgers.
    """

    flags = FraudFlags()

    sb = step_record["state_before"]
    sa = step_record["state_after"]

    engine = step_record["engine_report"]
    env = step_record.get("environment_report")

    dv = (
        sa.velocity[0] - sb.velocity[0],
        sa.velocity[1] - sb.velocity[1],
        sa.velocity[2] - sb.velocity[2],
    )

    accelerated = sum(x * x for x in dv) > 0

    if accelerated and engine.active:
        bad, reason = check_energy_payment(sb, sa, engine, env)
        if bad:
            flags.add("energy_without_work", reason)

        bad, reason = check_engine_agency(sb, sa, engine, env)
        if bad:
            flags.add("unjustified_engine_activity", reason)

    return {
        "flags": flags.flags,
        "reasons": flags.explanations,
    }
