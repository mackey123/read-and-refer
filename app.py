import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/get_books")
def get_books():
    books = list(mongo.db.books.find())
    return render_template("books.html", books=books)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    books = list(mongo.db.books.find({"$text": {"$search": query}}))
    return render_template("books.html", books=books)


# register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("username already exists")
            return redirect(url_for("register"))

        register = {
             "username": request.form.get("username").lower(),
             "password": generate_password_hash(request.form.get("password"))
         }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


# login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # check password
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # password incorrect
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # unknown username
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


# users profile
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # ////
    flash("Log Out Successful")
    session.pop("user")
    return redirect(url_for("login"))


# add a book review
@app.route("/add_books", methods=["GET", "POST"])
def add_books():
    if request.method == "POST":
        books = {
            "book_name": request.form.get("book_name"),
            "book_description": request.form.get("book_description"),
            "book_rating": request.form.get("book_rating"),
            "book_genre": request.form.get("book_genre"),
            "created_by": session["user"]
        }
        mongo.db.books.insert_one(books)
        flash("Book Successfully added!")
        return redirect(url_for("get_books"))

    return render_template("add_books.html")


# edit a book review
@app.route("/edit_books/<book_id>", methods=["GET", "POST"])
def edit_books(book_id):
    if request.method == "POST":
        submit = {
            "book_name": request.form.get("book_name"),
            "book_description": request.form.get("book_description"),
            "book_rating": request.form.get("book_rating"),
            "book_genre": request.form.get("book_genre"),
            "created_by": session["user"]
        }
        mongo.db.books.update({"_id": ObjectId(book_id)}, submit)
        flash("Book Successfully Updated!")

    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    return render_template("edit_books.html", book=book,)


@app.route("/delete_books/<book_id>")
def delete_books(book_id):
    mongo.db.books.remove({"_id": ObjectId(book_id)})
    flash("Book Review Deleted")
    return redirect(url_for("get_books"))


@app.route("/get_bookreviews")
def get_bookreviews():
    bookreviews = list(mongo.db.books.find().sort("book_name", 1))
    return render_template("bookreviews.html", bookreviews=bookreviews)


# admin add genre
@app.route("/add_genre", methods=["GET", "POST"])
def add_genre():
    if request.method == "POST":
        genre = {
            "genre_name": request.form.get("genre_name")
        }
        mongo.db.genre.insert_one(genre)
        flash("New Genre Added")
        return redirect(url_for("add_genre"))

    return render_template("add_genre.html")


# contact section
@app.route("/contact")
def contact():
    return render_template('/contact.html')


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
