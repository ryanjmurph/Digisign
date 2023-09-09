# Pius Gumo
# 14/08/2023
# This is the controller for creating, reading, updating and deleting posts

import os
from flask import Blueprint, redirect, render_template, abort, request, url_for
from flask_login import login_required
from models.Post import Post
from models.Group import Group
from models.User import User

controller = Blueprint("posts", __name__, template_folder="templates")


@controller.route("/", methods=["GET"])
def index():
    posts = Post.all()
    return render_template("posts/index.html", posts=posts)

@controller.route("/<int:id>/edit", methods=["GET", "POST"])


@controller.route("/<int:id>/edit", methods=["GET", "POST"])
def show_edit_page(id):
    # check if _method is set in the form and the value is PUT
    if request.method == "POST" and request.form["_method"].upper() == "PUT":
        return update_post(request, id)

    post = Post.find(id)
    return render_template("posts/edit.html", post=post, groups=Group.all())


def update_post(request, id):
    # check for the required fields
    required_fields = ["title", "start_date", "end_date", "post_type"]

    for field in required_fields:
        if field not in request.form:
            print(f"Required field {field} is missing")
            return abort(400, f"Required field {field} is missing")

    post = Post.find(id)

    if post is None:
        return abort(404, f"Post with id {request.form['id']} not found")

    # create an attributes dictionary with the new values
    attributes = {
        "title": request.form["title"],
        "type": "",
        "start_date": request.form["start_date"],
        "end_date": request.form["end_date"],
    }

    # check what attributes have changed
    updates = {}

    for key in attributes:
        if attributes[key] != getattr(post, key):
            updates[key] = attributes[key]

    removePreviousImage = False

    # check to see if post type changed from image
    if post.type == "IMAGE" and request.form["post_type"] != "image":
        updates["image_link"] = None
        os.remove(post.image_link)

    # available post types image,html,link
    if request.form["post_type"] == "image":
        updates["type"] = "IMAGE"

        newimage = request.files["image"]

        # if image is not provided, only update the other fields
        if newimage.filename == "":
            pass
        else:
            updates["image_link"] = f"static/images/{request.files['image'].filename}"
            if post.type == "IMAGE":
                removePreviousImage = True

            # store the image in the static/images folder
            image = request.files["image"]
            image.save(f"static/images/{image.filename}")

        if removePreviousImage:
            # delete the previous image
            if "image" in request.files:
                os.remove(post.image_link)

        # update the post
        post.updates(updates)

    elif request.form["post_type"] == "html":
        updates["type"] = "HTML"
        updates["html_content"] = request.form["htmlContent"]
        post.updates(updates)

    elif request.form["post_type"] == "link":
        updates["type"] = "WEB_LINK"
        updates["web_link"] = request.form["webLink"]
        post.updates(updates)

    # save the post groups
    if "post_groups" in request.form:
        post.save_groups(request.form["post_groups"])

    # redirect to the post create page with a success message
    return redirect(url_for("posts.list_posts"))


@controller.route("/new", methods=["POST"])
def create():
    # check for the required fields
    file_path = "user_id.txt"
    userID = ""
    try:
        with open(file_path, "r") as file:
            userID = file.read()
    except FileNotFoundError:
        pass

    required_fields = ["title", "start_date", "end_date", "post_type"]

    for field in required_fields:
        if field not in request.form:
            return abort(400, f"Required field {field} is missing")

    # available post types image,html,link
    if request.form["post_type"] == "image":
        # store the image in the static/images folder
        image = request.files["image"]
        image.save(f"static/images/{image.filename}")

        # create the post
        post = Post(
            title=request.form["title"],
            type="IMAGE",
            startDate=request.form["start_date"],
            endDate=request.form["end_date"],
            imageLink=f"static/images/{image.filename}",
            state="DRAFT",
            created_by= userID
        )

        # save the post
        post.insert()

    elif request.form["post_type"] == "html":
        # create the post
        post = Post(
            title=request.form["title"],
            type="HTML",
            startDate=request.form["start_date"],
            endDate=request.form["end_date"],
            htmlContent=request.form["htmlContent"],
            state="DRAFT",
            created_by= userID
        )
        # save the post
        post.insert()

    elif request.form["post_type"] == "link":
    # create the post
        post = Post(
        title=request.form["title"],
        type="WEB_LINK",
        startDate=request.form["start_date"],
        endDate=request.form["end_date"],
        webLink=request.form["web_link"],  # Update this line
        state="DRAFT",
        created_by= userID
        )
        # Check if the "Add QR code" checkbox is checked
        add_qr_code = request.form.get("add_qr_code")
        if add_qr_code:
            webLink=request.form["web_link"]
            post.createQR(webLink,True)

        else:
            webLink=request.form["web_link"]
            post.createQR(webLink,False)

        post.insert()


    # save the post groups
    if "post_groups" in request.form:
        post.save_groups(request.form["post_groups"])

    # redirect to the post create page with a success message
    return render_template(
        "posts/create.html", success="Post created successfully", groups=Group.all()
    )


