from .base import BaseEngine
from core_physics.effects import Effect
from core_physics.reports import EngineReport

class DummyEngine(BaseEngine):
    """
    Claims propulsion, produces nothing.
    Used to validate conservation framework.
    """

    def step(self, state, environment, dt):

        effect = [
            Effect(
                delta_p=[0.0, 0.0, 0.0],
                delta_e=0.0,
                delta_m=0.0,
                channel="ship",
                source="engine"
            )
        ]
        report =  EngineReport(
                    exhaust_momentum=[0.0, 0.0, 0.0],
                    energy_drawn=0.0,
                    mass_spent=0.0,
                    field_work=0.0,
                    channel="ship",
                    source="engine",
                    active=False
                )
        return effect, report
