from flask import Blueprint, render_template

static_bp = Blueprint("static", __name__)

@static_bp.route("/about")
def about():
    return render_template("about.html")