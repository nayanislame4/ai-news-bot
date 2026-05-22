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


# ================= GET ACCESS TOKEN =================

def get_access_token():
    url = "https://oauth2.googleapis.com/token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }

    try:
        res = requests.post(url, data=data, timeout=30)
        token_data = res.json()

        if "access_token" not in token_data:
            print("TOKEN ERROR RESPONSE:", token_data)
            return None

        return token_data["access_token"]

    except Exception as e:
        print("TOKEN ERROR:", e)
        return None


# ================= GET NEWS =================

feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("NO NEWS FOUND")
    exit()

entry = random.choice(feed.entries)

title = entry.title
summary = entry.summary

print("SELECTED NEWS:", title)


# ================= IMAGE =================

def get_image(query="news"):
    return f"https://source.unsplash.com/1200x600/?{query}"


# ================= GEMINI =================

def ai_rewrite(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Rewrite this into a professional news article:\n\n{text}"
                    }
                ]
            }
        ]
    }

    try:
        res = requests.post(url, json=payload, timeout=60)
        result = res.json()

        if "candidates" not in result:
            print("GEMINI ERROR:", result)
            return text

        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print("GEMINI ERROR:", e)
        return text


# ================= HTML =================

def make_html(title, content):
    image = get_image("world news")

    clean = content.replace("\n", "<br>")

    html = """
    <div style="font-family:Arial;padding:20px;max-width:800px;margin:auto;">

        <h1 style="color:#111;">{title}</h1>

        <img src="{image}" style="width:100%;border-radius:12px;margin:15px 0;">

        <div style="font-size:18px;line-height:1.8;color:#333;">
            {content}
        </div>

        <hr>

        <p style="color:gray;font-size:12px;">
            AI Generated News
        </p>

    </div>
    """

    return html.format(
        title=title,
        image=image,
        content=clean
    )


# ================= BLOG POST =================

def post_blog(title, content):
    access_token = get_access_token()

    if not access_token:
        print("FAILED TO GET ACCESS TOKEN")
        return

    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "title": title,
        "content": make_html(title, content),
        "status": "LIVE"
    }

    try:
        res = requests.post(url, headers=headers, json=data, timeout=60)

        print("BLOG STATUS:", res.status_code)
        print("BLOG RESPONSE:", res.text)

    except Exception as e:
        print("BLOG ERROR:", e)


# ================= RUN =================

print("BOT STARTED")

article = ai_rewrite(title + "\n\n" + summary)

post_blog(title, article)

print("DONE")
