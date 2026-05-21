import feedparser
import requests
import json
import os
from datetime import datetime

# ================= CONFIG =================
G = "AIzaSyC6RBTnuWqYC6iHpCAChX1SYm3vZSfwR-M"
BLOG_ID = "1025477209020710762"
ACCESS_TOKEN = "ya29.a0AQvPyIMLtl9tsviYulp-cPvhY-Oq0scfDomqSSYBRSe-dYKX3KFZ-mZc9CMS2wG4Bu9CNgxIEJr8_prtArGqNDMqFkOqT5IfXy-Q9OncKH9toLt2XuY8_fWO8dlsEkCvbD24MPOWFdZiDitJs9HfNWV3TMUp07vy_FkbzlORaghQh8pJN3ra3ju2Xc-CeIvZ33kSChEaCgYKAfMSARASFQHGX2MiYtQtwMQ8QPPZ9o5BXtFUMQ0206"

RSS_URL = "https://feeds.bbci.co.uk/news/rss.xml"


# ================= STATE MANAGER =================
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


# ================= AI WRITER =================
def ai_rewrite(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""
You are a professional news editor.

Rewrite this into a human-written news article:

Rules:
- Natural human tone
- 2–3 paragraphs
- Clean journalism style
- Attractive headline style

News:
{text}
"""

    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    res = requests.post(url, json=data)

    try:
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return text


# ================= HTML FORMAT =================
def to_html(title, content, image):
    return f"""
    <div style="font-family:Arial;padding:10px;">
        <h1>{title}</h1>

        <img src="{image}" style="width:100%;border-radius:10px;"/>

        <p><b>AI Generated News Article</b></p>
        <hr>

        <div style="line-height:1.6;">
            {content.replace('\n','<br>')}
        </div>
    </div>
    """


# ================= POST TO BLOGGER =================
def post_blog(title, content):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    image = get_image()
    html = to_html(title, content, image)

    data = {
        "title": title,
        "content": html
    }

    return requests.post(url, headers=headers, json=data).json()


# ================= DAILY LIMIT SYSTEM =================
state = load_state()
today = datetime.now().strftime("%Y-%m-%d")

if state["date"] != today:
    state["date"] = today
    state["count"] = 0

if state["count"] >= 4:
    print("Daily limit reached (4 posts)")
    exit()


# ================= GET NEWS =================
feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("No news found")
    exit()

entry = feed.entries[0]

title = entry.title
summary = entry.summary


# ================= RUN AI =================
article = ai_rewrite(title + " " + summary)


# ================= POST =================
result = post_blog(title, article)

print("POST RESULT:")
print(result)


# ================= UPDATE STATE =================
state["count"] += 1
save_state(state)

print("TOTAL POSTS TODAY:", state["count"])
