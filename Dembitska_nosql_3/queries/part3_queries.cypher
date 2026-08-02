///////////////////////////////////////////////////////////////////////////
// Query 1
// Find Thriller movies with average rating above 4.0
///////////////////////////////////////////////////////////////////////////

MATCH (m:Movie)-[:HAS_GENRE]->(:Genre {name:'Thriller'})
MATCH (m)<-[r:RATED]-()

WITH m, avg(r.rating) AS avgRating

WHERE avgRating > 4.0

RETURN
    m.title AS Movie,
    round(avgRating,2) AS AverageRating

ORDER BY AverageRating DESC, Movie;

///////////////////////////////////////////////////////////////////////////
// Query 2
// Users who rated more than 50 movies with the highest score (5)
///////////////////////////////////////////////////////////////////////////

MATCH (u:User)-[r:RATED]->()

WHERE r.rating = 5

WITH u, count(r) AS FiveStarRatings

WHERE FiveStarRatings > 50

RETURN
    u.userId AS UserID,
    FiveStarRatings

ORDER BY FiveStarRatings DESC;

///////////////////////////////////////////////////////////////////////////
// Query 3
// Movies highly rated (>=4) by both User 1 and User 2
///////////////////////////////////////////////////////////////////////////

MATCH (u1:User {userId:1})-[r1:RATED]->(m:Movie)<-[r2:RATED]-(u2:User {userId:2})

WHERE r1.rating >= 4
  AND r2.rating >= 4

RETURN
    m.title AS Movie,
    r1.rating AS User1Rating,
    r2.rating AS User2Rating

ORDER BY Movie;

///////////////////////////////////////////////////////////////////////////
// Query 4
// Genres with consistently high ratings
///////////////////////////////////////////////////////////////////////////

MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre)
MATCH (m)<-[r:RATED]-()

WITH
    g,
    avg(r.rating) AS AverageRating,
    count(r) AS NumberOfRatings

RETURN
    g.name AS Genre,
    round(AverageRating,2) AS AverageRating,
    NumberOfRatings

ORDER BY AverageRating DESC, NumberOfRatings DESC;

///////////////////////////////////////////////////////////////////////////
// Query 5
// Recommendation:
// Users with similar tastes also watched these movies
///////////////////////////////////////////////////////////////////////////

MATCH (target:User {userId:1})-[r1:RATED]->(m:Movie)<-[r2:RATED]-(other:User)

WHERE r1.rating >= 4
  AND r2.rating >= 4
  AND target <> other

WITH target, other, count(m) AS CommonMovies

ORDER BY CommonMovies DESC

LIMIT 20

MATCH (other)-[r:RATED]->(rec:Movie)

WHERE r.rating >= 4
  AND NOT EXISTS {
      MATCH (target)-[:RATED]->(rec)
  }

RETURN
    rec.title AS RecommendedMovie,
    count(*) AS RecommendationScore

ORDER BY RecommendationScore DESC

LIMIT 10;

///////////////////////////////////////////////////////////////////////////
// Query 6
// Shortest path between two users through common movies
///////////////////////////////////////////////////////////////////////////

MATCH (u1:User {userId:1}),
      (u2:User {userId:2})

MATCH p = shortestPath((u1)-[:RATED*..6]-(u2))

RETURN
    length(p) AS PathLength,
    p;