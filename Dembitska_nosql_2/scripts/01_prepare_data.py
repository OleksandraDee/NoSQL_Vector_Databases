import pandas as pd
import json
from pathlib import Path


INPUT_FILE = Path("data/arxiv-metadata-oai-snapshot.json")
OUTPUT_FILE = Path("data/arxiv_subset.parquet")

MAX_RECORDS = 5000


print("=" * 60)
print("Reading arXiv dataset...")
print("=" * 60)

records = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):

        if i >= MAX_RECORDS:
            break

        article = json.loads(line)

        records.append({
            "id": article.get("id"),
            "title": article.get("title"),
            "abstract": article.get("abstract"),
            "categories": article.get("categories"),
            "authors": article.get("authors"),
            "update_date": article.get("update_date")
        })

df = pd.DataFrame(records)

print(f"Loaded {len(df)} papers.")


print("\nCleaning dataset...")

df = df.dropna(subset=["title", "abstract"])

df["title"] = df["title"].str.strip()
df["abstract"] = df["abstract"].str.strip()

df = df[
    (df["title"] != "") &
    (df["abstract"] != "")
]


print("Preparing text field...")

df["text"] = (
    "Title: " +
    df["title"] +
    "\n\nAbstract:\n" +
    df["abstract"]
)


OUTPUT_FILE.parent.mkdir(exist_ok=True)

df.to_parquet(
    OUTPUT_FILE,
    index=False
)

print("\nDataset prepared successfully!")

print("=" * 60)
print(f"Documents: {len(df)}")
print(f"Saved to: {OUTPUT_FILE}")
print("=" * 60)

print("\nFirst document:\n")

print(df.iloc[0])