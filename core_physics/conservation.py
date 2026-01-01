class Conservation:

    def judge(self, state, delta_p, delta_e, delta_m):
        explanation = {}

        # 1. Momentum balance check
        m_check = self.momentum_balance_check(state, delta_p, delta_m)
        if not m_check["valid"]:
            return {"valid": False, "explain": m_check}

        # 2. Energy availability
        energy = self.energy_availability_check(state, delta_e)
        explanation["energy"] = energy
        if not energy["balanced"]:
            return {"valid": False, "explain": explanation}

        # 3. Mass flow validity
        mass = self.mass_flow_validity_check(state, delta_p, delta_m)
        explanation["mass"] = mass
        if not mass["valid"]:
            return {"valid": False, "explain": explanation}

        # If all checks pass
        return {"valid": True, "explain": explanation}

    def energy_availability_check(self, state, delta_e):
        return {
            "balanced": abs(delta_e) <= state.energy,
            "required": abs(delta_e),
            "available": state.energy
        }

    def mass_flow_validity_check(self, state, delta_p, delta_m):
        # No mass change claimed → OK unless mass exchange is required
        if delta_m == 0:
            return {"valid": True}

        # Mass change claimed but not allowed
        if not state.can_exchange_mass:
            return {
                "valid": False,
                "explain": "Mass exchange not permitted by environment"
            }

        return {"valid": True}


    def momentum_balance_check(self, state, delta_p, delta_m):
        if delta_p == 0:
            return {"valid": True}

        if delta_m != 0 and state.can_exchange_mass:
            return {"valid": True, "sink": "mass"}

        if state.can_exchange_radiation:
            return {"valid": True, "sink": "radiation"}

        if state.can_exchange_fields:
            return {"valid": True, "sink": "field"}

        return {
            "valid": False,
            "explain": "No permitted momentum exchange mechanism"
        }

