# Assignment 3 — Graph Knowledge for Recommendation System using Neo4j

## Student

**Oleksandra Dembitska**

Course: NoSQL Databases

---

# Project Overview

The purpose of this assignment is to design and implement a graph-based movie recommendation system using the MovieLens 1M dataset and Neo4j.

The project covers the complete workflow of building a graph database:

- designing an appropriate graph schema;
- converting the original dataset into CSV format;
- importing data into Neo4j;
- writing Cypher queries of different complexity;
- identifying graph supernodes;
- applying Graph Data Science algorithms;
- analyzing the advantages of graph databases compared to relational databases.

The implementation uses both Neo4j AuraDB Free and Neo4j Desktop. AuraDB was sufficient for loading and querying the data, while Neo4j Desktop was used to execute Graph Data Science algorithms because of the storage and memory limitations of the free AuraDB tier.

---

# Technologies

- Neo4j Desktop
- Neo4j AuraDB Free
- Graph Data Science Library (GDS)
- APOC Procedures
- Python 3
- Cypher Query Language

---

# Dataset

The project uses the **MovieLens 1M** dataset.

Original files:

- movies.dat
- users.dat
- ratings.dat

Before importing into Neo4j the dataset was converted into UTF-8 CSV format using a Python script (`convert.py`).

Generated files:

- movies.csv
- users.csv
- ratings.csv

---

# Project Structure

```
Dembitska_nosql_3/
│
├── data/
│   ├── movies.dat
│   ├── ratings.dat
│   └── users.dat
│
├── import/
│   ├── movies.csv
│   ├── ratings.csv
│   └── users.csv
│
├── queries/
│   ├── part2_load.cypher
│   ├── part3_queries.cypher
│   ├── part4_supernodes.cypher
│   └── part5_gds.cypher
│
├── screenshots/
│
├── convert.py
├── requirements.txt
└── README.md
```

---

# Part 1 — Graph Schema Design

Before importing the dataset into Neo4j, it is necessary to design an appropriate graph model. A well-designed schema simplifies graph traversals, reduces query complexity, and improves performance.

The MovieLens dataset naturally represents relationships between users and movies, making it a good candidate for a graph database.

## Graph Schema

```
              +----------------------+
              |        User          |
              |----------------------|
              | userId               |
              | gender               |
              | age                  |
              | occupation           |
              +----------------------+
                        |
                        | RATED
                        | rating
                        | timestamp
                        v
              +----------------------+
              |        Movie         |
              |----------------------|
              | movieId              |
              | title                |
              | year                 |
              +----------------------+
                        |
                        | HAS_GENRE
                        v
              +----------------------+
              |        Genre         |
              |----------------------|
              | name                 |
              +----------------------+
```

---

## Graph Nodes

### User

Properties:

- userId
- gender
- age
- occupation

Each user represents one person who rated one or more movies.

---

### Movie

Properties:

- movieId
- title
- year

Each movie is represented only once in the graph regardless of the number of ratings it receives.

---

### Genre

Properties:

- name

Each genre exists only once and is shared by all movies belonging to that genre.

---

## Graph Relationships

### RATED

```
(User)-[:RATED]->(Movie)
```

Properties:

- rating
- timestamp

Each relationship represents a single user's rating for a movie.

---

### HAS_GENRE

```
(Movie)-[:HAS_GENRE]->(Genre)
```

This relationship connects every movie with one or more genres.

---

## Question 1

### Which entities became nodes and which became relationships? Why?

Users, Movies and Genres were modeled as nodes because they represent independent entities with their own attributes and can participate in many different relationships.

Ratings were modeled as relationships because they naturally describe an interaction between a user and a movie. A rating cannot exist independently without both entities, making it a better fit as an edge instead of a node.

---

## Question 2

### Why was Rating modeled as a relationship instead of a separate node?

The relationship model

```
(User)-[:RATED]->(Movie)
```

is more natural because a rating connects exactly one user with exactly one movie.

Advantages:

- fewer nodes in the graph;
- simpler traversal;
- faster recommendation queries;
- lower storage requirements.

An alternative design would introduce Rating as a separate node:

