# Pius Gumo
# 14/08/2023
# This is the controller for creating, reading, updating and deleting posts

import os
from flask import Blueprint, redirect, flash,render_template, abort, request, url_for
from flask_login import current_user, login_required
from models.Post import Post
from models.Group import Group

from policies.PostPolicy import Policy as PostPolicy
from policies.UserPolicy import Policy as UserPolicy

controller = Blueprint("posts", __name__, template_folder="templates")


@controller.route("/", methods=["GET"])
@login_required
def index():
    posts = Post().all()
    return render_template("posts/index.html", posts=posts)


@controller.route("/<int:id>/edit", methods=["GET"])
@login_required
def edit(id):
    """
    Edit a post with the given id.

    Args:
        id (int): The id of the post to edit.

    Returns:
        str: The rendered HTML template for editing the post.

    Raises:
        HTTPException: If the user is not authorized to edit the post.
    """
    post = Post().find(id)

    post.groups = post.get_groups()

    # extract the group_ids from post_groups
    post.groups = [group["group_id"] for group in post.groups]

    if not PostPolicy(current_user).canManagePost(post):
        message = "You are not authorized to view this post"
        return render_template("errors/401.html", error_message=message)
    
    permissions = [
        canApprovePost := PostPolicy(current_user).canApprovePost(post),
        canWithdrawPost := PostPolicy(current_user).canEditPost(post),
        canEditPost := PostPolicy(current_user).canEditPost(post),
    ]

    return render_template("posts/edit.html", post=post, groups=Group.all(),permissions=permissions)

@controller.route("/<int:id>/postState", methods=["POST"])
def update_post_state(id):
    """
    Update the state of a post with the given id.

    Args:
        id (int): The id of the post to update.

    Returns:
        A redirect to the edit page of the updated post.

    Raises:
        404 error if the post with the given id is not found.
        401 error if the current user is not authorized to manage or edit the post.
    """
    post = Post().find(id)
    if post is None:
        return abort(404, f"Post with id {id} not found")
    
    if not PostPolicy(current_user).canManagePost(post):
        return render_template("errors/401.html", error_message="You are not authorized to manage this post")
    
    # determine allowed states depending on the current state ad the current user

    if PostPolicy(current_user).canApprovePost(post):
        allowed_states = ["APPROVED","WITHDRAWN","PUBLISHED"]
        if request.form["state"] in allowed_states:
            post.update({"state":request.form["state"]})
            flash("Post state updated successfully","success")
        else:
            flash("You are not authorized to change the state of this post","error")
    elif PostPolicy(current_user).canEditPost(post):
        allowed_states = ["DRAFT","WITHDRAWN","PUBLISHED"]
        if request.form["state"] in allowed_states:
            if request.form["state"] == "PUBLISHED" :
                if PostPolicy(current_user).postRequiresAnyApproval(post):
                    flash("Post sent for approval","success")
                    post.updates({"state":"PENDING_APPROVAL"})
                else:
                    flash("Post published successfully","success")
                    post.updates({"state":request.form["state"]})
            flash("Post state updated successfully","success")
            post.updates({"state":request.form["state"]})
        else:
            flash("You are not authorized to change the state of this post","error")

    return redirect(url_for("posts.edit", id=post.id))



@controller.route("/<int:id>/edit", methods=["POST"])
def update_post(id):
    """
    Updates an existing post with the given `id` using the data submitted in the request form.
    If the post is not found, returns a 404 error.
    If the current user is not authorized to edit the post, returns a 401 error.
    If the post type is changed from "IMAGE" to something else, removes the previous image.
    If the post type is changed to "IMAGE" and a new image is provided, saves the new image and updates the image link.
    If the post type is "HTML" or "WEB_LINK", updates the corresponding fields.
    Saves the post groups if they are included in the request form.
    Redirects to the list of posts with a success message.
    """
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
        "display_time": request.form["display_time"],
    }

    # set only the fillable attributes in this request
    post.fillable = ["title", "type", "start_date", "end_date", "state","display_time"]

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
        post.save_groups(request.form.getlist("post_groups"))

    # redirect to the post create page with a success message
    return redirect(url_for("posts.list_posts"))


