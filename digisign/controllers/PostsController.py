# Pius Gumo
# 14/08/2023
# This is the controller for creating, reading, updating and deleting posts

from flask import Blueprint, render_template, abort, request
from models.Post import Post
from models.Group import Group

controller = Blueprint("posts", __name__, template_folder="templates")


@controller.route("/", methods=["GET"])
def index():
    posts = Post.all()
    return render_template("posts/index.html", posts=posts)


@controller.route("/new", methods=["POST"])
def create():
    # check for the required fields
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
            webLink=request.form["webLink"],
            state="DRAFT",
        )
        # save the post
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
    groups = Group.all()
    # return the form in templates/posts/create.html
    return render_template("posts/create.html", groups=groups)


@controller.route("/admin-view", methods=["GET"])
def list_posts():
    # check if filter is set in the query string
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
