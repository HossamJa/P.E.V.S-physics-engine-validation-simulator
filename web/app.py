import os

import sqlite3
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from functools import wraps

# Core Fumctions
from cli_ui.cli import (
    choose_environment,
    choose_engine,
    define_state,
    run_simulation
)

from simulation.results.simulation_result import SimulationResult
from simulation.results.serializers import serialize_simulation


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Define the absolute path for the database file
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pevs.db")

# Check if the database file exists, otherwise create one
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.close()

# Configure CS50 Library to use SQLite database
db = SQL(f"sqlite:///{db_path}")

# Create the users table if its not there
db.execute("""
CREATE TABLE IF NOT EXISTS users (
           id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
           username TEXT NOT NULL, 
           hash TEXT NOT NULL
        );
""")

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
@login_required
def dashboard():
    # Get the current user id
    USER_ID = session.get("user_id")

    # Get Username of the current user 
    username = db.execute("SELECT username FROM users WHERE id = ?", USER_ID)[0]["username"]
    user_data = {
        "username": username,
    }
    return render_template("dashboard.html", user_data=user_data)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Get the username 
        username = request.form.get("username")
        # Check if the username is not blank
        if not username:
            return apology("Username is empty!")
        
        # Get the password
        password = request.form.get("password")
        # Check if the password is not blank
        if not password:
            return apology("Password is empty!")
        # Get password confirmation
        confirmation = request.form.get("confirmation")
        # Check if confirmation is not empty
        if not confirmation:
            return apology("Please confirm your password.")
        
        # Check if the password and confirmation match
        if confirmation != password:
            return apology("Password and Confirmation Don't Match")
        try:
            # Generate hash for the password to store it in db
            hash = generate_password_hash(password)
            # Store the username and pwhash in db
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            
            return redirect("/")
        
        except ValueError: # If the username already exist
            return apology("This username already exists.")
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Manage account info"""
    # Get the current user id 
    USER_ID = session.get("user_id")
    username = db.execute("SELECT username FROM users WHERE id = ?", USER_ID)[0]["username"]
    user_data = {
        "username": username,
    }
    message = {
        "message": "",
        }
    if request.method == "POST":
        current_pw = request.form.get("current_pw")
        new_pw = request.form.get("new_pw")
        confirm_pw = request.form.get("confirm_pw")
        if not current_pw or not new_pw or not confirm_pw:
            return apology("Missing a field!")

        current_hash = db.execute("SELECT hash FROM users WHERE id = ?", USER_ID)[0]["hash"]

        if not check_password_hash(current_hash, current_pw):
            return apology("Incorrect Password!")
        if new_pw != confirm_pw:
            return apology("New Password don't Match Confirmation Password!")
        
        new_hash = generate_password_hash(new_pw)
        
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, USER_ID)
        
        message["message"] = "Password Changed Successfully!"
        render_template("account.html", user_data=user_data, message=message)
    return render_template("account.html", user_data=user_data, message=message)

@app.route("/simulation", methods=["GET"])
@login_required
def simulation_page():
    return render_template("simulation.html")

@app.route("/api/simulation/run", methods=["POST"])
@login_required
def run_simulation_api():
    try:
        # --- ENVIRONMENT ---
        choice = request.form.get("environment")

        gravity_mass = float(request.form["gravity_mass"]) if choice == "3" else None
        gravity_source_position = (
            [
                float(request.form["gravity_source_x"]),
                float(request.form["gravity_source_y"]),
                float(request.form["gravity_source_z"]),
            ] if choice == "3" else None
        )
        G = float(request.form["G"]) if choice == "3" else None

        environment = choose_environment(choice, gravity_mass, gravity_source_position, G, ui=True)

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

        verdict, recorder = run_simulation(
            state=state,
            environment=environment,
            engine=engine,
            steps=int(request.form["steps"]),
            dt=float(request.form["dt"]),
            ui=True,
        )

        result = SimulationResult(verdict, recorder)
        return jsonify(serialize_simulation(result))

    except Exception as e:
        return jsonify({"error": str(e)}), 400
