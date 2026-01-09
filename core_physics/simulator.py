import copy
from .conservation import Conservation
from noron.auditor import detect_closed_system_fraud

class Simulator:
    def __init__(self, state, engine, environment, dt=0.01, recorder=None):
        self.state = state
        self.engine = engine
        self.environment = environment
        self.dt = dt
        self.conservation = Conservation()
        self.recorder = recorder

    def step(self, steps=1000):
        for step in range(steps):

            state_before = copy.deepcopy(self.state)

            # 1. Engine proposes effects (list)
            engine_effects, engine_report  = self.engine.step(self.state, self.environment, self.dt)
            if not isinstance(engine_effects, list):
                engine_effects = [engine_effects]

            # 2. Environment generates explicit FIELD effects (gravity, etc.)
            field_effects = []

            # --- Gravity as a first-class field effect ---
            extra_field_effects, environment_report = self.environment.apply_field(self.state, self.dt)
            if extra_field_effects:
                if not isinstance(extra_field_effects, list):
                    extra_field_effects = [extra_field_effects]
                field_effects.extend(extra_field_effects)

            # 3. Combine all effects
            all_effects = engine_effects + field_effects
            
            # 4. Conservation judges combined effect
            verdict = self.conservation.judge(
                self.state,
                all_effects,
                self.environment,
                dt=self.dt
            )

            if not verdict["valid"]:
                return {
                    "judge": verdict,
                    "step": step
                }

            # 5. Extract effects:

            # SHIP-only 
            ship_effects = [e for e in all_effects if e.channel == "ship"]

            # Field-only
            field_effects_only = [e for e in all_effects if e.channel == "field"]
           
           # --- Sum ship effects ---
            ship_dp = [0.0, 0.0, 0.0]
            ship_de = 0.0
            ship_dm = 0.0

            for e in ship_effects:
                for i in range(3):
                    ship_dp[i] += e.delta_p[i]
                ship_de += e.delta_e
                ship_dm += e.delta_m

            # 6. Apply approved effect (SYMPLECTIC)

            # --- Apply mass & energy to ship ---
            self.state.mass += ship_dm
            self.state.energy += ship_de

            # --- Apply TOTAL impulse directly to ship ---
            for i in range(3):
                self.state.momentum[i] += ship_dp[i]

            # --- Apply FIELD recoil (V2.1 FIX) ---
            for e in field_effects_only:
                self.environment.absorb_field_effect(e)

            # --- Drift using derived velocity ---
            v = [
                self.state.momentum[i] / self.state.mass
                for i in range(3)
            ]

            for i in range(3):
                self.state.position[i] += v[i] * self.dt

            self.state.time += self.dt

            state_after = self.state

            # 7. Recorder observes everything
            if self.recorder:
                self.recorder.record(
                    state_before,
                    state_after,
                    engine_report,
                    environment_report,
                    self.environment,
                    verdict,
                    self.dt,
                    step
                )

                fraud_verdict = detect_closed_system_fraud(self.recorder.records[-1])

        return {
            "judge": {"valid": True},
            "step": steps,
            "fraud verdict": fraud_verdict,
        }
