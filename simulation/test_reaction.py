from core_physics.simulator import Simulator
from core_physics.engines.reaction import ReactionEngine
from core_physics.state import State
from .recorder import Recorder

state = State(
    position=[0,0,0],
    velocity=[0,0,0],
    mass=100,
    energy=1e8,
    time=0,
    can_exchange_mass = True
)

engine = ReactionEngine(
    exhaust_velocity=1000,
    mass_flow_rate=1
)
recorder = Recorder()

sim = Simulator(
    state=state, 
    engine=engine,
    dt=1,
    recorder=recorder
)
result = sim.step(10)

print(recorder.records)