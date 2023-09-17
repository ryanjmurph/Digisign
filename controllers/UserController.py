from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from models.Post import Post
from models.User import User
from app import bcrypt

from policies.UserPolicy import Policy as UserAccessPolicy

controller = Blueprint("users", __name__, template_folder="templates")


@controller.route("/admin-view", methods=["GET"])
@login_required
def list_users():
    policy = UserAccessPolicy(user=current_user)

    if policy.canViewAllUsers():
        users = User().all()
        if policy.canApproveUsers():
            pending_users = User().where("state", "APPROVAL_REQUIRED").get()
            return render_template("users/list.html", users=users, pending_user_approvals=pending_users)

        return render_template("users/list.html", users=users)
    else:
        user = current_user
        if user.get_type() == "USER" or user.get_type() == "ADMINISTRATOR":
            posts = []
            posts = Post().where("created_by", id).get()
            print(posts)
        return render_template("users/edit.html", user=user, posts=posts)


@controller.route("/create/user", methods=["GET"])
@login_required
def create_user():
    policy = UserAccessPolicy(current_user)

    if not policy.can_create_user():
        error_message = "You do not have permission to create a user"
        return render_template("errors/401.html", error_message=error_message)

    return render_template("users/admin/create.html")


@controller.route("/create/user", methods=["POST"])
@login_required
def store_user():
    policy = UserAccessPolicy(current_user)
    if not policy.can_create_user():
        error_message = "You do not have permission to create a user"
        return render_template("errors/401.html", error_message=error_message)

    name = request.form["name"]
    email = request.form["username"]
    password = request.form["password"]
    password_confirmation = request.form["password_confirmation"]
    type = request.form["type"]

    if password != password_confirmation:
        flash("Passwords do not match", "error")
        return redirect(url_for("users.create_user"))

    user = User().where("email", email).first()
    if user:
        flash("User already exists", "error")
        return redirect(url_for("users.create_user"))
    pw_hash = bcrypt.generate_password_hash(password)

    user = User(email=email, name=name, password=pw_hash,
                type=type, state="APPROVED")
    user.insert()
    flash("User created successfully", "success")
    return redirect(url_for("users.list_users"))


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

    fields_changing = {
        "name": request.form["name"],
        "email": request.form["username"],
        "type": request.form["type"],
        "state": request.form["state"]
    }

    if request.form["password"] != "":
        fields_changing["password"] = bcrypt.generate_password_hash(
            request.form["password"])
        
    user.update(fields_changing)
    flash("User updated successfully", "success")
    return redirect(url_for("users.view_user", id=id))
