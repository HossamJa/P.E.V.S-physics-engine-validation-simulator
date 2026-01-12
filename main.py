from core_physics.state import State
from core_physics.environment import Environment
from core_physics.engines import (
                                    reaction,
                                    photon,
                                    field,
                                )
from core_physics.simulator import Simulator
from simulation.recorder import Recorder
from noron.auditor import detect_closed_system_fraud, detect_field_fraud


# Helpers
def to_float(value):

    try: 
        return float(value)
    except Exception:
        print(f"{value} is Not A valid Decimal Number!")
        return None

def to_vector(name, vector):
    if len(vector) != 3:
        print(f"{name} must have exactly 3 components")
        return None

    out = []
    for v in vector:
        num = to_float(v.strip())
        if num is None:
            print(f"Invalid {name} value")
            return None
        out.append(num)
    return out


def main():

    while True:
        ask = input("Start A New Simulation? y/n: ").strip().lower()
        if ask not in ["y", "yes"]:
            return
        environment = create_environment()
        state = create_state(environment)
        engine = dfine_engine()
        recorder = Recorder()
        start_simulator(state, environment, engine, recorder)
        get_audits(recorder)

def create_state(env):
    print("Define a State of the Simulation")

    position = input("Insert Initial Position as a Vector X,Y,Z: ").strip().split(",")
    position_vector = to_vector("Position", position)
    if not position_vector:
        return

    velocity = input("Insert Initial Velocity as a Vector Vx,Vy,Vz: ").strip().split(",")
    velocity_vector = to_vector("Velocity", velocity)
    if not velocity_vector:
        return

    mass = to_float(input("Insert State Mass Value: "))
    if mass is None:
        print("Invalid Mass Value, Insert a valid decimal number!")
        return

    energy = to_float(input("Insert State Energy Value: "))
    if energy is None:
        print("Invalid Energy Value, Insert a valid decimal number!")
        return

    time = to_float(input("Insert State Time Value: "))
    if time is None:
        print("Invalid Time Value, Insert a valid decimal number!")
        return

    ask_cef = input("Can exchange fields? y/n: ").strip().lower()
    ask_cem = input("Can exchange mass? y/n: ").strip().lower()
    ask_cer = input("Can exchange radiation? y/n: ").strip().lower()

    cef = ask_cef in ['y', 'yes']
    cem = ask_cem in ['y', 'yes']
    cer = ask_cer in ['y', 'yes']

    return State(
        position=position_vector,
        velocity=velocity_vector,
        mass=mass,
        energy=energy,
        time=time,
        environment=env,
        can_exchange_fields=cef,
        can_exchange_mass=cem,
        can_exchange_radiation=cer
    )

def create_environment():
    
    print("Insert Environment Initials")
    
    gravity_mass = to_float(input("Insert Gravity Mass: "))
    if gravity_mass is None:
        print("Invalid Gravity Mass value, Enter a Valid Decimal Number!")
        return
    
    gravity_source_position = to_vector("Gravity Source Position", 
                                        input("Insert Initial Gravity Source Position as a Vector x,y,z: ").strip().split(",")
                                    )
    if not gravity_source_position:
        return
    
    G = to_float(input("Insert Gravity Value: "))
    if G is None:
        print("Invalid gravity value, insert a valid decimal number!")
        return

    return Environment(
        gravity_mass=gravity_mass,
        gravity_source_position=gravity_source_position,
        G=G,
    )

def dfine_engine():
    print("Define an Engine")
    print(
        """
        Engine Models:
            1- Reaction Engine.
            2- Photon Engine
            3- Field Engine
       """
    )
    try:
        engine_model = int(input("Pick An Engine Model 1-3: ").strip())
        if not 0 < engine_model <=3:
            raise ValueError
    except:
        print("Invalid Engine Model")
        return

    if engine_model == 1:
        exhaust_velocity = to_float(input("Insert Exhaust Velocity: "))
        if exhaust_velocity is None:
            print("invalid Exhaust Velocity Value, Insert a Valid decimal number!")
            return
        mass_flow_rate = to_float(input("Insert Mass Flow Rate: "))
        if mass_flow_rate is None:
            print("Invalid Mass Flow Rate, Insert a Valid Decimal Number!")
            return
        
        direction = to_vector("Deriction",
                              input("Insert a direction as a Vector x,y,z: ").strip().split(",")
                              )
        if not direction:
            return

        return reaction.ReactionEngine(
            exhaust_velocity=exhaust_velocity,
            mass_flow_rate=mass_flow_rate,
            direction=direction
        )
 
    elif engine_model == 2:
        power = to_float(input("Insert Power: "))
        if power is None:
            print("Invalid Power Value, enter a valid decimal number")
            return
        return photon.PhotonEngine(power=power)

    elif engine_model == 3:
        efficiency = to_float(input("Insert Efficiency ∈ [0, 1]: "))
        if efficiency is None or (0 <= efficiency <= 1):
            print("Invalid efficiency value, enter a valid decimal number between 0 and 1!")
            return
        return field.GravityGradientEngine(efficiency=efficiency)
        

def start_simulator(stt, env, eng, rcdr):
    sim = Simulator(
            state=stt,
            environment=env,
            engine=eng,
            recorder=rcdr
            )
    steps = to_float(input("How namy steps to Run the Simulation? "))
    if steps is None:
        print("Invalid steps number!")
        return
    
    return sim.step(steps=int(steps))

def get_audits(recorder):
    last = recorder.records[-1]
    verdict = detect_closed_system_fraud(last)
    print("\nAUDIT RESULT:")
    print(verdict)


main()
