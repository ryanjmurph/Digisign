import bcrypt
from flask import Blueprint, request, flash, redirect, render_template, url_for

from models.User import User

controller = Blueprint(
    "authentication_controller", __name__, template_folder="templates"
)


@controller.route("/login", methods=["GET"])
def login():
    return render_template("authentication/login.html")


@controller.route("/login", methods=["POST"])
def login_post():
    required_fields = ["username", "password"]

    for field in required_fields:
        if field not in request.form:
            flash(f"Required field {field} is missing", "error")
            return redirect(url_for("authentication_controller.login"))

    username = request.form["username"]
    password = request.form["password"]

    user = User().find(username)

    if user == None:
        flash("The username or password you entered is incorrect", "error")
        return redirect(url_for("authentication_controller.login"))

    pw_hash = bcrypt.generate_password_hash(password)
    password_correct = bcrypt.check_password_hash(pw_hash, password)

    if not password_correct:
        flash("The username or password you entered is incorrect", "error")
        return redirect(url_for("authentication_controller.login"))

    return redirect(url_for("home_controller.index"))
