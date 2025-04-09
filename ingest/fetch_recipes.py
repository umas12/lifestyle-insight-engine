#ingest/fetch_recipes.py

from dotenv import load_dotenv; load_dotenv()
import os, requests, json, time, pathlib

from confluent_kafka import Producer
producer = Producer({"bootstrap.servers": "host.docker.internal:9092"})
print("Kafka bootstrap →", producer.list_topics(timeout=3).orig_broker_name)

OUT = pathlib.Path(__file__).with_name("recipes.json")
URL = ("https://api.spoonacular.com/recipes/random"f"?number=5&apiKey={os.getenv('SPOON_KEY')}")

while True:
    data = requests.get(URL, timeout=10).json()
    json.dump(data, OUT.open("w"), indent=2)
    
    # Publish to Redpanda
    producer.produce(
        topic="lifestyle.raw",
        key="recipes",                         # helps downstream route by type
        value=json.dumps(data).encode()     # bytes!
    )
    producer.flush()                        # make sure it actually sends
    
    print("🍲 saved", len(data.get("recipes", [])), "recipes")
    time.sleep(180)                      # 480 calls/day ≪ 3 000 free/mo
