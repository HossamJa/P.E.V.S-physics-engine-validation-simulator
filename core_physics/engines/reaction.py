from .base import BaseEngine
from core_physics.effects import Effect
from core_physics.reports import EngineReport

class ReactionEngine(BaseEngine):
    """
    Simple, honest reaction engine.
    """

    def __init__(self, exhaust_velocity, mass_flow_rate, direction=None):
        self.ve = exhaust_velocity      # m/s
        self.m_dot = mass_flow_rate     # kg/s
        self.direction = direction or [1.0, 0.0, 0.0]  # unit vector

    def step(self, state, environment, dt):
        # --- Mass expelled ---
        dm = self.m_dot * dt            # kg

        # --- Momentum magnitude ---
        dp_mag = dm * self.ve           # kg·m/s

        # --- Vector momentum ---
        dp = [dp_mag * d for d in self.direction]

        # --- Energy spent by ship ---
        de = 0.5 * dm * self.ve ** 2

        effects = [
            # ---------------- Ship ----------------
            Effect(
                delta_p=dp,              # ship gains +dp
                delta_m=-dm,             # ship loses mass
                delta_e=-de,             # ship spends energy
                channel="ship",
                source="reaction_engine"
            ),

            # --------------- Exhaust --------------
            Effect(
                delta_p=[-x for x in dp],  # exhaust carries −dp
                delta_m=+dm,               # exhaust gains mass
                delta_e=+de,               # exhaust carries KE
                channel="exhaust",
                source="reaction_engine"
            )
        ]
    
        report = EngineReport(
            exhaust_momentum=[-x for x in dp],
            energy_drawn=de,
            mass_spent=dm,
            field_work=0.0,
            active=True
        )

        return effects, report