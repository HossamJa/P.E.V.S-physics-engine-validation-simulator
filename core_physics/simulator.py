from .conservation import Conservation
from .engines.base import EngineEffect

# Utility Function
def vadd(a, b):
    return [a[i] + b[i] for i in range(3)]

class Simulator:
    def __init__(self, state, engine, environment, dt, recorder=None):
        self.state = state
        self.engine = engine
        self.environment = environment
        self.dt = dt
        self.conservation = Conservation()
        self.recorder = recorder

    def step(self, steps):
        for step in range(steps):

            # 1. Engine proposes
            engine_effect = self.engine.step(self.state, self.dt)

            # 2. Environment applies background physics
            env_effect = self.environment.apply(self.state, self.dt)

            # 3. Combine effects
            total_effect = EngineEffect(
                delta_p=vadd(
                        engine_effect.delta_p,
                        env_effect.delta_p
                    ),
                delta_e=engine_effect.delta_e + env_effect.delta_e,
                delta_m=engine_effect.delta_m + env_effect.delta_m
            )

            # 4. Conservation judges combined effect
            verdict = self.conservation.judge(
                self.state,
                total_effect.delta_p,
                total_effect.delta_e,
                total_effect.delta_m
            )

            # 5. Recorder observes everything
            if self.recorder:
                self.recorder.record(
                    self.state,
                    engine_effect,
                    env_effect,
                    total_effect,
                    verdict,
                    self.dt,
                    step
                )

            if not verdict["valid"]:
                return {
                    "judge": verdict,
                    "step": step
                }

            # 6. Apply approved effect
            
            # Apply momentum
            for i in range(3):
                self.state.momentum[i] += total_effect.delta_p[i]
            
            # Update velocity
            for i in range(len(self.state.velocity)):
                self.state.velocity[i] += total_effect.delta_p[i] / self.state.mass
            
            # Update position
            for i in range(len(self.state.position)):
                self.state.position[i] += self.state.velocity[i] * self.dt

            self.state.mass += total_effect.delta_m
            self.state.energy += total_effect.delta_e
            self.state.time += self.dt

        return {
            "judge": {"valid": True},
            "step": steps
        }
