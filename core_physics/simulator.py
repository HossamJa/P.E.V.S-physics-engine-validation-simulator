from .conservation import Conservation

class Simulator:
    def __init__(self, state, engine, dt, recorder=None):
        self.engine = engine
        self.dt = dt
        self.state = state
        self.conservation = Conservation()
        self.recorder = recorder

    def step(self, steps):
        for step in range(steps):
            effect = self.engine.step(self.state, self.dt)

            verdict = self.conservation.judge(
                self.state,
                effect.delta_p,
                effect.delta_e,
                effect.delta_m
            )

            if self.recorder:
                self.recorder.record(self.state, effect, verdict)

            if verdict["valid"] is False:
                return {
                    "judge": verdict,
                    "step": step
                }

            # --- Apply approved effect ---
            for i in range(len(self.state.velocity)):
                self.state.velocity[i] += effect.delta_p / self.state.mass

            for i in range(len(self.state.position)):
                self.state.position[i] += self.state.velocity[i] * self.dt

            self.state.mass += effect.delta_m
            self.state.energy += effect.delta_e
            self.state.time += self.dt

        return {
            "judge": {"valid": True},
            "step": steps
        }
