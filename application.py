import os,json

from flask import Flask, session, render_template, request, session, redirect, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["JSON_SORT_KEYS"] = False
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
import requests

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        name=request.form.get("name")
        username=request.form.get("username")
        password=request.form.get("password")
        isUniqueUser=db.execute("SELECT * FROM users WHERE username = :username",{"username":username}).fetchone()
        if isUniqueUser:
            return render_template("error.html", message="The username you entered already exists!")
        db.execute("INSERT INTO users (name, username, password) VALUES (:name, :username, :password)", {"name":name, "username":username, "password":password})
        db.commit()
        #display SUCCESS MESsage flash('Succesfully Created Account!','info')
        return redirect('/login')
    return render_template('register.html')

@app.route('/login',methods=['POST','GET'])
def login():
    session.clear()
    if request.method == 'POST':
        username=request.form.get("username")
        password=request.form.get("password")
        userPass= db.execute("SELECT password FROM users WHERE username = :username", {"username": username}).fetchone()
        if userPass[0] != password:
            return render_template("error.html", message="Incorrect Password")
        elif userPass[0] == password:
            session["USERNAME"]=username
            return redirect("/search")
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    if 'USERNAME' in session:
        return render_template('logout_success.html')
    return redirect("/")
@app.route('/search', methods=['POST','GET'])
def search():
    if request.method == 'POST':
        if 'USERNAME' not in session:
            return render_template("error.html", message="Must login first!")
        search=request.form.get("search").lower()
        arg='%'+search+'%'
        results=db.execute('SELECT * FROM books WHERE LOWER(title) LIKE :arg OR LOWER(author) LIKE :arg OR isbn LIKE :arg', {"arg":arg}).fetchall()
        if not results:
            return render_template("error.html", message="No books found. Try entering another!")
        else:   
            return render_template("search_results.html", results=results, search=search)
    return render_template('search.html')

@app.route('/<isbn>', methods=['POST','GET'])
def book(isbn):
    if request.method == 'GET':
        if 'USERNAME' not in session:
            return render_template("error.html", message="Must login first!")
        book=db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        reviews=db.execute("SELECT * from reviews WHERE isbn = :isbn",{"isbn":isbn}).fetchall()
        key="Tzb29VfOWaywGWL9modZg"
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":key, "isbns":isbn})
        result=res.json()
        return render_template("book.html",book=book, reviews=reviews, result=result['books'][0])
    else:
        review=request.form.get("review")
        rating=request.form.get("rating")
        if not review:
            return render_template("error.html", message="Must enter a review")
        ReviewCheck=db.execute("SELECT * FROM reviews WHERE username= :username AND isbn= :isbn", {"username":session.get("USERNAME"),"isbn":isbn}).fetchone()
        if not ReviewCheck:
            db.execute("INSERT INTO reviews (username, isbn, review,rating) VALUES (:username, :isbn, :review, :rating)", {"username":session.get("USERNAME"),"isbn":isbn, "review":review, "rating":rating})
            db.commit()   
            return redirect('/'+isbn) 
        return render_template("error.html", message="You've already reviewed this book!")


@app.route('/api/<isbn>', methods=['GET'])
def json_fcn(isbn):
    if 'USERNAME' not in session:
            return render_template("error.html", message="Must login first!")
    temp=db.execute("SELECT title, author, year, books.isbn, COUNT(reviews.review) as review_count, AVG(reviews.rating) as average_score FROM books INNER JOIN reviews ON books.isbn=reviews.isbn WHERE books.isbn= :isbn GROUP BY title, author, year, books.isbn", {"isbn":isbn})
    temp=temp.fetchone()
    if temp is None:
        return jsonify({"error": "invalid isbn"}),404
    js=dict(temp)
    js['average_score'] = float('%.2f'%(js['average_score']))
    return jsonify(js)


