class Recorder:
    """
    Records the evolution of State over time.
    Observer only — never modifies physics.
    """

    def __init__(self):
        self.records = []
        self.initial_mechanical_energy = None

    def _sum_effects(self, effects):
        """Safely aggregate a list of EngineEffect"""
        dp = [0.0, 0.0, 0.0]
        de = 0.0
        dm = 0.0

        for e in effects or []:
            for i in range(3):
                dp[i] += e.delta_p[i]
            de += e.delta_e
            dm += e.delta_m

        return dp, de, dm


    def record(
        self,
        state,
        engine_effects,
        env_effects,
        environment,        
        verdict,
        dt,
        step_index
    ):
        # ---------- Mechanical energy ----------
        kinetic_energy = state.kinetic_energy

        g = environment.gravity
        y = state.position[1]
        potential_energy = -state.mass * g[1] * y

        total_mechanical_energy = kinetic_energy + potential_energy

        if self.initial_mechanical_energy is None:
            self.initial_mechanical_energy = total_mechanical_energy

        mechanical_energy_drift = (
            total_mechanical_energy - self.initial_mechanical_energy
        )

        # ---------- Aggregate effects ----------
        eng_dp, eng_de, eng_dm = self._sum_effects(engine_effects)
        env_dp, env_de, env_dm = self._sum_effects(env_effects)

        total_dp = [
            eng_dp[i] + env_dp[i] for i in range(3)
        ]
        total_de = eng_de + env_de
        total_dm = eng_dm + env_dm

        # ---------- Record ----------
        self.records.append({
            "step": step_index,
            "time": state.time,
            "dt": dt,

            "position": state.position.copy(),
            "velocity": state.velocity.copy(),
            "momentum": state.momentum.copy(),

            "mass": state.mass,
            "stored_energy": state.energy,

            "kinetic_energy": kinetic_energy,
            "potential_energy": potential_energy,
            "total_mechanical_energy": total_mechanical_energy,
            "mechanical_energy_change_due_to_field": mechanical_energy_drift,

            "engine_effect": {
                "delta_p": eng_dp.copy(),
                "delta_e": eng_de,
                "delta_m": eng_dm,
            },
            "environment_effect": {
                "delta_p": env_dp.copy(),
                "delta_e": env_de,
                "delta_m": env_dm,
            },
            "total_effect": {
                "delta_p": total_dp.copy(),
                "delta_e": total_de,
                "delta_m": total_dm,
            },

            "conservation": verdict,
        })

    def analyze_drift(self):
        momentum_drift = [0.0, 0.0, 0.0]
        energy_drift = 0.0
        mass_drift = 0.0

        mech_drifts = []

        for r in self.records:
            res = r["conservation"]

            energy_drift += res.get("energy_residual", 0.0)
            mass_drift += res.get("mass_residual", 0.0)

            p = res.get("momentum_residual", [0.0, 0.0, 0.0])
            for i in range(3):
                momentum_drift[i] += p[i]

            mech_drifts.append(r["mechanical_energy_change_due_to_field"])

        return {
            "energy_drift": energy_drift,
            "mass_drift": mass_drift,
            "momentum_drift": momentum_drift,
            "max_mechanical_energy_drift": max(mech_drifts) if mech_drifts else 0.0,
            "min_mechanical_energy_drift": min(mech_drifts) if mech_drifts else 0.0,
            "final_mechanical_energy_drift": mech_drifts[-1] if mech_drifts else 0.0,
        }
