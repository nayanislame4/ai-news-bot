import feedparser
import requests
import os
import random

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

print("SELECTED:", title)

# ================= IMAGE GENERATOR =================
def get_image(query):
    # free dynamic image (no API needed)
    return f"https://source.unsplash.com/1200x600/?{query}"

# ================= AI REWRITE =================
def ai_rewrite(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": "Rewrite this news professionally in 2 paragraphs:\n\n" + text
            }]
        }]
    }

    try:
        res = requests.post(url, json=payload, timeout=30)
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("AI ERROR:", e)
        return text

# ================= HTML FORMAT =================
def make_html(title, content):
    image = get_image("news,world")

    html = f"""
    <div style="font-family:Arial;padding:15px;max-width:800px;margin:auto;">
        
        <h1 style="color:#222;">{title}</h1>

        <img src="{image}" style="width:100%;border-radius:12px;margin:10px 0;"/>

        <div style="font-size:16px;line-height:1.7;color:#333;">
            {content.replace("\n", "<br>")}
        </div>

        <hr>
        <p style="font-size:12px;color:gray;">AI Generated News Article</p>
    </div>
    """
    return html

# ================= BLOG POST =================
def post_blog(title, content):
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

    res = requests.post(url, headers=headers, json=data)

    print("STATUS:", res.status_code)
    print("RESPONSE:", res.text)

# ================= RUN =================
article = ai_rewrite(title + " " + summary)
post_blog(title, article)

print("DONE POSTED")
