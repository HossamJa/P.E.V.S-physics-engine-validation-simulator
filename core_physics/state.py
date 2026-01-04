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

        # Optional bookkeeping
        total_energy_consumed=0.0,
        total_mass_lost=0.0,

        # Momentum exchange permissions
        can_exchange_mass=False,
        can_exchange_radiation=False,
        can_exchange_fields=False,
    ):
        # Kinematics:
        self.position = position
        self.time = time
        self.frame = frame

        self.momentum = [mass * velocity[i] for i in range(3)]

        # Bookkeeping:
        self.total_energy_consumed = total_energy_consumed
        self.total_mass_lost = total_mass_lost

        # Resources"
        self.mass = mass
        self.energy = energy

        # Environment permissions
        self.can_exchange_mass = can_exchange_mass
        self.can_exchange_radiation = can_exchange_radiation
        self.can_exchange_fields = can_exchange_fields

 # ---------- Derived properties (NEVER stored) ----------

    @property
    def velocity(self):
        return [
            self.momentum[i] / self.mass
            for i in range(3)
        ]

    @property
    def kinetic_energy(self):
        v2 = sum(v * v for v in self.velocity)
        return 0.5 * self.mass * v2

    # Add derived potential energy without storing it
    @property
    def potential_energy(self):
        # Simple uniform gravity along Y
        # Environment will define g
        return None  # computed by Environment
