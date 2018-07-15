import csv
import os

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
connection = engine.connect()

def main():
    db.execute("CREATE TABLE import_books (book_id SERIAL PRIMARY KEY, ISBN VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR NOT NULL)")
    db.commit()
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn,title,author,years in reader:
        db.execute("INSERT INTO import_books (ISBN, title, author, year) VALUES (:ISBN, :title, :author, :years)",
                   {"ISBN": isbn, "title":title, "author": author, "years": years})
        print("added {}".format(title))
    db.commit()
    db.execute("DELETE FROM import_books WHERE isbn='isbn'")
    print("All books added")

if __name__ == "__main__":
    main()