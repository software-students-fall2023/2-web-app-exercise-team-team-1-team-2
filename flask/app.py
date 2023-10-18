from flask import Flask, render_template

app = Flask(__name__)

import os
import pymongo
import base64
import base62
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()

# object ID helper functions
b64tob62 = lambda b64: base62.encodebytes(base64.b64decode(b64)).decode('utf-8')
b62tob64 = lambda b62: base64.b64encode(base62.decodebytes(b62.encode('utf-8'))).decode('utf-8')

def main():
    # Connect to MongoDB Atlas (blocked on credentials)
    client = pymongo.MongoClient("mongodb+srv://projectuser:erickmichealahmedhenry@cluster0.12ybrgp.mongodb.net/?retryWrites=true&w=majority")
    db = client.test

# Front page, list articles
@app.route('/')
def home():
    #TODO: Implement route
    pass

# Takes: object id (_id) in base62
# Renders template at /html/display2.html
@app.route('/article/<id_b62>')
def article(id_b62):
    # Decode object ID
    id_b64 = b62tob64(id_b62)
    # Attempt to get article from database, return 404 if fail
    article = db.articles.find_one({'_id': id_b64})
    if article is None:
        return render_template('404.html'), 404
    else:
        return render_template('display2.html', article=article)

#TODO: Implement other routes

if __name__ == '__main__':
    main()