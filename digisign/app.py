from flask import Flask, render_template, request, redirect, Response, jsonify

from controllers import PostsController
from controllers import HomeController

from dotenv import dotenv_values

config = dotenv_values(".env")  # read the database credentials from .env file

## STEP 1: Create a Flask app
app = Flask(__name__, static_url_path="/static")

## STEP 2: Get Database Connection

from database.database import MYSQL

connection = MYSQL().get_connection()

## Step 3: Register Blueprints
app.register_blueprint(PostsController.controller, url_prefix="/posts")
app.register_blueprint(HomeController.controller, url_prefix="/")

## Step 4: Print the URL map
# print(app.url_map)


if __name__ == "__main__":
    print(
        "Starting Python Flask Server Digisign. The webapp will run on port "
        + config["FLASK_PORT"]
    )
    app.run(debug=True, port=config["FLASK_PORT"])
