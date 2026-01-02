from core_physics.simulator import Simulator
from core_physics.engines.claimed import DummyEngine
from core_physics.state import State
from .recorder import Recorder
from core_physics.environment import Environment 

state = State(
    position=[0,0,0],
    velocity=[0,0,0],
    mass=10,
    energy=100,
    time=0,
    can_exchange_fields=True   # <-- REQUIRED for gravity
)


engine = DummyEngine()
recorder = Recorder()
environment = Environment(gravity=[0, -9.81, 0])

sim = Simulator(
    state=state, 
    engine=engine,
    environment=environment,   
    dt=1,
    recorder=recorder,
)
result = sim.step(10)

print(result)
print(recorder.records)