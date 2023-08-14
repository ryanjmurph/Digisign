# Pius Gumo
# 14/08/2023
# This is the controller for creating, reading, updating and deleting posts

from flask import Blueprint, render_template
from models.Post import Post
from models.Group import Group

controller = Blueprint("posts", __name__, template_folder="templates")


@controller.route("/", methods=["GET"])
def index():
    posts = Post.all()
    return render_template("posts/index.html", posts=posts)


@controller.route("/new", methods=["GET"])
def new():
    groups = Group.all()
    # return the form in templates/posts/create.html
    return render_template("posts/create.html", groups=groups)
