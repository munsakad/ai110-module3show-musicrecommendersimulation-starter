# 🎵 Music Recommender Simulation

A content-based music recommender built with Python and Streamlit, simulating how platforms like Spotify suggest songs based on user taste profiles.

---

## How The System Works

Real-world platforms like Spotify use a hybrid of **collaborative filtering** (recommending based on what similar users liked) and **content-based filtering** (matching songs to a user's taste based on audio features like energy, tempo, and mood). At scale, these systems use machine learning models trained on billions of data points.

This simulation focuses on **content-based filtering**. Given a user profile (preferred genre, mood, energy level, etc.), the system scores every song in the catalog using a weighted algorithm and returns the top-k ranked results. It prioritizes **genre** and **mood** as the strongest signals, then fine-tunes results using numerical proximity on energy, valence, and danceability.

---

## Algorithm Recipe

| Feature | Points |
|---|---|
| Genre match | +2.0 |
| Mood match | +1.0 |
| Energy proximity | up to +1.0 |
| Valence proximity | up to +0.75 |
| Danceability proximity | up to +0.50 |

**Max possible score: 5.25**

Proximity formula: `points = weight × (1 - |song_value - target_value|)`
This rewards songs *closer* to the user's preference rather than simply higher or lower.

**Potential bias note:** This system may over-prioritize genre, causing great mood-matched songs from a different genre to rank lower than they deserve. Future improvement: make genre weight configurable.

---

## Song & UserProfile Features

**Song attributes used:**
- `genre` — categorical (e.g. pop, rock, hiphop, classical, lofi, electronic, country)
- `mood` — categorical (e.g. happy, energetic, calm, sad, melancholic)
- `energy` — float 0.0–1.0
- `valence` — float 0.0–1.0 (musical positivity)
- `danceability` — float 0.0–1.0

**UserProfile keys:**
- `favorite_genre`
- `favorite_mood`
- `target_energy`
- `target_valence`
- `target_danceability`

---

## Project Structure

```
Music-Recommender-Simulation/
├── app.py                  # Streamlit UI
├── requirements.txt
├── README.md
├── data/
│   └── songs.csv           # Song catalog (20 songs)
├── src/
│   ├── __init__.py
│   ├── recommender.py      # Core logic: load_songs, score_song, recommend_songs
│   └── main.py             # CLI entry point
├── tests/
│   ├── __init__.py
│   └── test_recommender.py # Unit tests
└── .streamlit/
    └── config.toml         # Spotify-inspired dark theme
```

---

## Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/Music-Recommender-Simulation.git
cd Music-Recommender-Simulation

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the CLI
python -m src.main

# 4. Run the Streamlit app
streamlit run app.py

# 5. Run tests
python -m pytest tests/
```

---

## Sample Recommendation Output

Output of `python -m src.main` for the default "pop / happy" profile:

```
Loaded songs: 20

=======================================================
       🎵  TOP RECOMMENDATIONS FOR YOU  🎵
=======================================================

#1  Levitating — Dua Lipa
    Score : 5.163
    Why   : genre match (+2.0), mood match (+1.0), energy proximity (+1.0), valence proximity (+0.713), danceability proximity (+0.45)

#2  Shape of You — Ed Sheeran
    Score : 5.125
    Why   : genre match (+2.0), mood match (+1.0), energy proximity (+0.9), valence proximity (+0.75), danceability proximity (+0.475)

#3  Sunflower — Post Malone
    Score : 5.052
    Why   : genre match (+2.0), mood match (+1.0), energy proximity (+0.85), valence proximity (+0.712), danceability proximity (+0.49)

#4  Blinding Lights — The Weeknd
    Score : 4.1
    Why   : genre match (+2.0), energy proximity (+0.95), valence proximity (+0.675), danceability proximity (+0.475)

#5  Anti-Hero — Taylor Swift
    Score : 3.84
    Why   : genre match (+2.0), energy proximity (+0.8), valence proximity (+0.6), danceability proximity (+0.44)

=======================================================
```

`src/main.py` also runs the recommender against several additional and
adversarial user profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock, and
three edge-case profiles) for evaluation purposes. The full output for every
profile, plus analysis of *why* the results look the way they do, lives in
[`model_card.md`](model_card.md#evaluation-process).

---

## Reflection

> This is a draft reflection generated while building out the evaluation and
> documentation phases — personalize it with your own voice before submitting.

**Biggest learning moment:** Watching the same scoring function produce very
different rankings just by changing *one* profile's inputs made the abstract
idea of a "weighted algorithm" concrete. Running the adversarial profiles (a
genre that doesn't exist in the catalog, a "sad but high-energy" request) was
the moment it really clicked that a recommender doesn't "understand" music —
it just adds up numbers, and its blind spots are a direct reflection of how
those numbers are weighted.

**How AI tools helped, and where I double-checked them:** AI assistance was
useful for scaffolding the CSV loading, the sorting/ranking loop, and for
brainstorming adversarial test profiles I wouldn't have thought of on my own
(like conflicting energy/mood targets). I double-checked the actual math by
hand for a couple of songs — recomputing the genre/mood/proximity points
myself — to confirm the "reasons" list matched the real score before trusting
it, and I re-ran the weight-shift experiment and diffed the code back to the
original weights afterward so the shipped algorithm still matches what's
documented in this README.

**What surprised me:** How much a simple rule-based system can still *feel*
like a real recommendation engine. Explaining every score with a plain-English
"reasons" list made even a hand-tuned weighted sum feel legitimate — right up
until an adversarial profile exposed how shallow the "understanding" actually
is (e.g., not knowing that "sad" and "high energy" rarely go together in this
dataset).

**What I'd try next:** Add the diversity penalty and mood-similarity ideas
from the Model Card's "Ideas for Improvement" section, and grow the catalog
past 20 songs so genre/mood imbalance stops dominating every result.

---

## Model Card

See [`model_card.md`](model_card.md) for the full VibeFinder 1.0 model card,
including the goal, dataset, algorithm summary, evaluation results across six
user profiles, observed biases/limitations, and ideas for improvement.
