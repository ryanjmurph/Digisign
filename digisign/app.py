from flask import Flask, render_template, request, redirect,Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary

from dotenv import load_dotenv

config = load_dotenv() # read the database credentials from .env file

## STEP 1: Create a Flask app
app = Flask(__name__)

## STEP 2: Configure the database connection using the username and password from .env file
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{config['MYSQL_USER']}:{config['MYSQL_PASSWORD']}@localhost:3306/{config['MYSQL_DATABASE']}"
db = SQLAlchemy(app)

## STEP 3: Create models for the database
## Models: User - Model,Post - Model,Device - Model,Group - Model,GroupModerator - Pivot
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    posts = db.relationship('Post', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.name}>"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<Post {self.title}>"
    
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    groups = db.relationship('Group', secondary='group_device', backref='devices', lazy=True)

    def __repr__(self):
        return f"<Device {self.name}>"
    
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    moderators = db.relationship('User', secondary='group_moderator', backref='groups', lazy=True)

    def __repr__(self):
        return f"<Group {self.name}>"
    
class GroupModerator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

    def __repr__(self):
        return f"<GroupModerator {self.id}>"
    
group_device = db.Table('group_device',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('device_id', db.Integer, db.ForeignKey('device.id'), primary_key=True)
)

group_moderator = db.Table('group_moderator',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

## STEP 4: Create routes for the app
# Create/Post Route
@app.route('/post/create',methods=['GET','POST'])
def create_post():
    if request.method == 'GET':
        # return the form to create a post
        return render_template('posts/create.html')
    elif request.method == 'POST':
        # create the post
        title = request.form['title']
        content = request.form['content']
        user_id = request.form['user_id']
        new_post = Post(title=title,content=content,user_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/post')
    





db = SQLAlchemy(app)

class Image(db.Model): # create a class that should be added to DB
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    mimetype = db.Column(db.String(100), nullable=False)
    content = db.Column(LargeBinary, nullable=False)

    def __repr__(self):
        return f"<UploadedFile {self.filename}>"

@app.route('/')
def index(): #initial page to be loaded
    return render_template('index.html')

@app.route('/upload_file')
def upload_file():
    return render_template('page.html')

@app.route('/upload_url')
def upload_url():
    return render_template('page.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            mimetype = file.mimetype
            content = file.read() # setting values of the uploaded image to these variables

            new_file = Image(filename=filename,mimetype=mimetype, content=content) # making an image object
            db.session.add(new_file)
            db.session.commit() # add to db

            return redirect('/')
    return redirect('/upload_file')

@app.route('/<int:id>') #allows the image to be retrieved by number e.g localhost:5000/1 for the first image in the db
def getImage(id):
    img = Image.query.filter_by(id=id).first()
    if not img:
        return "There is no such image",404
    return Response(img.content, mimetype=img.mimetype) # displays image
    
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all() #creates image
    app.run(debug=True) 