import feedparser
import requests
import os
import random

# ================= ENV =================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BLOG_ID = os.getenv("BLOG_ID")

RSS_URL = "https://feeds.bbci.co.uk/news/rss.xml"


# ================= NEWS FETCH =================
feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("NO NEWS FOUND")
    exit()

entry = random.choice(feed.entries)

title = entry.title
summary = entry.summary

print("SELECTED NEWS:", title)


# ================= IMAGE =================
def get_image(query="news world"):
    return f"https://source.unsplash.com/1200x600/?{query}"


# ================= AI REWRITE =================
def ai_rewrite(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": "Rewrite this news into a professional 2 paragraph article:\n\n" + text
            }]
        }]
    }

    try:
        res = requests.post(url, json=payload, timeout=30)
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("AI ERROR:", e)
        return text


# ================= HTML BUILDER =================
def make_html(title, content):

    image_url = get_image("news,world")

    clean_content = content.replace("\n", "<br>")

    html = f"""
    <div style="font-family:Arial;max-width:800px;margin:auto;padding:15px;">

        <h1 style="color:#222;">{title}</h1>

        <img src="{image_url}" style="width:100%;border-radius:12px;margin:10px 0;" />

        <div style="font-size:16px;line-height:1.7;color:#333;">
            {clean_content}
        </div>

        <hr>

        <p style="font-size:12px;color:gray;">AI Generated News Article</p>

    </div>
    """

    return html


# ================= POST TO BLOGGER =================
def post_blog(title, content):

    if not BLOG_ID or not ACCESS_TOKEN:
        print("MISSING ENV VARIABLES")
        return

    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "title": title,
        "content": make_html(title, content),
        "status": "LIVE"
    }

    try:
        res = requests.post(url, headers=headers, json=data, timeout=30)
        print("STATUS CODE:", res.status_code)
        print("RESPONSE:", res.text)
    except Exception as e:
        print("POST ERROR:", e)


# ================= RUN =================
print("BOT STARTED")

article = ai_rewrite(title + " " + summary)

post_blog(title, article)

print("DONE")
