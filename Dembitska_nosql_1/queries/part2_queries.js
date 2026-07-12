use("spotify");


// ======================================================
// TASK 1
// Party tracks
// ======================================================

print("======================================");
print("Task 1 - Party tracks");
print("======================================");

db.tracks.find(
{
    "audio_features.danceability": { $gt: 0.7 },
    "audio_features.energy": { $gt: 0.7 },
    duration_ms: {
        $gte: 180000,
        $lte: 300000
    }
},
{
    _id: 0,
    track_name: 1,
    artists: 1,
    duration_ms: 1,
    popularity: 1,
    "audio_features.danceability": 1,
    "audio_features.energy": 1
})
.limit(20)
.forEach(doc => printjson(doc));



// ======================================================
// TASK 2
// Popular artists
// ======================================================

print("\n======================================");
print("Task 2 - Popular artists");
print("======================================");

db.tracks.aggregate([

{
    $unwind: "$artists"
},

{
    $group: {
        _id: "$artists",

        tracks_count: {
            $sum: 1
        },

        min_popularity: {
            $min: "$popularity"
        },

        avg_popularity: {
            $avg: "$popularity"
        }
    }
},

{
    $match: {
        tracks_count: {
            $gte: 3
        },

        min_popularity: {
            $gte: 60
        }
    }
},

{
    $project: {

        _id: 0,

        artist: "$_id",

        tracks_count: 1,

        min_popularity: 1,

        avg_popularity: {
            $round: ["$avg_popularity",1]
        }

    }
},

{
    $sort:{
        avg_popularity:-1
    }
},

{
    $limit:20
}

]).forEach(doc=>printjson(doc));



// ======================================================
// TASK 3
// Unusual tracks (tempo > avg + 2*stdDev)
// ======================================================

print("\n======================================");
print("Task 3 - Unusual tracks");
print("======================================");

db.tracks.aggregate([

{
    $group:{
        _id:"$track_genre",

        avgTempo:{
            $avg:"$audio_features.tempo"
        },

        stdTempo:{
            $stdDevPop:"$audio_features.tempo"
        },

        tracks:{
            $push:"$$ROOT"
        }
    }
},

{
    $unwind:"$tracks"
},

{
    $project:{

        _id:0,

        track_name:"$tracks.track_name",

        artists:"$tracks.artists",

        genre:"$_id",

        tempo:"$tracks.audio_features.tempo",

        avgTempo:1,

        stdTempo:1,

        limit:{
            $add:[
                "$avgTempo",
                {
                    $multiply:[
                        2,
                        "$stdTempo"
                    ]
                }
            ]
        }

    }
},

{
    $match:{
        $expr:{
            $gt:[
                "$tempo",
                "$limit"
            ]
        }
    }
},

{
    $project:{
        track_name:1,
        artists:1,
        genre:1,
        tempo:1,
        avgTempo:{
            $round:["$avgTempo",2]
        },
        stdTempo:{
            $round:["$stdTempo",2]
        }
    }
},

{
    $sort:{
        tempo:-1
    }
},

{
    $limit:20
}

]).forEach(doc=>printjson(doc));




// ======================================================
// TASK 4
// Background tracks
// ======================================================

print("\n======================================");
print("Task 4 - Background tracks");
print("======================================");

db.tracks.find(
{
    "audio_features.loudness": { $lt: -10 },
    "audio_features.speechiness": { $lt: 0.1 },
    "audio_features.instrumentalness": { $gt: 0.5 },
    explicit: false
},
{
    _id: 0,
    track_name: 1,
    artists: 1,
    track_genre: 1,
    "audio_features.loudness": 1,
    "audio_features.speechiness": 1,
    "audio_features.instrumentalness": 1
}
)
.limit(20)
.forEach(doc => printjson(doc));