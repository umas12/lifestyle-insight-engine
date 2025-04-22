# preprocess/worker_weather.py

import json, uuid
from common import kafka_consumer, COL, EMBED

c = kafka_consumer("worker-weather")
print("☁️  weather worker ready")

while True:
    msg = c.poll(1.0)
    if msg is None or msg.error(): 
        continue
    if msg.key() != b"weather":   
        continue

    payload = json.loads(msg.value())
    cw = payload["current_weather"]
    city = payload.get("timezone", "unknown")
    text = f"Weather in {city}: {cw['temperature']}°C, wind {cw['windspeed']} km/h"
    vec  = EMBED.encode([text])[0].tolist()

    uid = f"weather_{uuid.uuid4().hex}"
    COL.add(ids=[uid], documents=[text], embeddings=[vec],
            metadatas=[{"type":"weather", "city": city}])
    print("✅ weather →", uid)
