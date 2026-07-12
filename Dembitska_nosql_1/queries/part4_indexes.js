use("spotify");


print("\n======================================");
print("TASK 1 - Explain BEFORE index");
print("======================================");

printjson(
db.tracks.find(
{
    track_genre: "pop",
    "audio_features.danceability": { $gte: 0.7 }
})
.sort({ popularity: -1 })
.explain("executionStats")
);


print("\n======================================");
print("TASK 2 - Create compound index");
print("======================================");

print(
db.tracks.createIndex(
{
    track_genre: 1,
    "audio_features.danceability": 1,
    popularity: -1
})
);


print("\n======================================");
print("TASK 3 - Explain AFTER index");
print("======================================");

printjson(
db.tracks.find(
{
    track_genre: "pop",
    "audio_features.danceability": { $gte: 0.7 }
})
.sort({ popularity: -1 })
.explain("executionStats")
);


print("\n======================================");
print("TASK 4 - Recommendation index");
print("======================================");

print(
db.tracks.createIndex(
{
    "audio_features.instrumentalness": 1,
    "audio_features.speechiness": 1,
    explicit: 1
})
);

printjson(
db.tracks.find(
{
    "audio_features.instrumentalness": { $gte: 0.5 },
    "audio_features.speechiness": { $lte: 0.1 },
    explicit: false
})
.explain("executionStats")
);


print("\n======================================");
print("TASK 5 - Covered Query");
print("======================================");

db.tracks.createIndex(
{
    track_genre: 1,
    popularity: -1
});

printjson(
db.tracks.find(
{
    track_genre: "pop"
},
{
    _id: 0,
    track_genre: 1,
    popularity: 1
})
.explain("executionStats")
);