
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from models.Group import Group
from models.User import User


controller = Blueprint("groups", __name__, template_folder="templates")

@controller.route("/create", methods=["GET"])
@login_required
def create():
    return render_template("groups/create.html")

@controller.route("/create", methods=["POST"])
@login_required
def create_post():
    required_fields = ["name"]
    moderation_required = False

    if "moderation_required" in request.form:
        moderation_required = True

    for field in required_fields:
        if field not in request.form:
            flash(f"Required field {field} is missing", "error")
            return redirect(url_for("groups.create"))
        
    name = request.form["name"]
    
    group = Group(name=name,moderation_required=moderation_required)
    group.save()

    return redirect(url_for("groups.index"))

@controller.route("/edit/<id>", methods=["GET"])
@login_required
def edit(id):
    group = Group().find(id)
    users = User().raw("SELECT id,name FROM users WHERE state = 'ACTIVE' AND type = 'USER'")
    return render_template("groups/edit.html", group=group,users=users)

@controller.route("/edit/<id>", methods=["POST"])
@login_required
def edit_post(id):
    group = Group().find(id)
    required_fields = ["name","description"]

    for field in required_fields:
        if field not in request.form:
            flash(f"Required field {field} is missing", "error")
            return redirect(url_for("groups.edit",id=id))

    moderator_id = None    
    moderation_required = False
    
    if "moderation_required" in request.form:
        moderation_required = True
        # check if the moderator_id is set
        if "moderator_id" not in request.form:
            flash(f"Required field moderator_id is missing", "error")
            return redirect(url_for("groups.edit",id=id))
        
        moderator_id = request.form["moderator_id"]

    name = request.form["name"]
    description = request.form["description"]
    
    changes = {
        "name": name,
        "description": description,
        "moderation_required": moderation_required,
        "moderator_id": moderator_id
    }

    group.update(changes)

    flash("Group updated successfully", "success")
    return redirect(url_for("groups.index"))



@controller.route("/admin-view", methods=["GET"])
@login_required
def index():
    groups = Group().all()

    for group in groups:
        # get count of posts attached to the group
        count = Group().getPostsCount(group["id"])
        group["posts_count"] = count

    return render_template("groups/list.html", groups=groups)
    
