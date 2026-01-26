from flask import Blueprint, render_template, jsonify, request, session
from app.helpers import login_required
from app.models import Simulation
from sqlalchemy import func

from app.extensions import db

# =========================
# UI: History Page
# =========================
history_bp = Blueprint("history", __name__)

@history_bp.route("/history")
@login_required
def history():
    return render_template("history.html")


# =========================
# API: History Data
# =========================
history_api_bp = Blueprint(
    "history_api",
    __name__,
    url_prefix="/api/history"
)

@history_api_bp.route("", methods=["GET"])
@login_required
def history_api():
    query = Simulation.query.filter_by(user_id=session["user_id"])

    # -------- Filters --------
    verdict = request.args.get("verdict")
    if verdict:
        query = query.filter(
            func.json_extract(Simulation.summary, "$.verdict") == verdict
        )

    engine = request.args.get("engine")
    if engine:
        query = query.filter(
            Simulation.engine_type == engine.capitalize()
        )

    environment = request.args.get("environment")
    if environment:
        query = query.filter(
            Simulation.environment == environment.capitalize()
        )
    simulations = query.order_by(Simulation.created_at.desc()).all()

    results = []
    for sim in simulations:
        summary = sim.summary
        accounting = sim.accounting
        audit = sim.audit["closed_system"]

        results.append({
            "id": sim.id,
            "created_at": sim.created_at.isoformat(),

            "engine": sim.engine_type,
            "environment": sim.environment,

            "steps": summary.get("steps_executed") if summary else None,
            "final_time": summary.get("final_time") if summary else None,

            "verdict": summary.get("verdict"),

            # Drif analysis
            "energy_drift": accounting.get("energy_drift") if accounting else None,
            "momentum_drift": accounting.get("momentum_drift") if accounting else None,

            # Canonical truth
            "audit_ok": audit.get("verdict") == "PASS"
        })

    return jsonify(results)

@history_api_bp.route("/<int:sim_id>", methods=["DELETE"])
@login_required
def delete_simulation(sim_id):
    sim = Simulation.query.filter_by(
        id=sim_id,
        user_id=session["user_id"]
    ).first()

    if not sim:
        return jsonify({"error": "Simulation not found"}), 404

    db.session.delete(sim)
    db.session.commit()

    return jsonify({"status": "deleted"})
