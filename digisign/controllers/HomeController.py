from flask import Blueprint, render_template,request
from models.Post import Post

controller = Blueprint("home_controller", __name__, template_folder="templates")


@controller.route("/", methods=["GET"])
def welcome_page():
    return render_template("home/index.html")


@controller.route("dashboard", methods=["GET"])
def dashboard():
    userID = request.args.get("userID")
    post = Post()
    amount = post.noOfPosts(str(userID))
    pendingAmount = post.noOfPendingPosts(str(userID))
    print(amount)
    return render_template("home/dashboard.html",userID = userID, amount = amount, pendingAmount = pendingAmount)
