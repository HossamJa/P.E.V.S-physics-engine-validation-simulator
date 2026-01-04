# Utility functions
def is_zero_vector(v, eps=1e-9):
    return all(abs(x) < eps for x in v)

def vadd(a, b):
    return [a[i] + b[i] for i in range(3)]

class Conservation:
    """
    Judges whether a set of proposed effects respects
    conservation of energy, mass, and momentum.
    """

    def judge(self, state, effects, environment):
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
            if state.can_exchange_fields and not is_zero_vector(field_dp):
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

        # Final verdict
        valid = energy_ok and mass_ok and momentum_ok

        return {
            "valid": valid,

            # Residuals (ALWAYS PRESENT)
            "energy_residual": energy_residual,
            "mass_residual": mass_residual,
            "momentum_residual": momentum_residual,

            "explain": explanation,
        }
