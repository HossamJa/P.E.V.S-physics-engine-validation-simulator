from core_physics.simulator import Simulator
from core_physics.engines.reaction import ReactionEngine
from core_physics.state import State

state = State(
    position=[0,0,0],
    velocity=[0,0,0],
    mass=100,
    energy=1e6,
    time=0,
    frame="inertial",
    can_exchange_momentum=True
)

engine = ReactionEngine(
    exhaust_velocity=1000,
    mass_flow_rate=1
)

dt = 1
simulate = Simulator(
    state=state, 
    engine=engine,
    dt=dt
)
run = simulate.step(10)
print(run)