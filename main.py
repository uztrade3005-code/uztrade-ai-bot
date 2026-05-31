import time
import feedparser
import requests
from telegram import Bot

TOKEN = "8519274333:AAHPzbYbjgUA-bStiKlRT8ye4xYZ3jQZfUI"
CHANNEL = "@uztrade_school"

bot = Bot(token=TOKEN)

FEEDS = [
    "https://www.investing.com/rss/news_25.rss",
    "https://www.investing.com/rss/news_14.rss",
    "https://news.google.com/rss/search?q=gold+forex"
]

posted = set()

def get_news():
    news = []

    for url in FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            if entry.link not in posted:
                posted.add(entry.link)
                news.append(entry)

    return news

def format_post(title, link):
    return f"""
💰 UZTRADE AI NEWS

📰 {title}

📊 AI анализ: влияние на рынок Forex / Gold

📎 {link}

#Forex #Gold #UZTRADE
"""

while True:
    try:
        news = get_news()

        for n in news:
            bot.send_message(chat_id=CHANNEL, text=format_post(n.title, n.link))

        time.sleep(1800)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)