```
(User)-[:MADE]->(Rating)-[:FOR]->(Movie)
```

Although this approach allows storing additional metadata about ratings, it increases graph complexity, requires more joins during traversals, and generally performs worse for recommendation queries.

For the MovieLens dataset, representing ratings as relationships is the better choice because recommendations mainly depend on the connection between users and movies.

---

## Question 3

### Why are genres stored as separate nodes instead of a list property?

Genres could be stored as a string list inside the Movie node.

Example:

```
genres = ["Comedy", "Drama"]
```

However, using separate Genre nodes has several advantages.

First, graph traversals become much simpler because all movies belonging to the same genre share the same Genre node.

Second, it allows efficient aggregation such as:

- number of movies in each genre;
- average ratings by genre;
- most popular genres.

Finally, Genre nodes can easily store additional information in the future without changing the schema.

For these reasons, modeling genres as separate nodes follows graph database best practices.

---

# Part 2 — Data Loading

The MovieLens dataset was imported into Neo4j after converting the original `.dat` files into UTF-8 CSV files.

To avoid duplicate nodes during repeated imports, the `MERGE` clause was used instead of `CREATE` wherever appropriate.

Before loading relationships, uniqueness constraints were created to speed up node lookups and prevent duplicates.

The import process consisted of the following steps:

1. Create constraints.
2. Load Movie nodes.
3. Load User nodes.
4. Create Genre nodes.
5. Create HAS_GENRE relationships.
6. Create RATED relationships.

---

## Dataset Conversion

The original dataset uses the separator `::` and Latin-1 encoding.

A Python script (`convert.py`) converts the files into UTF-8 CSV format before import.

After conversion the following files were generated:

- movies.csv
- users.csv
- ratings.csv

Screenshot:

- **01_convert_dataset.png**

---

## Creating Constraints

Before importing any data, uniqueness constraints were created for Movie, User and Genre nodes.

Purpose:

- prevent duplicate nodes;
- improve lookup performance;
- speed up relationship creation.

Screenshot:

- **02_constraints_created.png**

---

## Loading Movie Nodes

Movie information was imported from `movies.csv`.

Each movie is created only once using `MERGE`.

Movie properties:

- movieId
- title
- year

Screenshot:

- **03_movies_import.png**

---

## Loading User Nodes

User information was imported from `users.csv`.

Each user node stores:

- userId
- gender
- age
- occupation

Using `MERGE` ensures that the import script can safely be executed multiple times.

Screenshot:

- **04_users_import.png**

---

## Loading Genre Nodes

Each movie may belong to multiple genres.

Instead of storing genres as text properties, individual Genre nodes were created.

Movies were connected using the relationship:

```
(Movie)-[:HAS_GENRE]->(Genre)
```

Screenshot:

- **05_genres_import.png**

---

## Loading Rating Relationships

Ratings represent interactions between users and movies.

Each rating creates the relationship

```
(User)-[:RATED]->(Movie)
```

with the properties:

- rating
- timestamp

Because the MovieLens dataset contains more than one million ratings, relationships were imported in batches to reduce memory usage and improve stability.

Screenshot:

- **06_ratings_import.png**

---

## Database Verification

After completing the import, the database contents were verified by counting:

- users;
- movies;
- genres;
- rating relationships.

This step confirms that all data has been successfully imported.

Screenshot:

- **07_database_statistics.png**

---

# Part 3 — Cypher Queries

The purpose of this section is to demonstrate different types of Cypher queries, ranging from simple filtering to recommendation-oriented graph traversals.

All queries were saved in **queries/part3_queries.cypher**.

---

## Query 1 — Movies of a Specific Genre

This query finds all movies belonging to the **Thriller** genre whose average rating is greater than 4.0.

The query traverses the graph from **Movie** nodes to **Genre** nodes using the **HAS_GENRE** relationship and aggregates ratings through **RATED** relationships.

This demonstrates how graph traversal can naturally combine filtering and aggregation.

Screenshot:

- **08_query_movies_by_genre.png**

---

## Query 2 — Active Users with Many High Ratings

This query finds users who gave the maximum rating (5 stars) to more than 50 movies.

