# preprocess/worker_images.py

import io, json, uuid, requests
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from common import kafka_consumer, COL, EMBED
from transformers import BitsAndBytesConfig

print("⏳ loading BLIP-2 2.7 B (4-bit)…")
proc  = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-flan-t5-xl",
    device_map=None,         
    torch_dtype="float32",    
    offload_folder=None       # explicitly disable offloading
)

def caption(url):
    image = Image.open(io.BytesIO(requests.get(url, timeout=10).content)).convert("RGB")
    prompt = "Describe this photo in a short caption."
    inputs = proc(images=image, text=prompt, return_tensors="pt").to(model.device)
    output = model.generate(**inputs, max_new_tokens=20)
    return proc.tokenizer.decode(output[0], skip_special_tokens=True)

c = kafka_consumer("worker-images")
print("🖼️  image worker ready (CPU)")


while True:
    msg = c.poll(1.0)
    if msg is None or msg.error(): 
        continue
    if msg.key() != b"images":    
        continue

    batch = json.loads(msg.value())     
    for photo in batch:
        cap = caption(photo["urls"]["small"])
        vec = EMBED.encode([cap])[0].tolist()
        uid = f"img_{photo['id']}"
        COL.add(ids=[uid], documents=[cap], embeddings=[vec], metadatas=[{"type":"image"}])
        print("✅ image →", uid, ":", cap[:60], "…")
