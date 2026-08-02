"""
app.py — Streamlit UI for the Music Recommender Simulation.
Run with: streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv

from src.agent import run_concierge
from src.recommender import load_songs, recommend_songs

load_dotenv()

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

st.title("🎵 VibeFinder — Music Recommender & AI Concierge")
st.markdown(
    "A content-based music recommender, extended with an **AI Concierge** that turns a "
    "plain-English request into a taste profile, runs it through the same scoring engine, "
    "and explains the picks in natural language."
)

manual_tab, concierge_tab = st.tabs(["🎚️ Manual Preferences", "🤖 AI Concierge"])

# ── Manual mode (original Module 3 UI) ───────────────────────────────────────
with manual_tab:
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

    st.markdown(
        "Adjust your **taste profile** in the sidebar and see which songs best match your vibe. "
        "Scores are computed using a weighted content-based filtering algorithm."
    )
    st.divider()

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

    with st.expander("📋 View Full Song Catalog"):
        import pandas as pd
        df = pd.DataFrame(songs)
        st.dataframe(df, width="stretch")

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

# ── AI Concierge mode (agentic: plan -> act -> check -> respond) ─────────────
with concierge_tab:
    st.markdown(
        "Describe what you want to listen to in your own words. An agent turns that into a "
        "taste profile, the **same deterministic scorer** above ranks the catalog against it, "
        "and a second pass writes a short explanation grounded only in the actual scores."
    )
    st.caption(
        "Works with or without a GEMINI_API_KEY: with a key it uses Gemini for both steps; "
        "without one it automatically falls back to a rule-based parser and template "
        "explanation, so the app never breaks."
    )

    concierge_top_k = st.slider("Number of Recommendations", 1, len(songs), 5, key="concierge_k")
    query = st.text_area(
        "What are you in the mood for?",
        placeholder="e.g. \"I need something chill and relaxing to study to\" or "
                    "\"upbeat pop for a workout\"",
        key="concierge_query",
    )

    if st.button("Get Recommendations", type="primary"):
        if not query.strip():
            st.warning("Type a request first (or try an empty string to see the guardrail handle it).")
        with st.spinner("Extracting preferences, ranking, and writing an explanation..."):
            result = run_concierge(query, songs, k=concierge_top_k)

        mode_label = "🤖 Gemini" if result.extraction.mode == "llm" else "🛠️ Rule-based fallback"
        st.info(
            f"**Extraction mode:** {mode_label}  |  **Confidence:** {result.extraction.confidence:.2f}\n\n"
            f"*{result.extraction.rationale}*"
            + (f"\n\n_Fallback reason: {result.extraction.fallback_reason}_" if result.extraction.fallback_reason else "")
        )
        st.json(result.extraction.prefs)

        for w in result.warnings:
            st.warning(w)

        st.markdown(f"**Explanation ({'Gemini' if result.explanation_mode == 'llm' else 'template'}):**")
        st.write(result.explanation)

        st.subheader(f"🏆 Top {concierge_top_k} Recommendations")
        for i, song in enumerate(result.recommendations, 1):
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
