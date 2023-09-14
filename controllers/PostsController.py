# Pius Gumo
# 14/08/2023
# This is the controller for creating, reading, updating and deleting posts

import os
from flask import Blueprint, redirect, render_template, abort, request, url_for
from flask_login import current_user, login_required
from models.Post import Post
from models.Group import Group
from models.User import User

from policies.PostPolicy import Policy as PostPolicy

controller = Blueprint("posts", __name__, template_folder="templates")


@controller.route("/", methods=["GET"])
@login_required
def index():
    posts = Post().all()
    return render_template("posts/index.html", posts=posts)


@controller.route("/<int:id>/edit", methods=["GET"])
@login_required
def show_edit_page(id):
    post = Post().find(id)

    if not PostPolicy(current_user).canManagePost(post):
        message = "You are not authorized to view this post"
        return render_template("errors/401.html", error_message=message)
    
    permissions = [
        canApprovePost := PostPolicy(current_user).canApprovePost(post),
        canWithdrawPost := PostPolicy(current_user).canEditPost(post),
        canEditPost := PostPolicy(current_user).canEditPost(post),
    ]

    return render_template("posts/edit.html", post=post, groups=Group.all(),permissions=permissions)


@controller.route("/<int:id>/edit", methods=["POST"])
def update_post(id):
    post = Post().find(id)
    if post is None:
        return abort(404, f"Post with id {id} not found")

    if not PostPolicy(current_user).canEditPost(post):
        return render_template("errors/401.html", error_message="You are not authorized to view this post")

    # create an attributes dictionary with the new values
    attributes = {
        "title": request.form["title"],
        "type": "",
        "start_date": request.form["start_date"],
        "end_date": request.form["end_date"],
        "state": request.form["state"],
    }

    # set only the fillable attributes in this request
    post.fillable = ["title", "type", "start_date", "end_date", "state"]

    remove_previous_image = False
    previous_image_link = post.image_link

    # check to see if post type changed from image
    if post.type == "IMAGE" and request.form["post_type"] != "image":
        post.fillable.append("image_link")
        post.image_link = None
        os.remove(post.image_link)

    # if new post type is an image, check whether image was provided
    # and update the image link
    # otherwise update only the other fields
    if request.form["post_type"] == "image":
        attributes["type"] = "IMAGE"

        new_image = request.files["image"]

        # if no new image was provided, do nothing
        if new_image.filename == "":
            pass
        else:
            # if a new image was provided, update the image link
            attributes["image_link"] = f"static/images/{new_image.filename}"
            # a new image was provided so remove the previous image
            if post.type == "IMAGE":
                remove_previous_image = True

            # store the image in the static/images folder
            image = request.files["image"]
            image.save(f"static/images/{image.filename}")

    elif request.form["post_type"] == "html":
        attributes["type"] = "HTML"
        attributes["html_content"] = request.form["htmlContent"]
        post.fillable.append("html_content")

    elif request.form["post_type"] == "link":
        attributes["type"] = "WEB_LINK"
        attributes["web_link"] = request.form["webLink"]
        post.fillable.append("web_link")

    # update the post
    post.set_dict_to_model_attributes(attributes)
    post.update()

    # remove previous image if necessary
    if remove_previous_image:
        os.remove(previous_image_link)

    # save the post groups
    if "post_groups" in request.form:
        post.save_groups(request.form["post_groups"])

    # redirect to the post create page with a success message
    return redirect(url_for("posts.list_posts"))


@controller.route("/new", methods=["POST"])
@login_required
def create():
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
            created_by=current_user.get_id()
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
            created_by=current_user.get_id()
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
            created_by=current_user.get_id()
        )
        # Check if the "Add QR code" checkbox is checked
        add_qr_code = request.form.get("add_qr_code")
        if add_qr_code:
            web_link = request.form["web_link"]
            post.createQR(web_link, True)

        else:
            web_link = request.form["web_link"]
            post.createQR(web_link, False)

        post.insert()

    # save the post groups
    if "post_groups" in request.form:
        post.save_groups(request.form["post_groups"])

    # redirect to the post create page with a success message
    return render_template(
        "posts/create.html", success="Post created successfully", groups=Group.all()
    )


@controller.route("/new", methods=["GET"])
@login_required
def new():
    groups = Group().all()
    # return the form in templates/posts/create.html
    return render_template("posts/create.html", groups=groups)


@controller.route("/<int:id>/approve-action", methods=["GET"])
@login_required
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


@controller.route("/admin-view", methods=["GET"])
@login_required
def list_posts():

    user = current_user
    policy = PostPolicy(user)

    if policy.canViewAdminPostList():
        userposts = Post().all()
    elif policy.canViewPostList():
        userposts = Post.postsCreatedBy(current_user.get_id())
    else:
        error_message = "You are not authorized to view this page"
        return render_template("errors/401.html", error_message=error_message)

    active_filters = ""

    if "filter" in request.args:
        # check for filter by name
        if request.args["filter"] == "title":
            posts = Post.filter_by_title(request.args["search"])
            active_filters = "title=" + request.args["search"]

        # check for filter by state
        if request.args["filter"] == "state":
            posts = Post.filter_by_state(request.args["search"])
            active_filters = "state=" + request.args["search"]

        # check for filter by id
        if request.args["filter"] == "id":
            posts = Post.filter_by_id(request.args["search"])
            active_filters = "id=" + request.args["search"]
    else:
        posts = userposts

    # return the form in templates/posts/create.html
    return render_template(
        "posts/admin/list.html", posts=posts, activeFilters=active_filters
    )


@controller.route("/display")
@login_required
def display():
    folder_path = "static/images"  # Replace this with the path to your folder

    files_and_dirs = os.listdir(folder_path)
    filenames = [file for file in files_and_dirs if os.path.isfile(
        os.path.join(folder_path, file))]
    print(filenames)
    return render_template("display.html", filenames=filenames)
