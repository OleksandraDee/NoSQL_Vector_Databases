import os
import time
import numpy as np
import pandas as pd

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")

print("=" * 60)
print("Loading dataset...")
print("=" * 60)

df = pd.read_parquet("data/arxiv_subset.parquet")
embeddings = np.load("embeddings/embeddings.npy")

print(f"Documents: {len(df)}")
print(f"Embeddings: {embeddings.shape}")

print("\nConnecting to Pinecone...")

pc = Pinecone(api_key=API_KEY)

index = pc.Index(INDEX_NAME)

print("Connected successfully.")

print("\nUploading vectors...")

batch_size = 100

for start in range(0, len(df), batch_size):

    end = min(start + batch_size, len(df))

    vectors = []

    for i in range(start, end):

        vectors.append({

            "id": str(df.iloc[i]["id"]),

            "values": embeddings[i].tolist(),

            "metadata": {

                "title": str(df.iloc[i]["title"]),

                "categories": str(df.iloc[i]["categories"]),

                "authors": str(df.iloc[i]["authors"]),

                "update_date": str(df.iloc[i]["update_date"])

            }

        })

    index.upsert(vectors=vectors)

    print(f"Uploaded {end}/{len(df)}")

print("\nUpload completed!")

time.sleep(5)

stats = index.describe_index_stats()

print("=" * 60)
print("Index statistics")
print("=" * 60)

print(stats)