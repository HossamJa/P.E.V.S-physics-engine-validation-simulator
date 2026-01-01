
class BaseEngine:
    """
    Engines propose physical effects.
    They do NOT modify state directly.
    """

    def step(self, state, dt):
        raise NotImplementedError("Engine must implement step()")

class EngineEffect:
    """
    A proposed physical change over one timestep.
    This is NOT applied until Conservation approves it.
    """
    def __init__(self, delta_p=0, delta_e=0, delta_m=0):
        self.delta_p = delta_p
        self.delta_e = delta_e
        self.delta_m = delta_m
