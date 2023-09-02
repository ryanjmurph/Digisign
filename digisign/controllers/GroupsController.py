
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from models.Group import Group


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
    
