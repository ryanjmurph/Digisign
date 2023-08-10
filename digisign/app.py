from flask import Flask, render_template, request, redirect,Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary
import sqlite3
import json



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
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
    #return render_template(number)

    

if __name__ == "__main__":
    with app.app_context():
        db.create_all() #creates image
    app.run(debug=True) 




