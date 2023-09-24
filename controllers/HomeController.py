from flask import Blueprint, redirect, render_template,url_for
from flask_login import current_user

from models.Post import Post
from models.User import User
from models.GroupDevices import GroupDevices
from models.GroupModerator import GroupModerator
from models.Group import Group

from policies.DisplayPolicy import Policy as DisplayPolicy

controller = Blueprint("home_controller", __name__, template_folder="templates")


@controller.route("/", methods=["GET"])
def welcome_page():
    return redirect(url_for("home_controller.dashboard"))

@controller.route("/display", methods=["GET"])
def display():
    if not DisplayPolicy(current_user).can_view_displays():
        error_message="Only devices  are allowed to access this page"
        return render_template("home/error.html", error_message=error_message)
    
    # get posts the device can access
    group = Group()
    group_ids = GroupDevices(device_id=current_user.id).get_groups_for_device(current_user.id)
    posts = Post().get_active_posts(group_ids=group_ids)
    print(posts)

    
    ids = [item['id'] for item in posts]
    display_times = [item['display_time'] for item in posts]

    colors = []
    for id in ids: 
        array = group.getGroupID(id)
        number = array[0]["group_id"]
        colordict = group.getColors(number)
        colors.append(colordict[0]["color"])

    colors = ["#00008B","#7FFFD4"]

    return render_template("home/display.html", posts=posts,colors = colors)


@controller.route("dashboard", methods=["GET"])
def dashboard():

    if current_user.get_type() == "DEVICE":
        return redirect(url_for("home_controller.display"))

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
