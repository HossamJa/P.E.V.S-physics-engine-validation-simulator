"""
Closed-system fraud detection logic.
This module NEVER applies forces or alters state.
It only inspects before/after states and declared exchanges.
"""

import math

ENERGY_EPS = 1e-6


# -----------------------------
# Utilities
# -----------------------------

def vector_norm(v):
    return math.sqrt(sum(x * x for x in v))

def vector_delta(a, b):
    return [a[i] - b[i] for i in range(3)]

def approx_zero(x, tol=ENERGY_EPS):
    return abs(x) < tol

def is_external_field(engine, env):
    return (
        env
        and env.channel == "field"
        and env.source != engine.source
    )

# -----------------------------
# Fraud flags
# -----------------------------

class FraudFlags:
    def __init__(self):
        self.flags = []
        self.explanations = []

    def add(self, name, explanation):
        self.flags.append(name)
        self.explanations.append(explanation)

    def any(self):
        return bool(self.flags)


# -----------------------------
# Core checks
# -----------------------------

def check_momentum_sink(state_before, state_after, engine, env):
    """
    Flags momentum creation without a sink.
    """
    dp = vector_norm(vector_delta(
        state_after.momentum,
        state_before.momentum
    ))

    # External conservative field supplies work directly
    if is_external_field(engine, env):
        return False, "Work supplied by external field"

    if dp < ENERGY_EPS:
        return False, "No net momentum change"

    # Reaction exhaust
    if vector_norm(engine.exhaust_momentum) > ENERGY_EPS:
        return False, "Momentum balanced by exhaust"

    # Environment momentum must declare a valid channel
    if env and vector_norm(env.momentum_exchange) > ENERGY_EPS:
        if env.channel in ("gravity", "em", "constraint"):
            return False, f"Momentum balanced by environment ({env.channel})"

    return True, "Momentum created without a valid sink"


def check_energy_payment(state_before, state_after, engine, env):
    """
    Flags KE increase without energy payment.
    Conservative field work is allowed IF conservation approved it.
    """
    delta_E = (
        state_after.kinetic_energy
        + state_after.gravitational_potential_energy
        - state_before.kinetic_energy
        - state_before.gravitational_potential_energy
    )

    if approx_zero(delta_E):
        return False, "Mechanical energy conserved"

    paid = 0.0

    # External conservative field supplies work directly
    if is_external_field(engine, env):
        return False, "Work supplied by external field"
    
    if engine.channel == "ship":
        return False, None

    if engine.radiation_energy > 0 and engine.energy_drawn > 0:
        return False, None

    # Engine internal source
    if engine.source == "internal":
        paid += engine.energy_drawn

    if env and env.channel == "field" and env.source != engine.source:
        # External field supplied the energy
        return False, None
    
    # Engine using environment field
    if engine.source == "environment":
        if not env:
            return True, "Engine draws from environment but no EnvironmentReport"

        if engine.channel != env.channel:
            return True, "Engine/environment channel mismatch"

        paid += engine.field_work

    # Environment-only effects (gravity, EM, etc.)
    if env:
        paid += env.energy_exchange

    if approx_zero(delta_E + paid):
        return False, "Energy correctly paid"

    return True, "Energy increase without matching ledger payment"


def check_mass_energy_accounting(state_before, state_after, engine, env):
    """
    Flags momentum/energy change without mass, energy, exhaust, or field exchange.
    """
    dp = vector_norm(vector_delta(
        state_after.momentum,
        state_before.momentum
    ))

    dKE = state_after.kinetic_energy - state_before.kinetic_energy

    if approx_zero(dp) and approx_zero(dKE):
        return False, "No momentum or energy change"

    no_engine = (
        approx_zero(engine.mass_spent)
        and approx_zero(engine.energy_drawn)
        and approx_zero(vector_norm(engine.exhaust_momentum))
        and approx_zero(engine.field_work)
    )

    no_env = (
        env is None or (
            approx_zero(env.energy_exchange)
            and approx_zero(vector_norm(env.momentum_exchange))
            and approx_zero(env.field_work)
        )
    )

    if no_engine and no_env:
        return True, "State changed without engine or environment accounting"

    return False, "Mass/energy accounting valid"


def check_engine_agency(state_before, state_after, engine, env):

    dv = vector_norm(vector_delta(
        state_after.velocity,
        state_before.velocity
    ))

    # External conservative field supplies work directly
    if is_external_field(engine, env):
        return False, "Work supplied by external field"

    if dv < ENERGY_EPS:
        return False, "No acceleration"

    if not engine.active:
        return False, "Acceleration attributed to environment"

    contributed = (
        vector_norm(engine.exhaust_momentum) > ENERGY_EPS
        or abs(engine.energy_drawn) > ENERGY_EPS
        or abs(engine.mass_spent) > ENERGY_EPS
        or abs(engine.field_work) > ENERGY_EPS
    )

    if not contributed:
        return True, "Engine active but provides no causal contribution"

    # Field engines must have environment confirmation
    if engine.channel == "field":
        if not env:
            return True, "Field engine active but no EnvironmentReport"

        if engine.source == "environment" and env.channel != engine.channel:
            return True, "Field channel mismatch"

    return False, "Engine agency valid"


# -----------------------------
# Sanity checks
# -----------------------------

# Momentum growth vs applied force (Impulse sanity)
def check_impulse_consistency(state_before, state_after, engine, env, dt):
    """
    Physics rule:    ∆p ≈ F * ∆t
    If momentum changes without sufficient impulse, something is wrong.
    """

    dp = vector_norm(vector_delta(
        state_after.momentum,
        state_before.momentum
    ))

    declared = vector_norm(engine.exhaust_momentum)

    if env:
        declared += vector_norm(env.momentum_exchange)

    # Allow small numerical error
    if dp > declared * 1.1:
        return True, "Momentum exceeds declared impulse"

    return False, "Impulse consistent"


# Velocity vs energy consistency (KE sanity)
def check_velocity_energy_consistency(state):
    """
    Physics rule: KE = p² / 2*m
    Momentum and kinetic energy must agree.

    """

    p2 = vector_norm(state.momentum) ** 2
    ke_from_p = p2 / (2 * state.mass)

    if abs(ke_from_p - state.kinetic_energy) > ENERGY_EPS * max(1, ke_from_p):
        return True, "Momentum/energy mismatch"

    return False, "Momentum-energy consistent"


# Acceleration vs work sanity (Work–energy theorem)
def check_work_energy_balance(state_before, state_after, engine, env):
    """
    Physics rule:   W = ∆KE
    If KE increases, someone paid.
    """
    
    delta_ke = state_after.kinetic_energy - state_before.kinetic_energy

    paid = engine.energy_drawn

    if engine.channel == "ship" or engine.radiation_energy > 0:
        return False, None
    
    # External conservative field supplies work directly
    if is_external_field(engine, env):
        return False, "Work supplied by external field"

    if hasattr(engine, "exhaust_energy"):
        paid -= engine.exhaust_energy

    if hasattr(engine, "radiation_energy"):
        paid -= engine.radiation_energy

    if env:
        paid += env.field_work

    if abs(delta_ke - paid) > ENERGY_EPS * max(1, abs(delta_ke)):
        return True, "Work-energy violation"

    return False, "Work-energy balanced"


# -----------------------------
# Relativity warning
# -----------------------------

C = 299_792_458

def check_relativistic_warning(state):
    v = vector_norm(state.velocity)
    beta = v / C

    if beta > 0.1:
        return True, f"Relativistic regime entered (v={beta:.2f}c)"

    return False, "Newtonian regime"
