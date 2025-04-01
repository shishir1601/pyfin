import feedparser
from textblob import TextBlob
import time
from datetime import datetime, timedelta
import schedule
from collections import deque
import threading
from flask import Flask, jsonify

# Initialize Flask app for REST API
app = Flask(__name__)

# Store news items with timestamps in a deque (sliding window)
news_queue = deque(maxlen=1000)  # Large maxlen to handle high frequency, filtered by time later
sentiment_rating = 0.0  # Global variable for sentiment rating

# List of economic news RSS feeds (replace with your preferred sources)
RSS_FEEDS = [
    "http://feeds.reuters.com/reuters/businessNews",
    "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    "http://feeds.marketwatch.com/marketwatch/marketpulse/"
]

def fetch_news():
    """Fetch news from RSS feeds and return a list of entries with timestamps."""
    news_items = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = entry.get("title", "")
                published = entry.get("published", datetime.now().isoformat())
                try:
                    # Parse the published time, assume UTC if no timezone
                    pub_time = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z")
                except ValueError:
                    pub_time = datetime.now()  # Fallback to now if parsing fails
                news_items.append({"title": title, "time": pub_time})
        except Exception as e:
            print(f"Error fetching feed {feed_url}: {e}")
    return news_items

def analyze_sentiment(text):
    """Analyze sentiment of text using TextBlob and return polarity (-1 to 1)."""
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def update_sentiment():
    """Update the news queue and calculate combined sentiment rating."""
    global sentiment_rating, news_queue

    # Fetch new news
    new_items = fetch_news()

    # Add new items to the queue
    for item in new_items:
        news_queue.append(item)

    # Filter items within the last 100 hours
    cutoff_time = datetime.now() - timedelta(hours=100)
    current_news = [item for item in news_queue if item["time"] > cutoff_time]

    if not current_news:
        sentiment_rating = 2.5  # Neutral if no news
        return

    # Calculate average sentiment
    total_polarity = 0.0
    for item in current_news:
        polarity = analyze_sentiment(item["title"])
        total_polarity += polarity

    avg_polarity = total_polarity / len(current_news)
    
    # Map polarity (-1 to 1) to rating (0 to 5)
    # -1 -> 0, 0 -> 2.5, 1 -> 5
    sentiment_rating = ((avg_polarity + 1) / 2) * 5
    print(f"Updated sentiment rating: {sentiment_rating:.2f} (based on {len(current_news)} articles)")

def run_scheduler():
    """Run the scheduler to update sentiment periodically."""
    schedule.every(10).minutes.do(update_sentiment)
    
    # Initial run
    update_sentiment()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# REST API endpoint to get the sentiment rating
@app.route('/sentiment', methods=['GET'])
def get_sentiment():
    return jsonify({
        "sentiment_rating": round(sentiment_rating, 2),
        "scale": "0 (most pessimistic) to 5 (most optimistic)",
        "timestamp": datetime.now().isoformat()
    })

def start_api():
    """Start the Flask API server."""
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Start the Flask API in the main thread
    start_api()


