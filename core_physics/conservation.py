class Conservation:

    def judge(self, state, delta_p, delta_e, delta_m):
        explanation = {}

        # ---------- Energy ----------
        energy_required = abs(delta_e)
        energy_available = state.energy
        energy_residual = energy_required - energy_available

        energy_ok = energy_residual <= 0
        explanation["energy"] = {
            "balanced": energy_ok,
            "required": energy_required,
            "available": energy_available,
        }

        # ---------- Mass ----------
        if delta_m == 0:
            mass_ok = True
            mass_residual = 0.0
            explanation["mass"] = {"valid": True}
        else:
            if state.can_exchange_mass:
                mass_ok = True
                mass_residual = 0.0
                explanation["mass"] = {"valid": True}
            else:
                mass_ok = False
                mass_residual = abs(delta_m)
                explanation["mass"] = {
                    "valid": False,
                    "explain": "Mass exchange not permitted"
                }

        # ---------- Momentum ----------
        if delta_p == 0:
            momentum_ok = True
            momentum_residual = [0.0, 0.0, 0.0]
            explanation["momentum"] = {"valid": True}

        else:
            if delta_m != 0 and state.can_exchange_mass:
                momentum_ok = True
                momentum_residual = [0.0, 0.0, 0.0]
                explanation["momentum"] = {"valid": True, "sink": "mass"}

            elif state.can_exchange_radiation:
                momentum_ok = True
                momentum_residual = [0.0, 0.0, 0.0]
                explanation["momentum"] = {"valid": True, "sink": "radiation"}

            elif state.can_exchange_fields:
                momentum_ok = True
                momentum_residual = [0.0, 0.0, 0.0]
                explanation["momentum"] = {"valid": True, "sink": "field"}

            else:
                momentum_ok = False
                momentum_residual = delta_p
                explanation["momentum"] = {
                    "valid": False,
                    "explain": "No permitted momentum exchange mechanism"
                }

        # ---------- Final verdict ----------
        valid = energy_ok and mass_ok and momentum_ok

        return {
            "valid": valid,

            # Residuals (ALWAYS PRESENT)
            "energy_residual": energy_residual,
            "mass_residual": mass_residual,
            "momentum_residual": momentum_residual,

            "explain": explanation
        }
