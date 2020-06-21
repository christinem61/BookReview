#Christine Mathews
import csv, os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://jgecpwsafxnrrg:9248357497dba25513eda27b666dfec32410ad07f03c774e3efd026d6db9d519@ec2-34-193-117-204.compute-1.amazonaws.com:5432/d2jdpq3ctb9r84")
db = scoped_session(sessionmaker(bind=engine))

f = open("books.csv")  
reader = csv.reader(f)
for isbn, title, author, year in reader:
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
               {"isbn": isbn, "title": title, "author": author, "year": year})
    print(f"Added book with title: {title} to the database!")
    db.commit()