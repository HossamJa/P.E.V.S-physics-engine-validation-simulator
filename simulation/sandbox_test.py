from core_physics.simulator import Simulator
from core_physics.engines.reaction import ReactionEngine
from core_physics.state import State
from .recorder import Recorder
from core_physics.environment import Environment

environment = Environment(
    gravity_mass=5.972e24,              # Earth mass (example)
    gravity_source_position=[0, 0, 0],
    G=6.674e-11
)

state = State(
    position=[12, 12, 2], # 400 km orbit altitude
    velocity=[36,12,12],
    mass=321,
    energy=123432,
    time=0,
    environment=environment,
    can_exchange_fields=True,
    can_exchange_mass=True,
    can_exchange_radiation=True
)

engine = ReactionEngine(
    exhaust_velocity=133,
    mass_flow_rate=2,
    direction=[1,1,1]
)
recorder = Recorder()

steps = 111

sim = Simulator(
    state=state, 
    engine=engine,
    environment=environment,
    recorder=recorder,
)
result = sim.step(steps)

print("conservation verdict: ", result)
print("Records: ", recorder.records)