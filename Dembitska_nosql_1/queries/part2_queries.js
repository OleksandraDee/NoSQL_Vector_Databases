use("spotify");

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
}
)
.limit(20)
.forEach(doc => printjson(doc));

// =====================================
// Task 2 - Popular artists
// =====================================

print("\n======================================");
print("Task 2 - Popular artists");
print("======================================");

db.tracks.aggregate([
    // Кожного артиста з масиву робимо окремим документом
    {
        $unwind: "$artists"
    },

    // Групуємо по артисту
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

    // Мінімум 3 треки
    {
        $match: {
            tracks_count: { $gte: 3 },
            min_popularity: { $gte: 60 }
        }
    },

    // Красивий вивід
    {
        $project: {
            _id: 0,
            artist: "$_id",
            tracks_count: 1,
            min_popularity: 1,
            avg_popularity: {
                $round: ["$avg_popularity", 1]
            }
        }
    },

    // Найпопулярніші зверху
    {
        $sort: {
            avg_popularity: -1
        }
    },

    // TOP 20
    {
        $limit: 20
    }

]).forEach(doc => printjson(doc));


print("=====================================");
print("Task 3 - Most danceable genres");
print("=====================================");

db.tracks.aggregate([
  {
    $group: {
      _id: "$track_genre",
      avg_danceability: {
        $avg: "$audio_features.danceability"
      },
      tracks_count: {
        $sum: 1
      }
    }
  },
  {
    $match: {
      tracks_count: {
        $gte: 100
      }
    }
  },
  {
    $sort: {
      avg_danceability: -1
    }
  },
  {
    $project: {
      _id: 0,
      genre: "$_id",
      tracks_count: 1,
      avg_danceability: {
        $round: ["$avg_danceability", 3]
      }
    }
  },
  {
    $limit: 10
  }
]).forEach(doc => printjson(doc));