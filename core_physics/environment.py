from .engines.base import EngineEffect

class Environment:
    """
    Environment applies background physics.
    It does NOT decide validity — Conservation does.
    """

    def __init__(
        self,
        gravity=None,          # vector [gx, gy, gz] in m/s²
        allow_spacetime=True,  # allows momentum exchange with spacetime
    ):
        self.gravity = gravity
        self.allow_spacetime = allow_spacetime

    def apply(self, state, dt):
        """
        Returns an EngineEffect representing environmental influence.
        """
        if self.gravity is None:
            return EngineEffect()
        
        delta_p = [state.mass * self.gravity[i] * dt for i in range(3)]
        delta_e = 0.0
        delta_m = 0.0

        # Gravity = momentum exchange with spacetime
        if self.gravity:
            for i in range(3):
                dp = state.mass * self.gravity[i] * dt
                delta_p[i] += dp

        return EngineEffect(
            delta_p=delta_p,
            delta_e=delta_e,
            delta_m=delta_m
        )
