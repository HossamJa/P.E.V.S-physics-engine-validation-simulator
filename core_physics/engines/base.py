class BaseEngine:
    """
    Engines propose physical effects.
    They do NOT modify state directly.
    """

    def step(self, state, dt):
        raise NotImplementedError("Engine must implement step()")

class FieldEngine(BaseEngine):
    """
    Base class for engines that exchange momentum with fields.
    """

    def step(self, state, environment, dt):
        raise NotImplementedError(
            "FieldEngine must implement step(state, environment, dt)"
        )
