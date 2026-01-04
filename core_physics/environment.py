from .engines.base import EngineEffect

class Environment:
    """
    Environment applies external field effects.
    Conservation decides validity.
    """

    def __init__(self, gravity):
        self.gravity = gravity  # [gx, gy, gz]

    def apply_field(self, state, dt):
        if not state.can_exchange_fields:
            return []

        m = state.mass
        g = self.gravity

        # Δp = F dt = m g dt
        delta_p = [m * g[i] * dt for i in range(3)]

        return [
            EngineEffect(
                delta_p=delta_p,
                delta_e=0.0,
                delta_m=0.0,
                channel="field",
                source="gravity"
            )
        ]
