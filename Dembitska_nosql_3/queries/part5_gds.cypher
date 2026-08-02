///////////////////////////////////////////////////////////////////////////
// PART 5
// Graph Data Science Algorithms
///////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////
// 5.1 PageRank
///////////////////////////////////////////////////////////////////////////

MATCH (m1:Movie)<-[r1:RATED]-(u:User)-[r2:RATED]->(m2:Movie)
WHERE r1.rating >= 4
  AND r2.rating >= 4
  AND id(m1) < id(m2)

WITH m1, m2, count(u) AS weight

WHERE size([(m1)<-[:RATED]-() | 1]) > 20
  AND size([(m2)<-[:RATED]-() | 1]) > 20

WITH m1, m2, weight
ORDER BY weight DESC
LIMIT 50000

MERGE (m1)-[co:CO_RATED]-(m2)
SET co.weight = weight;

CALL gds.graph.project(

    'movieGraph',

    'Movie',

    {
        CO_RATED:{
            orientation:'UNDIRECTED',
            properties:'weight'
        }
    }

)
YIELD graphName,nodeCount,relationshipCount;

CALL gds.pageRank.stream(

    'movieGraph',

    {
        relationshipWeightProperty:'weight'
    }

)

YIELD nodeId,score

RETURN

gds.util.asNode(nodeId).title AS Movie,

round(score,4) AS PageRank

ORDER BY PageRank DESC

LIMIT 10;

CALL gds.graph.drop('movieGraph');

MATCH ()-[co:CO_RATED]-()

DELETE co;

///////////////////////////////////////////////////////////////////////////
// 5.2 Louvain Community Detection
///////////////////////////////////////////////////////////////////////////

MATCH (u1:User)-[r1:RATED]->(m:Movie)<-[r2:RATED]-(u2:User)

WHERE r1.rating>=4
  AND r2.rating>=4
  AND id(u1)<id(u2)

WITH u1,u2,count(m) AS weight

ORDER BY weight DESC

LIMIT 50000

MERGE (u1)-[sim:SIMILAR]-(u2)

SET sim.weight=weight;

CALL gds.graph.project(

'userSimilarity',

'User',

{

SIMILAR:{

orientation:'UNDIRECTED',

properties:'weight'

}

}

)

YIELD graphName,nodeCount,relationshipCount;

CALL gds.louvain.stream(

'userSimilarity',

{

relationshipWeightProperty:'weight'

}

)

YIELD nodeId,communityId

WITH communityId,gds.util.asNode(nodeId) AS user

RETURN

communityId,

count(user) AS Members

ORDER BY Members DESC

LIMIT 10;

///////////////////////////////////////////////////////////////////////////
// Top genres inside every community
///////////////////////////////////////////////////////////////////////////

CALL gds.louvain.stream(

'userSimilarity',

{

relationshipWeightProperty:'weight'

}

)

YIELD nodeId,communityId

WITH communityId,gds.util.asNode(nodeId) AS u

MATCH (u)-[r:RATED]->(m:Movie)-[:HAS_GENRE]->(g:Genre)

WHERE r.rating>=4

WITH communityId,g.name AS Genre,count(*) AS Votes

ORDER BY communityId,Votes DESC

RETURN

communityId,

collect({

Genre:Genre,

Votes:Votes

})[0..3] AS TopGenres

LIMIT 10;

CALL gds.graph.drop('userSimilarity');

MATCH ()-[sim:SIMILAR]-()

DELETE sim;

///////////////////////////////////////////////////////////////////////////
// 5.3 Dijkstra Shortest Path
///////////////////////////////////////////////////////////////////////////

MATCH (u1:User)-[r1:RATED]->(m:Movie)<-[r2:RATED]-(u2:User)

WHERE r1.rating>=4
  AND r2.rating>=4
  AND id(u1)<id(u2)

WITH u1,u2,count(m) AS weight

ORDER BY weight DESC

LIMIT 50000

MERGE (u1)-[sim:SIMILAR]-(u2)

SET sim.weight=1.0/weight;

CALL gds.graph.project(

'userGraph',

'User',

{

SIMILAR:{

orientation:'UNDIRECTED',

properties:'weight'

}

}

)

YIELD graphName,nodeCount,relationshipCount;

MATCH (source:User {userId:1})

MATCH (target:User {userId:3})

CALL gds.shortestPath.dijkstra.stream(

'userGraph',

{

sourceNode:id(source),

targetNode:id(target),

relationshipWeightProperty:'weight'

}

)

YIELD totalCost,nodeIds

RETURN

totalCost,

[nodeId IN nodeIds | gds.util.asNode(nodeId).userId] AS Path;

CALL gds.graph.drop('userGraph');

MATCH ()-[sim:SIMILAR]-()

DELETE sim;