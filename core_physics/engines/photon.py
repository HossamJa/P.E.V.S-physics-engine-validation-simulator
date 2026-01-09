from .base import BaseEngine
from core_physics.effects import Effect
from core_physics.reports import EngineReport

C = 299792458  # speed of light (m/s)

class PhotonEngine(BaseEngine):
    """
    A photon engine (a.k.a. photon rocket) works by emitting radiation.
    Core physics (non-negotiable): p = E/c
    Where:
        p = momentum carried by photons as vector [x, y, z]
        E = emitted energy
        c = speed of light
    """

    def __init__(self, power):
        """
        power: watts (J/s)
        """
        self.power = power

    def step(self, state, environment, dt):
        # Energy emitted this timestep
        dE = self.power * dt

        dp_mag = dE / C
        direction = [1.0, 0.0, 0.0]

        # Momentum carried by photons
        dp = [dp_mag * d for d in direction]

        effect = [
            Effect(
                delta_p=dp,
                delta_e=-dE,
                delta_m=0.0,
                channel="ship",
                source="photon_engine"
            )
        ]
        report = EngineReport(
                exhaust_momentum=[-x for x in dp],  # photons carry momentum away
                energy_drawn=dE,
                mass_spent=0.0,
                field_work=0.0,
                active=True
            )
        return effect, report
