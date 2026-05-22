import feedparser
import requests
import os
import random

# ================= CONFIG =================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BLOG_ID = os.getenv("BLOG_ID")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

RSS_URL = "https://feeds.bbci.co.uk/news/rss.xml"


# ================= ACCESS TOKEN =================

def get_access_token():
    url = "https://oauth2.googleapis.com/token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }

    res = requests.post(url, data=data)

    token = res.json()

    if "access_token" not in token:
        print("TOKEN ERROR:", token)
        return None

    return token["access_token"]


# ================= NEWS =================

feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("NO NEWS FOUND")
    exit()

entry = random.choice(feed.entries)

title = entry.title
summary = entry.get("summary", "")

print("SELECTED:", title)


# ================= GEMINI =================

def ai(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": f"Write a professional news article:\n\n{text}"
            }]
        }]
    }

    res = requests.post(url, json=payload)
    data = res.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        print("GEMINI ERROR:", data)
        return text


# ================= HTML =================

def html(title, content):
    return f"""
    <div style="font-family:Arial;max-width:800px;margin:auto;padding:20px">
        <h1>{title}</h1>
        <p style="line-height:1.7">{content.replace("\n", "<br>")}</p>
    </div>
    """


# ================= POST BLOG =================

def post(title, content):
    token = get_access_token()

    if not token:
        print("NO ACCESS TOKEN")
        return

    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "title": title,
        "content": html(title, content),
        "isDraft": False
    }

    res = requests.post(url, headers=headers, json=data)

    print("STATUS:", res.status_code)
    print("RESPONSE:", res.text)


# ================= RUN =================

print("BOT START")

article = ai(title + "\n\n" + summary)

post(title, article)

print("DONE")
