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

        had_field_effect = False

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
                had_field_effect = True

        had_field_effect = not is_zero_vector(field_dp)

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

        # ======================
        # Field Energy Conservation (V2.3.5 FINAL)
        # ======================

        if had_field_effect:
            # --- ONLY conservative external fields enter here ---

            dp = field_dp

            # Velocity BEFORE field impulse
            v_before = [
                state.momentum[i] / state.mass
                for i in range(3)
            ]

            # Velocity AFTER field impulse
            v_after = [
                (state.momentum[i] + dp[i]) / state.mass
                for i in range(3)
            ]

            # Midpoint velocity
            v_mid = [(v_before[i] + v_after[i]) * 0.5 for i in range(3)]

            # Displacement during dt
            dx = [v_mid[i] * dt for i in range(3)]

            # Force approximation
            F = [dp[i] / dt for i in range(3)]

            # Work done by field
            work = sum(F[i] * dx[i] for i in range(3))

            # Kinetic energy change
            ke_before = kinetic_energy(state.momentum, state.mass)
            ke_after  = kinetic_energy(
                [state.momentum[i] + dp[i] for i in range(3)],
                state.mass
            )
            delta_ke = ke_after - ke_before

            FIELD_ENERGY_EPS = 1e-6
            energy_field_ok = abs(delta_ke - work) <= FIELD_ENERGY_EPS

            if not energy_field_ok:
                energy_ok = False
                explanation["field_energy"] = {
                    "valid": False,
                    "delta_ke": delta_ke,
                    "work": work,
                    "residual": delta_ke - work,
                    "explain": "Conservative field violated work–energy consistency"
                }
            else:
                explanation["field_energy"] = {
                    "valid": True,
                    "delta_ke": delta_ke,
                    "work": work,
                    "residual": delta_ke - work
                }

        else:
            # No external conservative field involved
            energy_field_ok = True
            explanation["field_energy"] = {
                "valid": True,
                "skipped": "No external conservative field interaction"
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
