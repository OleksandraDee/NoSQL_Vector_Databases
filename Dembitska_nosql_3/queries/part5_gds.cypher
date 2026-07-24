// ------------------------------------------------------
// 1. Verify data
// ------------------------------------------------------

MATCH (m:Movie)
RETURN count(m) AS Movies;

MATCH (u:User)
RETURN count(u) AS Users;

MATCH (g:Genre)
RETURN count(g) AS Genres;

MATCH ()-[r:RATED]->()
RETURN count(r) AS Ratings;


// ------------------------------------------------------
// 2. Create graph projection
// ------------------------------------------------------

CALL gds.graph.project(
    'movieGraph',
    ['User', 'Movie'],
    ['RATED']
);


// ------------------------------------------------------
// 3. PageRank
// ------------------------------------------------------

CALL gds.pageRank.stream('movieGraph')
YIELD nodeId, score

WITH gds.util.asNode(nodeId) AS n, score
WHERE n:Movie

RETURN
    n.title AS Movie,
    round(score,4) AS PageRank

ORDER BY PageRank DESC
LIMIT 10;


// ------------------------------------------------------
// 4. Louvain Community Detection
// ------------------------------------------------------

CALL gds.louvain.stream('movieGraph')
YIELD communityId

RETURN
    communityId,
    count(*) AS Size

ORDER BY Size DESC
LIMIT 10;


// ------------------------------------------------------
// 5. Create weighted graph for Dijkstra
// ------------------------------------------------------

CALL gds.graph.drop('movieGraph', false);

CALL gds.graph.project(
    'movieGraphWeighted',
    ['User', 'Movie'],
    {
        RATED: {
            properties: 'rating'
        }
    }
);


// ------------------------------------------------------
// 6. Demo graph for Dijkstra
// (used because full MovieLens graph requires
// significantly more memory for shortest path search)
// ------------------------------------------------------

CREATE (u1:DemoUser {id:1});
CREATE (u2:DemoUser {id:2});
CREATE (u3:DemoUser {id:3});

CREATE (u1)-[:LINK {weight:1}]->(u2);
CREATE (u2)-[:LINK {weight:2}]->(u3);
CREATE (u1)-[:LINK {weight:5}]->(u3);


// ------------------------------------------------------
// 7. Create demo projection
// ------------------------------------------------------

CALL gds.graph.project(
    'demoGraph',
    'DemoUser',
    {
        LINK: {
            properties: 'weight'
        }
    }
);


// ------------------------------------------------------
// 8. Dijkstra Shortest Path
// ------------------------------------------------------

MATCH (source:DemoUser {id:1})
MATCH (target:DemoUser {id:3})

CALL gds.shortestPath.dijkstra.stream(
    'demoGraph',
    {
        sourceNode: id(source),
        targetNode: id(target),
        relationshipWeightProperty: 'weight'
    }
)
YIELD totalCost, nodeIds

RETURN
    totalCost,
    [nodeId IN nodeIds | gds.util.asNode(nodeId).id] AS Path;