import asyncio
import feedparser
import json
import os
from telegram import Bot
from telegram.error import TelegramError

# ─── CONFIG ───────────────────────────────────────────────
TOKEN   = "YOUR_NEW_TOKEN_HERE"   # ← paste new token from @BotFather
CHANNEL = "@uztrade_school"
INTERVAL = 1800  # 30 minutes
# ──────────────────────────────────────────────────────────

FEEDS = [
    "https://www.investing.com/rss/news_25.rss",
    "https://www.investing.com/rss/news_14.rss",
    "https://news.google.com/rss/search?q=gold+forex",
]

POSTED_FILE = "posted.json"


def load_posted():
    if os.path.exists(POSTED_FILE):
        try:
            with open(POSTED_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_posted(posted):
    with open(POSTED_FILE, "w") as f:
        json.dump(list(posted)[-500:], f)


def get_news(posted):
    news = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                link  = getattr(entry, "link",  None)
                title = getattr(entry, "title", None)
                if link and title and link not in posted:
                    posted.add(link)
                    news.append({"title": title, "link": link})
        except Exception as e:
            print(f"Feed error ({url}): {e}")
    return news


def analyze(title):
    t = title.lower()
    if any(k in t for k in ["rise","surge","rally","gain","bullish","рост","растёт"]):
        return "📈 Bullish сигнал — возможен рост"
    if any(k in t for k in ["fall","drop","crash","decline","bearish","падение","снижение"]):
        return "📉 Bearish сигнал — возможно снижение"
    return "🔍 Наблюдаем за реакцией рынка"


def format_post(title, link):
    return (
        "💰 *UZTRADE AI NEWS*\n\n"
        f"📰 {title}\n\n"
        f"📊 *AI Анализ:* {analyze(title)}\n\n"
        f"📎 [Читать полностью]({link})\n\n"
        "#Forex #Gold #UZTRADE"
    )


async def main():
    bot    = Bot(token=TOKEN)
    posted = load_posted()
    print(f"🤖 UZTRADE Bot started → {CHANNEL}")

    while True:
        try:
            news = get_news(posted)
            if news:
                print(f"📨 {len(news)} new article(s) found, sending...")
                for item in news:
                    try:
                        await bot.send_message(
                            chat_id=CHANNEL,
                            text=format_post(item["title"], item["link"]),
                            parse_mode="Markdown",
                        )
                        print(f"✅ Sent: {item['title'][:70]}")
                        await asyncio.sleep(2)
                    except TelegramError as e:
                        print(f"❌ Telegram error: {e}")
                save_posted(posted)
            else:
                print("💤 No new articles.")

            print(f"⏳ Sleeping {INTERVAL // 60} min...")
            await asyncio.sleep(INTERVAL)

        except Exception as e:
            print(f"🔥 Loop error: {e}")
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
