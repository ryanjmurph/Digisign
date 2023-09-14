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
    posts = Post.all()
    return render_template("posts/index.html", posts=posts)


@controller.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def show_edit_page(id):
    # check if _method is set in the form and the value is PUT

    post = Post()
    link = post.getLink(id)
    time = post.getDisplayTimeFromDB(id)
    print(time)
    if link == None:
        link = ""
    if request.method == "POST" and request.form["_method"].upper() == "PUT":
        return update_post(request, id)

    post = Post.find(id)
    return render_template("posts/edit.html", post=post, groups=Group.all(), link = link, time = time )


def update_post(request, id):
    # check for the required fields
    required_fields = ["title", "start_date", "end_date", "post_type", "display_time"]

    
    

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
        "display_time" : request.form["display_time"]
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
            imgName = "static/images/"+ str(id)+"_"+  request.files['image'].filename
            updates["image_link"] = imgName
            if post.type == "IMAGE":
                removePreviousImage = True

            # store the image in the static/images folder
            image = request.files["image"]
            image.save(imgName)

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
        
        add_qr_code = request.form.get("add_qr_code")
        post.removeFromDevice(id)

        if add_qr_code:
            webLink=request.form["web_link"]
            post.createQR(webLink,True,id)
        else:
            webLink=request.form["web_link"]
            post.createQR(webLink,False,id)
            
        updates["web_link"] = request.form["web_link"]
        post.updates(updates)

            
    # save the post groups
    if "post_groups" in request.form:
        post.save_groups(request.form["post_groups"])

    # redirect to the post create page with a success message
    return redirect(url_for("posts.list_posts"))


@controller.route("/new", methods=["POST"])
@login_required
def create():
    
    userID = current_user.get_id()
    somePost = Post()
    postid = somePost.maxId()

    required_fields = ["title", "start_date", "end_date", "post_type","display_time"]

    for field in required_fields:
        if field not in request.form:
            return abort(400, f"Required field {field} is missing")

    # available post types image,html,link
    if request.form["post_type"] == "image":
        # store the image in the static/images folder
        image = request.files["image"]
        # create the post
        post = Post(
            title=request.form["title"],
            type="IMAGE",
            startDate=request.form["start_date"],
            endDate=request.form["end_date"],
            imageLink=  "static/images/" + str(postid) +"_"+ image.filename,
            state="DRAFT",
            created_by= userID,
            display_time= request.form["display_time"] 
            
        )

        # save the post
        post.insert()
        id = post.get_id()
        image.save("static/images/"+str(id)+"_"+image.filename)

    elif request.form["post_type"] == "html":
        # create the post
        post = Post(
            title=request.form["title"],
            type="HTML",
            startDate=request.form["start_date"],
            endDate=request.form["end_date"],
            htmlContent=request.form["htmlContent"],
            state="DRAFT",
            created_by= userID,
            display_time= request.form["display_time"]            
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
        webLink=request.form["web_link"], 
        state="DRAFT",
        created_by= userID,
        display_time= request.form["display_time"] 
        )
        post.insert()

        add_qr_code = request.form.get("add_qr_code")
        id = str(post.get_id())
        if add_qr_code:
            webLink=request.form["web_link"]
            post.createQR(webLink,True,id)

        else:
            webLink=request.form["web_link"]
            post.createQR(webLink,False,id)

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
        userposts = Post.all()
    elif policy.canViewPostList():
         userposts = Post.postsCreatedBy(current_user.get_id()) 
    else:
        error_message = "You are not authorized to view this page"
        return render_template("errors/401.html", error_message=error_message)
    


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
        posts = userposts

    # return the form in templates/posts/create.html
    post = Post()
    
    return render_template(
        "posts/admin/list.html", posts=posts, activeFilters=activeFilters
    )

@controller.route("/<int:id>/delete")
@login_required
def delete(id):
    post = Post()
    post.deletePost(id)
    post.removeFromDevice(id)
    
    return redirect(url_for('posts.list_posts'))
    
    


@controller.route("/display")
@login_required
def display():
    folder_path = "static/images"  # Replace this with the path to your folder

    post = Post()
    display_times = []

    files_and_dirs = os.listdir(folder_path)
    filenames = [file for file in files_and_dirs if os.path.isfile(os.path.join(folder_path, file))] # names of the files

    for filename in filenames:
        id = post.getIDFromFileName(filename) # getting the post id from their filenames
        print(id)

        times = post.getDisplayTimesFromDB(id) # getting the display time for each post bases on its id
        if times:
            display_time = times[0]['display_time'] 
            display_times.append(display_time*1000) 

    # This is a workaround for the problem in the javascript script
    # The js in display.html is using the 1st element instead of the 0th element for the first time
    # Moving every time up by one and putting the last time first has solved the problem
    lastTime = display_times.pop() 
    display_times = [lastTime]+ display_times


    print(display_times)
    return render_template("display.html", filenames = filenames, display_times = display_times)
        
