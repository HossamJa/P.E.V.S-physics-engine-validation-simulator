class Recorder:
    """
    Records the evolution of State over time.
    Observer only — never modifies physics.
    """

    def __init__(self):
        self.records = []

    def record(
        self,
        state,
        engine_effect,
        env_effect,
        total_effect,
        verdict,
        dt,
        step_index
    ):
        self.records.append({
                    "step": step_index,
                    "time": state.time,
                    "dt": dt,

                    "position": state.position.copy(),
                    "velocity": state.velocity.copy(),
                    "momentum": state.momentum.copy(),
                    "kinetic_energy": state.kinetic_energy,

                    "mass": state.mass,
                    "energy": state.energy,

                    "engine_effect": {
                        "delta_p": engine_effect.delta_p,
                        "delta_E": engine_effect.delta_e,
                        "delta_m": engine_effect.delta_m,
                    },
                    "environment_effect": {
                        "delta_p": env_effect.delta_p,
                        "delta_E": env_effect.delta_e,
                        "delta_m": env_effect.delta_m,
                    },
                    "total_effect": {
                        "delta_p": total_effect.delta_p,
                        "delta_E": total_effect.delta_e,
                        "delta_m": total_effect.delta_m,
                    },

                    "conservation": verdict,
                })

    def analyze_drift(self):
        energy_drift = sum(r["conservation"]["energy_residual"] for r in self.records)
        mass_drift = sum(r["conservation"]["mass_residual"] for r in self.records)

        momentum_drift = [0, 0, 0]
        for r in self.records:
            p = r["conservation"]["momentum_residual"]
            momentum_drift = [
                momentum_drift[i] + p[i] for i in range(3)
            ]

        return {
            "energy_drift": energy_drift,
            "mass_drift": mass_drift,
            "momentum_drift": momentum_drift,
        }
