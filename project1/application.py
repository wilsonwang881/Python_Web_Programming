# key: kdscrSYrjF3PxtfQQcVrQ
# secret: qFW9Lmr42gAx8PLRzNSWUo8J4AW9VXcNaUXWZddU
# https://www.goodreads.com/api/keys

import os

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

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

res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KEY", "isbns": "9781632168146"})
# print(res.json())


@app.route("/")
def index():
    headline = "guests"
    return render_template("index.html", headline=headline)

@app.route("/registration")
def registration():
    headline = "registration"
    return render_template("index.html", headline=headline)

@app.route("/login", methods=["POST", "GET"])
def login():
    if requests.methods == "GET":
        return "Try submitting data first"
    else:
        if session.get("user_id") is None:
            session["user_id"] = []
        else:
            name = requests.form.get("name")
            password = requests.form.get("password")
            session["user_id"].append(name)
            return render_template("index.html")

@app.route("/logout")
def logout():
    headline = "registration"
    return render_template("index.html", headline=headline)

@app.route("/search")
def search():
    headline = "search"
    return render_template("index.html", headline=headline)

#########################
# registration x
# login x
# logout x
# import
# search x
# book page
# review submission
# goodreads review data
# api access
#########################