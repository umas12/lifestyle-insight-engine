# preprocess/worker_recipes.py

import json, uuid, re, html
from common import kafka_consumer, COL, EMBED

TAG_RE = re.compile(r"<[^>]+>")   # remove HTML tags from Spoonacular summary

def clean(html_text):
    return TAG_RE.sub("", html.unescape(html_text))

c = kafka_consumer("worker-recipes")
print("🍲  recipe worker ready")

while True:
    msg = c.poll(1.0)
    if msg is None or msg.error(): 
        continue
    if msg.key() != b"recipes":   
        continue

    payload = json.loads(msg.value())  
    summaries = [clean(r["summary"]) for r in payload["recipes"]]
    text  = " ".join(summaries)
    vec  = EMBED.encode([text])[0].tolist()

    uid = f"recipe_{uuid.uuid4().hex}"
    COL.add(ids=[uid], documents=[text], embeddings=[vec],
            metadatas=[{"type":"recipe", "count": len(summaries)}])
    print("✅ recipes →", uid)
