from flask import Flask
from .config import Config
from .extensions import db, migrate
from .helpers import disable_cache

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if app.config.get("DISABLE_CACHE", True):
        @app.after_request
        def after_request(response):
            return disable_cache(response)

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import auth, simulation, history, static

    app.register_blueprint(auth.bp)
    app.register_blueprint(simulation.bp)
    app.register_blueprint(simulation.simulation_api_bp)

    app.register_blueprint(history.history_bp)
    app.register_blueprint(history.history_api_bp)

    app.register_blueprint(static.static_bp)

    return app
