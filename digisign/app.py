import datetime
from flask import Flask, render_template, request, redirect, Response, jsonify
import pymysql

from dotenv import dotenv_values

config = dotenv_values(".env")  # read the database credentials from .env file

## STEP 1: Create a Flask app
app = Flask(__name__)

## STEP 2: Configure the database connection using the username and password from .env file
connection = pymysql.connect(
    host="127.0.0.1",
    user=config["MYSQL_USER"],
    password=config["MYSQL_PASSWORD"],
    db=config["MYSQL_DATABASE"],
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)

## STEP 3: Run Database Migrations
# Create User Table

user_table = "CREATE TABLE IF NOT EXISTS user (id INT(11) NOT NULL AUTO_INCREMENT, name VARCHAR(100) NOT NULL, PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
posts_table = "CREATE TABLE IF NOT EXISTS post (id INT(11) NOT NULL AUTO_INCREMENT, title VARCHAR(100) NOT NULL, content TEXT, user_id INT(11) NOT NULL, PRIMARY KEY (id), FOREIGN KEY (user_id) REFERENCES user (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
devices_table = "CREATE TABLE IF NOT EXISTS device (id INT(11) NOT NULL AUTO_INCREMENT, name VARCHAR(100) NOT NULL, PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
groups_table = "CREATE TABLE IF NOT EXISTS `group` (id INT(11) NOT NULL AUTO_INCREMENT, name VARCHAR(100) NOT NULL, PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
group_devices_table = "CREATE TABLE IF NOT EXISTS group_device (id INT(11) NOT NULL AUTO_INCREMENT, device_id INT(11) NOT NULL, group_id INT(11) NOT NULL, PRIMARY KEY (id), FOREIGN KEY (device_id) REFERENCES device (id), FOREIGN KEY (group_id) REFERENCES `group` (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
group_moderator_table = "CREATE TABLE IF NOT EXISTS group_moderator (id INT(11) NOT NULL AUTO_INCREMENT, user_id INT(11) NOT NULL, group_id INT(11) NOT NULL, PRIMARY KEY (id), FOREIGN KEY (user_id) REFERENCES user (id), FOREIGN KEY (group_id) REFERENCES `group` (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

with connection.cursor() as cursor:
    cursor.execute(user_table)
    cursor.execute(posts_table)
    cursor.execute(devices_table)
    cursor.execute(groups_table)
    cursor.execute(group_devices_table)
    cursor.execute(group_moderator_table)
    connection.commit()


# Post Model
class Post:
    id = None
    title = None
    content = None
    user_id = None
    start_date = None
    end_date = None

    def __init__(self, title, content, user_id, start_date, end_date):
        self.title = title
        self.content = content
        self.user_id = user_id
        # set start_date and end_date to Today's date if not provided
        self.start_date = (
            start_date if start_date else datetime.now().strftime("%Y-%m-%d")
        )
        self.end_date = end_date if end_date else datetime.now().strftime("%Y-%m-%d")

    def __repr__(self):
        return "<Post %r>" % self.title

    def insert(self):
        with connection.cursor() as cursor:
            sql = "INSERT INTO post (title, content, user_id,start_date,end_date) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(
                sql,
                (
                    self.title,
                    self.content,
                    self.user_id,
                    self.start_date,
                    self.end_date,
                ),
            )
            connection.commit()
            self.id = cursor.lastrowid
        return self


## STEP 4: Create routes for the app
# Create/Post Route
@app.route("/post/create", methods=["GET", "POST"])
def create_post():
    if request.method == "GET":
        # return the form to create a post
        return render_template("posts/create.html")
    elif request.method == "POST":
        # create the post
        title = request.form["title"]
        content = request.form["content"]
        user_id = request.form["user_id"]
        new_post = Post(title=title, content=content, user_id=user_id)
        new_post.insert()
        return redirect("/post")


if __name__ == "__main__":
    print(
        "Starting Python Flask Server Digisign. The webapp will run on port "
        + config["FLASK_PORT"]
    )
    app.run(debug=True, port=config["FLASK_PORT"])
