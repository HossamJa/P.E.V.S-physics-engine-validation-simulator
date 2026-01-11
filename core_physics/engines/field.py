from .base import FieldEngine
from core_physics.effects import Effect
from core_physics.reports import EngineReport


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

        # --- Work done by field ---
        v = state.velocity
        F_vec = [F_mag * d for d in r_hat]
        field_work = sum(F_vec[i] * v[i] for i in range(3)) * dt

        effects = [
            # Ship gains momentum
            Effect(
                delta_p=dp,
                channel="ship",
                source="gravity_gradient_engine"
            ),

            # Field loses momentum (reaction sink)
            Effect(
                delta_p=[-x for x in dp],
                channel="field",
                source="gravity_gradient_engine"
            )
        ]

        report = EngineReport(
                exhaust_momentum=[0.0, 0.0, 0.0],
                energy_drawn=0.0,
                mass_spent=0.0,
                field_work=field_work,
                source="gravity_gradient_engine",
                channel="field",
                active=True
            )
        return effects, report