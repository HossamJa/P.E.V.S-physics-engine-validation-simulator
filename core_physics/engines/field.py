
from .base import FieldEngine, EngineEffect
import math


class GravityGradientEngine(FieldEngine):
    """
    Legitimate field engine.
    Redirects gravitational field momentum into controlled thrust.
    (Think gravity-gradient tether / attitude control)
    """

    def __init__(self, efficiency=1.0):
        """
        efficiency ∈ [0, 1]
        1.0 = perfect coupling (idealized)
        """
        self.efficiency = max(0.0, min(1.0, efficiency))

    def step(self, state, environment, dt):
        if not environment.has_gravity:
            return []

        # Vector from ship to gravity source
        r_vec = environment.vector_to_gravity_source(state.position)
        r = environment.distance_to_gravity_source(state.position)

        if r == 0:
            return []

        # Unit vector toward gravity source
        r_hat = [x / r for x in r_vec]

        # Gravitational acceleration magnitude
        G = environment.G
        M = environment.gravity_mass
        a_mag = G * M / (r * r)

        # Gravitational force
        F_mag = state.mass * a_mag * self.efficiency

        # Momentum exchanged this step
        dp = [F_mag * dt * d for d in r_hat]

        return [
            # Ship gains momentum
            EngineEffect(
                delta_p=dp,
                channel="ship",
                source="gravity_gradient_engine"
            ),

            # Field loses momentum (reaction sink)
            EngineEffect(
                delta_p=[-x for x in dp],
                channel="field",
                source="gravity_gradient_engine"
            )
        ]