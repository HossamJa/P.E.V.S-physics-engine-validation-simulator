"""
Closed-system fraud detection logic.
This module NEVER applies forces or alters state.
It only inspects before/after states and declared exchanges.
"""

import math


# -----------------------------
# Utility helpers
# -----------------------------

def vector_norm(v):
    return math.sqrt(sum(x * x for x in v))


def vector_delta(v_after, v_before):
    return [v_after[i] - v_before[i] for i in range(3)]


def approx_zero(x, tol=1e-9):
    return abs(x) < tol


ENERGY_EPS = 1e-6


# -----------------------------
# Fraud flags container
# -----------------------------

class FraudFlags:
    def __init__(self):
        self.momentum_without_sink = False
        self.energy_without_work = False
        self.unpaid_mass_energy = False
        self.unjustified_engine_activity = False

        self.explanations = []

    def add(self, flag_name, explanation):
        setattr(self, flag_name, True)
        self.explanations.append(explanation)

    def any(self):
        return (
            self.momentum_without_sink
            or self.energy_without_work
            or self.unpaid_mass_energy
        )


# -----------------------------
# Core fraud detectors
# -----------------------------

def check_momentum_sink(state_before, state_after, engine_report, env_report):
    """
    Flags momentum creation without a sink.
    """

    dp = vector_delta(
        state_after.momentum,
        state_before.momentum
    )

    if vector_norm(dp) < ENERGY_EPS:
        return False, "No net momentum change"

    if vector_norm(engine_report.exhaust_momentum) > ENERGY_EPS:
        return False, "Momentum balanced by exhaust"

    if env_report and vector_norm(env_report.momentum_exchange) > ENERGY_EPS:
        return False, "Momentum balanced by environment"

    return True, "Momentum gained with no exhaust or field sink"


def check_energy_payment(
    state_before,
    state_after,
    engine_report,
    env_report,
    field_energy_explain
):
    """
    Flags KE increase without energy payment.
    Conservative field work is allowed IF conservation approved it.
    """

    delta_mech = (
        (state_after.kinetic_energy + state_after.gravitational_potential_energy)
        - (state_before.kinetic_energy + state_before.gravitational_potential_energy)
    )

    if abs(delta_mech) < ENERGY_EPS:
        return False, "Mechanical energy conserved by field"

    # Engine payment
    paid = engine_report.energy_drawn

    # Environment energy exchange (non-field)
    if env_report:
        paid += env_report.energy_exchange
    
    if field_energy_explain and field_energy_explain.get("source") == "environment":
        return False, 
    
    # Field work approved by conservation?
    if field_energy_explain and field_energy_explain.get("valid", False):
        return False, "Energy paid by conservative field"

    # Bellow assumes:
        # engine_drawn is negative
        # env_exchange is negative when environment loses energy

    if abs(delta_mech + paid) < ENERGY_EPS:
        return False, "Energy conserved"

    return True, "Kinetic energy increased without engine or field payment"


def check_mass_energy_accounting(
    state_before,
    state_after,
    engine_report,
    env_report
):
    """
    Flags momentum/energy change without mass, energy, exhaust, or field exchange.
    """

    dp = vector_norm(
        vector_delta(
            state_after.momentum,
            state_before.momentum
        )
    )

    dKE = (
        state_after.kinetic_energy
        - state_before.kinetic_energy
    )

    if approx_zero(dp) and approx_zero(dKE):
        return False, "No momentum or energy change"

    if (
        approx_zero(engine_report.mass_spent)
        and approx_zero(engine_report.energy_drawn)
        and approx_zero(vector_norm(engine_report.exhaust_momentum))
        and (env_report is None or approx_zero(env_report.energy_exchange))
    ):
        return True, (
            "Momentum or energy changed with no mass loss, "
            "energy draw, exhaust, or environment exchange"
        )

    return False, "Mass/energy accounting valid"


def check_engine_agency(state_before, state_after, engine_report, env_report):
    
    assert hasattr(engine_report, "active"), \
    "EngineReport must declare active=True/False"
    
    dv = vector_delta(
        state_after.velocity,
        state_before.velocity
    )

    if vector_norm(dv) < ENERGY_EPS:
        return False, "No acceleration"

    # Only care if engine claims activity
    if not engine_report.active:
        return False, "Acceleration due to environment"

    if engine_report.active and engine_report.field_work != 0:
        if not env_report:
            return True, "Field work claimed but no environment interaction"
    
    if engine_report.field_work != 0 and vector_norm(env_report.momentum_exchange) < ENERGY_EPS:
        return True, "Field work with no momentum exchange"

    engine_contributed  = (
        vector_norm(engine_report.exhaust_momentum) > ENERGY_EPS
        or abs(engine_report.energy_drawn) > ENERGY_EPS
        or abs(engine_report.mass_spent) > ENERGY_EPS
        or abs(engine_report.field_work) > ENERGY_EPS
    )

    if not engine_contributed:
        return True, "Engine active but provides no causal contribution"

    return False, "Engine agency plausible"