@controller.route("/new", methods=["POST"])
@login_required
def create():
    """
    Creates a new post based on the form data submitted by the user.

    All required fields are checked to ensure they are present in the form data
    before the Post is saved to the DB.
    """
    required_fields = ["title", "start_date", "end_date", "post_type","display_time"]

    for field in required_fields:
        if field not in request.form:
            return abort(400, f"Required field {field} is missing")

    


    # available post types image,html,link
    if request.form["post_type"] == "image":
        """
        If the post type is "image", the function also saves the image file to the
        static/images folder and updates the post object with the image link.
        """
        # store the image in the static/images folder
        image = request.files["image"]

        # if no new image was provided, return an error
        if image.filename == "":
            flash("No image was provided","error")
            return redirect(url_for("posts.new"))


        image.save(f"static/images/{image.filename}")

        # create the post
        post = Post(
            title=request.form["title"],
            type="IMAGE",
            startDate=request.form["start_date"],
            endDate=request.form["end_date"],
            imageLink=f"static/images/{image.filename}",
            state="DRAFT",
            created_by=current_user.get_id(),
            display_time = request.form["display_time"]
        )
        # if QR code is present in the form, create a QR code, store it in
        # the static/images folder and update the post
        if "add_qr_code" in request.form:
            post.create_qr("image_link")

        # save the post
        post.save()

    elif request.form["post_type"] == "html":
        """
        If the post type is "html", the function updates the post object with the
        HTML content specified in the form data.
        """
        # create the post
        post = Post(
            title=request.form["title"],
            type="HTML",
            startDate=request.form["start_date"],
            endDate=request.form["end_date"],
            htmlContent=request.form["htmlContent"],
            state="DRAFT",
            created_by=current_user.get_id(),
            display_time = request.form["display_time"]
        )
        # save the post
        post.save()

    elif request.form["post_type"] == "link":
        """
        If the post type is "link", the function updates the post object with the
        web link specified in the form data.
        """
        # create the post
        post = Post(
            title=request.form["title"],
            type="WEB_LINK",
            startDate=request.form["start_date"],
            endDate=request.form["end_date"],
            webLink=request.form["web_link"],  # Update this line
            state="DRAFT",
            created_by=current_user.get_id(),
            display_time = request.form["display_time"]
        )
        if "add_qr_code" in request.form:
            post.create_qr("web_link")

        post.save()

    # save the post groups to ensure an association is created
    if "post_groups" in request.form:
        post.save_groups(request.form["post_groups"])

    flash("Post created successfully. Publish the post once you are ready for it to be viewable","success") 

    # redirect to the post create page with a success message
    return redirect(url_for("posts.edit", id=post.id))


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
    post = Post().find(id)

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
    """
    This function lists all the posts that a user is authorized to view based on their role and permissions.
    It also allows filtering of posts by title, state, or id.
    """
    user = current_user
    policy = PostPolicy(user)

    if policy.canViewAdminPostList():
        userposts = Post().all()
    elif policy.canViewPostList():
        userposts = Post().postsCreatedBy(current_user.get_id())
    else:
        error_message = "You are not authorized to view this page"
        return render_template("errors/401.html", error_message=error_message)

    active_filters = ""

    if "filter" in request.args:
        # check for filter by name
        if request.args["filter"] == "title":
            posts = Post().filter_by_title(request.args["search"])
            active_filters = "title=" + request.args["search"]

        # check for filter by state
        if request.args["filter"] == "state":
            posts = Post().filter_by_state(request.args["search"])
            active_filters = "state=" + request.args["search"]

        # check for filter by id
        if request.args["filter"] == "id":
            posts = Post().filter_by_id(request.args["search"])
            active_filters = "id=" + request.args["search"]
    else:
        posts = userposts

    # return the form in templates/posts/create.html
    return render_template(
        "posts/admin/list.html", posts=posts, activeFilters=active_filters
    )

