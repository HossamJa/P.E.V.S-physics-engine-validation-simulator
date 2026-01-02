from .base import BaseEngine, EngineEffect

class ReactionEngine(BaseEngine):
    """
    Simple, honest reaction engine (V1).
    """

    def __init__(self, exhaust_velocity, mass_flow_rate):
        self.ve = exhaust_velocity      # m/s
        self.m_dot = mass_flow_rate     # kg/s

    def step(self, state, dt):
        dm = self.m_dot * dt          # mass expelled
        
        direction = [1.0, 0.0, 0.0]  # thrust along +x
        dp = [dm * self.ve * d for d in direction]   # exhaust momentum as vector [x,y,z]
        
        # Assumes ideal conversion; efficiency modeled in V2
        de = 0.5 * dm * self.ve**2      # kinetic energy of exhaust

        #delta_p is vehicle momentum change, not exhaust momentum
        return EngineEffect(
            delta_p = dp,               # vehicle gains +dp
            delta_m = -dm,              # vehicle loses mass
            delta_e = -de               # vehicle spends energy
        )
