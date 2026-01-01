from .state import State
from .conservation import Conservation

class Simulator:
    def __init__(self, state, engine, dt):
        self.engine = engine
        self.dt = dt
        self.state = state
        self.conservation = Conservation()

    def step(self, steps=1):
        for step in range(steps):
            effect = self.engine.step(self.state, self.dt)

            verdict = {"judge": self.conservation.judge(
                self.state,
                effect.delta_p,
                effect.delta_e,
                effect.delta_m
            ), 
            "step": step,
            }

            if not verdict["judge"]["valid"]:
                print("❌ Conservation rejected effect")
                return verdict

            # --- Apply approved physics ---

            # 1D momentum → velocity
            self.state.velocity[0] += effect.delta_p / self.state.mass

            # Position update
            self.state.position[0] += self.state.velocity[0] * self.dt

            # Mass & energy
            self.state.mass += effect.delta_m
            self.state.energy += effect.delta_e

            # Time
            self.state.time += self.dt

        return {"valid": True, "state": self.state}
