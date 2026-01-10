"""
Central reasoning engine.
Determines whether a simulation step is physically legitimate
or violates closed-system conservation laws.
"""
from noron.diagnostics import (
    check_momentum_sink,
    check_energy_payment,
    check_engine_agency,
    FraudFlags,
    vector_norm
)

def detect_closed_system_fraud(step_record):
    flags = FraudFlags()
    reasons = []

    # --- Required inputs ---
    sb = step_record["state_before"]
    sa = step_record["state_after"]

    engine_report = step_record["engine_report"]
    environment_report = step_record.get("environment_report")

    # Pull conservation explanation (field work lives here)
    conservation = step_record.get("conservation", {})
    field_energy = conservation.get("explain", {}).get("field_energy", None)

    # -----------------------------
    # Momentum fraud check
    # -----------------------------
    bad, reason = check_momentum_sink(
        sb,
        sa,
        engine_report,
        environment_report
    )

    if bad:
        flags.momentum_without_sink = True
        reasons.append(reason)

    # -----------------------------
    # Energy fraud check
    # -----------------------------
    bad, reason = check_energy_payment(
        sb,
        sa,
        engine_report,
        environment_report,
        field_energy  # critical
    )
 
    if bad:
        flags.energy_without_work = True
        reasons.append(reason)

    bad, reason = check_engine_agency(sb, sa, engine_report, environment_report)
    if bad:
        flags.unjustified_engine_activity = True
        reasons.append(reason)

    if flags.energy_without_work:
        verdict = "FAIL"
        reasons.append("Field acceleration without declared field work or momentum exchange")

    # -----------------------------
    # Final verdict
    # -----------------------------
    verdict = "FAIL" if (
        flags.momentum_without_sink
        or flags.energy_without_work
        or flags.unpaid_mass_energy
        or flags.unjustified_engine_activity
    ) else "PASS"

    return {
        "verdict": verdict,
        "flags": {
            "momentum_without_sink": flags.momentum_without_sink,
            "energy_without_work": flags.energy_without_work,
            "unpaid_mass_energy": flags.unpaid_mass_energy,
            "unjustified_engine_activity": flags.unjustified_engine_activity,
        },
        "reasons": reasons,
    }


def detect_field_fraud(step_record):
    flags = FraudFlags()

    accelerated = step_record.delta_v_magnitude > 0
    engine_active = step_record.engine_report is not None

    if accelerated and engine_active:
        er = step_record.engine_report

        paid_energy = er.field_work > 0
        paid_momentum = (
            hasattr(er, "field_momentum") and
            vector_norm(er.field_momentum) > 0
        )
        has_exhaust = vector_norm(er.exhaust_momentum) > 0

        if not (paid_energy or paid_momentum or has_exhaust):
            flags.energy_without_work = True

    return flags
