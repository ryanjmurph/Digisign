from flask import Blueprint, flash, jsonify, make_response, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from models.Post import Post
from models.User import User
from datetime import datetime
import bcrypt

from policies.UserPolicy import Policy as UserAccessPolicy

controller = Blueprint("users", __name__, template_folder="templates")


# TODO : Legacy, to decomission
@controller.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_email = request.form["login_email"]
        login_password = request.form["login_password"]

        user = User()
        result = user.find(login_email)

        if result and bcrypt.checkpw(
            login_password.encode("utf-8"), result["password"].encode("utf-8")
        ):
            return "Login successful"
        else:
            error_message = "Invalid email or password"
            return render_template("login.html", error_message=error_message)
    else:
        return render_template("login.html")


# TODO : Legacy, to decomission
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
            updated_at=datetime.now(),
        )

        if new_user.find(email) == "not found":
            new_user.insert()
            return "Account created"
        else:
            error_message = "Email already in use"
            return render_template("create_account.html", error_message=error_message)
    else:
        return render_template("create_account.html")


@controller.route("/admin-view", methods=["GET"])
@login_required
def list_users():
    
    policy = UserAccessPolicy(user = current_user)

    if policy.canViewAllUsers():
        users = User().all()
        return render_template("users/list.html", users=users)
    else:
        user = current_user 
        id = user.get_id()
        if user.get_type() == "USER" or user.get_type() == "ADMINISTRATOR":
            posts = [] 
            posts = Post().where("created_by", id).get()
        return render_template("users/edit.html", user=user, posts=posts)

    
    
    # user = user_instance.readFromTxt()
    # users = user.all()
    
    # if (user.get_type()!= "ADMINISTRATOR"):
    #     error_message = "This tab can only be accessed by an admin user"
    #     return render_template("users/error.html", error_message = error_message)

    


@controller.route("/<int:id>/edit", methods=["GET"])
@login_required
def view_user(id):

    policy = UserAccessPolicy(current_user)

    if not policy.canEditUser(id):
        error_message = "You do not have permission to edit this user"
        return render_template("users/error.html", error_message=error_message)

    user = User().findById(id)

    posts = []
    print(f"User type: {user.get_type()}")
    if user.get_type() == "USER" or user.get_type() == "ADMINISTRATOR":
        posts = Post().where("created_by", id).get()
    print(posts)
    return render_template("users/admin/edit.html", user=user, posts=posts)


@controller.route("/<int:id>/update", methods=["POST"])
@login_required
def update_user(id):
    
    policy = UserAccessPolicy(current_user)

    if not policy.canEditUser(id):
        error_message = "You do not have permission to edit this user"
        return render_template("users/error.html", error_message=error_message)

    user = User().findById(id)

    fields_changing = {}

    fields_available = ["name", "email", "type", "password","state"]
    for field in fields_available:
        if request.form[field]:
            # check the attribute in the user object. If it is different from the one in the form, update it
            if getattr(user, field) != request.form[field]:
                fields_changing[field] = request.form[field]

    if fields_changing:
        try:
            user.update(fields_changing)
        except Exception as e:
            flash("An error occured, kindly try again", "error")
            return redirect(url_for("users.view_user", id=id))

    flash("User updated successfully", "success")
    return redirect(url_for("users.view_user", id=id))
