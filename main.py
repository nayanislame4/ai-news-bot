import feedparser
import requests

# ===== তোমার API =====
GEMINI_API_KEY = "AIzaSyC6RBTnuWqYC6iHpCAChX1SYm3vZSfwR-M"
BLOG_ID = "1025477209020710762"
ACCESS_TOKEN = "ya29.a0AQvPyIMLtl9tsviYulp-cPvhY-Oq0scfDomqSSYBRSe-dYKX3KFZ-mZc9CMS2wG4Bu9CNgxIEJr8_prtArGqNDMqFkOqT5IfXy-Q9OncKH9toLt2XuY8_fWO8dlsEkCvbD24MPOWFdZiDitJs9HfNWV3TMUp07vy_FkbzlORaghQh8pJN3ra3ju2Xc-CeIvZ33kSChEaCgYKAfMSARASFQHGX2MiYtQtwMQ8QPPZ9o5BXtFUMQ0206"

# ===== নিউজ সোর্স =====
RSS_URL = "https://feeds.bbci.co.uk/news/rss.xml"

feed = feedparser.parse(RSS_URL)
entry = feed.entries[0]

title = entry.title
summary = entry.summary

# ===== AI লেখে =====
def ai(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

    data = {
        "contents": [{
            "parts": [{
                "text": "এই নিউজটা সুন্দর করে লিখো: " + text
            }]
        }]
    }

    r = requests.post(url, json=data)

    try:
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return text

article = ai(title + summary)

# ===== Blogger এ পোস্ট =====
def post():
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "title": title,
        "content": article
    }

    return requests.post(url, headers=headers, json=data).json()

result = post()
print(result)
