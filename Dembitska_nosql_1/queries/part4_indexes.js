use("spotify");

// ======================================================
// PART 4 - INDEXES & EXPLAIN
// ======================================================


// ======================================================
// TASK 1
// Explain BEFORE index
// ======================================================

print("\n========================================");
print("TASK 1 - Explain BEFORE index");
print("========================================");

printjson(
    db.tracks.find(
        {
            popularity: { $gte: 80 }
        }
    ).explain("executionStats")
);


// ======================================================
// TASK 2
// Create single field index
// ======================================================

print("\n========================================");
print("TASK 2 - Create popularity index");
print("========================================");

printjson(
    db.tracks.createIndex(
        {
            popularity: 1
        }
    )
);


// ======================================================
// TASK 3
// Explain AFTER index
// ======================================================

print("\n========================================");
print("TASK 3 - Explain AFTER index");
print("========================================");

printjson(
    db.tracks.find(
        {
            popularity: { $gte: 80 }
        }
    ).explain("executionStats")
);


// ======================================================
// TASK 4
// Compound index
// ======================================================

print("\n========================================");
print("TASK 4 - Compound index");
print("========================================");

printjson(

    db.tracks.createIndex(

        {
            track_genre: 1,
            popularity: -1
        }

    )

);


// ======================================================
// TASK 5
// Query using compound index
// ======================================================

print("\n========================================");
print("TASK 5 - Query with compound index");
print("========================================");

db.tracks.find(

    {
        track_genre: "pop",
        popularity: { $gte: 80 }
    },

    {
        _id: 0,
        track_name: 1,
        popularity: 1
    }

).limit(10).forEach(doc => printjson(doc));


// ======================================================
// TASK 6
// Covered Query
// ======================================================

print("\n========================================");
print("TASK 6 - Covered Query");
print("========================================");

printjson(

    db.tracks.find(

        {
            track_genre: "pop"
        },

        {
            _id: 0,
            track_genre: 1,
            popularity: 1
        }

    ).explain("executionStats")

);


