import pandas as pd

# ==========================================================
# Configuration
# ==========================================================

INPUT_FILE = "data/arxiv_subset.parquet"

FIXED_CHUNK_SIZE = 500

# ==========================================================
# Load dataset
# ==========================================================

print("=" * 60)
print("Loading dataset...")
print("=" * 60)

df = pd.read_parquet(INPUT_FILE)

text = df.iloc[0]["text"]

print("Article loaded.\n")

# ==========================================================
# Fixed-size Chunking
# ==========================================================

print("=" * 60)
print("Fixed-size Chunking")
print("=" * 60)

fixed_chunks = []

for i in range(0, len(text), FIXED_CHUNK_SIZE):

    fixed_chunks.append(
        text[i:i + FIXED_CHUNK_SIZE]
    )

print(f"Chunks created: {len(fixed_chunks)}")

avg_fixed = sum(len(c) for c in fixed_chunks) / len(fixed_chunks)

print(f"Average chunk length: {avg_fixed:.1f} characters")

print("\nFirst chunk:\n")
print(fixed_chunks[0])

# ==========================================================
# Paragraph Chunking
# ==========================================================

print("\n")
print("=" * 60)
print("Paragraph Chunking")
print("=" * 60)

paragraph_chunks = [

    paragraph.strip()

    for paragraph in text.split("\n\n")

    if paragraph.strip()

]

print(f"Chunks created: {len(paragraph_chunks)}")

avg_paragraph = sum(len(c) for c in paragraph_chunks) / len(paragraph_chunks)

print(f"Average chunk length: {avg_paragraph:.1f} characters")

print("\nFirst chunk:\n")
print(paragraph_chunks[0])

# ==========================================================
# Comparison
# ==========================================================

print("\n")
print("=" * 60)
print("Comparison")
print("=" * 60)

print(f"Fixed-size chunks : {len(fixed_chunks)}")
print(f"Paragraph chunks  : {len(paragraph_chunks)}")

print(f"Average fixed chunk      : {avg_fixed:.1f}")

print(f"Average paragraph chunk  : {avg_paragraph:.1f}")

print("""
Conclusion

Fixed-size chunking creates chunks of equal size,
which is simple but may split sentences.

Paragraph chunking preserves the logical structure
of the document and usually produces more meaningful
chunks for semantic search.
""")