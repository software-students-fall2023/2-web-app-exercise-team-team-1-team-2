from flask import Flask, render_template, abort, request, redirect

app = Flask(__name__)

import os
import pymongo
import base64
import base62
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# object ID helper functions
b64tob62 = lambda b64: base62.encodebytes(base64.b64decode(b64)).decode("utf-8")
b62tob64 = lambda b62: base64.b64encode(base62.decodebytes(b62.encode("utf-8"))).decode("utf-8")

def main():
    # Connect to MongoDB Atlas
    mongo_uri = os.environ.get("MONGO_URI")
    client = pymongo.MongoClient(mongo_uri)
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
    # Run Flask app on port 8080, localhost (we don't have any plans to put this on the Internet)
    app.run(host="127.0.0.1", port=8080, debug=True)


# Front page, list at most 10 articles
@app.route("/")
def home():
    # Get articles sorted in descending order by article.date
    articles = db.articles.find().sort("date", pymongo.DESCENDING).limit(10)
    # Convert object IDs to base62 (for hrefs)
    for article in articles:
        article["_id"] = b64tob62(article["_id"])
    return render_template("html/display1.html", articles=articles)


# Takes: object id (_id) in base62
# Renders template at /html/display2.html
@app.route("/article/<id_b62>")
def article(id_b62):
    # Decode object ID
    id_b64 = b62tob64(id_b62)
    # Attempt to get article from database, return 404 if fail
    article = db.articles.find_one({"_id": id_b64})
    if article is None:
        abort(404)
    else:
        # Convert article.date to string (e.g. Tuesday, October 17 2023, 10:00:00 PM)
        article["date"] = article["date"].strftime("%A, %B %d %Y, %I:%M:%S %p")
        return render_template("display2.html", article=article)


# Submission form
@app.route("/submit")
def submit():
    return render_template("submit.html")


# Receive submission form
@app.route("/submit_blog", methods=["POST"])
def submit_blog():
    # Get article.title, article.content from POST
    title = request.form["title"]
    content = request.form["content"]
    # Get datetime
    date = datetime.datetime.utcnow()
    # Insert article into database
    result = db.articles.insert_one({"title": title, "content": content, "date": date})
    # Redirect to article page
    return redirect("/article/" + b64tob62(result.inserted_id))


# Edit existing article form
@app.route("/edit/<id_b62>")
def edit(id_b62):
    # Prepopulate form with article.title, article.content
    # Get article from database
    id_b64 = b62tob64(id_b62)
    article = db.articles.find_one({"_id": id_b64})
    if article is None:
        abort(404)
    else:
        return render_template("html/edit.html", article=article)


# Receive edit form
@app.route("/submit_edit", methods=["POST"])
def submit_edit():
    # Get article.title, article.content, article.id from POST
    title = request.form["title"]
    content = request.form["content"]
    id_b62 = request.form["id"]
    # Convert article.id to base64
    id_b64 = b62tob64(id_b62)
    # Update article in database
    db.articles.update_one(
        {"_id": id_b64}, {"$set": {"title": title, "content": content}}
    )
    # Redirect to article page
    return redirect("/article/" + id_b62)


# TODO: Implement delete article page @ /delete/<id_b62>
# Return 200 even if article doesn't exist
@app.route("/delete/<id_b62>")
def delete(id_b62):
    # Convert id_b62 to id_b64
    id_b64 = b62tob64(id_b62)
    # Delete article from database
    db.articles.delete_one({"_id": id_b64})
    # Redirect to front page
    return redirect("/")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("html/404.html"), 404


if __name__ == "__main__":
    main()
