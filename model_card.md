# Model Card — VibeFinder 1.0

## Model Name
**VibeFinder 1.0** — a rule-based, content-based music recommender.

## Goal / Task
Given a user's stated music taste (a favorite genre, a favorite mood, and target
levels of energy, valence, and danceability), VibeFinder ranks a fixed catalog of
songs and returns the top-k tracks it thinks the user would most enjoy, along with
a plain-language list of *reasons* for each recommendation. It does not predict
clicks, plays, or ratings — it simulates a simple, explainable version of
content-based filtering, the same family of technique real platforms like Spotify
use alongside collaborative filtering.

## Data Used
- **Source:** `data/songs.csv`, a hand-curated catalog of **20 songs**.
- **Features per song:** `title`, `artist`, `genre`, `mood` (categorical), and
  `energy`, `valence`, `danceability`, `acousticness` (floats 0.0–1.0), plus
  `tempo_bpm` (integer, not currently used in scoring).
- **Genre distribution:** pop 6, hiphop 3, rock 2, classical 2, lofi 2,
  electronic 2, country 2, soul 1. Pop makes up **30%** of the catalog — the
  single largest genre by a wide margin.
- **Mood distribution:** 11 distinct mood labels across 20 songs (happy 5,
  calm 3, energetic 3, melancholic 2, then sad/dramatic/confident/dark/nostalgic/
  intense/reflective at 1 each). Most moods appear on only one or two songs.
- **Limits:** the catalog is tiny by real-world standards, genre and mood are
  free-text labels rather than a controlled taxonomy, and there is no listening
  history — every recommendation is generated from a single static profile with
  no personalization over time.

## Algorithm Summary
For every song, VibeFinder adds up points from five signals and keeps a running
list of reasons:
- **+2.0** if the song's genre matches the user's favorite genre exactly.
- **+1.0** if the song's mood matches the user's favorite mood exactly.
- **Up to +1.0** for how close the song's energy is to the user's target energy
  (closer = more points, on a sliding scale).
- **Up to +0.75** for valence closeness, using the same sliding scale.
- **Up to +0.5** for danceability closeness, using the same sliding scale.

The maximum possible score is **5.25**. All songs are scored this way, then
sorted from highest to lowest score, and the top `k` are returned. Genre and
mood are exact-match "bonuses," while energy/valence/danceability are graded on
a curve — a song doesn't need to be a perfect numeric match to earn some credit.

