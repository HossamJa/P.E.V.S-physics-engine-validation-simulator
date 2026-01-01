from core_physics.state import State
from core_physics.conservation import Conservation
from core_physics.engines.reaction import ReactionEngine

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
effect = engine.step(state, dt)

judge = Conservation().judge(
    state,
    effect.delta_p,
    effect.delta_e,
    effect.delta_m
)

print(judge)
