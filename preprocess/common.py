from dotenv import load_dotenv; load_dotenv()
import chromadb
from chromadb.config import Settings
from confluent_kafka import Consumer
from sentence_transformers import SentenceTransformer

BOOT = "host.docker.internal:9092"   # works from any container on Docker Desktop

def kafka_consumer(group):
    c = Consumer({
        "bootstrap.servers": BOOT,
        "group.id": group,
        "auto.offset.reset": "earliest"
    })
    c.subscribe(["lifestyle.raw"])
    return c 

chroma = chromadb.HttpClient(
    host="host.docker.internal",
    port=8000,
    settings=Settings(anonymized_telemetry=False)
)
COL    = chroma.get_or_create_collection("lifestyle")

EMBED  = SentenceTransformer("all-MiniLM-L6-v2")   # 80 MB, fine for CPU
