from flask import Flask, render_template, request, redirect,Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary
import sqlite3
import qrcode
import PIL
import mimetypes



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
db = SQLAlchemy(app)

class Image(db.Model): # create a class that should be added to DB
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    mimetype = db.Column(db.String(100), nullable=False)
    content = db.Column(LargeBinary, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)

class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String(100), nullable=False)
    content = db.Column(LargeBinary, nullable=False)

@app.route('/')
def index(): #initial page to be loaded
    return render_template('create.html')


@app.route('/create_account', methods=['POST'])
def create_account():
    username = request.form['username1']
    password = request.form['password1']
    department = request.form['department']

    new_user = User(username=username, password=password, department=department)
    db.session.add(new_user)
    db.session.commit()

    return 'Account created successfully'

@app.route('/user_table')
def userTable():
    users = User.query.all()
    return render_template('usertable.html',users=users)


@app.route('/upload_file')
def upload_file():
    return render_template('page.html')

@app.route('/upload_url')
def upload_url():
    return render_template('qrcode.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    webname = request.form['websiteName']
    qr = qrcode.QRCode(version=1)
    qr.add_data(webname)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("static/qr.png")

    image_path = "static/qr.png"

    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    print(content)
    filename = "qr.png"
    mimetype ,encoded= mimetypes.guess_type(image_path)

    new_file = Image(filename=filename,mimetype=mimetype, content=content) # making an image object
    db.session.add(new_file)
    db.session.commit() # add to db

    return "Created"

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
    
@app.route('/display')
def display_images():
    database = sqlite3.connect('instance/files.db')
    cursorfordatabase = database.cursor()
    print("Connection is established")

    query = "SELECT content FROM image"
    query2 = "SELECT id FROM image"
    cursorfordatabase.execute(query)
    records = cursorfordatabase.fetchall()

    images = records
    number = len(records)
    print(number)

    return render_template('display.html', number = number)
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all() #creates image
    app.run(debug=True) 




