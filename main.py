import os
import feedparser
import requests
import json
from datetime import datetime

# ================= CONFIG =================
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


# ================= AI =================
def ai_rewrite(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": "Rewrite this news into a human article (2-3 paragraphs): " + text
            }]
        }]
    }

    try:
        res = requests.post(url, json=payload, timeout=30)
        data = res.json()

        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]

        return text

    except:
        return text


# ================= HTML (SAFE VERSION) =================
def make_html(title, content):
    content = content.replace("\n", "<br>")

    html = """
    <div style="font-family:Arial;padding:10px">
        <h1>{title}</h1>
        <img src="{img}" style="width:100%;border-radius:10px;">
        <hr>
        <p style="line-height:1.6">{content}</p>
    </div>
    """.format(
        title=title,
        img=get_image(),
        content=content
    )

    return html


# ================= POST BLOG =================
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


# ================= LIMIT =================
state = load_state()
today = datetime.now().strftime("%Y-%m-%d")

if state["date"] != today:
    state["date"] = today
    state["count"] = 0

if state["count"] >= 4:
    print("LIMIT REACHED")
    exit()


# ================= NEWS =================
feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("NO NEWS")
    exit()

entry = feed.entries[0]

title = entry.title
summary = getattr(entry, "summary", "")


# ================= RUN =================
article = ai_rewrite(title + " " + summary)
post_blog(title, article)

state["count"] += 1
save_state(state)

print("DONE | COUNT:", state["count"])
