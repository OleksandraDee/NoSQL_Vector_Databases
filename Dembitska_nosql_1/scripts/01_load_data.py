import os
from pathlib import Path

import pandas as pd

from pymongo import MongoClient
from dotenv import load_dotenv
from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI не знайдено у файлі .env")

DB_NAME = "spotify"
CSV_PATH = BASE_DIR / "dataset.csv"
BATCH_SIZE = 1000

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

db["tracks_raw"].drop()

print("Читаємо CSV...")

df = pd.read_csv(CSV_PATH)

print(f"Знайдено {len(df)} треків")

df["explicit"] = df["explicit"].astype(bool)

int_cols = [
    "popularity",
    "duration_ms",
    "key",
    "mode",
    "time_signature",
]

for col in int_cols:
    df[col] = df[col].astype(int)

float_cols = [
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
]

for col in float_cols:
    df[col] = df[col].astype(float)

query = df["artists"].isna() | df["track_name"].isna()

records = df[~query].to_dict("records")

print("Завантажуємо у MongoDB...")

for i in tqdm(range(0, len(records), BATCH_SIZE)):
    db["tracks_raw"].insert_many(records[i:i+BATCH_SIZE])

print()
print("=" * 50)
print("Завантаження завершено")
print("=" * 50)

print(f"Документів: {db['tracks_raw'].count_documents({})}")

print()

print("Перший документ:")

print(db["tracks_raw"].find_one())