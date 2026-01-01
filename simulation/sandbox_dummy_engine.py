from core_physics.state import State
from core_physics.conservation import Conservation
from core_physics.engines.claimed import DummyEngine

# Initial state
state = State(
    position=[0, 0, 0],
    velocity=[1, 0, 0],
    mass=10,
    energy=100,
    time=0,
    frame="inertial",
    can_exchange_momentum=False
)

engine = DummyEngine()
conservation = Conservation()

dt = 1.0

for step in range(10):
    effect = engine.step(state, None, dt)

    verdict = conservation.judge(
        state,
        effect.delta_p,
        effect.delta_e,
        effect.delta_m
    )

    if verdict["valid"] is False:
        print("❌ Conservation rejected effect")
        break

    # Apply effect manually (V1 — no automation yet)
    # Nothing should change
    state.time += dt

print("Final state:")
print(state.position, state.velocity, state.mass, state.energy)
