
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required,current_user
from models.Group import Group
from models.GroupModerator import GroupModerator
from models.User import User
from models.GroupDevices import GroupDevices as GroupDevice
from policies.UserPolicy import Policy as UserAccessPolicy


controller = Blueprint("groups", __name__, template_folder="templates")

@controller.route("/create", methods=["GET"])
@login_required
def create():
    available_users = User().raw("SELECT id,name FROM users WHERE state = 'ACTIVE' AND (type = 'USER' OR type='ADMINISTRATOR')")
    available_devices = User().raw("SELECT id,name FROM users WHERE state = 'ACTIVE' AND type = 'DEVICE'")
    return render_template("groups/create.html",available_users=available_users,available_devices=available_devices)

@controller.route("/create", methods=["POST"])
@login_required
def create_post():
    required_fields = ["name","description"]
    moderation_required = False

    if "moderation_required" in request.form:
        moderation_required = True
        if "available_moderators" not in request.form:
            flash(f"Moderators have not been set", "error")
            return redirect(url_for("groups.create"))

    for field in required_fields:
        if field not in request.form:
            flash(f"Required field {field} is missing", "error")
            return redirect(url_for("groups.create"))
        
    name = request.form["name"]
    description = request.form["description"]
    color = request.form["color"]
    
    group = Group(name=name,description=description,moderation_required=moderation_required,color=color)
    group.save()

    return redirect(url_for("groups.index"))

@controller.route("/edit/<id>", methods=["GET"])
@login_required
def edit(id):
    group:Group = Group().find(id)
    users = User().raw("SELECT id,name FROM users WHERE state = 'ACTIVE' AND (type = 'USER' OR type='ADMINISTRATOR')")
    devices = User().raw("SELECT id,name FROM users WHERE type = 'DEVICE'")

    group.devices = group.get_devices()
    group.devices = [device["id"] for device in group.devices]

    moderators = group.getModerators();
    selected_moderators = ''
    for moderator in moderators:
        selected_moderators += str(moderator["id"]) + ','

    selected_moderators = selected_moderators[:-1]


    return render_template("groups/edit.html", group=group,available_users=users,available_moderators=moderators,selected_moderators=selected_moderators,devices=devices)

@controller.route("/edit/<id>/devices", methods=["POST"])
@login_required
def edit_devices(id):
    group = Group().find(id)
    devices = request.form.getlist("device_id")

    print("devices",devices)

    associate_devices_with_groups(group,devices)

    flash("Devices associated successfully", "success")
    return redirect(url_for("groups.edit",id=id))


@controller.route("/edit/<id>", methods=["POST"])
@login_required
def edit_post(id):
    group = Group().find(id)
    required_fields = ["name","description"]

    for field in required_fields:
        if field not in request.form:
            flash(f"Required field {field} is missing", "error")
            return redirect(url_for("groups.edit",id=id))

    
    moderation_required = False
    
    if "moderation_required" in request.form:
        moderation_required = True
        # check if the moderator_id is set
        if "selected_moderators" not in request.form or len(request.form["selected_moderators"].split(",")) == 0 :
            flash(f"No moderators have been selected", "error")
            return redirect(url_for("groups.edit",id=id))
        
        selected_moderators = request.form["selected_moderators"].split(",")
        associateModeratorsWithGroup(group,selected_moderators)

    name = request.form["name"]
    description = request.form["description"]
    color = request.form["color"]

    changes = {
        "name": name,
        "description": description,
        "moderation_required": moderation_required,
        "color": color
    }

    group.update(changes)

    flash("Group updated successfully", "success")
    return redirect(url_for("groups.edit",id=id))



@controller.route("/admin-view", methods=["GET"])
@login_required
def index():
    
    user = current_user
    policy = UserAccessPolicy(user)
    if policy.canviewAllGroups(): 
        groups = Group().all()

     # if the user is a moderator, only the groups that they moderate should be displayed   
    elif policy.isAModerator():
        anotherGroup = Group()
        
        array = []
        data = anotherGroup.groupByModerator(user.get_id())
        for i in range(0,len(data),1):
            val = data[i]
            number = val['group_id'] 
            array.append(number)        
    
        combined_data = []  

        for j in range(0, len(data), 1):
            value = anotherGroup.getGroupWithID(array[j])
            combined_data.extend(value) 
    
        groups = combined_data
    
    else:
        groups = []
    
    for group in groups:
        # get count of posts attached to the group
        count = Group().getPostsCount(group["id"])
        group["posts_count"] = count

    return render_template("groups/list.html", groups=groups)


def associate_devices_with_groups(group:Group,devices):
    # cast str to int and remove any empty values
    device_ids = [int(i) for i in devices if i != '' and int(i) != 0]

    print("device ids ",device_ids)

    current_devices = group.get_devices()

    device_ids_removed = []
    for device in current_devices:
        if device["id"] not in device_ids:
            device_ids_removed.append(device["id"])
            GroupDevice().raw(f"DELETE FROM {GroupDevice.table_name} WHERE group_id = {group.id} AND device_id = {device['id']}")

    device_ids_added = []
    for device_id in device_ids:
        if device_id not in [device["id"] for device in current_devices]:
            device_ids_added.append(device_id)
            GroupDevice(group_id=group.id,device_id=device_id).save()

def associateModeratorsWithGroup(group:Group,moderator_ids):

    # filter moderator_ids to only include integers and remove '' values or 0 values
    moderator_ids = [int(i) for i in moderator_ids if i != '' and int(i) != 0]

    print("moderator ids ",moderator_ids)

    added_moderators = []
    current_moderators = group.getModerators()

    for moderator_id in moderator_ids:
        user = User().findById(moderator_id)
        if not user:
            #throw an error
            print("User not found",moderator_id)
            continue
            
        pending_moderator = GroupModerator(group,user,current_moderators)
        if pending_moderator.addModerator():
            added_moderators.append(moderator_id)

    if moderator_ids == []:
        # remove all moderators
        for moderator in current_moderators:
            groupModerator = GroupModerator(group,User().findById(moderator["id"]),current_moderators)
            groupModerator.removeModerator()
            print("removed moderator",moderator["id"])

        return []
        

    # remove moderators that have been removed, ensure moderator casted
    for moderator in current_moderators:
        if moderator["id"] not in [int(i) for i in moderator_ids]:
            groupModerator = GroupModerator(group,User().findById(moderator["id"]),current_moderators)
            groupModerator.removeModerator()
            print("removed moderator",moderator["id"])

    return added_moderators
    
    
    
    

