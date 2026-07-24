import csv
from pathlib import Path

DATA_DIR = Path("data")
IMPORT_DIR = Path("import")

IMPORT_DIR.mkdir(exist_ok=True)


def convert_movies():
    with open(DATA_DIR / "movies.dat", encoding="latin-1") as fin, \
         open(IMPORT_DIR / "movies.csv", "w", newline="", encoding="utf-8") as fout:

        writer = csv.writer(fout)
        writer.writerow(["movieId", "title", "genres"])

        for line in fin:
            writer.writerow(line.strip().split("::"))

    print("✓ movies.csv created")


def convert_users():
    with open(DATA_DIR / "users.dat", encoding="latin-1") as fin, \
         open(IMPORT_DIR / "users.csv", "w", newline="", encoding="utf-8") as fout:

        writer = csv.writer(fout)
        writer.writerow(["userId", "gender", "age", "occupation"])

        for line in fin:
            parts = line.strip().split("::")
            writer.writerow(parts[:4])

    print("✓ users.csv created")


def convert_ratings():
    with open(DATA_DIR / "ratings.dat", encoding="latin-1") as fin, \
         open(IMPORT_DIR / "ratings.csv", "w", newline="", encoding="utf-8") as fout:

        writer = csv.writer(fout)
        writer.writerow(["userId", "movieId", "rating", "timestamp"])

        for line in fin:
            writer.writerow(line.strip().split("::"))

    print("✓ ratings.csv created")


if __name__ == "__main__":
    print("Converting MovieLens dataset...\n")

    convert_movies()
    convert_users()
    convert_ratings()

    print("\nDone!")