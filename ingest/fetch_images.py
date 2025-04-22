# ingest/fetch_images.py

from dotenv import load_dotenv; load_dotenv()
import os, requests, json, time, pathlib, random

from confluent_kafka import Producer
producer = Producer({"bootstrap.servers": "host.docker.internal:9092"})
print("Kafka bootstrap →", producer.list_topics(timeout=3).orig_broker_name)

QUERIES = ["interior design", "fitness", "travel", "vegan food"]
HEADERS = {"Authorization": "Client-ID " + os.getenv("UNSPLASH_KEY")}
OUT = pathlib.Path(__file__).with_name("images.json")

while True:
    q  = random.choice(QUERIES)
    url = f"https://api.unsplash.com/photos/random?query={q}&count=10"
    data = requests.get(url, headers=HEADERS, timeout=10).json()
    json.dump(data, OUT.open("w"), indent=2)
    
    # Publish to Redpanda
    producer.produce(
        topic="lifestyle.raw",
        key="images",                        
        value=json.dumps(data).encode()     
    )
    producer.flush() 
    
    print("📷 grabbed 10 photos for", q)
    time.sleep(120)                       # 40 calls/hr (Unsplash free cap is 50 / hr)