The query groups ratings by user and counts only those with the highest score.

Such users can be considered highly active movie enthusiasts.

Screenshot:

- **09_query_users_high_rating.png**

---

## Query 3 — Movies Rated Highly by Two Users

This query finds movies that were rated at least 4 stars by both User 1 and User 2.

The graph model makes this query straightforward because both users are connected directly to Movie nodes through RATED relationships.

Screenshot:

- **10_query_top_rated_movies.png**

---

## Query 4 — Genre Statistics

This query calculates:

- average rating for each genre;
- number of ratings.

The result identifies genres that consistently receive high ratings rather than only having a few highly rated movies.

Screenshot:

- **13_query_genre_statistics.png**

---

## Query 5 — Recommendation Query

This recommendation follows the principle:

> Users with similar tastes also liked these movies.

The algorithm:

1. finds users with similar ratings;
2. excludes movies already watched by the target user;
3. recommends movies highly rated by similar users.

This demonstrates one of the strongest advantages of graph databases, where recommendation queries are naturally expressed as graph traversals.

Screenshot:

- **12_query_similar_users.png**

---

## Query 6 — Shortest Path Between Users

This query searches for the shortest path between two users through shared movies.

The path alternates between User and Movie nodes.

Example:

```
User → Movie → User
```

This allows discovering indirect similarity between users.

Screenshot:

- **11_query_most_active_users.png**

---

## The Meaning of Path Length

### Path Length = 2

```
User → Movie → User
```

Both users rated the same movie.

This is the strongest possible direct similarity.

---

### Path Length = 4

```
User
 ↓
Movie
 ↓
User
 ↓
Movie
 ↓
User
```

The users do not share a movie directly.

Instead, they are connected through another user who rated movies watched by both.

This represents indirect similarity.

---

### Path Length = 6

A path of length six indicates an even weaker connection.

Several intermediate users connect the two target users.

Although they are still connected inside the recommendation graph, their movie preferences are less similar.

Generally, longer paths represent weaker relationships.

---

# Part 4 — Supernodes

Supernodes are nodes that have an exceptionally large number of relationships.

Although graph databases are optimized for traversals, supernodes may significantly reduce query performance because many relationships must be inspected.

All queries are stored in:

```
queries/part4_supernodes.cypher
```

---

## Identified Supernodes

The largest Genre nodes were:

| Genre | Movies |
|--------|-------:|
| Drama | 1603 |
| Comedy | 1200 |
| Action | 503 |
| Thriller | 492 |
| Romance | 471 |

Screenshot:

- **14_supernodes.png**

---

## Why Are Supernodes Slower?

When Neo4j traverses a relationship connected to a supernode, it must inspect thousands of outgoing relationships.

For example, searching movies connected to the Drama node requires traversing more than 1600 relationships.

Even with indexes, relationship traversal still dominates the query cost.

Therefore, queries involving supernodes are slower than queries involving ordinary nodes.

---

## Possible Optimization Strategies

Several approaches can reduce the impact of supernodes.

For this dataset, the following strategies are appropriate:

- filter movies before reaching the Genre node;
- use graph projections for Graph Data Science algorithms;
- materialize frequently used relationships;
- limit traversals using rating thresholds.

These approaches reduce the number of relationships explored during query execution.

---

# Part 5 — Graph Data Science

Graph Data Science algorithms were executed using Neo4j Desktop because AuraDB Free does not support full GDS functionality for this assignment.

All queries are stored in:

```
queries/part5_gds.cypher
```

---

## Graph Projection

Before running Graph Data Science algorithms, an in-memory graph projection was created.

The projection contained:

- User nodes
- Movie nodes
- RATED relationships

Graph projection allows GDS algorithms to execute efficiently without modifying the stored database.

Screenshot:

- **16_graph_projection.png**

---

## PageRank

PageRank identifies the most influential nodes in a graph.

After executing the algorithm, the highest ranked movies included:

- American Beauty (1999)
- Star Wars Episode VI
- Star Wars Episode IV
- Saving Private Ryan

Screenshot:

- **17_pagerank.png**

### Interpretation

A high PageRank does **not** necessarily mean that a movie has the highest average rating.

