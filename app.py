from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db"
mongo = PyMongo(app)

# mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")

@app.route("/")
def index():
    listings = mongo.db.data_scrape_col.find_one()
    return render_template("index.html", listings=listings)


@app.route("/scrape")
def scraper():
    scrape_mars.scrape()
    listings = mongo.db.data_scrape_col.find_one()
    return render_template("index.html", listings=listings)
    # listings = mongo.db.data_scrape_col

    # listings_data = scrape_mars.scrape()
    
    # listings.update({}, listings_data, upsert=True)
    # return redirect("/", code=302)

if __name__ == "__main__":
    app.run()
