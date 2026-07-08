"""
main.py — CLI entry point for the Music Recommender Simulation.
Run with: python -m src.main
"""

import sys

from src.recommender import load_songs, recommend_songs

# Windows terminals default to cp1252, which can't encode emoji; force UTF-8 output.
if sys.stdout.encoding is not None and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# ── Default user profile ──────────────────────────────────────────────────────
DEFAULT_USER = {
    "favorite_genre":      "pop",
    "favorite_mood":       "happy",
    "target_energy":       0.75,
    "target_valence":      0.8,
    "target_danceability": 0.8,
}

# ── Evaluation profiles ────────────────────────────────────────────────────────
# Distinct musical tastes plus a few adversarial / edge-case profiles used to
# stress-test the scoring logic (see model_card.md "Evaluation Process").
EVAL_PROFILES = {
    "High-Energy Pop": {
        "favorite_genre":      "pop",
        "favorite_mood":       "energetic",
        "target_energy":       0.95,
        "target_valence":      0.7,
        "target_danceability": 0.85,
    },
    "Chill Lofi": {
        "favorite_genre":      "lofi",
        "favorite_mood":       "calm",
        "target_energy":       0.2,
        "target_valence":      0.5,
        "target_danceability": 0.4,
    },
    "Deep Intense Rock": {
        "favorite_genre":      "rock",
        "favorite_mood":       "dramatic",
        "target_energy":       0.7,
        "target_valence":      0.45,
        "target_danceability": 0.45,
    },
    "Adversarial: High Energy + Sad Mood": {
        # Conflicting signals: energetic numeric targets paired with a sad mood.
        "favorite_genre":      "pop",
        "favorite_mood":       "sad",
        "target_energy":       0.9,
        "target_valence":      0.9,
        "target_danceability": 0.9,
    },
    "Adversarial: Genre Not In Catalog": {
        # No song in songs.csv has this genre; tests the "no match" fallback.
        "favorite_genre":      "reggaeton",
        "favorite_mood":       "happy",
        "target_energy":       0.5,
        "target_valence":      0.5,
        "target_danceability": 0.5,
    },
    "Adversarial: All-Zero Targets": {
        "favorite_genre":      "classical",
        "favorite_mood":       "calm",
        "target_energy":       0.0,
        "target_valence":      0.0,
        "target_danceability": 0.0,
    },
}


def print_recommendations(label: str, recommendations: list[dict]) -> None:
    """Print one profile's ranked recommendations in a clean, readable layout."""
    print(f"\n----- {label} -----")
    for i, song in enumerate(recommendations, 1):
        print(f"#{i}  {song['title']} — {song['artist']}  (score {song['score']})")
        print(f"     Why: {', '.join(song['reasons'])}")


def main():
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    default_recs = recommend_songs(DEFAULT_USER, songs, k=5)
    print("=" * 55)
    print("       🎵  TOP RECOMMENDATIONS FOR YOU  🎵")
    print("=" * 55)
    for i, song in enumerate(default_recs, 1):
        print(f"\n#{i}  {song['title']} — {song['artist']}")
        print(f"    Score : {song['score']}")
        print(f"    Why   : {', '.join(song['reasons'])}")
    print("\n" + "=" * 55)

    print("\n" + "#" * 55)
    print("  EVALUATION: Additional & Adversarial Profiles")
    print("#" * 55)
    for label, prefs in EVAL_PROFILES.items():
        recs = recommend_songs(prefs, songs, k=5)
        print_recommendations(label, recs)


if __name__ == "__main__":
    main()
