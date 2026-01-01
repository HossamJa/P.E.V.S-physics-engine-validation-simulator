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
        frame,
        can_exchange_momentum=None
    ):
        # Kinematics:
        self.position = position
        self.velocity= velocity
        self.time = time
        self.frame = frame

        # Resources"
        self.mass = mass
        self.energy = energy
        # Environment:

        # What exchanges are physically allowed
        self.can_exchange_momentum = can_exchange_momentum


