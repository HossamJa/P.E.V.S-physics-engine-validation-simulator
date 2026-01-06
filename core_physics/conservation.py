# Utility functions
def is_zero_vector(v, eps=1e-9):
    return all(abs(x) < eps for x in v)

def vadd(a, b):
    return [a[i] + b[i] for i in range(3)]

# Helpers 
def kinetic_energy(momentum, mass):
    if mass <= 0:
        return 0.0
    return sum(p*p for p in momentum) / (2 * mass)

def potential_energy(position, environment, mass):
    # Example: Newtonian gravity from central body
    if not environment.has_gravity:
        return 0.0

    r = max(environment.distance_to_gravity_source(position), environment.r_min)

    if r == 0:
        return 0.0

    G = environment.G
    M = environment.gravity_mass
    return -G * M * mass / r


class Conservation:
    """
    Judges whether a set of proposed effects respects
    conservation of energy, mass, and momentum.
    """

    def judge(self, state, effects, environment, dt):
        explanation = {}

        # Accumulators
        ship_dp = [0.0, 0.0, 0.0]
        ship_de = 0.0
        ship_dm = 0.0

        exhaust_dp = [0.0, 0.0, 0.0]
        field_dp = [0.0, 0.0, 0.0]

        # --- Collect effects ---
        for effect in effects:
            if effect.channel == "ship":
                ship_dp = vadd(ship_dp, effect.delta_p)
                ship_de += effect.delta_e
                ship_dm += effect.delta_m

            elif effect.channel == "exhaust":
                exhaust_dp = vadd(exhaust_dp, effect.delta_p)

            elif effect.channel == "field":
                field_dp = vadd(field_dp, effect.delta_p)


        # ======================
        # Energy conservation
        # ======================

        # Only ship energy draws from stored energy
        energy_required = -min(0.0, ship_de)

        if energy_required <= state.energy:
            energy_ok = True
            energy_residual = 0.0
        else:
            energy_ok = False
            energy_residual = energy_required - state.energy

        explanation["energy"] = {
            "balanced": energy_ok,
            "required": energy_required,
            "available": state.energy,
        }

        # ======================
        # Mass conservation
        # ======================

        if ship_dm == 0.0:
            mass_ok = True
            mass_residual = 0.0
        else:
            if state.can_exchange_mass:
                mass_ok = True
                mass_residual = 0.0
            else:
                mass_ok = False
                mass_residual = abs(ship_dm)

        explanation["mass"] = {
            "valid": mass_ok,
            "delta_m": ship_dm,
        }

        # ======================
        # Momentum conservation
        # ======================

        # Internal momentum (ship + exhaust)
        internal_dp = vadd(ship_dp, exhaust_dp)

        if is_zero_vector(internal_dp):
            # Ship momentum fully balanced by exhaust
            momentum_ok = True
            momentum_residual = [0.0, 0.0, 0.0]
            explanation["momentum"] = {
                "valid": True,
                "balanced_against": "exhaust",
            }

        else:
            if state.can_exchange_fields:
                # Momentum exchanged with external field (gravity, EM, spacetime)
                momentum_ok = True
                momentum_residual = [0.0, 0.0, 0.0]
                explanation["momentum"] = {
                    "valid": True,
                    "balanced_against": "external_field",
                }
            else:
                # Reactionless momentum creation
                momentum_ok = False
                momentum_residual = internal_dp.copy()
                explanation["momentum"] = {
                    "valid": False,
                    "residual": internal_dp,
                    "explain": "Unbalanced momentum without exhaust or external field",
                }

        if not is_zero_vector(field_dp):
            # --- FIELD ENERGY CONSERVATION ONLY ---

            momentum_before = state.momentum

            momentum_after_field = [
                state.momentum[i] + field_dp[i]
                for i in range(3)
            ]

            ke_before = kinetic_energy(momentum_before, state.mass)
            ke_after  = kinetic_energy(momentum_after_field, state.mass)

            # Position drift due ONLY to field-induced velocity
            v_before = [momentum_before[i] / state.mass for i in range(3)]
            v_after  = [momentum_after_field[i] / state.mass for i in range(3)]
            v_mid    = [(v_before[i] + v_after[i]) * 0.5 for i in range(3)]

            predicted_position = [
                state.position[i] + v_mid[i] * dt
                for i in range(3)
            ]

            pe_before = potential_energy(state.position, environment, state.mass)
            pe_after  = potential_energy(predicted_position, environment, state.mass)

            # Gravity does work: KE ↑ while PE ↓, total must remain constant
            delta_ke = ke_after - ke_before
            delta_pe = pe_after - pe_before

            energy_field_ok = abs(delta_ke + delta_pe) < 1e-6

            explanation["field_energy"] = {
                "valid": energy_field_ok,
                "delta_ke": delta_ke,
                "delta_pe": delta_pe,
                "sum": delta_ke + delta_pe,
            }

        else:
            energy_field_ok = True
            explanation["field_energy"] = {
                "valid": True,
                "skipped": "No field momentum exchange",
                "delta_ke": 0.0,
                "delta_pe": 0.0,
                "sum": 0.0,
            }
        # Final verdict
        valid = energy_ok and mass_ok and momentum_ok and energy_field_ok

        return {
            "valid": valid,

            # Residuals (ALWAYS PRESENT)
            "energy_residual": energy_residual,
            "mass_residual": mass_residual,
            "momentum_residual": momentum_residual,

            "explain": explanation,
        }
