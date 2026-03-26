"""
Streamlit Storytelling App
Dark Fairy Theme — linear immersive reading experience.
"""

import base64
import io
import json
import pathlib
import socket
import urllib.parse
from urllib.parse import urlparse

import requests
import streamlit as st
from PIL import Image

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="The Unsleeping Echo",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — Dark Fairy Theme
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap');

    /* ── App background: deep obsidian ── */
    .stApp { background-color: #08080c; }

    /* ── Story title: tarnished gold Cinzel ── */
    h1.story-title {
        font-family: 'Cinzel', Georgia, serif;
        color: #b8860b;
        font-size: 3rem;
        text-align: center;
        letter-spacing: 0.06em;
        margin-top: 1.5rem;
        margin-bottom: 0.3rem;
        line-height: 1.2;
        text-shadow: 0 0 30px #b8860b44, 0 2px 8px #00000066;
    }

    h1.story-title::before {
        content: "❍  ◈  ❍";
        display: block;
        font-size: 1.2rem;
        color: #b8860b;
        letter-spacing: 0.6em;
        margin-bottom: 0.8rem;
        text-align: center;
        opacity: 0.85;
    }

    /* ── Chapter heading: crimson Cinzel ── */
    h2.chapter-heading {
        font-family: 'Cinzel', Georgia, serif;
        color: #c41e3a;
        font-size: 1.7rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        text-align: center;
        letter-spacing: 0.05em;
        text-shadow: 0 0 15px rgba(196, 30, 58, 0.4), 0 0 30px rgba(196, 30, 58, 0.2);
        position: relative;
    }

    h2.chapter-heading::after {
        content: "~";
        display: block;
        color: #c41e3a;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.3rem;
        opacity: 0.7;
    }

    /* ── Story body text: ghostly pale EB Garamond on obsidian-crimson ── */
    .story-text {
        font-family: 'EB Garamond', Georgia, serif;
        font-size: 1.15rem;
        line-height: 2.0;
        color: #f0ebe0;
        text-align: justify;
        background-color: #0f0a14;
        padding: 1.5rem 2rem;
        border-left: 3px solid #8b0000;
        border-right: 3px solid #8b0000;
        border-radius: 4px;
        box-shadow: inset 0 0 20px #00000044, 0 4px 16px rgba(139, 0, 0, 0.2);
    }

    /* ── Author byline: ghostly silver italic ── */
    .byline {
        font-family: 'EB Garamond', Georgia, serif;
        font-style: italic;
        color: #b8b0a0;
        font-size: 1.15rem;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: 0.08em;
    }

    /* ── Ornamental page divider ── */
    hr {
        border: none;
        text-align: center;
        margin: 2rem 0;
        color: #b8860b;
        letter-spacing: 0.8em;
        font-size: 1rem;
        overflow: hidden;
    }
    hr::before {
        content: "~  ❍  ~  ❍  ~";
        white-space: pre;
        color: #b8860b;
        opacity: 0.8;
    }

    /* ── Sidebar: dark indigo with gold border ── */
    section[data-testid="stSidebar"] {
        background-color: #1a1625;
        border-right: 2px solid #c9a227;
    }

    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Cinzel', Georgia, serif;
        color: #c9a227;
    }

    /* Sidebar divider */
    section[data-testid="stSidebar"] hr {
        color: #b8860b;
        letter-spacing: 0.4em;
        font-size: 0.9rem;
        opacity: 0.7;
    }
    section[data-testid="stSidebar"] hr::before {
        content: "§  ☽  §";
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        font-family: 'Cinzel', Georgia, serif;
        font-size: 0.9rem;
        color: #e8dcc8;
        background-color: #12100e;
        border: 1px solid #c9a227;
        border-radius: 3px;
        width: 100%;
        transition: all 0.25s ease;
        letter-spacing: 0.03em;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #c41e3a;
        border-color: #c41e3a;
        color: #e8dcc8;
    }

    /* ── Main-area navigation buttons ── */
    div[data-testid="column"] button {
        font-family: 'Cinzel', Georgia, serif;
        font-size: 1rem;
        color: #e8dcc8;
        background-color: #1a1625;
        border: 2px solid #c9a227;
        border-radius: 4px;
        width: 100%;
        letter-spacing: 0.08em;
        transition: all 0.25s ease;
    }

    div[data-testid="column"] button:hover {
        background-color: #c41e3a;
        border-color: #c41e3a;
        color: #e8dcc8;
    }

    /* ── Chapter progress indicator ── */
    .chapter-indicator {
        font-family: 'Cinzel', Georgia, serif;
        text-align: center;
        color: #f0ebe0;
        font-size: 0.95rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        padding: 0.5rem 0;
        opacity: 0.9;
    }

    /* ── Cover splash styles ── */
    .cover-splash {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(180deg, #08080c 0%, #1a0a10 50%, #08080c 100%);
        border-radius: 8px;
        margin: 2rem 0;
    }

    .cover-splash h1 {
        font-family: 'Cinzel', Georgia, serif;
        color: #f0f0e8;
        font-size: 3.5rem;
        letter-spacing: 0.1em;
        text-shadow: 0 0 40px rgba(139, 0, 0, 0.5), 0 4px 12px #00000088;
        margin-bottom: 0.5rem;
    }

    .cover-splash h1::before {
        content: "❍  ◈  ❍";
        display: block;
        font-size: 1.4rem;
        letter-spacing: 0.8em;
        margin-bottom: 1rem;
        opacity: 0.8;
        color: #b8860b;
    }

    .cover-splash .cover-author {
        font-family: 'EB Garamond', Georgia, serif;
        font-style: italic;
        color: #8a7f6e;
        font-size: 1.3rem;
        letter-spacing: 0.1em;
        margin-bottom: 3rem;
    }

    .cover-splash .open-book-btn {
        font-family: 'Cinzel', Georgia, serif;
        font-size: 1.2rem;
        color: #e8dcc8;
        background-color: #1a1625;
        border: 2px solid #c9a227;
        border-radius: 6px;
        padding: 0.8rem 3rem;
        letter-spacing: 0.15em;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
    }

    .cover-splash .open-book-btn:hover {
        background-color: #c41e3a;
        border-color: #c41e3a;
        box-shadow: 0 0 20px rgba(196, 30, 58, 0.4);
    }

    /* ── Ending screen ── */
    .ending-screen {
        text-align: center;
        padding: 5rem 2rem;
        background: linear-gradient(180deg, #08080c 0%, #1a0a10 50%, #08080c 100%);
        border-radius: 8px;
        margin: 2rem 0;
    }

    .ending-screen h1 {
        font-family: 'Cinzel', Georgia, serif;
        color: #f0f0e8;
        font-size: 3rem;
        letter-spacing: 0.2em;
        text-shadow: 0 0 40px rgba(139, 0, 0, 0.6), 0 0 80px rgba(139, 0, 0, 0.3);
        margin-bottom: 1rem;
    }

    .ending-screen h1::before {
        content: "◇  ~  ◇";
        display: block;
        font-size: 1.2rem;
        letter-spacing: 0.6em;
        margin-bottom: 1.5rem;
        opacity: 0.7;
        color: #b8860b;
    }

    .ending-screen h1::after {
        content: "◇  ~  ◇";
        display: block;
        font-size: 1.2rem;
        letter-spacing: 0.6em;
        margin-top: 1.5rem;
        opacity: 0.7;
        color: #b8860b;
    }

    .ending-screen .read-again-btn {
        font-family: 'Cinzel', Georgia, serif;
        font-size: 1rem;
        color: #e8dcc8;
        background-color: #1a1625;
        border: 2px solid #c9a227;
        border-radius: 6px;
        padding: 0.7rem 2.5rem;
        letter-spacing: 0.12em;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
        margin-top: 2rem;
    }

    .ending-screen .read-again-btn:hover {
        background-color: #5c0000;
        border-color: #5c0000;
    }

    /* ── Edit mode headings ── */
    h2, h3, h4 {
        font-family: 'Cinzel', Georgia, serif;
        color: #c9a227;
    }

    /* ── Progress bar ── */
    .progress-bar-container {
        width: 100%;
        padding: 0.5rem 0;
        margin: 1rem 0;
    }

    .progress-gold {
        height: 3px;
        background: linear-gradient(90deg, #5c0000 0%, #b8860b 100%);
        border-radius: 2px;
        transition: width 0.4s ease;
    }

    /* ── Form inputs: dark bg, parchment text ── */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        font-family: 'EB Garamond', Georgia, serif;
        background-color: #12100e;
        color: #e8dcc8;
        border: 1px solid #c9a22755;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #c41e3a;
        box-shadow: 0 0 8px rgba(196, 30, 58, 0.3);
    }

    /* ── Images: subtle shadow + slight border-radius ── */
    img {
        border-radius: 4px;
        box-shadow: 0 4px 20px rgba(139, 0, 0, 0.35), 0 0 12px rgba(139, 0, 0, 0.15);
    }

    /* ── Radio buttons ── */
    .stRadio label, .stRadio > div > label {
        font-family: 'EB Garamond', Georgia, serif;
        color: #e8dcc8;
        font-size: 1.05rem;
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        font-family: 'Cinzel', Georgia, serif;
        color: #c9a227;
    }

    /* ── Success/info messages ── */
    .stSuccess, .stInfo {
        border-left: 3px solid #c9a227;
    }

    /* ── Cover image in read mode ── */
    .cover-image-container {
        display: flex;
        justify-content: center;
        margin: 1rem 0 2rem 0;
    }

    .cover-image-container img {
        max-height: 300px;
        width: auto;
        border-radius: 6px;
        box-shadow: 0 8px 32px rgba(139, 0, 0, 0.35), 0 0 20px rgba(200, 210, 255, 0.08);
    }

    /* ── Image toggle container ── */
    .image-toggle-container {
        position: relative;
        display: inline-block;
        width: 100%;
    }

    .image-toggle-btn {
        position: absolute;
        bottom: 10px;
        right: 10px;
        background: rgba(26, 22, 37, 0.85);
        border: 1px solid #c9a227;
        border-radius: 50%;
        width: 44px;
        height: 44px;
        cursor: pointer;
        color: #e8dcc8;
        font-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.25s ease;
    }

    .image-toggle-btn:hover {
        background: rgba(196, 30, 58, 0.9);
        border-color: #c41e3a;
        transform: scale(1.1);
    }

    /* ── Particle canvas ── */
    #particle-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
    }

    .stApp > div:first-child {
        position: relative;
        z-index: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
SAMPLE_STORY_PATH = pathlib.Path(__file__).parent / "sample_story.json"
_ALLOWED_SCHEMES = {"http", "https"}


def load_sample_story() -> dict:
    """Return the bundled sample story."""
    with open(SAMPLE_STORY_PATH, encoding="utf-8") as f:
        return json.load(f)


def _is_safe_url(url: str) -> bool:
    """Return True only for public http/https URLs."""
    parsed = urlparse(url)
    if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
        return False
    hostname = parsed.hostname or ""
    if not hostname:
        return False
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
    except (socket.gaierror, ValueError):
        return False
    return True


import ipaddress

def fetch_image(source) -> Image.Image | None:
    """Load a PIL Image from a URL string, an uploaded file object, a PIL Image, or None."""
    if source is None:
        return None
    if isinstance(source, Image.Image):
        return source
    try:
        if isinstance(source, str):
            url = source.strip()
            if not url or not _is_safe_url(url):
                return None
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return Image.open(io.BytesIO(resp.content))
        return Image.open(source)
    except (requests.RequestException, OSError, SyntaxError):
        return None


def display_chapter_card(chapter: dict, chapter_idx: int, total_chapters: int, image_override=None, gif_override=None) -> None:
    """Render a single chapter as a focused dark fairy reading card."""
    st.markdown(
        f'<h2 class="chapter-heading">{chapter["title"]}</h2>',
        unsafe_allow_html=True,
    )

    # Progress indicator
    st.markdown(
        f"<p class='chapter-indicator'>Chapter {chapter_idx + 1} of {total_chapters}</p>",
        unsafe_allow_html=True,
    )

    img_source = image_override if image_override is not None else chapter.get("image", "")
    img = fetch_image(img_source)
    gif_img = fetch_image(gif_override) if gif_override else None

    # Check if both static image and GIF are available for toggle
    has_both = img is not None and gif_img is not None
    show_gif = st.session_state.show_gif.get(chapter_idx, False)

    if img:
        col_text, col_img = st.columns([3, 2])
        with col_text:
            st.markdown(
                f'<p class="story-text">{chapter["text"]}</p>',
                unsafe_allow_html=True,
            )
        with col_img:
            if has_both:
                render_image_toggle(img, gif_img, chapter_idx, show_gif)
            else:
                st.image(img, use_container_width=True)
    else:
        st.markdown(
            f'<p class="story-text">{chapter["text"]}</p>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)


def render_cover_splash(title: str, author: str, cover_image: str) -> None:
    """Render the immersive book-opening splash screen."""
    cover_img = fetch_image(cover_image)

    st.markdown("<div class='cover-splash'>", unsafe_allow_html=True)

    if cover_img:
        st.markdown("<div class='cover-image-container'>", unsafe_allow_html=True)
        st.image(cover_img, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='cover-author'>by {author}</p>", unsafe_allow_html=True)

    if st.button("Open the Book", key="open_book_btn"):
        st.session_state.current_chapter = 0
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_ending_screen() -> None:
    """Render the styled 'The End' screen."""
    st.markdown("<div class='ending-screen'>", unsafe_allow_html=True)
    st.markdown("<h1>The Echo Fades</h1>", unsafe_allow_html=True)

    if st.button("Read Again", key="read_again_btn"):
        st.session_state.current_chapter = -1
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_image_toggle(static_image, gif_image, chapter_idx, show_gif):
    """Render an image with a toggle button to switch between static image and animated GIF."""
    # Encode images to base64
    static_b64 = ""
    gif_b64 = ""

    if static_image:
        static_bytes = io.BytesIO()
        static_image.save(static_bytes, format=static_image.format or "PNG")
        static_b64 = base64.b64encode(static_bytes.getvalue()).decode()

    if gif_image:
        gif_bytes = io.BytesIO()
        gif_image.save(gif_bytes, format="GIF")
        gif_b64 = base64.b64encode(gif_bytes.getvalue()).decode()

    icon = "🎬" if show_gif else "🖼️"
    current_b64 = gif_b64 if show_gif else static_b64
    current_type = "gif" if show_gif else "png"

    if not current_b64:
        return

    # Toggle URL - appends/removes a query param that Streamlit will read
    toggle_url = f"?toggle_gif_{chapter_idx}=1" if not show_gif else f"?toggle_gif_{chapter_idx}=0"

    toggle_script = f"""
    <div class="image-toggle-container">
        <img src="data:image/{current_type};base64,{current_b64}" style="width:100%;border-radius:4px;box-shadow:0 4px 20px rgba(139,0,0,0.35),0 0 12px rgba(139,0,0,0.15);" />
        <button class="image-toggle-btn" onclick="window.location.href='{toggle_url}'" title="Toggle image/GIF">{icon}</button>
    </div>
    """
    st.html(toggle_script)


def render_particle_background():
    """Render floating particle background with sparkles/dust effect."""
    particle_script = """
    <canvas id="particle-canvas"></canvas>
    <script>
    (function() {
        var canvas = document.getElementById('particle-canvas');
        var ctx = canvas.getContext('2d');
        var particles = [];
        var colors = ['#b8860b', '#c41e3a', '#f0ebe0'];

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }

        function createParticle() {
            return {
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                size: 2 + Math.random() * 4,
                opacity: 0.15 + Math.random() * 0.35,
                color: colors[Math.floor(Math.random() * colors.length)],
                vx: (Math.random() - 0.5) * 0.3,
                vy: 0.2 + Math.random() * 0.4
            };
        }

        function init() {
            resize();
            particles = [];
            var count = 60 + Math.floor(Math.random() * 20);
            for (var i = 0; i < count; i++) {
                particles.push(createParticle());
            }
        }

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (var i = 0; i < particles.length; i++) {
                var p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.vx += (Math.random() - 0.5) * 0.05;

                if (p.y > canvas.height + 10) {
                    p.y = -10;
                    p.x = Math.random() * canvas.width;
                }
                if (p.x > canvas.width + 10) p.x = -10;
                if (p.x < -10) p.x = canvas.width + 10;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, 2 * Math.PI);
                ctx.fillStyle = p.color;
                ctx.globalAlpha = p.opacity;
                ctx.fill();
            }
            ctx.globalAlpha = 1;
            requestAnimationFrame(animate);
        }

        window.addEventListener('resize', resize);
        init();
        animate();
    })();
    </script>
    """
    st.html(particle_script)

# Floating particle background (call after function definition)
render_particle_background()

# ---------------------------------------------------------------------------
# Session-state initialisation
# ---------------------------------------------------------------------------
if "story" not in st.session_state:
    st.session_state.story = load_sample_story()
if "current_chapter" not in st.session_state:
    st.session_state.current_chapter = -1  # -1 = cover splash, 0+ = chapters
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Read"  # "Read" | "Edit"
if "chapter_images" not in st.session_state:
    st.session_state.chapter_images = {}
if "chapter_gifs" not in st.session_state:
    st.session_state.chapter_gifs = {}
if "show_gif" not in st.session_state:
    st.session_state.show_gif = {}

story: dict = st.session_state.story
chapters: list = story.get("chapters", [])

# Handle toggle query params for GIF switching
try:
    query_params = st.experimental_get_query_params()
    for key, values in query_params.items():
        if key.startswith("toggle_gif_"):
            try:
                ch_idx = int(key.replace("toggle_gif_", ""))
                if values and values[0] == "1":
                    st.session_state.show_gif[ch_idx] = True
                elif values and values[0] == "0":
                    st.session_state.show_gif[ch_idx] = False
            except (ValueError, IndexError):
                pass
    # Clear query params after processing
    st.experimental_set_query_params()
except Exception:
    pass

# ---------------------------------------------------------------------------
# Sidebar — navigation & editing controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🪞 The Unsleeping Echo")
    st.markdown("---")

    view_mode = st.radio(
        "Mode",
        options=["Read Story", "Edit Story"],
        index=0 if st.session_state.view_mode == "Read" else 1,
    )
    st.session_state.view_mode = "Read" if view_mode == "Read Story" else "Edit"

    st.markdown("---")

    if st.button("🔄 Load sample story"):
        st.session_state.story = load_sample_story()
        st.session_state.current_chapter = -1
        st.session_state.chapter_images = {}
        st.session_state.chapter_gifs = {}
        st.session_state.show_gif = {}
        st.rerun()

    # Upload a custom story JSON file
    uploaded_story = st.file_uploader(
        "📂 Upload story JSON", type=["json"], key="story_upload"
    )
    if uploaded_story is not None:
        try:
            loaded = json.load(uploaded_story)
            st.session_state.story = loaded
            st.session_state.current_chapter = -1
            st.session_state.chapter_images = {}
            st.session_state.chapter_gifs = {}
            st.session_state.show_gif = {}
            st.rerun()
        except json.JSONDecodeError:
            st.error("Invalid JSON file.")

    st.markdown("---")
    st.markdown("*A mirror never lies...*")

# ---------------------------------------------------------------------------
# Main area — READ mode
# ---------------------------------------------------------------------------
if st.session_state.view_mode == "Read":
    if not chapters:
        st.info("No chapters yet. Switch to **Edit Story** mode to add content.")
    else:
        idx = st.session_state.current_chapter

        # Cover splash (-1 state)
        if idx == -1:
            render_cover_splash(
                title=story.get("title", "Untitled Story"),
                author=story.get("author", "Unknown"),
                cover_image=story.get("cover_image", ""),
            )

        # Ending screen (past last chapter)
        elif idx >= len(chapters):
            render_ending_screen()

        # Chapter display (0 to N-1)
        else:
            chapter = chapters[idx]
            image_override = st.session_state.chapter_images.get(idx)
            gif_override = st.session_state.chapter_gifs.get(idx)
            display_chapter_card(chapter, idx, len(chapters), image_override=image_override, gif_override=gif_override)

            # Navigation buttons
            col_prev, col_spacer, col_next = st.columns([1, 2, 1])

            with col_prev:
                if idx > 0 and st.button("← Return"):
                    st.session_state.current_chapter -= 1
                    st.rerun()

            with col_next:
                if idx < len(chapters) - 1:
                    if st.button("Continue →"):
                        st.session_state.current_chapter += 1
                        st.rerun()
                else:
                    # Last chapter — go to ending
                    if st.button("The Echo Fades 🍎"):
                        st.session_state.current_chapter = len(chapters)
                        st.rerun()

# ---------------------------------------------------------------------------
# Main area — EDIT mode
# ---------------------------------------------------------------------------
else:
    st.markdown("## ✏️ Edit Your Story")

    # Preview button
    if st.button("👁 Preview Story (Dark Mode)"):
        st.session_state.view_mode = "Read"
        st.session_state.current_chapter = -1
        st.rerun()

    st.markdown("---")

    with st.expander("Story details", expanded=True):
        new_title = st.text_input("Story title", value=story.get("title", ""))
        new_author = st.text_input("Author name", value=story.get("author", ""))
        new_cover = st.text_input(
            "Cover image URL (optional)", value=story.get("cover_image", "")
        )
        if new_title != story.get("title") or new_author != story.get("author") or new_cover != story.get("cover_image"):
            story["title"] = new_title
            story["author"] = new_author
            story["cover_image"] = new_cover

    st.markdown("### Chapters")

    # Edit existing chapters
    for i, ch in enumerate(chapters):
        with st.expander(f"📄 {ch['title']}", expanded=(i == 0)):
            ch["title"] = st.text_input(
                "Chapter title", value=ch["title"], key=f"ch_title_{i}"
            )
            ch["text"] = st.text_area(
                "Chapter text", value=ch["text"], height=200, key=f"ch_text_{i}"
            )
            ch["image"] = st.text_input(
                "Image URL", value=ch.get("image", ""), key=f"ch_img_{i}"
            )
            uploaded = st.file_uploader(
                "Or upload an image", type=["png", "jpg", "jpeg", "webp"],
                key=f"ch_upload_{i}"
            )
            if uploaded is not None:
                st.session_state.chapter_images[i] = uploaded
                img = fetch_image(uploaded)
                if img:
                    st.image(img, width=300)
            elif ch.get("image"):
                img = fetch_image(ch["image"])
                if img:
                    st.image(img, width=300)

            # GIF upload
            uploaded_gif = st.file_uploader(
                "Animated GIF (optional)", type=["gif"],
                key=f"ch_gif_upload_{i}"
            )
            if uploaded_gif is not None:
                st.session_state.chapter_gifs[i] = uploaded_gif
                gif_img = fetch_image(uploaded_gif)
                if gif_img:
                    st.image(gif_img, width=300)
            elif i in st.session_state.chapter_gifs:
                gif_img = fetch_image(st.session_state.chapter_gifs[i])
                if gif_img:
                    st.image(gif_img, width=300)

            if st.button(f"🗑 Delete chapter {i + 1}", key=f"del_{i}"):
                chapters.pop(i)
                st.session_state.chapter_images = {
                    (k if k < i else k - 1): v
                    for k, v in st.session_state.chapter_images.items()
                    if k != i
                }
                st.session_state.chapter_gifs = {
                    (k if k < i else k - 1): v
                    for k, v in st.session_state.chapter_gifs.items()
                    if k != i
                }
                st.session_state.show_gif = {
                    k: v for k, v in st.session_state.show_gif.items()
                    if k != i
                }
                st.session_state.current_chapter = -1
                st.rerun()

    # Add new chapter
    st.markdown("---")
    st.markdown("### ➕ Add a new chapter")
    with st.form("new_chapter_form", clear_on_submit=True):
        new_ch_title = st.text_input("Chapter title")
        new_ch_text = st.text_area("Chapter text", height=150)
        new_ch_img = st.text_input("Image URL (optional)")
        submitted = st.form_submit_button("Add chapter")
        if submitted and new_ch_title.strip():
            chapters.append(
                {"title": new_ch_title.strip(), "text": new_ch_text.strip(), "image": new_ch_img.strip()}
            )
            st.success(f"Chapter '{new_ch_title}' added!")
            st.rerun()

    # Export story as JSON
    st.markdown("---")
    st.markdown("### 💾 Export story")
    story_json = json.dumps(story, indent=2, ensure_ascii=False)
    st.download_button(
        label="Download story as JSON",
        data=story_json,
        file_name="my_story.json",
        mime="application/json",
    )
