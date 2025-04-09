#fetch_weather.py

from dotenv import load_dotenv; load_dotenv()
import os, requests, json, time, pathlib

from confluent_kafka import Producer
producer = Producer({"bootstrap.servers": "host.docker.internal:9092"})
print("Kafka bootstrap →", producer.list_topics(timeout=3).orig_broker_name)

CITY = os.getenv("WEATHER_CITY", "London")

# 1 · geo‑lookup
geo = requests.get(
    f"https://geocoding-api.open-meteo.com/v1/search?name={CITY}&count=1",
    timeout=10).json()
if not geo.get("results"):
    raise SystemExit(f"City '{CITY}' not found")
lat, lon = geo["results"][0]["latitude"], geo["results"][0]["longitude"]

# 2 · forecast params
params = {
    "latitude": lat, "longitude": lon,
    "current_weather": "true",
    "hourly": "temperature_2m,relativehumidity_2m,precipitation",
    "timezone": "auto", "forecast_days": 1
}
BASE = "https://api.open-meteo.com/v1/forecast"
OUT  = pathlib.Path(__file__).with_name("weather.json")

while True:
    data = requests.get(BASE, params=params, timeout=10).json()
    json.dump(data, OUT.open("w"), indent=2)
    cw = data["current_weather"]
    
    # Publish to Redpanda
    producer.produce(
        topic="lifestyle.raw",
        key="weather",                         # helps downstream route by type
        value=json.dumps(data).encode()     # bytes!
    )
    producer.flush()                        # make sure it actually sends
    
    print(f"☁️ {CITY}: {cw['temperature']}°C, wind {cw['windspeed']} km/h")
    time.sleep(600)                      # once every 6 hrs (no API key, no hard cap)
