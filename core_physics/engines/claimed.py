from .base import BaseEngine, EngineEffect

class DummyEngine(BaseEngine):
    """
    Claims propulsion, produces nothing.
    Used to validate conservation framework.
    """

    def step(self, state, environment, dt):
        return EngineEffect(
            delta_p=0,
            delta_e=0,
            delta_m=0
        )