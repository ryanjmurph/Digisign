import datetime
from flask import Blueprint, redirect, render_template,request, url_for
from models.GroupModerator import GroupModerator
from models.Post import Post
from flask_login import current_user, login_required

from models.User import User

controller = Blueprint("home_controller", __name__, template_folder="templates")


@controller.route("/", methods=["GET"])
def welcome_page():
    return redirect(url_for("home_controller.dashboard"))


@controller.route("dashboard", methods=["GET"])
def dashboard():
    permissions = {
        "can_view_moderation_actions": False,
        "can_view_devices_online": False,
    }

    counts = {
        "active_posts_count": 0,
        "device_online_count": 0,
        "pending_posts_count": 0,
        "pending_users_count": 0,
    }

    if current_user.get_type() == "ADMINISTRATOR":
        permissions["can_view_moderation_actions"] = True
        permissions["can_view_devices_online"] = True

        counts["pending_posts_count"] = Post().get_pending_posts_count()
        counts["pending_users_count"] = len(User().get_pending_users())

        counts["active_posts_count"] = len(Post().get_active_posts())

    elif current_user.isModerator():
        group_ids = GroupModerator(user=current_user).getGroupsCanModerate()
        counts["pending_posts_count"] = Post().get_pending_posts_count(group_ids=group_ids)
    else:
        counts["active_posts_count"] = len(Post().get_active_posts(user_id=current_user.id))
        
    
    return render_template("home/dashboard.html",permissions=permissions, counts=counts)
