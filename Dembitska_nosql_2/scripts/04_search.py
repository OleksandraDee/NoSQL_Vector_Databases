import os

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# ==========================================================
# Configuration
# ==========================================================

load_dotenv()

API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

# ==========================================================
# Connect to Pinecone
# ==========================================================

print("=" * 60)
print("Connecting to Pinecone...")
print("=" * 60)

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
# Semantic search function
# ==========================================================

def semantic_search(query, top_k=5, filter=None):

    print("\n" + "=" * 60)
    print("Query:")
    print(query)
    print("=" * 60)

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

        metadata = match["metadata"]

        print(f"\nResult {i}")
        print("-" * 60)
        print(f"Score: {match['score']:.4f}")
        print(f"Title: {metadata['title']}")
        print(f"Category: {metadata['categories']}")
        print(f"Authors: {metadata['authors']}")
        print(f"Date: {metadata['update_date']}")

# ==========================================================
# TASK 1
# Semantic Search
# ==========================================================

print("\n")
print("=" * 60)
print("TASK 1 - Semantic Search")
print("=" * 60)

semantic_search(
    query="deep learning for image classification",
    top_k=5
)

# ==========================================================
# TASK 2
# Semantic Search + Filter
# ==========================================================

print("\n")
print("=" * 60)
print("TASK 2 - Semantic Search + Filter")
print("=" * 60)

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
# Another Semantic Search
# ==========================================================

print("\n")
print("=" * 60)
print("TASK 3 - Another Semantic Query")
print("=" * 60)

semantic_search(
    query="quantum computing algorithms",
    top_k=5
)

# ==========================================================
# Done
# ==========================================================

print("\n" + "=" * 60)
print("Search completed successfully.")
print("=" * 60)