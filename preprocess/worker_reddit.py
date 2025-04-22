# preprocess/worker_reddit.py

import json, uuid
from common import kafka_consumer, COL, EMBED

c = kafka_consumer("worker-reddit")
print("🔺  reddit worker ready")

while True:
    msg = c.poll(1.0)
    if msg is None or msg.error():          # no message
        continue
    if msg.key() != b"reddit":
        continue

    posts = json.loads(msg.value())       
    text  = " ".join(p["title"] for p in posts)
    vec  = EMBED.encode([text])[0].tolist()

    uid = f"reddit_{uuid.uuid4().hex}"
    COL.add(ids=[uid], documents=[text], embeddings=[vec],
            metadatas=[{"type":"reddit", "count": len(posts)}])
    print("✅ reddit →", uid)
