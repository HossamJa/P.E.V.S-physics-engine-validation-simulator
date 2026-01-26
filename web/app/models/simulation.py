from app.extensions import db
from datetime import datetime

class Simulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    engine_type = db.Column(db.String(32))
    environment = db.Column(db.String(32))

    # JSON blobs
    setup = db.Column(db.JSON, nullable=False)
    accounting = db.Column(db.JSON, nullable=False)
    summary = db.Column(db.JSON, nullable=False)
    audit = db.Column(db.JSON, nullable=False)
    final_state = db.Column(db.JSON, nullable=False)
