"""
Streamlit Storytelling App
Dark Fairy Theme — linear immersive reading experience.
"""

import base64
import html
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

    /* Keep all content within a laptop-friendly canvas */
    .block-container {
        max-width: 1180px;
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
    }

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
        font-size: clamp(1rem, 1.05vw, 1.15rem);
        line-height: 2.0;
        color: #f0ebe0;
        text-align: justify;
        background-color: #0f0a14;
        padding: clamp(1rem, 1.8vw, 1.5rem) clamp(1rem, 2.2vw, 2rem);
        border-left: 3px solid #8b0000;
        border-right: 3px solid #8b0000;
        border-radius: 4px;
        box-shadow: inset 0 0 20px #00000044, 0 4px 16px rgba(139, 0, 0, 0.2);
        max-height: 68vh;
        overflow-y: auto;
    }
    .story-text p {
        margin: 0 0 1em 0;
    }
    .story-text p:last-child {
        margin-bottom: 0;
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
        max-width: 100%;
        height: auto;
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
        max-height: min(42vh, 320px);
        width: auto;
        border-radius: 6px;
        box-shadow: 0 8px 32px rgba(139, 0, 0, 0.35), 0 0 20px rgba(200, 210, 255, 0.08);
    }

    /* Streamlit image wrappers: prevent over-expansion on laptop viewport */
    [data-testid="stImage"] img {
        max-height: 62vh;
        object-fit: contain;
    }

    /* Slightly denser spacing for smaller laptop heights */
    @media (max-height: 860px) {
        h1.story-title {
            font-size: 2.5rem;
            margin-top: 1rem;
        }
        h2.chapter-heading {
            font-size: 1.45rem;
            margin-top: 1.2rem;
            margin-bottom: 0.7rem;
        }
        .cover-splash {
            padding: 2.2rem 1.2rem;
            margin: 1rem 0;
        }
        .ending-screen {
            padding: 2.8rem 1.2rem;
            margin: 1rem 0;
        }
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
            path_or_url = source.strip()
            if not path_or_url:
                return None
            parsed = urlparse(path_or_url)
            if parsed.scheme.lower() in _ALLOWED_SCHEMES:
                if not _is_safe_url(path_or_url):
                    return None
                resp = requests.get(path_or_url, timeout=10)
                resp.raise_for_status()
                return Image.open(io.BytesIO(resp.content))
            local_path = pathlib.Path(path_or_url).expanduser()
            if not local_path.is_absolute():
                local_path = pathlib.Path(__file__).parent / local_path
            if local_path.exists() and local_path.is_file():
                return Image.open(local_path)
            return None
        if hasattr(source, "seek"):
            source.seek(0)
        return Image.open(source)
    except (requests.RequestException, OSError, SyntaxError):
        return None


def fetch_gif_bytes(source) -> bytes | None:
    """Load GIF bytes from a URL, local path, uploaded file, bytes, or None."""
    if source is None:
        return None
    if isinstance(source, (bytes, bytearray)):
        return bytes(source)
    try:
        if isinstance(source, str):
            path_or_url = source.strip()
            if not path_or_url:
                return None
            parsed = urlparse(path_or_url)
            if parsed.scheme.lower() in _ALLOWED_SCHEMES:
                if not _is_safe_url(path_or_url):
                    return None
                resp = requests.get(path_or_url, timeout=10)
                resp.raise_for_status()
                return resp.content
            local_path = pathlib.Path(path_or_url).expanduser()
            if not local_path.is_absolute():
                local_path = pathlib.Path(__file__).parent / local_path
            if local_path.exists() and local_path.is_file():
                with open(local_path, "rb") as f:
                    return f.read()
            return None
        if hasattr(source, "seek"):
            source.seek(0)
        if hasattr(source, "read"):
            return source.read()
    except (requests.RequestException, OSError, SyntaxError):
        return None
    return None


def render_gif(gif_bytes: bytes, use_container_width: bool = True) -> None:
    """Render GIF bytes as an HTML image so animation always plays."""
    width_style = (
        "width:100%;max-height:62vh;height:auto;object-fit:contain;"
        if use_container_width
        else "max-width:100%;max-height:62vh;height:auto;object-fit:contain;"
    )
    encoded = base64.b64encode(gif_bytes).decode("ascii")
    st.markdown(
        f'<img src="data:image/gif;base64,{encoded}" style="{width_style} border-radius: 4px;" alt="Animated GIF">',
        unsafe_allow_html=True,
    )


def render_gif_fullscreen(gif_bytes: bytes) -> None:
    """Render GIF in a full-width cinematic layout."""
    encoded = base64.b64encode(gif_bytes).decode("ascii")
    st.markdown(
        f"""
        <div style="margin: 0 -1rem 1rem -1rem;">
            <img
                src="data:image/gif;base64,{encoded}"
                alt="Animated GIF"
                style="display:block;width:100vw;max-width:100vw;height:auto;object-fit:contain;"
            >
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_image_compat(image, use_container_width: bool = False, width: int | None = None) -> None:
    """Display image with compatibility across Streamlit versions."""
    if width is not None:
        st.image(image, width=width)
        return
    if use_container_width:
        try:
            st.image(image, use_container_width=True)
        except TypeError:
            st.image(image, use_column_width=True)
        return
    st.image(image)


def render_story_text(text: str) -> None:
    """Render story text while preserving empty lines and style."""
    safe_text = html.escape(text or "")
    paragraphs = [p for p in safe_text.split("\n\n") if p.strip()]
    if paragraphs:
        content = "".join(f"<p>{p.replace(chr(10), '<br>')}</p>" for p in paragraphs)
    else:
        content = "<p></p>"
    st.markdown(
        f'<div class="story-text">{content}</div>',
        unsafe_allow_html=True,
    )


def build_media_pages(chapter: dict, chapter_idx: int) -> list[dict]:
    """Build media flow: first png -> first gif -> second png -> second gif."""
    pages: list[dict] = []

    image_1_src = st.session_state.chapter_images.get(chapter_idx)
    image_1 = fetch_image(image_1_src if image_1_src is not None else chapter.get("image", ""))
    gif_1 = st.session_state.chapter_gifs.get(chapter_idx)
    if gif_1 is None:
        gif_1 = fetch_gif_bytes(chapter.get("gif", ""))

    image_2_src = st.session_state.chapter_images_2.get(chapter_idx)
    image_2 = fetch_image(image_2_src if image_2_src is not None else chapter.get("image_2", ""))
    gif_2 = st.session_state.chapter_gifs_2.get(chapter_idx)
    if gif_2 is None:
        gif_2 = fetch_gif_bytes(chapter.get("gif_2", ""))

    if image_1 is not None:
        pages.append({"kind": "image", "content": image_1})
    if gif_1 is not None:
        pages.append({"kind": "gif", "content": gif_1})
    if image_2 is not None:
        pages.append({"kind": "image", "content": image_2})
    if gif_2 is not None:
        pages.append({"kind": "gif", "content": gif_2})

    return pages


def display_chapter_card(chapter: dict, chapter_idx: int, total_chapters: int, page=0, media_pages=None) -> None:
    """Render a single chapter with ordered media pages."""
    st.markdown(
        f'<h2 class="chapter-heading">{chapter["title"]}</h2>',
        unsafe_allow_html=True,
    )
    pages = media_pages or []
    page_count = len(pages)

    if page_count > 0:
        safe_page = max(0, min(page, page_count - 1))
        st.markdown(
            f"<p class='chapter-indicator'>Chapter {chapter_idx + 1} of {total_chapters} &bull; Page {safe_page + 1} of {page_count}</p>",
            unsafe_allow_html=True,
        )
        current_page = pages[safe_page]
        if current_page["kind"] == "gif":
            col_text, col_img = st.columns([3, 2])
            with col_text:
                render_story_text(chapter["text"])
            with col_img:
                render_gif(current_page["content"], use_container_width=True)
        else:
            col_text, col_img = st.columns([3, 2])
            with col_text:
                render_story_text(chapter["text"])
            with col_img:
                show_image_compat(current_page["content"], use_container_width=True)
    else:
        st.markdown(
            f"<p class='chapter-indicator'>Chapter {chapter_idx + 1} of {total_chapters}</p>",
            unsafe_allow_html=True,
        )
        render_story_text(chapter["text"])

    st.markdown("<hr>", unsafe_allow_html=True)


def render_cover_splash(title: str, author: str, cover_image: str) -> None:
    """Render the immersive book-opening splash screen."""
    cover_img = fetch_image(cover_image)

    st.markdown("<div class='cover-splash'>", unsafe_allow_html=True)

    if cover_img:
        st.markdown("<div class='cover-image-container'>", unsafe_allow_html=True)
        show_image_compat(cover_img, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='cover-author'>by {author}</p>", unsafe_allow_html=True)

    if st.button("Open the Book", key="open_book_btn"):
        st.session_state.current_chapter = 0
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_ending_screen() -> None:
    """Render the styled 'The End' screen."""
    ending_img = fetch_image("src/ending.png")
    st.markdown("<div class='ending-screen'>", unsafe_allow_html=True)
    if ending_img:
        show_image_compat(ending_img, use_container_width=True)
    st.markdown("<h1>The Echo Fades</h1>", unsafe_allow_html=True)

    if st.button("Read Again", key="read_again_btn"):
        st.session_state.current_chapter = -1
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


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
    st.markdown(particle_script, unsafe_allow_html=True)

# Floating particle background (call after function definition)
render_particle_background()

# ---------------------------------------------------------------------------
# Session-state initialisation
# ---------------------------------------------------------------------------
if "story" not in st.session_state:
    st.session_state.story = load_sample_story()
if "current_chapter" not in st.session_state:
    st.session_state.current_chapter = -1  # -1 = cover splash, 0+ = chapters
if "chapter_images" not in st.session_state:
    st.session_state.chapter_images = {}
if "chapter_gifs" not in st.session_state:
    st.session_state.chapter_gifs = {}
if "chapter_images_2" not in st.session_state:
    st.session_state.chapter_images_2 = {}
if "chapter_gifs_2" not in st.session_state:
    st.session_state.chapter_gifs_2 = {}
if "chapter_page" not in st.session_state:
    st.session_state.chapter_page = {}

story: dict = st.session_state.story
chapters: list = story.get("chapters", [])

# Handle next_page query params for multi-page chapters
try:
    query_params = st.query_params
    for key, values in query_params.items():
        if key.startswith("next_page_"):
            try:
                ch_idx = int(key.replace("next_page_", ""))
                if values and values[0] == "1":
                    st.session_state.chapter_page[ch_idx] = 1
            except (ValueError, IndexError):
                pass
        elif key.startswith("prev_page_"):
            try:
                ch_idx = int(key.replace("prev_page_", ""))
                if values and values[0] == "1":
                    st.session_state.chapter_page[ch_idx] = 0
            except (ValueError, IndexError):
                pass
    # Clear query params after processing
    st.query_params.clear()
except Exception:
    pass

# ---------------------------------------------------------------------------
# Sidebar — navigation & editing controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## The Unsleeping Echo")

    st.markdown("### Chapter Shortcuts")
    if st.button("Cover", key="go_cover"):
        st.session_state.current_chapter = -1
        st.rerun()

    for i, chapter in enumerate(chapters):
        chapter_title = chapter.get("title", f"Chapter {i + 1}")
        if st.button(f"{i + 1}. {chapter_title}", key=f"go_chapter_{i}"):
            st.session_state.current_chapter = i
            st.session_state.chapter_page[i] = 0
            st.rerun()

    if st.button("Ending", key="go_ending"):
        st.session_state.current_chapter = len(chapters)
        st.rerun()

    st.markdown("---")
    current_idx = st.session_state.current_chapter
    if current_idx == -1:
        st.markdown("*Now reading: Cover*")
    elif 0 <= current_idx < len(chapters):
        st.markdown(f"*Now reading: Chapter {current_idx + 1}*")
    else:
        st.markdown("*Now reading: Ending*")

# ---------------------------------------------------------------------------
# Main area — READ mode
# ---------------------------------------------------------------------------
if not chapters:
    st.info("No chapters available in the story.")
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
        media_pages = build_media_pages(chapter, idx)
        page_count = len(media_pages)
        current_page = st.session_state.chapter_page.get(idx, 0)
        if page_count > 0:
            current_page = max(0, min(current_page, page_count - 1))
        else:
            current_page = 0
        st.session_state.chapter_page[idx] = current_page

        display_chapter_card(
            chapter,
            idx,
            len(chapters),
            page=current_page,
            media_pages=media_pages,
        )

        # Navigation buttons
        col_prev, col_spacer, col_next = st.columns([1, 2, 1])

        with col_prev:
            if page_count > 0 and current_page > 0:
                if st.button("← Previous"):
                    st.session_state.chapter_page[idx] = current_page - 1
                    st.rerun()
            elif idx > 0:
                if st.button("← Return"):
                    st.session_state.current_chapter -= 1
                    st.rerun()
            elif idx == 0 and current_page == 0:
                if st.button("← Back to Cover"):
                    st.session_state.current_chapter = -1
                    st.rerun()

        with col_next:
            if page_count > 0 and current_page < page_count - 1:
                if st.button("Next Page →"):
                    st.session_state.chapter_page[idx] = current_page + 1
                    st.rerun()
            elif idx < len(chapters) - 1:
                if st.button("Continue →"):
                    st.session_state.current_chapter += 1
                    st.session_state.chapter_page[idx] = 0
                    st.rerun()
            else:
                # Last chapter — go to ending
                if st.button("The Echo Fades 🍎"):
                    st.session_state.current_chapter = len(chapters)
                    st.rerun()
