#fetch_reddit.py

from dotenv import load_dotenv; load_dotenv()
import os, json, time, pathlib, praw

from confluent_kafka import Producer
producer = Producer({"bootstrap.servers": "host.docker.internal:9092"})
print("Kafka bootstrap →", producer.list_topics(timeout=3).orig_broker_name)

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)


SUBS = ["nutrition", "TheLifestyle", "Fitness", "Cooking", "AsianBeauty", "BeautyGuruChatter", "SkincareAddiction"]     #Communities in reddit
OUT  = pathlib.Path(__file__).with_name("reddit.json")

while True:
    posts = []
    for sub in SUBS:
        for p in reddit.subreddit(sub).new(limit=12):
            posts.append({"sub": sub, "title": p.title, "score": p.score})
    json.dump(posts, OUT.open("w"), indent=2)
    
    # Publish to Redpanda
    producer.produce(
        topic="lifestyle.raw",
        key="reddit",                         # helps downstream route by type
        value=json.dumps(posts).encode()     # bytes!
    )
    producer.flush()                        # make sure it actually sends
    
    print("🔺", len(posts), "Reddit posts saved")
    time.sleep(120)                      # every 2 min (well within Reddit rules)
