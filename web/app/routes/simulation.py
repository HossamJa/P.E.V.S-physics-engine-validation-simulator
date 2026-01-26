from flask import Blueprint, render_template, request, jsonify, session
from app.helpers import login_required
from cli_ui.cli import choose_environment, choose_engine, define_state, run_simulation
from simulation.results.simulation_result import SimulationResult
from simulation.results.serializers import serialize_simulation

from app.models import Simulation
from app.extensions import db

bp = Blueprint("simulation", __name__)

@bp.route("/simulation")
@login_required
def simulation_page():
    return render_template("simulation.html")


@bp.route("/api/simulation/run", methods=["POST"])
@login_required
def run_simulation_api():
    try:
        # --- ENVIRONMENT ---
        env_choice = request.form.get("environment")

        gravity_mass = float(request.form["gravity_mass"]) if env_choice == "3" else None
        gravity_source_position = (
            [
                float(request.form["gravity_source_x"]),
                float(request.form["gravity_source_y"]),
                float(request.form["gravity_source_z"]),
            ] if env_choice == "3" else None
        )
        G = float(request.form["G"]) if env_choice == "3" else None

        environment = choose_environment(env_choice, gravity_mass, gravity_source_position, G, ui=True)

        # --- STATE ---
        position = [float(request.form[f"position_{c}"]) for c in "xyz"]
        direction = [float(request.form[f"iv_direction_{c}"]) for c in "xyz"]

        state = define_state(
            env=environment,
            ui=True,
            position=position,
            direction=direction,
            mass=float(request.form["mass"]),
            energy=float(request.form.get("energy", 0)),
            speed=float(request.form.get("speed", 0)),
        )

        # --- ENGINE ---
        engine_type = request.form.get("engine_type")

        engine = choose_engine(
            choice=engine_type,
            exv=float(request.form["exhaust_velocity"]) if engine_type == "1" else None,
            mfr=float(request.form["mass_flow_rate"]) if engine_type == "1" else None,
            td=[float(request.form[f"thrust_direction_{c}"]) for c in "xyz"] if engine_type == "1" else None,
            pwr=float(request.form["power"]) if engine_type == "2" else None,
            efcy=float(request.form["efficiency"]) if engine_type == "3" else None,
            ui=True
        )
        
        # Collecting simulation setup for history
        param = {
             "env_type": env_choice,
             "eng_type": engine_type,
             "setup": request.form.to_dict()
        }

        verdict, recorder = run_simulation(
            state=state,
            environment=environment,
            engine=engine,
            steps=int(request.form["steps"]),
            dt=float(request.form["dt"]),
            ui=True,
        )

        result = SimulationResult(verdict, recorder)

        # Store the importamt data in the simulation db table
        engines = ["Reaction", "Photon", "Field", "Reactionless"]
        environments = ["Space", "Orbit", "Custom"]

        sim = Simulation(
            user_id=session["user_id"],

            accounting=result.accounting(),

            engine_type=engines[int(engine_type)-1],
            environment=environments[int(env_choice)-1],

            setup=param,
            summary=result.summary(),
            audit=result.audit(),
            final_state=result.final_state(),
        )

        db.session.add(sim)
        db.session.commit()

        return jsonify(serialize_simulation(result))
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


simulation_api_bp = Blueprint(
    "simulation_api",
    __name__,
    url_prefix="/api/simulation"
)

@simulation_api_bp.route("/rerun/<int:sim_id>", methods=["GET"])
@login_required
def rerun_simulation(sim_id):
    sim = Simulation.query.filter_by(
        id=sim_id,
        user_id=session["user_id"]
    ).first_or_404()

    return jsonify(sim.setup)
