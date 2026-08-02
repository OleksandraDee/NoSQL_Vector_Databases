///////////////////////////////////////////////////////////////////////////
// PART 2 - DATA LOADING
// Neo4j AuraDB + MovieLens 1M
///////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////
// 1. Constraints
///////////////////////////////////////////////////////////////////////////

CREATE CONSTRAINT movie_id IF NOT EXISTS
FOR (m:Movie)
REQUIRE m.movieId IS UNIQUE;

CREATE CONSTRAINT user_id IF NOT EXISTS
FOR (u:User)
REQUIRE u.userId IS UNIQUE;

CREATE CONSTRAINT genre_name IF NOT EXISTS
FOR (g:Genre)
REQUIRE g.name IS UNIQUE;

///////////////////////////////////////////////////////////////////////////
// 2. Import Movies
///////////////////////////////////////////////////////////////////////////

LOAD CSV WITH HEADERS
FROM 'https://raw.githubusercontent.com/OleksandraDee/NoSQL_Vector_Databases/main/Dembitska_nosql_3/import/movies.csv'
AS row

MERGE (m:Movie {movieId: toInteger(row.movieId)})
SET
    m.title = row.title;

///////////////////////////////////////////////////////////////////////////
// 3. Import Users
///////////////////////////////////////////////////////////////////////////

LOAD CSV WITH HEADERS
FROM 'https://raw.githubusercontent.com/OleksandraDee/NoSQL_Vector_Databases/main/Dembitska_nosql_3/import/users.csv'
AS row

MERGE (u:User {userId: toInteger(row.userId)})
SET
    u.gender = row.gender,
    u.age = toInteger(row.age),
    u.occupation = toInteger(row.occupation);

///////////////////////////////////////////////////////////////////////////
// 4. Create Genre Nodes and Relationships
///////////////////////////////////////////////////////////////////////////

LOAD CSV WITH HEADERS
FROM 'https://raw.githubusercontent.com/OleksandraDee/NoSQL_Vector_Databases/main/Dembitska_nosql_3/import/movies.csv'
AS row

MATCH (m:Movie {movieId: toInteger(row.movieId)})

UNWIND split(row.genres, '|') AS genreName

MERGE (g:Genre {name: genreName})
MERGE (m)-[:HAS_GENRE]->(g);

///////////////////////////////////////////////////////////////////////////
// 5. Import Rating Relationships
///////////////////////////////////////////////////////////////////////////

CALL apoc.periodic.iterate(

'
LOAD CSV WITH HEADERS
FROM "https://raw.githubusercontent.com/OleksandraDee/NoSQL_Vector_Databases/main/Dembitska_nosql_3/import/ratings.csv"
AS row
RETURN row
',

'
MATCH (u:User {userId: toInteger(row.userId)})
MATCH (m:Movie {movieId: toInteger(row.movieId)})

MERGE (u)-[r:RATED]->(m)

SET
    r.rating = toFloat(row.rating),
    r.timestamp = toInteger(row.timestamp)
',

{
    batchSize: 10000,
    parallel: false
}

);

///////////////////////////////////////////////////////////////////////////
// 6. Verify Import
///////////////////////////////////////////////////////////////////////////

MATCH (u:User)
RETURN count(u) AS Users;

MATCH (m:Movie)
RETURN count(m) AS Movies;

MATCH (g:Genre)
RETURN count(g) AS Genres;

MATCH ()-[r:RATED]->()
RETURN count(r) AS Ratings;