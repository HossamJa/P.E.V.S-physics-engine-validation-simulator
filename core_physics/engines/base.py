
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

    def __init__(
                self,
                delta_p=None,
                delta_e=0.0,
                delta_m=0.0,
                channel="ship",
                source=None
            ):

        self.delta_p = delta_p if delta_p is not None else [0.0, 0.0, 0.0]
        self.delta_e = float(delta_e)
        self.delta_m = float(delta_m)
        self.channel = channel   # "ship", "exhaust", "field"
        self.source = source

        self._validate()

    def _validate(self):
        if not isinstance(self.delta_p, list) or len(self.delta_p) != 3:
            raise ValueError("delta_p must be a 3-vector [px, py, pz]")
        
        if self.channel not in ("ship", "exhaust", "field"):
            raise ValueError("Invalid EngineEffect channel")

    @staticmethod
    def zero(channel="ship"):
        return [EngineEffect(channel=channel)]

    def _merge_source(self, other):
        if self.source and other.source:
            return f"{self.source} + {other.source}"
        return self.source or other.source
