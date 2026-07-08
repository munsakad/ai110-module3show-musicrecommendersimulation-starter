"""
tests/test_recommender.py — Unit tests for the Music Recommender Simulation.
Run with: python -m pytest tests/
"""

import pytest
from src.recommender import load_songs, score_song, recommend_songs

SONGS_PATH = "data/songs.csv"

USER_POP_HAPPY = {
    "favorite_genre":      "pop",
    "favorite_mood":       "happy",
    "target_energy":       0.75,
    "target_valence":      0.85,
    "target_danceability": 0.85,
}

USER_CLASSICAL = {
    "favorite_genre":      "classical",
    "favorite_mood":       "calm",
    "target_energy":       0.1,
    "target_valence":      0.6,
    "target_danceability": 0.1,
}


# ── load_songs ────────────────────────────────────────────────────────────────

def test_load_songs_returns_list():
    songs = load_songs(SONGS_PATH)
    assert isinstance(songs, list)
    assert len(songs) > 0

def test_load_songs_numeric_types():
    songs = load_songs(SONGS_PATH)
    for song in songs:
        assert isinstance(song["energy"],       float)
        assert isinstance(song["valence"],      float)
        assert isinstance(song["tempo_bpm"],    int)
        assert isinstance(song["danceability"], float)
        assert isinstance(song["acousticness"], float)

def test_load_songs_required_keys():
    songs = load_songs(SONGS_PATH)
    required = {"title", "artist", "genre", "mood", "energy", "valence", "tempo_bpm"}
    for song in songs:
        assert required.issubset(song.keys())


# ── score_song ────────────────────────────────────────────────────────────────

def test_score_song_returns_tuple():
    songs = load_songs(SONGS_PATH)
    result = score_song(USER_POP_HAPPY, songs[0])
    assert isinstance(result, tuple)
    assert len(result) == 2

def test_score_song_genre_match_adds_points():
    pop_song = {
        "genre": "pop", "mood": "sad",
        "energy": 0.5, "valence": 0.5, "danceability": 0.5,
    }
    non_pop_song = {
        "genre": "rock", "mood": "sad",
        "energy": 0.5, "valence": 0.5, "danceability": 0.5,
    }
    score_match, _    = score_song(USER_POP_HAPPY, pop_song)
    score_no_match, _ = score_song(USER_POP_HAPPY, non_pop_song)
    assert score_match > score_no_match

def test_score_song_mood_match_adds_points():
    happy_song = {
        "genre": "rock", "mood": "happy",
        "energy": 0.5, "valence": 0.5, "danceability": 0.5,
    }
    sad_song = {
        "genre": "rock", "mood": "sad",
        "energy": 0.5, "valence": 0.5, "danceability": 0.5,
    }
    score_happy, _ = score_song(USER_POP_HAPPY, happy_song)
    score_sad, _   = score_song(USER_POP_HAPPY, sad_song)
    assert score_happy > score_sad

def test_score_song_reasons_list():
    songs = load_songs(SONGS_PATH)
    _, reasons = score_song(USER_POP_HAPPY, songs[0])
    assert isinstance(reasons, list)
    assert len(reasons) > 0


# ── recommend_songs ───────────────────────────────────────────────────────────

def test_recommend_songs_returns_k_results():
    songs = load_songs(SONGS_PATH)
    recs  = recommend_songs(USER_POP_HAPPY, songs, k=3)
    assert len(recs) == 3

def test_recommend_songs_sorted_descending():
    songs = load_songs(SONGS_PATH)
    recs  = recommend_songs(USER_POP_HAPPY, songs, k=5)
    scores = [r["score"] for r in recs]
    assert scores == sorted(scores, reverse=True)

def test_recommend_songs_classical_profile():
    songs = load_songs(SONGS_PATH)
    recs  = recommend_songs(USER_CLASSICAL, songs, k=3)
    top_genres = [r["genre"] for r in recs]
    assert "classical" in top_genres

def test_recommend_songs_has_score_and_reasons():
    songs = load_songs(SONGS_PATH)
    recs  = recommend_songs(USER_POP_HAPPY, songs, k=5)
    for rec in recs:
        assert "score"   in rec
        assert "reasons" in rec
        assert isinstance(rec["reasons"], list)
