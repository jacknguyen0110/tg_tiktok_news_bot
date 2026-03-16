import os
import requests
import feedparser

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def get_hot_news():

    if NEWSAPI_KEY:

        url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=1&apiKey={NEWSAPI_KEY}"

        data = requests.get(url).json()

        article = data["articles"][0]

        return {
            "title": article["title"],
            "content": article["description"],
            "url": article["url"]
        }

    feed = feedparser.parse("https://rss.cnn.com/rss/edition.rss")

    item = feed.entries[0]

    return {
        "title": item.title,
        "content": item.summary,
        "url": item.link
    }