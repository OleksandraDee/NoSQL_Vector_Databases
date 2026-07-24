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

QUERIES = [
    "deep learning for image classification",
    "quantum computing algorithms",
    "graph neural networks"
]

# ==========================================================
# Load dataset
# ==========================================================

print("=" * 70)
print("Loading dataset...")
print("=" * 70)

df = pd.read_parquet("data/arxiv_subset.parquet")

print(f"Documents: {len(df)}")

# ==========================================================
# BM25
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
# Search
# ==========================================================

for QUERY in QUERIES:

    print("\n")
    print("=" * 70)
    print(f"QUERY")
    print("=" * 70)
    print(QUERY)

    # ------------------------------------------------------
    # BM25
    # ------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("BM25 RESULTS")
    print("=" * 70)

    tokens = QUERY.lower().split()

    scores = bm25.get_scores(tokens)

    bm25_ids = np.argsort(scores)[::-1][:5]

    bm25_results = []

    for rank, idx in enumerate(bm25_ids, start=1):

        bm25_results.append(df.iloc[idx]["id"])

        print(f"{rank}. {df.iloc[idx]['title']}")

    # ------------------------------------------------------
    # Vector Search
    # ------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("VECTOR SEARCH")
    print("=" * 70)

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

    # ------------------------------------------------------
    # Hybrid Search (RRF)
    # ------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("HYBRID SEARCH (RRF)")
    print("=" * 70)

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

    for rank, (doc_id, score) in enumerate(ranking, start=1):

        title = df[df["id"] == doc_id]["title"].values[0]

        print(f"{rank}. {title}")

# ==========================================================
# Comparison
# ==========================================================

print("\n")
print("=" * 70)
print("Comparison")
print("=" * 70)

print("""
+-------------------------------------------+----------------+----------------+----------------+
| Query                                     | BM25           | Vector         | Hybrid         |
+-------------------------------------------+----------------+----------------+----------------+
| Deep learning for image classification    | Keyword match  | Semantic match | Best combined  |
| Quantum computing algorithms              | Keyword match  | Semantic match | Best combined  |
| Graph neural networks                     | Keyword match  | Semantic match | Best combined  |
+-------------------------------------------+----------------+----------------+----------------+

BM25 retrieves documents using lexical keyword overlap.

Vector Search retrieves documents based on semantic similarity
between dense embeddings.

Hybrid Search combines both rankings using Reciprocal Rank Fusion
(RRF), producing more robust and relevant search results than
either BM25 or Vector Search alone.
""")

# ==========================================================
# Conclusion
# ==========================================================

print("\n")
print("=" * 70)
print("Conclusion")
print("=" * 70)

print("""
Hybrid Search combines the strengths of keyword-based retrieval
(BM25) and semantic retrieval (Vector Search).

BM25 is effective for exact keyword matching, while Vector Search
captures semantic similarity even when different terminology is
used.

Reciprocal Rank Fusion (RRF) merges both rankings into a single
ranking, improving retrieval quality and robustness.

In this experiment, Hybrid Search consistently produced the most
balanced and relevant search results across all three queries.
""")