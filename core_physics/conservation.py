class Conservation:

    def judge(self, state, delta_p, delta_e, delta_m):
        explanation = {}

        # 1. Reactionless kill switch (V1 mass-only world)
        if self.reactionless_kill_switch(delta_p, delta_m, delta_e):
            return {
                "valid": False,
                "explain": {"reason": "Reactionless momentum claim (V1)"}
            }

        # 2. Energy availability
        energy = self.energy_availability_check(state, delta_e)
        explanation["energy"] = energy
        if not energy["balanced"]:
            return {"valid": False, "explain": explanation}

        # 3. Mass flow validity
        mass = self.mass_flow_validity_check(delta_p, delta_m)
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

    def mass_flow_validity_check(self, delta_p, delta_m):
        if delta_p != 0 and delta_m == 0:
            return {"valid": False, "explain": "No mass-based momentum sink (V1)"}
        return {"valid": True}

    def reactionless_kill_switch(self, delta_p, delta_m, delta_e):
        return delta_p != 0 and delta_m == 0
