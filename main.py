import os
import feedparser
import requests
import json
from datetime import datetime

# ================= CONFIG (FROM GITHUB SECRETS) =================
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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": f"""
You are a professional journalist.

Rewrite this news into a human-written article:
- Natural tone
- 2-3 paragraphs
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

        if "candidates" not in data:
            print("AI ERROR:", data)
            return text

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print("AI EXCEPTION:", e)
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


# ================= POST TO BLOGGER =================
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

        if res.status_code != 200:
            print("BLOG ERROR:", res.text)

        return res.json()

    except Exception as e:
        print("BLOG EXCEPTION:", e)
        return {}


# ================= DAILY LIMIT SYSTEM =================
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

entry = feed.entries[0]

title = entry.title
summary = getattr(entry, "summary", "")


# ================= RUN =================
article = ai_rewrite(title + " " + summary)
post_blog(title, article)

state["count"] += 1
save_state(state)

print("DONE | TOTAL POSTS TODAY:", state["count"])
