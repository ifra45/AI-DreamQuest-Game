
import streamlit as st
import subprocess
import sys
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
HEROINE_IMAGE = BASE_DIR / "assets" / "heroine.png"
GAME_FILE = BASE_DIR / "game.py"

# Page setup
st.set_page_config(
    page_title="DreamQuest AI",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dreamy purple styling
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 15% 25%,
            rgba(111, 67, 170, 0.35), transparent 35%),
        radial-gradient(circle at 85% 70%,
            rgba(57, 93, 160, 0.28), transparent 35%),
        linear-gradient(135deg, #100b2b, #241449, #101b38);
    color: white;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1150px;
}

.game-title {
    text-align: center;
    font-size: 48px;
    font-weight: 800;
    color: #f0d7ff;
    text-shadow: 0 0 22px #9b6bff;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 17px;
    color: #d7c5ff;
    letter-spacing: 2px;
    margin-bottom: 32px;
}

.magic-card {
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(215, 190, 255, 0.25);
    border-radius: 22px;
    padding: 28px;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.22);
}

.story {
    color: #e7dcff;
    font-size: 17px;
    line-height: 1.8;
}

.stButton > button {
    background: linear-gradient(90deg, #9b69ed, #695ce7);
    color: white;
    border: 1px solid #c5a7ff;
    border-radius: 14px;
    padding: 12px 20px;
    font-weight: bold;
    min-height: 48px;
    transition: 0.2s;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #b58cff, #8175ff);
    color: white;
    border-color: white;
}

.stTextInput input {
    background: rgba(255,255,255,0.09);
    color: white;
    border: 1px solid #a78bfa;
    border-radius: 10px;
}

label, p, h1, h2, h3 {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Heading
st.markdown(
    '<div class="game-title">🌙 DreamQuest AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'EVERY DREAM HIDES A MAGICAL ADVENTURE ✨'
    '</div>',
    unsafe_allow_html=True
)

# Front page layout
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown('<div class="magic-card">', unsafe_allow_html=True)

    if HEROINE_IMAGE.exists():
        st.image(str(HEROINE_IMAGE), use_container_width=True)
    else:
        st.warning("Heroine image not found in assets/heroine.png")

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="magic-card">', unsafe_allow_html=True)

    st.markdown("## ✨ Welcome, Dreamer!")
    st.markdown(
        '<div class="story">'
        'A magical world is waiting for you. Explore an enchanted '
        'forest, discover glowing crystals, overcome obstacles, '
        'and find the hidden treasure. Your adventure begins here!'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")
    hero_name = st.text_input(
        "Choose your hero's name",
        value="Luna",
        max_chars=20
    )

    st.write("")

    if st.button("✨ Begin My Adventure", use_container_width=True):
        if not GAME_FILE.exists():
            st.error("game.py nahi mili. Isay DreamQuestAI folder mein rakho.")
        elif not hero_name.strip():
            st.warning("Please enter your hero's name.")
        else:
            try:
                subprocess.Popen(
                    [sys.executable, str(GAME_FILE)],
                    cwd=str(BASE_DIR)
                )
                st.success(
                    f"Your adventure is starting, {hero_name.strip()}! "
                    "Check your game window."
                )
            except Exception as error:
                st.error(f"Could not launch the game: {error}")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("")
st.markdown(
    "<p style='text-align:center;color:#c8b5ed;'>"
    "🌟 Believe in the magic. Discover your destiny. 🌟"
    "</p>",
    unsafe_allow_html=True
)
