from flask import Flask, render_template, abort, request, redirect

app = Flask(__name__, template_folder = "../html")

import os
import pymongo
import base62
import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

# object ID helper functions: ObjectID() <-> base62 string
oidtob62 = lambda oid: base62.encodebytes(oid.binary)
b62tooid = lambda b62: ObjectId(base62.decodebytes(b62))


def main():
    # Connect to MongoDB Atlas
    mongo_uri = os.environ.get("MONGO_URI")
    client = pymongo.MongoClient(mongo_uri, server_api=ServerApi(version="1"))
    global db
    # Trying to connect to database
    try:
        client.admin.command("ping")
        db = client["Cluster0"]
        print("Connected!")
    except Exception as e:
        print("Failed to connect at ", mongo_uri)
        print("Database connection error", e)
    db = client.test
    # Run Flask app on port 5000, localhost (we don't have any plans to put this on the Internet)
    app.run(host="127.0.0.1", port=5000, debug=True)


# Front page, list at most 10 articles
@app.route("/")
def home():
    # Get articles sorted in descending order by article.date
    articles = db.articles.find().sort("date", pymongo.DESCENDING).limit(10)
    # Convert object IDs to base62 (for hrefs)
    articles = list(articles)
    for article in articles:
        article["id"] = oidtob62(article["_id"]) # This is for the hrefs
    return render_template("display1.html", articles=articles)


# Takes: object id (_id) in base62
# Renders template at /html/display2.html
@app.route("/article/<id_b62>")
def article(id_b62):
    # Decode object ID
    oid = b62tooid(id_b62)
    # Attempt to get article from database, return 404 if fail
    article = db.articles.find_one({"_id": oid})
    if article is None:
        abort(404)
    else:
        # Convert article.date to string (e.g. Tuesday, October 17 2023, 10:00:00 PM)
        article["id"]=id_b62
        article["date"] = article["date"].strftime("%A, %B %d %Y, %I:%M:%S %p")
        return render_template("display2.html", article=article)


# Submission form
@app.route("/submit")
def submit():
    return render_template("write.html")


# Receive submission form
@app.route("/submit_blog", methods=["POST"])
def submit_blog():
    # Get article.title, article.content from POST
    title = request.form["title"]
    content = request.form["content"]
    author = request.form["author"]
    # Get datetime
    date = datetime.datetime.utcnow()
    # Insert article into database
    result = db.articles.insert_one({"title": title, "author": author, "content": content, "date": date})
    # Redirect to article page
    return redirect("/article/" + oidtob62(result.inserted_id))


# Edit existing article form
@app.route("/edit/<id_b62>")
def edit(id_b62):
    # Prepopulate form with article.title, article.content
    # Get article from database
    oid = b62tooid(id_b62)
    article = dict(db.articles.find_one({"_id": oid}))
    if article is None:
        abort(404)
    else:
        article["id"] = id_b62
        print(article["id"])
        return render_template("edit.html", article=article)


# Receive edit form
@app.route("/submit_edit/<id_b62>", methods=["POST"])
def submit_edit(id_b62):
    # Get article.title, article.content, article.id from POST
    title = request.form["title"]
    content = request.form["content"]
    author = request.form["author"]
    # Convert article.id to base64
    oid = b62tooid(id_b62)
    # Update article in database
    db.articles.update_one(
        {"_id": oid}, {"$set": {"title": title, "author": author, "content": content}}
    )
    # Redirect to article page
    return redirect("/article/" + id_b62)


# Returns 200 even if article doesn't exist
@app.route("/delete/<id_b62>")
def delete(id_b62):
    # Convert id_b62 to oid
    oid = b62tooid(id_b62)
    # Delete article from database
    db.articles.delete_one({"_id": oid})
    # Redirect to front page
    return redirect("/")

# Takes search query from display1.html and returns results
@app.route("/search", methods=["GET","POST"])
def search():
    query = request.form["search"]
    # Get articles by title, article content, or author in descending date order (no limit)
    articles = db.articles.find(
        {
            "$or":[
                {"title":{"$regex":query}},
                {"content":{"$regex":query}},
                {"author":{"$regex":query}}
            ]
        }
    ).sort("date", pymongo.DESCENDING)
    # Convert object IDs to base62 (for hrefs)
    articles = list(articles)
    for article in articles:
        article["id"] = oidtob62(article["_id"])
    return render_template("search.html", articles=articles)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    main()
