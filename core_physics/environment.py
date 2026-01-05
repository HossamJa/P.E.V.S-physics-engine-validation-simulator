from .engines.base import EngineEffect
import math

class Environment:
    """
    Conservative external environment (e.g. gravity).
    Energy is NOT injected — only momentum is exchanged.
    Potential energy is derived from position.
    """

    def __init__(self, gravity_mass=None, gravity_source_position=None, G=6.674e-11, r_min=1e6):
        """
        gravity_mass: mass of central body (None = no gravity)
        gravity_source_position: [x, y, z]
        G: gravitational constant
        """
        self.gravity_mass = gravity_mass
        self.gravity_source_position = gravity_source_position or [0.0, 0.0, 0.0]
        self.G = G
        self.r_min = r_min  # meters, or body radius

        self.has_gravity = gravity_mass is not None

    # -----------------------------------
    # Geometry helpers (USED BY CONSERVATION)
    # -----------------------------------

    def distance_to_gravity_source(self, position):
        dx = position[0] - self.gravity_source_position[0]
        dy = position[1] - self.gravity_source_position[1]
        dz = position[2] - self.gravity_source_position[2]
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    def gravity_direction(self, position):
        dx = self.gravity_source_position[0] - position[0]
        dy = self.gravity_source_position[1] - position[1]
        dz = self.gravity_source_position[2] - position[2]

        r = math.sqrt(dx*dx + dy*dy + dz*dz)
        if r == 0:
            return [0.0, 0.0, 0.0]

        return [dx / r, dy / r, dz / r]

    # -----------------------------------
    # Field application (momentum only)
    # -----------------------------------

    def apply_field(self, state, dt):
        if not state.can_exchange_fields or not self.has_gravity:
            return []

        m = state.mass
        r = self.distance_to_gravity_source(state.position)

        if r == 0:
            return []

        # Newtonian gravity force magnitude
        F = self.G * self.gravity_mass * m / (r * r)

        direction = self.gravity_direction(state.position)

        # Δp = F * dt * direction
        delta_p = [F * direction[i] * dt for i in range(3)]

        return [
            EngineEffect(
                delta_p=delta_p,
                delta_e=0.0,   # ❗ NO ENERGY INJECTION
                delta_m=0.0,
                channel="field",
                source="gravity"
            )
        ]
