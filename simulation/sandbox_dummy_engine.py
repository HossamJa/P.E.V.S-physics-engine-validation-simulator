from core_physics.simulator import Simulator
from core_physics.engines.claimed import DummyEngine
from core_physics.state import State
from .recorder import Recorder
from core_physics.environment import Environment

environment = Environment(
    gravity_mass=5.972e24,              # Earth mass (example)
    gravity_source_position=[0, 0, 0],
    G=6.674e-11
)

state = State(
    position=[0.0, 6.371e6 + 400e3, 0.0], # 400 km orbit altitude
    velocity=[0,0,0],
    mass=10,
    energy=100,
    time=0,
    environment=environment,
    can_exchange_fields=True
)


engine = DummyEngine()
recorder = Recorder()

steps = 4

sim = Simulator(
    state=state, 
    engine=engine,
    environment=environment,
    recorder=recorder,
)
result = sim.step(steps)

print("conservation verdict: ", result)
print("Records: ", recorder.records)