@controller.route("/new", methods=["GET"])
def new():
    groups = Group().all()
    # return the form in templates/posts/create.html
    return render_template("posts/create.html", groups=groups)


@controller.route("/<int:id>/approve-action", methods=["GET"])
def approve_action(id):
    # get action from the query string
    action = request.args["action"]

    # check if the action is valid
    if action not in ["APPROVE", "WITHDRAW"]:
        return abort(400, f"Invalid action {action} provided")

    # get the post
    post = Post.find(id)

    if not post is None:
        updated_state = "APPROVED" if action == "APPROVE" else "WITHDRAWN"
        updates = {"state": updated_state}
        post.updates(updates)

    else:
        return abort(404, f"Post with id {id} not found")

    # redirect to /posts/admin-view
    return redirect(url_for("posts.list_posts"))


@controller.route("/user-view", methods=["GET"])
def list_users_posts():
    # check if filter is set in the query string
    user_instance = User()
    user = user_instance.readFromTxt()
    activeFilters = ""

    if "filter" in request.args:
        # check for filter by name
        if request.args["filter"] == "title":
            posts = Post.filter_by_title(request.args["search"])
            activeFilters = "title=" + request.args["search"]

        # check for filter by state
        if request.args["filter"] == "state":
            posts = Post.filter_by_state(request.args["search"])
            activeFilters = "state=" + request.args["search"]

        # check for filter by id
        if request.args["filter"] == "id":
            posts = Post.filter_by_id(request.args["search"])
            activeFilters = "id=" + request.args["search"]
    else:
        posts = Post.postWithID(user.get_id())

    # return the form in templates/posts/create.html
    return render_template(
        "posts/admin/list.html", posts=posts, activeFilters=activeFilters
    )

@controller.route("/admin-view", methods=["GET"])
@login_required
def list_posts():
    # check if filter is set in the query string
    user_instance = User()
    user = user_instance.readFromTxt()
    
    print(user.get_type,"this is the user type")

    if (user.get_type()!= "ADMINISTRATOR"):
        error_message = "This tab can only be accessed by an admin user"
        return render_template("users/error.html", error_message = error_message)


    activeFilters = ""

    if "filter" in request.args:
        # check for filter by name
        if request.args["filter"] == "title":
            posts = Post.filter_by_title(request.args["search"])
            activeFilters = "title=" + request.args["search"]

        # check for filter by state
        if request.args["filter"] == "state":
            posts = Post.filter_by_state(request.args["search"])
            activeFilters = "state=" + request.args["search"]

        # check for filter by id
        if request.args["filter"] == "id":
            posts = Post.filter_by_id(request.args["search"])
            activeFilters = "id=" + request.args["search"]
    else:
        posts = Post.all()

    # return the form in templates/posts/create.html
    return render_template(
        "posts/admin/list.html", posts=posts, activeFilters=activeFilters
    )


@controller.route("/display")
def display():
    folder_path = "static/images"  


    files_and_dirs = os.listdir(folder_path)
    filenames = [file for file in files_and_dirs if os.path.isfile(os.path.join(folder_path, file))]
    print(filenames)
    return render_template("display.html", filenames = filenames)
    