## Observed Behavior / Biases
Testing surfaced a clear **genre filter bubble**: because a genre match (+2.0)
is worth more than any single numeric feature and almost as much as *all three
numeric features combined* (max 2.25), songs from the user's stated genre
dominate the top of every ranking, even when a song from a different genre is a
much closer numeric/mood match. In the "Adversarial: Genre Not In Catalog" test
(favorite genre `reggaeton`, which doesn't exist in the dataset), the genre
bonus never fires for anyone, and the top 5 results become far more sensitive to
small mood/numeric differences — proof that genre is normally "papering over"
those differences for users whose genre *is* in the catalog.

A second bias comes from the **mood taxonomy being too fine-grained**: with 11
unique mood labels spread across only 20 songs, most songs simply can't win the
mood bonus for most users, so mood ends up contributing far less than genre in
practice. Because genre and mood are checked independently with no notion of
which combinations make musical sense, the "Adversarial: High Energy + Sad
Mood" test (target energy 0.9, favorite mood "sad") still returned confident,
high-scoring pop recommendations — the system doesn't recognize that in this
dataset, "sad" songs are actually low-energy, so it can't flag the request as
self-contradictory; it just optimizes each feature independently and produces a
plausible-looking list regardless.

Finally, because pop is 30% of the catalog, users who like pop are simply more
likely to see a strong genre match than fans of underrepresented genres like
soul (1 song) — the system's quality is not evenly distributed across tastes.

## Evaluation Process
Six profiles were run through `python -m src.main`, in addition to the default
"Pop / Happy" profile: three realistic tastes (**High-Energy Pop**, **Chill
Lofi**, **Deep Intense Rock**) and three adversarial/edge-case profiles
(**High Energy + Sad Mood**, **Genre Not In Catalog**, **All-Zero Targets**).
Full terminal output for every profile is below.

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

#######################################################
  EVALUATION: Additional & Adversarial Profiles
#######################################################

----- High-Energy Pop -----
#1  Blinding Lights — The Weeknd  (score 5.05)
     Why: genre match (+2.0), mood match (+1.0), energy proximity (+0.85), valence proximity (+0.75), danceability proximity (+0.45)
#2  Levitating — Dua Lipa  (score 3.912)
     Why: genre match (+2.0), energy proximity (+0.8), valence proximity (+0.637), danceability proximity (+0.475)
#3  Shape of You — Ed Sheeran  (score 3.875)
     Why: genre match (+2.0), energy proximity (+0.7), valence proximity (+0.675), danceability proximity (+0.5)
#4  Sunflower — Post Malone  (score 3.827)
     Why: genre match (+2.0), energy proximity (+0.65), valence proximity (+0.712), danceability proximity (+0.465)
#5  Anti-Hero — Taylor Swift  (score 3.69)
     Why: genre match (+2.0), energy proximity (+0.6), valence proximity (+0.675), danceability proximity (+0.415)

----- Chill Lofi -----
#1  Study Lofi — Various  (score 5.087)
     Why: genre match (+2.0), mood match (+1.0), energy proximity (+0.95), valence proximity (+0.712), danceability proximity (+0.425)
#2  Midnight Rain — Lofi Girl  (score 4.125)
     Why: genre match (+2.0), energy proximity (+1.0), valence proximity (+0.675), danceability proximity (+0.45)
#3  Experience — Ludovico Einaudi  (score 2.947)
     Why: mood match (+1.0), energy proximity (+0.95), valence proximity (+0.637), danceability proximity (+0.36)
#4  Clair de Lune — Debussy  (score 2.925)
     Why: mood match (+1.0), energy proximity (+0.9), valence proximity (+0.675), danceability proximity (+0.35)
#5  Stay With Me — Sam Smith  (score 1.875)
     Why: energy proximity (+0.85), valence proximity (+0.525), danceability proximity (+0.5)

----- Deep Intense Rock -----
#1  Bohemian Rhapsody — Queen  (score 5.212)
     Why: genre match (+2.0), mood match (+1.0), energy proximity (+1.0), valence proximity (+0.712), danceability proximity (+0.5)
#2  Hotel California — Eagles  (score 4.037)
     Why: genre match (+2.0), energy proximity (+0.85), valence proximity (+0.712), danceability proximity (+0.475)
#3  HUMBLE. — Kendrick Lamar  (score 2.05)
     Why: energy proximity (+1.0), valence proximity (+0.675), danceability proximity (+0.375)
#4  DNA. — Kendrick Lamar  (score 1.965)
     Why: energy proximity (+0.85), valence proximity (+0.75), danceability proximity (+0.365)
#5  Anti-Hero — Taylor Swift  (score 1.873)
     Why: energy proximity (+0.85), valence proximity (+0.638), danceability proximity (+0.385)

----- Adversarial: High Energy + Sad Mood -----
#1  Levitating — Dua Lipa  (score 4.062)
     Why: genre match (+2.0), energy proximity (+0.85), valence proximity (+0.712), danceability proximity (+0.5)
#2  Blinding Lights — The Weeknd  (score 3.925)
     Why: genre match (+2.0), energy proximity (+0.9), valence proximity (+0.6), danceability proximity (+0.425)
#3  Shape of You — Ed Sheeran  (score 3.9)
     Why: genre match (+2.0), energy proximity (+0.75), valence proximity (+0.675), danceability proximity (+0.475)
#4  Sunflower — Post Malone  (score 3.777)
     Why: genre match (+2.0), energy proximity (+0.7), valence proximity (+0.637), danceability proximity (+0.44)
#5  Anti-Hero — Taylor Swift  (score 3.565)
     Why: genre match (+2.0), energy proximity (+0.65), valence proximity (+0.525), danceability proximity (+0.39)

----- Adversarial: Genre Not In Catalog -----
#1  Bluebird — John Denver  (score 2.838)
     Why: mood match (+1.0), energy proximity (+0.9), valence proximity (+0.488), danceability proximity (+0.45)
#2  Sunflower — Post Malone  (score 2.822)
     Why: mood match (+1.0), energy proximity (+0.9), valence proximity (+0.562), danceability proximity (+0.36)
#3  Shape of You — Ed Sheeran  (score 2.7)
     Why: mood match (+1.0), energy proximity (+0.85), valence proximity (+0.525), danceability proximity (+0.325)
#4  Levitating — Dua Lipa  (score 2.538)
     Why: mood match (+1.0), energy proximity (+0.75), valence proximity (+0.488), danceability proximity (+0.3)
#5  Happier — Marshmello  (score 2.49)
     Why: mood match (+1.0), energy proximity (+0.7), valence proximity (+0.45), danceability proximity (+0.34)

----- Adversarial: All-Zero Targets -----
#1  Clair de Lune — Debussy  (score 4.65)
     Why: genre match (+2.0), mood match (+1.0), energy proximity (+0.9), valence proximity (+0.3), danceability proximity (+0.45)
#2  Experience — Ludovico Einaudi  (score 4.552)
     Why: genre match (+2.0), mood match (+1.0), energy proximity (+0.85), valence proximity (+0.262), danceability proximity (+0.44)
#3  Study Lofi — Various  (score 2.312)
     Why: mood match (+1.0), energy proximity (+0.75), valence proximity (+0.337), danceability proximity (+0.225)
#4  Stay With Me — Sam Smith  (score 1.55)
     Why: energy proximity (+0.65), valence proximity (+0.6), danceability proximity (+0.3)
#5  Midnight Rain — Lofi Girl  (score 1.5)
     Why: energy proximity (+0.8), valence proximity (+0.45), danceability proximity (+0.25)
```

### Why "Levitating" ranks #1 for the default Pop / Happy profile
Levitating hits both exact-match bonuses (genre `pop`, mood `happy`) *and* its
audio features (energy 0.75, valence 0.85, danceability 0.9) sit almost on top
of the user's targets (0.75 / 0.8 / 0.8) — so it collects nearly the maximum
possible points on every single signal. It isn't winning on one strength; it's
winning because it's a near-perfect match on all five signals at once.

### Profile comparisons
- **High-Energy Pop vs. Deep Intense Rock:** the High-Energy Pop profile
  surfaces fast, upbeat pop/energetic tracks (Blinding Lights, Levitating),
  while the Deep Intense Rock profile pulls in Bohemian Rhapsody and Hotel
  California — this makes sense because both profiles ask for a *different*
  genre and a *different* energy/valence target, and the genre bonus plus
  proximity scoring correctly separate the two clusters.
- **Chill Lofi vs. Deep Intense Rock:** Chill Lofi's top picks (Study Lofi,
  Midnight Rain) have energy around 0.2–0.25, while Deep Intense Rock's top
  pick (Bohemian Rhapsody) has energy 0.7 — the two lists barely overlap
  because the target energy gap between the profiles is large and energy
  proximity swings the score a lot once genre/mood are tied.
  "Explained simply: a person who wants quiet study music and a person who
  wants a big dramatic rock song are never going to want the same songs, and
  the system correctly keeps their recommendation lists apart."
- **Default Pop/Happy vs. Adversarial (Genre Not In Catalog):** the default
  profile's top 5 are all pop songs with big genre bonuses; the moment the
  genre bonus disappears (because "reggaeton" isn't in the catalog), the
  ranking reshuffles around mood + numeric closeness only, and a country song
  (Bluebird) can suddenly outrank pop songs it would have lost to otherwise.
  This is the clearest evidence of the genre filter bubble described above.
- **Adversarial: High Energy + Sad Mood vs. Adversarial: All-Zero Targets:**
  the "sad + high energy" profile still returns upbeat pop songs because no
  sad song in the catalog is also high-energy, so the numeric targets simply
  outvote the (unmet) mood request. The "all-zero" profile, by contrast,
  correctly finds the two lowest-energy songs in the whole catalog (Clair de
  Lune, Experience) — showing the proximity math itself is working correctly
  even when the mood/genre request is unusual.

### Weight-shift experiment
As a sensitivity test, the genre bonus was temporarily **halved (2.0 → 1.0)**
and the energy weight was **doubled (max 1.0 → 2.0)**, then `main.py` was
re-run and reverted afterward (the shipped code in `src/recommender.py` still
uses the original weights described in the Algorithm Summary above).
The clearest change showed up in the **High-Energy Pop** profile: with the
original weights, the top 5 were all pop songs (Blinding Lights, Levitating,
Shape of You, Sunflower, Anti-Hero). With energy weighted more heavily than
genre, **Sicko Mode (hiphop)** and **Roses (electronic)** — both very
high-energy tracks — broke into the top 5, displacing lower-energy pop songs.
This confirms the filter-bubble finding above: genre weight is currently the
main reason non-pop, high-energy songs don't get recommended to pop fans, and
turning that dial down measurably increases genre diversity in the results.
Whether that's "more accurate" depends on what the user actually wants — for
someone who cares about energy more than genre labels, the reweighted version
arguably produces *better* recommendations; for someone who genuinely wants
"more pop songs like the ones I like," the original weighting is more accurate.

## Intended Use and Non-Intended Use
**Intended use:** an educational simulation of content-based recommendation for
learning how scoring, ranking, and explainability work together. Good for
demoing the *idea* of a recommender on a small, fixed catalog.

**Not intended for:** production music recommendations, any real user-facing
product, or any decision with real-world stakes. The catalog is far too small
and hand-picked, the scoring weights were chosen by guesswork rather than
learned from real listening data, and the system has no way to detect or
correct for the biases described above. It should not be used to make claims
about real listener behavior or musical taste.

## Ideas for Improvement
1. **Weight normalization by catalog composition** — scale the genre bonus
   down (or the danceability/energy weights up) based on how common a genre
   already is in the catalog, so popular genres don't automatically dominate.
2. **Smarter mood matching** — replace exact string matching with a small
   mood-similarity table (e.g., "energetic" and "confident" are closer than
   "energetic" and "calm") so near-miss moods still earn partial credit.
3. **Diversity penalty** — after picking the top result, apply a small penalty
   to later songs that share an artist or genre with songs already in the
   top-k, so the final list feels less repetitive (see Challenge 3).

## Reflection
See the **Reflection** section in `README.md` for the personal write-up on the
engineering process, AI-assisted workflow, and what I'd try next.
