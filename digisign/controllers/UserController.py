from flask import Blueprint, render_template, request, redirect, url_for
from models.User import User
from datetime import datetime
import bcrypt

controller = Blueprint("users", __name__, template_folder="templates")


@controller.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_email = request.form["login_email"]
        login_password = request.form["login_password"]

        user = User()
        result = user.find(login_email)
        
        if result and bcrypt.checkpw(login_password.encode("utf-8"), result["password"].encode("utf-8")):
            return "Login successful"
        else:
            error_message = "Invalid email or password"
            return render_template("login.html", error_message=error_message)
    else:
        return render_template("login.html")



@controller.route("/new_user", methods=["GET", "POST"])
def new_user():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        new_user = User(
            name=name,
            email=email,
            password=password,
            type="USER",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        if new_user.find(email) == "not found":
            new_user.insert()
            return "Account created"
        else:
            error_message = "Email already in use"
            return render_template("create_account.html", error_message=error_message)
    else:
        return render_template("create_account.html")


