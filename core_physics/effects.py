class Effect:
    """
    A proposed physical delta over one timestep.
    Neutral: can come from engine or environment.
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
        self.channel = channel      # ship | exhaust | field
        self.source = source

        self._validate()

    def _validate(self):
        if not isinstance(self.delta_p, list) or len(self.delta_p) != 3:
            raise ValueError("delta_p must be a 3-vector")

        if self.channel not in ("ship", "exhaust", "field"):
            raise ValueError(f"Invalid channel: {self.channel}")
