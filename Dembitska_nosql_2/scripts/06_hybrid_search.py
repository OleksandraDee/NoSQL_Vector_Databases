import os
import numpy as np
import pandas as pd

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# ==========================================================
# Configuration
# ==========================================================

load_dotenv()

API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

# ==========================================================
# Load data
# ==========================================================

print("=" * 60)
print("Loading dataset...")
print("=" * 60)

df = pd.read_parquet("data/arxiv_subset.parquet")

print("Documents:", len(df))

# ==========================================================
# BM25 index
# ==========================================================

print("\nBuilding BM25 index...")

tokenized = [text.lower().split() for text in df["text"]]

bm25 = BM25Okapi(tokenized)

print("BM25 ready.")

# ==========================================================
# Pinecone
# ==========================================================

print("\nConnecting to Pinecone...")

pc = Pinecone(api_key=API_KEY)
index = pc.Index(INDEX_NAME)

print("Connected.")

# ==========================================================
# Embedding model
# ==========================================================

print("\nLoading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Model loaded.")

# ==========================================================
# Query
# ==========================================================

QUERY = "deep learning for image classification"

print("\n")
print("=" * 60)
print("QUERY")
print("=" * 60)

print(QUERY)

# ==========================================================
# BM25 SEARCH
# ==========================================================

print("\n")
print("=" * 60)
print("BM25 RESULTS")
print("=" * 60)

tokens = QUERY.lower().split()

scores = bm25.get_scores(tokens)

bm25_ids = np.argsort(scores)[::-1][:5]

bm25_results = []

for rank, idx in enumerate(bm25_ids, start=1):

    bm25_results.append(df.iloc[idx]["id"])

    print(f"{rank}. {df.iloc[idx]['title']}")

# ==========================================================
# VECTOR SEARCH
# ==========================================================

print("\n")
print("=" * 60)
print("VECTOR SEARCH")
print("=" * 60)

query_vector = model.encode(QUERY).tolist()

response = index.query(
    vector=query_vector,
    top_k=5,
    include_metadata=True
)

vector_results = []

for rank, match in enumerate(response["matches"], start=1):

    vector_results.append(match["id"])

    print(f"{rank}. {match['metadata']['title']}")

# ==========================================================
# RRF
# ==========================================================

print("\n")
print("=" * 60)
print("HYBRID SEARCH (RRF)")
print("=" * 60)

rrf_scores = {}

K = 60

for rank, doc in enumerate(bm25_results):

    rrf_scores[doc] = rrf_scores.get(doc, 0) + 1 / (K + rank + 1)

for rank, doc in enumerate(vector_results):

    rrf_scores[doc] = rrf_scores.get(doc, 0) + 1 / (K + rank + 1)

ranking = sorted(
    rrf_scores.items(),
    key=lambda x: x[1],
    reverse=True
)

for i, (doc_id, score) in enumerate(ranking, start=1):

    title = df[df["id"] == doc_id]["title"].values[0]

    print(f"{i}. {title}")

# ==========================================================
# Conclusion
# ==========================================================

print("\n")
print("=" * 60)
print("Conclusion")
print("=" * 60)

print("""
BM25 searches using keyword overlap.

Semantic search finds documents with similar meaning.

Hybrid Search combines both rankings using
Reciprocal Rank Fusion (RRF), producing
more relevant and robust results.
""")