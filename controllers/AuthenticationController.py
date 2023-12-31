from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from app import bcrypt
from models.User import User

controller = Blueprint(
    "authentication_controller", __name__, template_folder="templates"
)


@controller.route("/login", methods=["GET"])
def login():
    return render_template("authentication/login.html")


@controller.route("/register", methods=["GET"])
def register():
    return render_template("authentication/register.html")


@controller.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for("authentication_controller.login"))


@controller.route("/register", methods=["POST"])
def register_post():
    """
    Registers a new user with the given name, username, password, and password confirmation.
    If any required field is missing, an error message is flashed and the user is redirected to the registration page.
    If the password and password confirmation do not match, an error message is flashed and the user is redirected to the registration page.
    If the username already exists, an error message is flashed and the user is redirected to the registration page.
    Otherwise, the user is created, logged in, and redirected to the registration success page.
    """
    required_fields = ["name", "username", "password", "password_confirmation"]

    for field in required_fields:
        if field not in request.form:
            flash(f"Required field {field} is missing", "error")
            return redirect(url_for("authentication_controller.register"))

    name = request.form["name"]
    username = request.form["username"]
    password = request.form["password"]
    password_confirmation = request.form["password_confirmation"]

    if password != password_confirmation:
        flash("Passwords do not match", "error")
        return redirect(url_for("authentication_controller.register"))

    user = User().find(username)

    if user is not None:
        flash("Username already exists", "error")
        return redirect(url_for("authentication_controller.register"))

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(email=username, password=pw_hash, name=name,
                type="USER", state="APPROVAL_REQUIRED")

    user.insert()

    login_user(user)

    flash("Account created successfully", "success")

    return render_template("authentication/register.html")


@controller.route("/login", methods=["POST"])
def login_post():
    """
    Logs in a user with the provided username and password.

    Returns:
        A redirect to the dashboard if the login is successful, otherwise a redirect to the login page with an error message.
    """
    required_fields = ["username", "password"]

    for field in required_fields:
        if field not in request.form:
            flash(f"Required field {field} is missing", "error")
            return redirect(url_for("authentication_controller.login"))

    username = request.form["username"]
    password = request.form["password"]

    user = User().find(username)

    if user is None:
        flash(
            "The username or password you entered is incorrect [username]", "error")
        return redirect(url_for("authentication_controller.login"))

    # if user.get_state() == "APPROVAL_REQUIRED":
    #     flash("Your account is not approved yet", "error")
    #     return redirect(url_for("authentication_controller.login"))

    if user.get_state() == "INACTIVE" or user.get_state() == "DELETED":
        flash("Your account is not active. Kindly reach out to an administrator", "error")
        return redirect(url_for("authentication_controller.login"))

    password_correct = bcrypt.check_password_hash(user.password, password)

    if not password_correct:
        flash("The username or password you entered is incorrect", "error")
        return redirect(url_for("authentication_controller.login"))

    login_user(user, remember=True)

    return redirect(url_for("home_controller.dashboard"))
