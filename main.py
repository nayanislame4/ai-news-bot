import feedparser
import requests
import json
import os
from datetime import datetime
import random

# ================= CONFIG (GITHUB SECRETS) =================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BLOG_ID = os.getenv("BLOG_ID")

RSS_URL = "https://feeds.bbci.co.uk/news/rss.xml"

# ================= STATE =================
def load_state():
    try:
        with open("state.json", "r") as f:
            return json.load(f)
    except:
        return {"date": "", "count": 0}

def save_state(state):
    with open("state.json", "w") as f:
        json.dump(state, f)

# ================= IMAGE =================
def get_image():
    return "https://source.unsplash.com/800x400/?news,world"

# ================= AI REWRITE =================
def ai_rewrite(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": f"""
Rewrite this news into a professional journalist article.

Rules:
- 2–3 paragraphs
- natural tone
- simple English

News:
{text}
"""
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

# ================= HTML GENERATOR (FIXED) =================
def make_html(title, content):

    safe_content = content.replace("\n", "<br>")

    html = f"""
    <div style="font-family:Arial;padding:10px">
        <h1>{title}</h1>
        <img src="{get_image()}" style="width:100%;border-radius:10px;">
        <hr>
        <p style="line-height:1.6">{safe_content}</p>
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
        "kind": "blogger#post",
        "title": title,
        "content": make_html(title, content),
        "status": "LIVE"
    }

    print("\n===== DEBUG START =====")
    print("BLOG_ID:", BLOG_ID)
    print("TITLE:", title)

    try:
        res = requests.post(url, headers=headers, json=data, timeout=30)

        print("STATUS CODE:", res.status_code)
        print("RESPONSE:", res.text)

        print("===== DEBUG END =====\n")

        return res.json()

    except Exception as e:
        print("POST ERROR:", e)
        return {}

# ================= DAILY LIMIT =================
state = load_state()
today = datetime.now().strftime("%Y-%m-%d")

if state["date"] != today:
    state["date"] = today
    state["count"] = 0

if state["count"] >= 4:
    print("DAILY LIMIT REACHED")
    exit()

# ================= NEWS FETCH =================
feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("NO NEWS FOUND")
    exit()

entry = random.choice(feed.entries)

title = entry.title
summary = entry.summary

# ================= RUN =================
print("BOT STARTED...")

article = ai_rewrite(title + " " + summary)

result = post_blog(title, article)

# ================= UPDATE STATE =================
state["count"] += 1
save_state(state)

print("DONE | POSTS TODAY:", state["count"])
