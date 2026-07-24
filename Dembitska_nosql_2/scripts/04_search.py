import os

import numpy as np
import pandas as pd

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cdist

# ==========================================================
# Configuration
# ==========================================================

load_dotenv()

API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

DATASET = "data/arxiv_subset.parquet"
EMBEDDINGS = "embeddings/embeddings.npy"

# ==========================================================
# Load local data
# ==========================================================

print("=" * 70)
print("Loading local dataset...")
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

print("Connected!")

# ==========================================================
# Load embedding model
# ==========================================================

print("\nLoading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Model loaded.")

# ==========================================================
# Semantic Search Function
# ==========================================================

def semantic_search(query, top_k=5, filter=None):

    print("\n" + "=" * 70)
    print("Query:")
    print(query)
    print("=" * 70)

    query_vector = model.encode(query).tolist()

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        filter=filter
    )

    if len(results["matches"]) == 0:
        print("No results found.")
        return

    for i, match in enumerate(results["matches"], start=1):

        meta = match["metadata"]

        print(f"\nResult {i}")
        print("-" * 60)
        print(f"Score    : {match['score']:.4f}")
        print(f"Title    : {meta['title']}")
        print(f"Category : {meta['categories']}")
        print(f"Authors  : {meta['authors']}")
        print(f"Date     : {meta['update_date']}")

# ==========================================================
# TASK 1
# Semantic Search
# ==========================================================

print("\n")
print("=" * 70)
print("TASK 1 - Semantic Search")
print("=" * 70)

semantic_search(
    query="deep learning for image classification",
    top_k=5
)

# ==========================================================
# TASK 2
# Semantic Search + Category Filter
# ==========================================================

print("\n")
print("=" * 70)
print("TASK 2 - Category Filter")
print("=" * 70)

semantic_search(
    query="neural networks",
    top_k=5,
    filter={
        "categories": {
            "$eq": "cs.LG"
        }
    }
)

# ==========================================================
# TASK 3
# Semantic Search
# ==========================================================

print("\n")
print("=" * 70)
print("TASK 3 - Another Semantic Query")
print("=" * 70)

semantic_search(
    query="quantum computing algorithms",
    top_k=5
)

# ==========================================================
# TASK 4
# Publication Year Filter
# ==========================================================

print("\n")
print("=" * 70)
print("TASK 4 - Publication Year Filter")
print("=" * 70)

semantic_search(
    query="deep learning",
    top_k=5,
    filter={
        "update_year": {
            "$gte": 2010
        }
    }
)

# ==========================================================
# TASK 5
# Local Metric Comparison
# ==========================================================

print("\n")
print("=" * 70)
print("TASK 5 - Cosine vs Dot Product vs L2")
print("=" * 70)

query = "deep learning for image classification"

query_embedding = model.encode(query)

###########################################################
# COSINE
###########################################################

cos_scores = cosine_similarity(
    [query_embedding],
    embeddings
)[0]

cos_idx = np.argsort(cos_scores)[::-1][:5]

print("\nCOSINE")
print("-" * 60)

for rank, idx in enumerate(cos_idx, start=1):

    print(
        f"{rank}. "
        f"{df.iloc[idx]['title']} "
        f"(score={cos_scores[idx]:.4f})"
    )

###########################################################
# DOT PRODUCT
###########################################################

dot_scores = embeddings @ query_embedding

dot_idx = np.argsort(dot_scores)[::-1][:5]

print("\nDOT PRODUCT")
print("-" * 60)

for rank, idx in enumerate(dot_idx, start=1):

    print(
        f"{rank}. "
        f"{df.iloc[idx]['title']} "
        f"(score={dot_scores[idx]:.4f})"
    )

###########################################################
# L2 DISTANCE
###########################################################

l2_scores = cdist(
    [query_embedding],
    embeddings,
    metric="euclidean"
)[0]

l2_idx = np.argsort(l2_scores)[:5]

print("\nL2 DISTANCE")
print("-" * 60)

for rank, idx in enumerate(l2_idx, start=1):

    print(
        f"{rank}. "
        f"{df.iloc[idx]['title']} "
        f"(distance={l2_scores[idx]:.4f})"
    )

###########################################################
# Discussion
###########################################################

print("\n")
print("=" * 70)
print("Discussion")
print("=" * 70)

print("""
Cosine similarity compares vectors by their angle and ignores vector magnitude.

Dot Product considers both angle and magnitude, therefore rankings may differ
when embedding norms are different.

L2 Distance measures the Euclidean distance between vectors.

Because sentence embeddings are not perfectly normalized, Cosine, Dot Product,
and L2 may produce slightly different rankings.

Cosine similarity is generally preferred for semantic search because it focuses
on semantic direction rather than vector length.
""")

# ==========================================================
# Done
# ==========================================================

print("\n")
print("=" * 70)
print("Search completed successfully.")
print("=" * 70)