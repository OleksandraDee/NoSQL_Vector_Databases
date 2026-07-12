import numpy as np
import pandas as pd
from pathlib import Path

from sentence_transformers import SentenceTransformer
from tqdm import tqdm


INPUT_FILE = Path("data/arxiv_subset.parquet")
OUTPUT_FILE = Path("embeddings/embeddings.npy")

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

BATCH_SIZE = 32

print("=" * 60)
print("Loading dataset...")
print("=" * 60)

df = pd.read_parquet(INPUT_FILE)

texts = df["text"].tolist()

print(f"Documents: {len(texts)}")

print("\nLoading SPECTER2 model...")
model = SentenceTransformer(MODEL_NAME)

print("Model loaded successfully.")

print("\nGenerating embeddings...")

embeddings = []

for i in tqdm(range(0, len(texts), BATCH_SIZE)):

    batch = texts[i:i+BATCH_SIZE]

    vectors = model.encode(
        batch,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    embeddings.append(vectors)

embeddings = np.vstack(embeddings)

OUTPUT_FILE.parent.mkdir(exist_ok=True)

np.save(
    OUTPUT_FILE,
    embeddings
)

print("\nEmbedding generation completed!")

print("=" * 60)
print(f"Embeddings shape: {embeddings.shape}")
print(f"Saved to: {OUTPUT_FILE}")
print("=" * 60)

print("\nFirst embedding (first 10 values):")

print(embeddings[0][:10])