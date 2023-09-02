from flask import Flask, flash, render_template, request, redirect, Response, jsonify, url_for
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from dotenv import dotenv_values

from models.User import User

config = dotenv_values(".env")  # read the database credentials from .env file

## STEP 1: Create a Flask app
app = Flask(__name__, static_url_path="/static")

## Step 2 : Initialize Flask Login
app.secret_key = config["SECRET_KEY"]
login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

## STEP 3: Get Database Connection
from database.database import MYSQL

connection = MYSQL().get_connection()


@login_manager.user_loader
def load_user(user_id=""):
    return User().findById(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to view that page.", "error")
    return redirect(url_for("authentication_controller.login"))


if __name__ == "__main__":
    ## STEP 4: Import Controllers
    from controllers import AuthenticationController, HomeController, PostsController,GroupsController

    ## Step 4: Register Blueprints
    app.register_blueprint(PostsController.controller, url_prefix="/posts")
    app.register_blueprint(HomeController.controller, url_prefix="/")
    app.register_blueprint(AuthenticationController.controller, url_prefix="/auth")
    app.register_blueprint(GroupsController.controller, url_prefix="/groups")
    print(
        "Starting Python Flask Server Digisign. The webapp will run on port "
        + config["FLASK_PORT"]
    )
    app.run(debug=True, port=config["FLASK_PORT"])
