class State:
    """
    State = objective facts of the universe at a timestep.
    """

    def __init__(
        self,
        position,        # vector [x, y, z]
        velocity,        # vector [vx, vy, vz]
        mass,            # scalar
        energy,          # scalar
        time,            # scalar
        frame="inertial",

        # Momentum exchange permissions
        can_exchange_mass=False,
        can_exchange_radiation=False,
        can_exchange_fields=False,
    ):
        # Kinematics:
        self.position = position
        self.velocity= velocity
        self.time = time
        self.frame = frame

        # Resources"
        self.mass = mass
        self.energy = energy

        # Environment permissions
        self.can_exchange_mass = can_exchange_mass
        self.can_exchange_radiation = can_exchange_radiation
        self.can_exchange_fields = can_exchange_fields

