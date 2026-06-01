import asyncio
import feedparser
import json
import os
import requests
from telegram import Bot
from telegram.error import TelegramError

# ─── CONFIG ───────────────────────────────────────────────
TOKEN        = "8519274333:AAHPzbYbjgUA-bStiKlRT8ye4xYZ3jQZfUI"      # ← your Telegram bot token
CHANNEL      = "@uztrade_school"
GEMINI_KEY   = "AQ.Ab8RN6IcOjC9tJxKnzSfNViZ7A5mjQVV8J0UGR6ViI6MFClvqw"
INTERVAL     = 1800  # 30 minutes
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
        return {
            "en": "📈 Bullish signal — possible growth",
            "ru": "📈 Бычий сигнал — возможен рост",
            "uz": "📈 O'sish signali — narx ko'tarilishi mumkin",
        }
    if any(k in t for k in ["fall","drop","crash","decline","bearish","падение","снижение"]):
        return {
            "en": "📉 Bearish signal — possible decline",
            "ru": "📉 Медвежий сигнал — возможно снижение",
            "uz": "📉 Tushish signali — narx pasayishi mumkin",
        }
    return {
        "en": "🔍 Watching market reaction",
        "ru": "🔍 Наблюдаем за реакцией рынка",
        "uz": "🔍 Bozor reaktsiyasini kuzatmoqdamiz",
    }


def translate_title(title):
    """Translate title to Russian and Uzbek using Gemini API."""
    try:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        )
        payload = {
            "contents": [{
                "parts": [{
                    "text": (
                        f"Translate this financial news headline into Russian and Uzbek.\n"
                        f"Headline: {title}\n\n"
                        f"Respond ONLY in this exact format, no extra text:\n"
                        f"RU: <russian translation>\n"
                        f"UZ: <uzbek translation>"
                    )
                }]
            }]
        }
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()

        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"🌐 Translation raw: {text}")

        lines = {}
        for line in text.splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                lines[key.strip()] = val.strip()

        ru = lines.get("RU", title)
        uz = lines.get("UZ", title)
        return ru, uz

    except Exception as e:
        print(f"❌ Translation error: {e}")
        return title, title  # fallback to original


def format_post(title, link):
    ru_title, uz_title = translate_title(title)
    signal = analyze(title)

    return (
        "💰 *UZTRADE NEWS*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        "🇬🇧 *English:*\n"
        f"📰 {title}\n"
        f"📊 {signal['en']}\n\n"

        "🇷🇺 *Русский:*\n"
        f"📰 {ru_title}\n"
        f"📊 {signal['ru']}\n\n"

        "🇺🇿 *O'zbek:*\n"
        f"📰 {uz_title}\n"
        f"📊 {signal['uz']}\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
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
