# ingest/fetch_news.py
    
from dotenv import load_dotenv; load_dotenv()
import os, requests, json, time, pathlib

from confluent_kafka import Producer
producer = Producer({
    "bootstrap.servers": "host.docker.internal:9092"
})


OUT = pathlib.Path(__file__).with_name("news.json")
URL = ("https://newsapi.org/v2/top-headlines?category=health&language=en&apiKey=" + os.getenv("NEWS_KEY"))

while True:
    data = requests.get(URL, timeout=10).json()
    json.dump(data, OUT.open("w"), indent=2)
    
    # Publish to Redpanda
    producer.produce(
        topic="lifestyle.raw",
        key="news",                         # helps downstream route by type
        value=json.dumps(data).encode()     # bytes!
    )
    producer.flush()                        # make sure it actually sends
    
    print("📰", len(data.get("articles", [])), "articles saved")
    time.sleep(60)                       # poll every minute (well under free 100 req/day)

