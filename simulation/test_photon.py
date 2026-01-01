from core_physics.state import State
from core_physics.engines.photon import PhotonEngine
from core_physics.simulator import Simulator

state = State(
    position=[0, 0, 0],
    velocity=[0, 0, 0],
    mass=1000,
    energy=1e9,      # large energy store
    time=0,
    can_exchange_radiation=True
)

engine = PhotonEngine(power=1e6)  # 1 MW

sim = Simulator(
    state=state,
    engine=engine,
    dt=1
)

result = sim.step(10)

print("Final velocity:", state.velocity)
print("Remaining energy:", state.energy)
print("Verdict:", result)
