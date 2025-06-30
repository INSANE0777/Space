import requests
import os
from datetime import datetime, timedelta

def run(previous_data: dict) -> dict:
    """
    Fetch latest news articles about a topic using NewsAPI
    and add results under 'news' key in previous_data.
    """

    # Determine the topic from previous_data or default to 'SpaceX'
    topic = previous_data.get("topic") or "SpaceX"

    api_key = os.getenv("NEWSAPI_API_KEY")
    if not api_key:
        raise Exception("NEWSAPI_API_KEY environment variable is not set.")

    # Use a recent date (e.g., 7 days ago) for the 'from' parameter
    from_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": topic,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": api_key,
        "pageSize": 5,  # limit number of articles to 5
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"NewsAPI error: {response.status_code} - {response.text}")

    data = response.json()

    articles = []
    for article in data.get("articles", []):
        articles.append({
            "title": article.get("title"),
            "source": article.get("source", {}).get("name"),
            "url": article.get("url"),
            "publishedAt": article.get("publishedAt"),
            "description": article.get("description"),
        })

    previous_data["news"] = {
        "success": True,
        "topic": topic,
        "articles": articles,
    }

    return previous_data
