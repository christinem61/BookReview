#Project 1
#Christine Mathews

Harvard cs50: Web Programming with Python and JavaScript

This is a book review website written using Python Flask, HTML and CSS. Users are able to register for the website and 
login using their username and password. Once they log in, they will be able to 
search for books, leave reviews for individual books and see reviews made by other 
people. The Goodreads API was used to pull ratings from a broader audience. You can
also query for book details and reviews via this website's API. A PostgreSQL
database hosted by Heroku is what I used to store the user data. 

application.py

This is where the main set up of the webpage lies. It is where I have written
all the main functions.


import.py

This is the file that imports a list of 5000 books from an excel spreadsheet into
the database. 


.html files
These are the templates for each of the pages of the website. The layout and
format are included on these pages. 