Instead, it indicates that the movie is connected to many other important movies through users who rated them highly.

Therefore, PageRank measures structural importance rather than popularity alone.

---

## Louvain Community Detection

The Louvain algorithm detects communities of densely connected nodes.

Multiple communities were identified with different sizes.

The largest community contained more than two thousand nodes.

Screenshot:

- **18_louvain.png**

### Do the Communities Make Sense?

The obtained communities appear to represent groups of users with similar movie preferences.

Large communities probably correspond to mainstream audiences, while smaller communities may represent users with more specialized interests.

### How Was This Verified?

Communities were analyzed by comparing:

- community sizes;
- rating patterns;
- dominant movie genres.

This confirms that users inside one community tend to rate similar movies highly.

---

## Dijkstra Shortest Path

The original MovieLens graph contains more than one million relationships.

Running Dijkstra directly on this graph exceeded the available memory.

Therefore, a small demonstration graph was created to illustrate the algorithm.

Screenshot:

- **19_dijkstra.png**

The shortest path was:

```
1 → 2 → 3
```

with a total cost of **3**.

### Interpretation

The algorithm successfully selected the lowest-cost path instead of the direct but more expensive edge.

This demonstrates how weighted shortest-path algorithms operate.

---

## Is This a Small World?

Even though the demonstration graph is small, recommendation graphs usually exhibit small-world properties.

Most users can be connected through only a few intermediate users.

This supports the intuition behind collaborative filtering.

---

## Does the Dataset Support the Six Degrees Hypothesis?

The MovieLens graph appears to have relatively short paths between users because many people rate popular movies.

Although the exact average path length was not computed, the graph structure suggests that users are generally connected through only a few intermediate nodes, which is consistent with the small-world phenomenon.

---

# Part 6 — Analysis and Conclusions

## Graph Databases vs Relational Databases

Graph databases excel at relationship-oriented queries.

For example, the recommendation query:

> "Users with similar tastes also liked..."

can be expressed naturally in Cypher by traversing relationships.

Implementing the same logic in SQL would require multiple self-joins on large tables, making the query significantly more complex and often less efficient.

Therefore, recommendation systems are one of the strongest use cases for graph databases.

---

## Where SQL Performs Better

Relational databases remain superior for:

- reporting;
- analytical summaries;
- aggregation over all records;
- exporting structured tabular data.

For example, calculating the average rating of every movie can be performed efficiently using SQL aggregation without traversing relationships.

---

## Possible Schema Improvements

Several improvements could further optimize the graph.

First, materialized similarity relationships between users could be stored permanently instead of computing them repeatedly.

Second, additional indexes on frequently searched properties could improve lookup speed.

Finally, precomputed recommendation relationships could significantly accelerate recommendation queries at the cost of additional storage.

---

# Screenshots

## Dataset Conversion

- 01_convert_dataset.png

## Data Loading

- 02_constraints_created.png
- 03_movies_import.png
- 04_users_import.png
- 05_genres_import.png
- 06_ratings_import.png
- 07_database_statistics.png

## Cypher Queries

- 08_query_movies_by_genre.png
- 09_query_users_high_rating.png
- 10_query_top_rated_movies.png
- 11_query_most_active_users.png
- 12_query_similar_users.png
- 13_query_genre_statistics.png

## Supernodes

- 14_supernodes.png

## Graph Data Science

- 15_desktop_database_statistics.png
- 16_graph_projection.png
- 17_pagerank.png
- 18_louvain.png
- 19_dijkstra.png

---

# Final Conclusion

This project demonstrates how graph databases can effectively model recommendation systems.

Neo4j provides an intuitive way to represent relationships between users, movies, and genres while allowing complex traversals to be expressed using concise Cypher queries.

The Graph Data Science library extends these capabilities by enabling advanced algorithms such as PageRank, Louvain community detection, and Dijkstra shortest path.

Compared with relational databases, graph databases simplify recommendation-oriented queries and graph analytics, while SQL databases remain preferable for reporting and large-scale aggregations.

Overall, the project successfully demonstrates graph modeling, graph querying, graph analytics, and recommendation techniques using the MovieLens dataset.

--