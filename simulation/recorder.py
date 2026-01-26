class Recorder:
    """
    Records the evolution of State over time.
    Observer only — never modifies physics.
    """

    def __init__(self):
        self.records = []
        self.initial_mechanical_energy = None

    # Helper
    def _snapshot_state(self, state):
        """Create an immutable snapshot for reasoning"""
        return {
            "time": state.time,
            "position": state.position.copy(),
            "velocity": state.velocity.copy(),
            "momentum": state.momentum.copy(),
            "mass": state.mass,
            "stored_energy": state.energy,
            "kinetic_energy": state.kinetic_energy,
            "potential": state.gravitational_potential_energy,
        }
    def _snapshot_eng_report(self, eng_report):
        return {
            "exhaust_momentum": eng_report.exhaust_momentum,
            "energy_drawn": eng_report.energy_drawn,
            "mass_spent": eng_report.mass_spent,
            "field_work": eng_report.field_work,
            "exhaust_energy": eng_report.exhaust_energy,
            "radiation_energy": eng_report.radiation_energy
        }

    def _snapshot_env_report(self, env_report):
        return {
            "momentum_exchange": env_report.momentum_exchange,
            "energy_exchange": env_report.energy_exchange,
            "mass_exchange": env_report.mass_exchange,
            "field_work": env_report.field_work,
            "field_momentum": env_report.field_momentum
        }
    
    # ----------------------------------------
    # Main recorder entry
    # ----------------------------------------

    def record(
        self,
        state_before,
        state_after,
        engine_report,
        environment_report,
        env_explain,
        environment,
        verdict,
        dt,
        step_index,
    ):

        energetics = verdict.get("explain", {}).get("field_energy", {})

        # ---------- Record ----------
        self.records.append({

                "step": step_index,
                "time": state_after.time,
                "dt": dt,

                # TRUE physics objects
                "state_before": state_before,
                "state_after": state_after,

                # Immutable snapshots (for UI / debugging)
                "state_before_snapshot": self._snapshot_state(state_before),
                "state_after_snapshot": self._snapshot_state(state_after),

                # Reports (verbatim) objects
                "engine_report": engine_report,
                "environment_report": environment_report,
                "no_env_report": env_explain,

                # Reports
                "engine_report_snapshot": self._snapshot_eng_report(engine_report),
                "environment_report_snapshot": self._snapshot_env_report(environment_report),

                "field_energy_exchange": energetics,
                # "mechanical_energy_change_due_to_field": ?

                # Physics judge
                "conservation": verdict,
            })

    # ----------------------------------------
    # Drift analysis
    # ----------------------------------------

    def analyze_drift(self):
        momentum_drift = [0.0, 0.0, 0.0]
        energy_drift = 0.0
        mass_drift = 0.0

        mech_drifts = []

        for r in self.records:
            res = r["conservation"]

            energy_drift += res.get("energy_residual")
            mass_drift += res.get("mass_residual")

            p = res.get("momentum_residual")
            for i in range(3):
                momentum_drift[i] += p[i]

            # mech_drifts.append(r["mechanical_energy_change_due_to_field"])

        return {
            "energy_drift": energy_drift,
            "mass_drift": mass_drift,
            "momentum_drift": momentum_drift,
            "max_mechanical_energy_drift": max(mech_drifts) if mech_drifts else 0.0,
            "min_mechanical_energy_drift": min(mech_drifts) if mech_drifts else 0.0,
            "final_mechanical_energy_drift": mech_drifts[-1] if mech_drifts else 0.0,
        }
