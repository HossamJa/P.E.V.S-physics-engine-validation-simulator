class Recorder:
    """
    Records the evolution of State over time.
    Observer only — never modifies physics.
    """

    def __init__(self):
        self.history = []

    def record(self, state, effect=None, verdict=None):
        snapshot = {
            "time": state.time,
            "position": list(state.position),
            "velocity": list(state.velocity),
            "mass": state.mass,
            "energy": state.energy,
            "momentum": [
                state.mass * v for v in state.velocity
            ],
            "effect": {
                "delta_p": effect.delta_p if effect else None,
                "delta_e": effect.delta_e if effect else None,
                "delta_m": effect.delta_m if effect else None,
            } if effect else None,
            "verdict": verdict
        }

        self.history.append(snapshot)

    def last(self):
        return self.history[-1] if self.history else None

    def summary(self):
        return {
            "steps": len(self.history),
            "initial": self.history[0] if self.history else None,
            "final": self.history[-1] if self.history else None,
        }
