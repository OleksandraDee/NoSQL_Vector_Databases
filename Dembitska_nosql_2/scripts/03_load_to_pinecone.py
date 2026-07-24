import os
import time
import numpy as np
import pandas as pd

from dotenv import load_dotenv
from pinecone import Pinecone

# ==========================================================
# Configuration
# ==========================================================

load_dotenv()

API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")

DATASET = "data/arxiv_subset.parquet"
EMBEDDINGS = "embeddings/embeddings.npy"

# ==========================================================
# Load dataset
# ==========================================================

print("=" * 70)
print("Loading dataset...")
print("=" * 70)

df = pd.read_parquet(DATASET)
embeddings = np.load(EMBEDDINGS)

print(f"Documents : {len(df)}")
print(f"Embeddings: {embeddings.shape}")

# ==========================================================
# Connect to Pinecone
# ==========================================================

print("\nConnecting to Pinecone...")

pc = Pinecone(api_key=API_KEY)
index = pc.Index(INDEX_NAME)

print("Connected successfully.")

# ==========================================================
# Upload vectors
# ==========================================================

print("\nUploading vectors...")

BATCH_SIZE = 100

for start in range(0, len(df), BATCH_SIZE):

    end = min(start + BATCH_SIZE, len(df))

    vectors = []

    for i in range(start, end):

        row = df.iloc[i]

        # extract publication year
        year = int(str(row["update_date"])[:4])

        vectors.append({

            "id": str(row["id"]),

            "values": embeddings[i].tolist(),

            "metadata": {

                "title": str(row["title"]),

                "categories": str(row["categories"]),

                "authors": str(row["authors"]),

                "update_date": str(row["update_date"]),

                "update_year": year

            }

        })

    index.upsert(vectors=vectors)

    print(f"Uploaded {end}/{len(df)}")

# ==========================================================
# Wait until indexing completes
# ==========================================================

print("\nWaiting for indexing...")

time.sleep(5)

# ==========================================================
# Show index statistics
# ==========================================================

stats = index.describe_index_stats()

print("\n" + "=" * 70)
print("Index statistics")
print("=" * 70)

print(stats)

print("\nUpload completed successfully.")