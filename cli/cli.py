# cli.py

from core_physics.state import State
from core_physics.environment import Environment
from core_physics.simulator import Simulator
from core_physics.engines.reaction import ReactionEngine
from core_physics.engines.photon import PhotonEngine
from core_physics.engines.field import GravityGradientEngine
from core_physics.engines.claimed import DummyEngine
from simulation.recorder import Recorder
from .cli_output import (
    print_simulation_summary,
    print_conservation_summary,
    print_step_table,
    print_fraud_verdict,
    print_step_details,
    print_environment_summary,
    print_momentum_accounting,
    print_frame_sanity,
    print_engine_compliance,
)

# -------------------------------------------------
# Helpers
# -------------------------------------------------

def ask_float(prompt, min_val=None, max_val=None):
    try:
        val = float(input(prompt))
        if min_val is not None and val < min_val:
            raise ValueError
        if max_val is not None and val > max_val:
            raise ValueError
        return val
    except Exception:
        print("❌ Invalid numeric input.")
        return None


def ask_vector(prompt):
    try:
        raw = input(prompt).split(",")
        if len(raw) != 3:
            raise ValueError
        return [float(x.strip()) for x in raw]
    except Exception:
        print("❌ Vector must have 3 numeric components.")
        return None


def normalize(vec):
    import math
    mag = math.sqrt(sum(v*v for v in vec))
    if mag == 0:
        return [0, 0, 0]
    return [v / mag for v in vec]


# -------------------------------------------------
# CLI Flow
# -------------------------------------------------

def main():
    print("="*45)
    print(" Physics Engine Validation Lab ")
    print("="*45)

    while True:
        try:
            start = input("\nStart a new simulation? (y/n): ").lower()
            if start not in ("y", "yes"):
                break
        except KeyboardInterrupt:
            print("\nSee ya!")
            break
        environment = choose_environment()
        if not environment:
            continue

        state = define_state(environment)
        if not state:
            continue

        engine = choose_engine()
        if not engine:
            continue

        steps, dt = simulation_control()
        if steps is None:
            continue

        run_simulation(state, environment, engine, steps, dt)


# -------------------------------------------------
# Environment
# -------------------------------------------------

def choose_environment():
    print("\n--- Environment Selection ---")
    print("[1] Deep space (no gravity)")
    print("[2] Near Earth orbit")
    print("[3] Custom (advanced)")

    choice = input("Select option (1–3): ").strip()

    if choice == "1":
        return Environment(
            gravity_mass=0,
            gravity_source_position=[0, 0, 0],
            G=0
        )

    if choice == "2":
        return Environment(
            gravity_mass=5.972e24,
            gravity_source_position=[0, 0, 0],
            G=6.674e-11
        )

    if choice == "3":
        gm = ask_float("Gravity mass: ", 0)
        gpos = ask_vector("Gravity source position (x,y,z): ")
        G = ask_float("Gravitational constant G: ", 0)
        if None in (gm, gpos, G):
            return None
        return Environment(gm, gpos, G)

    print("❌ Invalid environment choice.")
    return None


# -------------------------------------------------
# State
# -------------------------------------------------

def define_state(environment):
    print("\n--- Spacecraft Initial Conditions ---")

    mass = ask_float("Mass (kg): ", 0)
    energy = ask_float("Initial energy (J): ", 0)
    speed = ask_float("Initial speed (m/s): ", 0)

    direction = ask_vector("Direction (x,y,z): ")
    if None in (mass, energy, speed, direction):
        return None

    direction = normalize(direction)
    velocity = [speed * d for d in direction]

    position = [0.0, 6.371e6 + 400e3, 0.0]

    return State(
        position=position,
        velocity=velocity,
        mass=mass,
        energy=energy,
        time=0,
        environment=environment,
        can_exchange_fields=True,
        can_exchange_mass=True,
        can_exchange_radiation=True
    )


# -------------------------------------------------
# Engine
# -------------------------------------------------

def choose_engine():
    print("\n--- Engine Selection ---")
    print("[1] Reaction engine")
    print("[2] Photon engine")
    print("[3] Field interaction engine")
    print("[4] Reactionless claim (test)")

    choice = input("Select engine (1–4): ").strip()

    if choice == "1":
        v = ask_float("Exhaust velocity (m/s): ", 0)
        m = ask_float("Mass flow rate (kg/s): ", 0)
        d = ask_vector("Thrust direction (x,y,z): ")
        if None in (v, m, d):
            return None
        return ReactionEngine(
            exhaust_velocity=v,
            mass_flow_rate=m,
            direction=normalize(d)
        )

    if choice == "2":
        p = ask_float("Power (W): ", 0)
        if p is None:
            return None
        return PhotonEngine(power=p)

    if choice == "3":
        return GravityGradientEngine()

    if choice == "4":
        return DummyEngine()

    print("❌ Invalid engine choice.")
    return None


# -------------------------------------------------
# Simulation Control
# -------------------------------------------------

def simulation_control():
    print("\n--- Simulation Control ---")
    steps = ask_float("Number of steps: ", 1)
    dt = ask_float("Time step dt (s): ", 0)
    if None in (steps, dt):
        return None, None
    return int(steps), dt


# -------------------------------------------------
# Run + Output
# -------------------------------------------------

def run_simulation(state, environment, engine, steps, dt):
    recorder = Recorder()

    sim = Simulator(
        state=state,
        environment=environment,
        engine=engine,
        recorder=recorder,
        dt=dt
    )

    print("\nRunning simulation...\n")
    verdict = sim.step(steps)

    print("="*40)
    print(" SIMULATION VERDICT ")
    print("="*40)

    print_simulation_summary(recorder, verdict)
    print_conservation_summary(recorder)
    print_step_table(recorder)

    print_environment_summary(recorder)
    print_momentum_accounting(recorder)
    print_frame_sanity(recorder)
    print_engine_compliance(recorder)

    print_fraud_verdict(verdict["fraud verdict"])

    show = input("\nEnter Forensic Mode? (y/n): ").lower()
    if show in ("y", "yes"):
        print("\n--- Forensic ---")
        print_step_details(recorder.records[-1])

# -------------------------------------------------
if __name__ == "__main__":
    main()
