import feedparser
import requests
import json
from datetime import datetime
import os

# ================= CONFIG =================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BLOG_ID = os.getenv("BLOG_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

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

# ================= AI =================
def ai_rewrite(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": f"""
You are a professional journalist.

Rewrite this news into a human-style article:

- Natural tone
- 2–3 paragraphs
- Clean journalism style

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
    except:
        return text

# ================= HTML =================
def make_html(title, content):
    return f"""
    <div style="font-family:Arial;padding:10px">
        <h1>{title}</h1>
        <img src="{get_image()}" style="width:100%;border-radius:10px;">
        <hr>
        <p style="line-height:1.6">{content.replace('\n','<br>')}</p>
    </div>
    """

# ================= POST =================
def post_blog(title, content):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "title": title,
        "content": make_html(title, content)
    }

    try:
        res = requests.post(url, headers=headers, json=data, timeout=30)
        print(res.text)
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

# ================= NEWS =================
feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("NO NEWS")
    exit()

entry = feed.entries[0]

title = entry.title
summary = entry.summary

# ================= RUN =================
article = ai_rewrite(title + " " + summary)
post_blog(title, article)

state["count"] += 1
save_state(state)

print("DONE | POSTS TODAY:", state["count"])
