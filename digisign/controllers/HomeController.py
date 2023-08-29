from flask import Blueprint, render_template


controller = Blueprint("home_controller", __name__, template_folder="templates")


@controller.route("/", methods=["GET"])
def welcome_page():
    return render_template("home/index.html")


@controller.route("dashboard", methods=["GET"])
def dashboard():
    return render_template("home/dashboard.html")
