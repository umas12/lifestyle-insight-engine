# preprocess/worker_news.py 

import json, uuid, time
from common import kafka_consumer, COL, EMBED

c = kafka_consumer("worker-news")       # group id

print("📰  news worker running…")
while True:
    msg = c.poll(1.0)
    if msg is None or msg.error():         
        continue
    if msg.key() != b"news":                # skip images, reddit, etc.
        continue

    payload = json.loads(msg.value())
    text = " ".join(a["title"] for a in payload["articles"])
    vec  = EMBED.encode([text])[0].tolist()


    uid = f"news_{uuid.uuid4().hex}"
    COL.add(ids=[uid], documents=[text], embeddings=[vec],
            metadatas=[{"type":"news"}])
    print("✅ stored", uid, "chars:", len(text))
