from flask import Blueprint, render_template, request, redirect, session, flash
from app.extensions import db
from app.models.user import User
from app.helpers import error, login_required

bp = Blueprint("auth", __name__)

@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return error("All fields are required")

        if password != confirmation:
            return error("Passwords do not match")

        if User.query.filter_by(username=username).first():
            return error("Username already exists")

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        flash("You have successfully created your P.E.V.S account", "success")

        return redirect("/login")

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():

    session.pop("user_id", None)

    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form.get("username")
        ).first()

        if not user or not user.check_password(request.form.get("password")):
            return error("Invalid username or password")

        session["user_id"] = user.id
        return redirect("/dashboard")

    return render_template("login.html")



@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@bp.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    return render_template("dashboard.html", user_data={"username": user.username})


@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user = User.query.get(session["user_id"])
    message = ""

    if request.method == "POST":
        if not user.check_password(request.form.get("current_pw")):
            return error("Incorrect current password")

        if request.form.get("new_pw") != request.form.get("confirm_pw"):
            return error("Passwords do not match")

        user.set_password(request.form.get("new_pw"))
        db.session.commit()
        message = "Password updated"
        flash("Password updated successfully", "success")
    return render_template(
        "account.html",
        user_data={"username": user.username},
        message={"message": message},
    )
