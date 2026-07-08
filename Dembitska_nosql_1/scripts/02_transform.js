use("spotify");

db.tracks.drop();

db.tracks_raw.aggregate([
  {
    $project: {
      _id: 0
    }
  },

  {
    $set: {
      artists_raw: "$artists"
    }
  },

  {
    $set: {
      artists: {
        $split: ["$artists", ";"]
      }
    }
  },

  {
    $set: {
      audio_features: {
        danceability: "$danceability",
        energy: "$energy",
        key: "$key",
        loudness: "$loudness",
        mode: "$mode",
        speechiness: "$speechiness",
        acoustiness: "$acoustiness",
        instrumentalness: "$instrumentalness",
        liveness: "$liveness",
        valence: "$valence",
        tempo: "$tempo",
        time_signature: "$time_signature"
      }
    }
  },

  {
    $set: {
      duration_sec: {
        $round: [
          {
            $divide: ["$duration_ms", 1000]
          },
          0
        ]
      }
    }
  },

  {
    $set: {
      popularity_tier: {
        $switch: {
          branches: [
            {
              case: { $gte: ["$popularity", 80] },
              then: "High"
            },
            {
              case: { $gte: ["$popularity", 50] },
              then: "Medium"
            }
          ],
          default: "Low"
        }
      }
    }
  },

  {
    $unset: [
      "danceability",
      "energy",
      "key",
      "loudness",
      "mode",
      "speechiness",
      "acoustiness",
      "instrumentalness",
      "liveness",
      "valence",
      "tempo",
      "time_signature"
    ]
  },
  
  {
  $unset: [
    "Unnamed: 0"
  ]},

  {
    $out: "tracks"
  }
]);

print("=================================");
print("Transformation completed!");
print("Collection 'tracks' created.");
print("=================================");