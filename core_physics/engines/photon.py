from .base import BaseEngine, EngineEffect

C = 299792458  # speed of light (m/s)
class PhotonEngine(BaseEngine):
    """
    A photon engine (a.k.a. photon rocket) works by emitting radiation.
    Core physics (non-negotiable): p = E/c
    Where:
        p = momentum carried by photons
        E = emitted energy
        c = speed of light
        
    """

    def __init__(self, power):
        """
        power: watts (J/s)
        """
        self.power = power

    def step(self, state, dt):
        # Energy emitted this timestep
        dE = self.power * dt

        # Momentum carried by photons
        dp = dE / C

        return EngineEffect(
            delta_p=dp,     # vehicle gains momentum
            delta_e=-dE,    # energy spent
            delta_m=0       # no mass loss
        )