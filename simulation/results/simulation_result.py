class SimulationResult:
    def __init__(self, simulator_output, recorder):
        self.simulator_output = simulator_output
        self.recorder = recorder

        self.records = recorder.records

        self.last = recorder.records[-1]

    # ----------------------------
    # SUMMARY
    # ----------------------------

    def summary(self):
        verdict = self.simulator_output["judge"]

        return {
            "verdict": "PASS" if verdict["valid"] else "FAIL",
            "steps_executed": self.simulator_output["steps_executed"],
            "frame": self.last["state_after"].frame,
            "final_time": self.last["state_after"].time,
        }

    # ----------------------------
    # FINAL STATE
    # ----------------------------

    def final_state(self, state=None, raw=False):

        sa = self.last["state_after_snapshot"]

        if raw:
            sa = state

        return {
            "position": sa["position"],
            "velocity": sa["velocity"],
            "speed": (sum(v*v for v in sa["velocity"])) ** 0.5,
            "mass": sa["mass"],

            "energy": {
                "stored": sa["stored_energy"],
                "kinetic": sa["kinetic_energy"],
                "potential": sa["potential"],
                "total": (
                    sa["stored_energy"]
                    + sa["kinetic_energy"]
                    + sa["potential"]
                ),
            },
        }

    # ----------------------------
    # TIME SERIES For (UI + ML)
    # ----------------------------

    def timeseries(self):
        ts = {
            "time": [],
            "position": [],
            "velocity": [],
            "mass": [],
            "energy": [],
            "momentum": [],
        }

        for r in self.records:
            s = r["state_after_snapshot"]
            ts["time"].append(s["time"])
            ts["position"].append(s["position"]) # [x,y,z]
            ts["velocity"].append(s["velocity"]) # [vx,vy,vz]
            ts["mass"].append(s["mass"])
            ts["energy"].append({
                "stored": s["stored_energy"],
                "kinetic": s["kinetic_energy"],
                "potential": s["potential"],
            })
            ts["momentum"].append(s["momentum"]) # [x,y,z]

        return ts

    # ----------------------------
    # CONSERVATION (human-readable)
    # ----------------------------

    def conservation(self, conserv=None, raw=False):
        conservation = self.last["conservation"]
        if raw:
            conservation = conserv

        explain = conservation["explain"]
 
        return {
            "judge": conservation["valid"],
            "energy": {
                "valid": explain["energy"]["balanced"],
                "required": explain["energy"]["required"],
                "available": explain["energy"]["available"],
            },
            "mass": explain["mass"],
            "momentum": explain["momentum"],
            "field_energy": explain.get("field_energy"),

            "energy_residual": conservation["energy_residual"],
            "mass_residual": conservation["mass_residual"],
            "momentum_residual": conservation["momentum_residual"],
        }
 
    # ----------------------------
    # ENGINE
    # ----------------------------

    def engine(self, report=None, raw=False):
        er = self.last["engine_report"]

        if raw:
            er = report

        return {
            "active": er.active,
            "source": er.source,
            "channel": er.channel,

            "momentum_exchange": er.exhaust_momentum,
            "energy_drawn": er.energy_drawn,
            "mass_spent": er.mass_spent,
            "field_work": er.field_work,
            "radiation_energy": er.radiation_energy,

            # Compliance
            "momentum_declared": "Yes" if (any(abs(x) > 0 for x in er.exhaust_momentum)) else "No",
            "energy_declared": "Yes" if er.energy_drawn > 0 else "No",
            "field_work_declared": "Yes" if er.field_work != 0.0 else "No",
        }

    # ----------------------------
    # ENVIRONMENT
    # ----------------------------

    def environment(self, report=None, raw=False):
        env = self.last["environment_report"]

        if raw:
            env = report

        return {
            "source": env.source,
            "channel": env.channel,
            "momentum_exchange": env.momentum_exchange,
            "energy_exchange": env.energy_exchange,
            "mass_exchange": env.mass_exchange,
            "field_work": env.field_work,
        }

    # ----------------------------
    # REPORTS
    # ----------------------------

    def reports(self):
        report = []
        for r in self.records:
            report.append({
                "environment_report_snapshot": r["environment_report_snapshot"],
                "engine_report_snapshot": r["engine_report_snapshot"],
            })
        return report
    
    # ----------------------------
    # ACCOUNTING
    # ----------------------------

    def accounting(self):
        drift = self.recorder.analyze_drift()

        return {
            "momentum_drift": drift["momentum_drift"],
            "energy_drift": drift["energy_drift"],
            "mass_drift": drift["mass_drift"],
        }

    # ----------------------------
    # AUDIT / FRAUD
    # ----------------------------

    def audit(self):
        return {
            "closed_system": self.simulator_output["closed_system_fraud"],
            "field": self.simulator_output["field_froud"],
        }

    def raw_data(self):
        data = []

        data.append({
            "Verdict": self.summary(),
            "Accounting": self.accounting(),
            "Audit": self.audit()
            })
        
        for record in self.records:
            data.append({
            "Step" : record["step"],
            "Time" : record["time"],
            "dt" : record["dt"],

            "Conservation" : self.conservation(record["conservation"], raw=True),
            "State" : self.final_state(record["state_after_snapshot"], raw=True),
            
            "Engine Report" : self.engine(record["engine_report"], raw=True),
            "Environment Report" : self.environment(record["environment_report"]),
            "No Report Explain" : record["no_env_report"],

            "Field Energy Exchange" : record["field_energy_exchange"],
            })

        return data

