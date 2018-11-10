from bs4 import BeautifulSoup as bs
import requests
import pymongo
from splinter import Browser
import pandas as pd
import time

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mars_db
collection = db.data_scrape_col

url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest" 
images_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
weather_tweet_url = "https://twitter.com/marswxreport?lang=en"
mars_facts_url = "https://space-facts.com/mars/"
hemispheres_base_url = "https://astrogeology.usgs.gov/search/map/Mars/Viking/"
hemisphere_image_base_url = "https://astrogeology.usgs.gov"
hemispheres = ["cerberus_enhanced", "schiaparelli_enhanced", "syrtis_major_enhanced", "valles_marineris_enhanced"]

#response = requests.get(url)
#soup = bs(response.text, 'html.parser')
    
executable_path = {'executable_path': 'chromedriver.exe'}

def scrape():

    collection.drop()

    browser = Browser('chrome', **executable_path, headless=False)
    browser.visit(url)

    time.sleep(5)

    soup = bs(browser.html, 'html.parser')

    results = soup.find('li', class_ = "slide")

    news_title = results.find('div', class_ = 'content_title').text
    news_p = results.find('div', class_ = 'article_teaser_body').text

    browser.visit(images_url)

    time.sleep(5)

    browser.click_link_by_partial_text('FULL IMAGE')

    time.sleep(5)

    soup = bs(browser.html, 'html.parser')

    featured_image_url = "https://www.jpl.nasa.gov" + soup.find('img', class_ = "fancybox-image")['src']

    browser.visit(weather_tweet_url)

    time.sleep(5)

    soup = bs(browser.html, 'html.parser')

    mars_weather = soup.find('p', class_ = "tweet-text").text

    browser.visit(mars_facts_url)

    time.sleep(5)

    tables = pd.read_html(mars_facts_url)

    df = tables[0]
    df.columns = ["Statistic Name", "Stats"]
    df.set_index("Statistic Name", inplace = True)

    html_table = df.to_html()
    html_table.replace('\n', '')

    hemisphere_image_url = []

    #Test Code
    #browser.visit(hemispheres_base_url + hemispheres[0])
    #time.sleep(5)
    #soup = bs(browser.html, 'html.parser')
    #hemisphere_name = soup.find('h2', class_ = "title").text
    #hemisphere_img = soup.find('img', class_ = "wide-image")['src']
    #hemisphere_img

    for hemisphere in hemispheres:
        browser.visit(hemispheres_base_url + hemisphere)
        
        time.sleep(5)
        
        soup = bs(browser.html, 'html.parser')
        
        hemisphere_name = soup.find('h2', class_ = "title").text
        hemisphere_img = soup.find('img', class_ = "wide-image")['src']
        
        hemisphere_dict = {"title": hemisphere_name, "image_url": hemisphere_image_base_url + hemisphere_img}
        
        hemisphere_image_url.append(hemisphere_dict)



    title = news_title
    text = news_p
    main_image_url = featured_image_url
    weather = mars_weather
    stat_table = html_table

    listings = {"title":title,
                    "text":text,
                    "main_image":main_image_url,
                    "weather":weather,
                    "stat_table":stat_table,
                    "hemisphere_images":hemisphere_image_url}

    collection.insert_one(listings)

    return

