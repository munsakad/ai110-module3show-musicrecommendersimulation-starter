"""
recommender.py — Core logic for the Music Recommender Simulation.
"""

import csv


def load_songs(filepath: str) -> list[dict]:
    """Load songs from a CSV file and return a list of dictionaries with typed values."""
    songs = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["energy"]       = float(row["energy"])
            row["valence"]      = float(row["valence"])
            row["tempo_bpm"]    = int(row["tempo_bpm"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def score_song(user_prefs: dict, song: dict) -> tuple[float, list[str]]:
    """
    Score a single song against user preferences.

    Scoring recipe:
        +2.0  for a genre match
        +1.0  for a mood match
        +1.0  max for energy proximity   (1 - |song_energy - target_energy|)
        +0.75 max for valence proximity  (0.75 * (1 - |song_valence - target_valence|))
        +0.5  max for danceability proximity

    Returns (score, reasons) where reasons is a human-readable list of what contributed.
    """
    score   = 0.0
    reasons = []

    # Genre match
    if song["genre"].lower() == user_prefs.get("favorite_genre", "").lower():
        score += 2.0
        reasons.append("genre match (+2.0)")

    # Mood match
    if song["mood"].lower() == user_prefs.get("favorite_mood", "").lower():
        score += 1.0
        reasons.append("mood match (+1.0)")

    # Energy proximity
    energy_diff = abs(song["energy"] - user_prefs.get("target_energy", 0.5))
    energy_pts  = round(1.0 - energy_diff, 3)
    score      += energy_pts
    reasons.append(f"energy proximity (+{energy_pts})")

    # Valence proximity
    valence_diff = abs(song["valence"] - user_prefs.get("target_valence", 0.5))
    valence_pts  = round(0.75 * (1.0 - valence_diff), 3)
    score       += valence_pts
    reasons.append(f"valence proximity (+{valence_pts})")

    # Danceability proximity
    dance_diff = abs(song["danceability"] - user_prefs.get("target_danceability", 0.5))
    dance_pts  = round(0.5 * (1.0 - dance_diff), 3)
    score      += dance_pts
    reasons.append(f"danceability proximity (+{dance_pts})")

    return round(score, 3), reasons


def recommend_songs(user_prefs: dict, songs: list[dict], k: int = 5) -> list[dict]:
    """
    Rank all songs by score and return the top-k recommendations.
    Each item in the returned list contains the song dict plus 'score' and 'reasons'.
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append({**song, "score": score, "reasons": reasons})

    # sorted() returns a new list; does not mutate the original
    ranked = sorted(scored, key=lambda s: s["score"], reverse=True)
    return ranked[:k]
