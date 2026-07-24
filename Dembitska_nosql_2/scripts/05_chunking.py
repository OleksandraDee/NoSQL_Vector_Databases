import os
import time

import pandas as pd
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# ==========================================================
# Configuration
# ==========================================================

load_dotenv()

API_KEY = os.getenv("PINECONE_API_KEY")

FIXED_INDEX = "arxiv-fixed"
PARAGRAPH_INDEX = "arxiv-paragraph"

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

DATASET = "data/arxiv_subset.parquet"

FIXED_CHUNK_SIZE = 500

# ==========================================================
# Load article
# ==========================================================

print("=" * 70)
print("Loading dataset...")
print("=" * 70)

df = pd.read_parquet(DATASET)

text = df.iloc[0]["text"]

print("Article loaded.")

# ==========================================================
# Create chunks
# ==========================================================

print("\n" + "=" * 70)
print("Creating chunks...")
print("=" * 70)

fixed_chunks = [
    text[i:i + FIXED_CHUNK_SIZE]
    for i in range(0, len(text), FIXED_CHUNK_SIZE)
]

paragraph_chunks = [
    p.strip()
    for p in text.split("\n\n")
    if p.strip()
]

print(f"Fixed chunks      : {len(fixed_chunks)}")
print(f"Paragraph chunks  : {len(paragraph_chunks)}")

avg_fixed = sum(len(c) for c in fixed_chunks) / len(fixed_chunks)
avg_paragraph = sum(len(c) for c in paragraph_chunks) / len(paragraph_chunks)

# ==========================================================
# Load embedding model
# ==========================================================

print("\nLoading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Model loaded.")

# ==========================================================
# Connect Pinecone
# ==========================================================

print("\nConnecting to Pinecone...")

pc = Pinecone(api_key=API_KEY)

print("Connected.")

# ==========================================================
# Create index
# ==========================================================

def create_index(index_name):

    indexes = pc.list_indexes().names()

    if index_name not in indexes:

        print(f"Creating index: {index_name}")

        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    return pc.Index(index_name)

# ==========================================================
# Upload chunks
# ==========================================================

def upload_chunks(index, chunks):

    vectors = []

    for i, chunk in enumerate(chunks):

        embedding = model.encode(chunk)

        vectors.append({

            "id": str(i),

            "values": embedding.tolist(),

            "metadata": {

                "text": chunk

            }

        })

    index.upsert(vectors=vectors)

# ==========================================================
# Fixed index
# ==========================================================

print("\nUploading fixed chunks...")

fixed_index = create_index(FIXED_INDEX)

upload_chunks(fixed_index, fixed_chunks)

print("Waiting for indexing...")
time.sleep(5)

print(fixed_index.describe_index_stats())

# ==========================================================
# Paragraph index
# ==========================================================

print("\nUploading paragraph chunks...")

paragraph_index = create_index(PARAGRAPH_INDEX)

upload_chunks(paragraph_index, paragraph_chunks)

print("Waiting for indexing...")
time.sleep(5)

print(paragraph_index.describe_index_stats())

# ==========================================================
# Search function
# ==========================================================

def search(index, query):

    query_vector = model.encode(query)

    return index.query(
        vector=query_vector.tolist(),
        top_k=3,
        include_metadata=True
    )

# ==========================================================
# Search query
# ==========================================================

query = "prompt diphoton production"

# ==========================================================
# Fixed search
# ==========================================================

print("\n")
print("=" * 70)
print("SEARCH - FIXED CHUNKS")
print("=" * 70)

results = search(fixed_index, query)

for i, match in enumerate(results["matches"], start=1):

    print(f"\nResult {i}")
    print("-" * 60)
    print(f"Score : {match['score']:.4f}")
    print(match["metadata"]["text"][:300])

# ==========================================================
# Paragraph search
# ==========================================================

print("\n")
print("=" * 70)
print("SEARCH - PARAGRAPH CHUNKS")
print("=" * 70)

results = search(paragraph_index, query)

for i, match in enumerate(results["matches"], start=1):

    print(f"\nResult {i}")
    print("-" * 60)
    print(f"Score : {match['score']:.4f}")
    print(match["metadata"]["text"][:300])

# ==========================================================
# Comparison
# ==========================================================

print("\n")
print("=" * 70)
print("Comparison")
print("=" * 70)

print(f"Fixed-size chunks      : {len(fixed_chunks)}")
print(f"Paragraph chunks       : {len(paragraph_chunks)}")

print(f"Average fixed chunk    : {avg_fixed:.1f}")
print(f"Average paragraph      : {avg_paragraph:.1f}")

print("""
Conclusion

Fixed-size chunking splits documents into equal-length segments.
It is simple and efficient but may cut sentences or logical ideas.

Paragraph chunking preserves the original document structure,
making each chunk more semantically meaningful.

The search results from the paragraph-based index are generally
more coherent because each chunk represents a complete paragraph,
while fixed-size chunking may split important context across chunks.
""")