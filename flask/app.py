from flask import Flask, render_template

app = Flask(__name__)

import os
import pymongo
import base64
import base62
import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()

# object ID helper functions
b64tob62 = lambda b64: base62.encodebytes(base64.b64decode(b64)).decode('utf-8')
b62tob64 = lambda b62: base64.b64encode(base62.decodebytes(b62.encode('utf-8'))).decode('utf-8')

def main():
    # Connect to MongoDB Atlas
    mongo_uri = os.environ.get ( 'MONGO_URI' )
    client = pymongo.MongoClient ( mongo_uri )
    # db = client.test

    # Trying to connect to database
    try:
        client.admin.command ( "ping" )
        db = client [ "Cluster0" ]
        collection = db [ "User_Posts" ]
        print ( 'Connected!')
    except Exception as e:
        print ( 'Failed to connect at ', mongo_uri )
        print ( 'Database connection error', e )
    db = client.test
    # Run Flask app on port 8080, localhost (we don't have any plans to put this on the Internet)
    app.run(host='127.0.0.1', port=8080, debug=True)

# Front page, list at most 10 articles
@app.route('/')
def home():
    # Get articles sorted in descending order by article.date
    articles = db.articles.find().sort('date', pymongo.DESCENDING).limit(10)
    # Convert object IDs to base62 (for hrefs)
    for article in articles:
        article['_id'] = b64tob62(article['_id'])
    return render_template('index.html', articles=articles)

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

# TODO: Implement article writing page @ /submit

# TODO: Receive POST @ /submit_blog, containing article.title, article.content, automatically generate article.date

# TODO: Implement edit article page @ /edit/<id_b62>,

# TODO: Receive POST @ /submit_edit, containing article.title, article.content, article.date, article.id

# TODO: Implement delete article page @ /delete/<id_b62>


if __name__ == '__main__':
    main()