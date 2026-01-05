from core_physics.state import State
from core_physics.engines.photon import PhotonEngine
from core_physics.simulator import Simulator
from core_physics.environment import Environment 
from .recorder import Recorder

environment = Environment(
    gravity_mass=5.972e24,              # Earth mass (example)
    gravity_source_position=[0, 0, 0],
    G=6.674e-11
)
state = State(
    position=[0.0, 6.371e6 + 400e3, 0.0], # 400 km orbit altitude
    velocity=[0, 0, 0],
    mass=1000,
    energy=1e9,      # large energy store
    time=0,
    environment=environment,
    can_exchange_radiation=True,
    can_exchange_fields = True
)

engine = PhotonEngine(power=1e6)  # 1 MW

recorder = Recorder()
sim = Simulator(
    state=state, 
    engine=engine,
    environment=environment, 
    dt=1,
    recorder=recorder
)

result = sim.step(4)

print("Final velocity:", state.velocity)
print("Remaining energy:", state.energy)
print("Verdict:", result)
print("Records: ", recorder.records)
