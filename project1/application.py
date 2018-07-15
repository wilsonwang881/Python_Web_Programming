import os

from flask import Flask, session, render_template, request, redirect, url_for
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
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
connection = engine.connect()

@app.route("/")
def index():
    if "user_id" in session:
        return render_template("index.html", user=session["user_id"])
    else:
        return render_template("log_reg.html", headline="")

@app.route("/registration")
def registration():
    return render_template("reg.html",
                           taken="",
                           passwd_diff="",
                           passwd_error="",
                           email_error="",
                           answer_error="")

@app.route("/registration_handler", methods=["POST", "GET"])
def registration_handler():
    if request.method == "GET":
        return "Try submitting data first"
    else:
        if session.get("user_id") is None:
            session["user_id"] = []
            return render_template("reg.html")
        else:
            username = request.form["name"]
            password = request.form["password"]
            re_password = request.form["re_password"]
            email = request.form["email"]
            question = request.form.get("question_select")
            if question == "city":
                question_number = 1
            elif question == "name":
                question_number = 2
            else:
                question_number = 3
            answer = request.form["answer"]
            query = db.execute("SELECT user_name FROM users WHERE user_name=:username",{"username":username})
            username_results = []
            for row in query:
                username_results.append(row[0])
            query = db.execute("SELECT user_name FROM users WHERE user_email=:email", {"email":email})
            email_results = []
            for row in query:
                email_results.append(row[0])
            taken = ""
            password_error = ""
            passwd_diff = ""
            email_error = ""
            answer_error = ""
            valid = True
            if len(username_results) != 0:
                taken = "Username already exists"
                valid = False
            if not username:
                taken = "Please enter a username"
                valid = False
            if not password:
                password_error = "Please enter a password"
                valid = False
            if password != re_password:
                passwd_diff = "Please enter the same password"
                valid = False
            if "@" not in email:
                email_error = "Invalid email address"
                valid = False
            if len(email_results)!=0:
                email_error = "Email address already registered"
                valid = False
            if not answer:
                answer_error = "Please enter the answer"
                valid = False
            if not valid:
                return render_template("reg.html",
                                       taken=taken,
                                       passwd_diff=passwd_diff,
                                       passwd_error=password_error,
                                       email_error=email_error,
                                       answer_error=answer_error)
            else:
                db.execute("INSERT INTO users (user_password, user_email, security_question_number, security_question_answer, user_name) VALUES (:password, :email, :question_number, :answer, :username)",
                           {"password":password, "email":email, "question_number":question_number, "answer":answer, "username":username})
                db.commit()
                return render_template("reg_succ.html", user=username)

@app.route("/login_redirect")
def login_redirect():
    return render_template("log_reg.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return ("Try login first")
    else:
        if session.get("user_id") is None:
            session["user_id"] = []
        name = request.form["name"]
        password = request.form["password"]
        if name and password:
            query = db.execute("SELECT user_password FROM users WHERE user_name=:name", {"name":name})
            results = []
            for row in query:
                results.append(row[0])
            session["user_id"].append(name)
            print(session)
            if results!=[] and results[0] == password:
                return redirect(url_for("user"))
            else:
                return render_template("log_reg.html", headline="Error!")
        else:
            return render_template("log_reg.html", headline="Enter something")

@app.route("/user")
def user():
    return render_template("index.html", user=session["user_id"][0])

@app.route("/settings")
def settings():
    return render_template("settings.html", user=session["user_id"][0])

@app.route("/update_username", methods=["POST", "GET"])
def update_username():
    current_user = session["user_id"]
    return "OK"

@app.route("/update_password", methods=["POST", "GET"])
def update_password():
    current_user = session["user_id"]
    return "OK"

@app.route("/update_email", methods=["POST", "GET"])
def update_email():
    current_user = session["user_id"]
    return "OK"

@app.route("/logout")
def logout():
    session.pop("user_id")
    return redirect("/")

@app.route("/search")
def search():
    return render_template("search.html", user=session["user_id"][0], books=None, nomatches=None)

@app.route("/search_handler", methods=["POST", "GET"])
def search_handler():
    if request.method == "GET":
        return ("search request must be submitted via form")
    else:
        info = request.form["info"]
        info_regex = "%{}%".format(info)
        res = db.execute("SELECT * FROM import_books WHERE title LIKE :title OR isbn LIKE :ISBN OR author LIKE :author",
                         {"title":info_regex, "ISBN":info_regex, "author":info_regex}).fetchall()
        if not res:
            return render_template("search.html", user=session["user_id"][0], books=None, nomatches="Yes")
        return render_template("search.html", user=session["user_id"][0], books=res, nomatches=None)

@app.route("/books/<isbn>")
def books(isbn):
    res = db.execute("SELECT * FROM import_books WHERE isbn=:book_isbn", {"book_isbn":isbn})
    if res is None:
        return render_template("404.html", message="No such book found")
    return render_template("books.html", books=res)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message=None),404

##################################################
# registration            -> functional
# login                   -> functional
# logout                  -> functional
# import                  -> functional
# search                  -> functional
# book page
# review submission
# goodreads review data
# api access
##################################################