"""
app.py — Streamlit UI for the Music Recommender Simulation.
Run with: streamlit run app.py
"""

import streamlit as st
from src.recommender import load_songs, recommend_songs

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Music Recommender Simulation",
    page_icon="🎵",
    layout="wide",
)

# ── Load data ─────────────────────────────────────────────────────────────────
songs = load_songs("data/songs.csv")

GENRES = sorted(set(s["genre"] for s in songs))
MOODS  = sorted(set(s["mood"]  for s in songs))

# ── Sidebar — User Profile ────────────────────────────────────────────────────
st.sidebar.header("🎧 Your Taste Profile")

favorite_genre      = st.sidebar.selectbox("Favorite Genre",      GENRES)
favorite_mood       = st.sidebar.selectbox("Favorite Mood",       MOODS)
target_energy       = st.sidebar.slider("Target Energy",       0.0, 1.0, 0.75, 0.05)
target_valence      = st.sidebar.slider("Target Valence (Positivity)", 0.0, 1.0, 0.80, 0.05)
target_danceability = st.sidebar.slider("Target Danceability", 0.0, 1.0, 0.80, 0.05)
top_k               = st.sidebar.slider("Number of Recommendations", 1, len(songs), 5)

user_prefs = {
    "favorite_genre":      favorite_genre,
    "favorite_mood":       favorite_mood,
    "target_energy":       target_energy,
    "target_valence":      target_valence,
    "target_danceability": target_danceability,
}

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("🎵 Music Recommender Simulation")
st.markdown(
    "Adjust your **taste profile** in the sidebar and see which songs best match your vibe. "
    "Scores are computed using a weighted content-based filtering algorithm."
)

st.divider()

# ── Run recommender ───────────────────────────────────────────────────────────
results = recommend_songs(user_prefs, songs, k=top_k)

st.subheader(f"🏆 Top {top_k} Recommendations")

for i, song in enumerate(results, 1):
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### #{i} — {song['title']}")
            st.markdown(f"**Artist:** {song['artist']}  |  **Genre:** {song['genre']}  |  **Mood:** {song['mood']}")
            st.markdown("**Why recommended:**")
            for reason in song["reasons"]:
                st.markdown(f"- {reason}")
        with col2:
            st.metric("Score", f"{song['score']:.3f}")
            st.progress(min(song["score"] / 5.25, 1.0))
        st.divider()

# ── Song catalog expander ─────────────────────────────────────────────────────
with st.expander("📋 View Full Song Catalog"):
    import pandas as pd
    df = pd.DataFrame(songs)
    st.dataframe(df, use_container_width=True)

# ── Algorithm explainer ───────────────────────────────────────────────────────
with st.expander("⚙️ How the Scoring Algorithm Works"):
    st.markdown("""
| Feature | Points |
|---|---|
| Genre match | +2.0 |
| Mood match | +1.0 |
| Energy proximity | up to +1.0 |
| Valence proximity | up to +0.75 |
| Danceability proximity | up to +0.50 |

**Max possible score: 5.25**

Proximity scores reward songs that are *closer* to your target value, not just higher or lower.
Formula: `points = weight × (1 - |song_value - target_value|)`
    """)
