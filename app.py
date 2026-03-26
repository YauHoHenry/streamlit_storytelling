"""
Streamlit Storytelling App
Brings stories and generated/uploaded images together in an interactive web interface.
"""

import ipaddress
import io
import json
import pathlib
import socket
from urllib.parse import urlparse

import requests
import streamlit as st
from PIL import Image

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Story Weaver",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Main background */
    .stApp { background-color: #fdf8f2; }

    /* Story title */
    h1.story-title {
        font-family: 'Georgia', serif;
        color: #3b2a1a;
        font-size: 2.6rem;
        margin-bottom: 0.2rem;
    }

    /* Chapter heading */
    h2.chapter-heading {
        font-family: 'Georgia', serif;
        color: #5c3d2e;
        font-size: 1.5rem;
        border-bottom: 2px solid #c8a97e;
        padding-bottom: 0.3rem;
        margin-top: 1.5rem;
    }

    /* Story body text */
    .story-text {
        font-family: 'Georgia', serif;
        font-size: 1.1rem;
        line-height: 1.85;
        color: #2e2010;
        text-align: justify;
    }

    /* Author byline */
    .byline {
        font-style: italic;
        color: #7a5c3e;
        font-size: 1rem;
    }

    /* Navigation buttons */
    div[data-testid="column"] button {
        width: 100%;
    }

    /* Sidebar header */
    section[data-testid="stSidebar"] .stMarkdown h2 {
        color: #5c3d2e;
    }

    /* Divider colour */
    hr { border-top: 1px solid #c8a97e; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
SAMPLE_STORY_PATH = pathlib.Path(__file__).parent / "sample_story.json"


def load_sample_story() -> dict:
    """Return the bundled sample story."""
    with open(SAMPLE_STORY_PATH, encoding="utf-8") as f:
        return json.load(f)


_ALLOWED_SCHEMES = {"http", "https"}


def _is_safe_url(url: str) -> bool:
    """
    Return True only for public http/https URLs.
    Blocks private/loopback addresses to prevent SSRF.
    """
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


def fetch_image(source) -> Image.Image | None:
    """
    Load a PIL Image from a URL string, an uploaded file object,
    or return None if the source is empty / unavailable.
    Only http/https URLs pointing to public hosts are fetched.
    """
    if source is None:
        return None
    try:
        if isinstance(source, str):
            url = source.strip()
            if not url or not _is_safe_url(url):
                return None
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return Image.open(io.BytesIO(resp.content))
        # Uploaded file object
        return Image.open(source)
    except (requests.RequestException, OSError, SyntaxError):
        return None


def display_chapter(chapter: dict, image_override=None) -> None:
    """Render a single chapter with its image."""
    st.markdown(
        f'<h2 class="chapter-heading">{chapter["title"]}</h2>',
        unsafe_allow_html=True,
    )

    img_source = image_override if image_override is not None else chapter.get("image", "")
    img = fetch_image(img_source)

    if img:
        col_text, col_img = st.columns([3, 2])
        with col_text:
            st.markdown(
                f'<p class="story-text">{chapter["text"]}</p>',
                unsafe_allow_html=True,
            )
        with col_img:
            st.image(img, use_container_width=True)
    else:
        st.markdown(
            f'<p class="story-text">{chapter["text"]}</p>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session-state initialisation
# ---------------------------------------------------------------------------
if "story" not in st.session_state:
    st.session_state.story = load_sample_story()
if "current_chapter" not in st.session_state:
    st.session_state.current_chapter = 0
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Read"  # "Read" | "Edit"
if "chapter_images" not in st.session_state:
    # Overrides for uploaded images keyed by chapter index
    st.session_state.chapter_images = {}

story: dict = st.session_state.story
chapters: list = story.get("chapters", [])

# ---------------------------------------------------------------------------
# Sidebar — navigation & editing controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 📖 Story Weaver")
    st.markdown("---")

    view_mode = st.radio(
        "Mode",
        options=["Read Story", "Edit Story"],
        index=0 if st.session_state.view_mode == "Read" else 1,
    )
    st.session_state.view_mode = "Read" if view_mode == "Read Story" else "Edit"

    st.markdown("---")

    if chapters:
        st.markdown("**Jump to chapter**")
        for i, ch in enumerate(chapters):
            label = ch["title"]
            if st.button(label, key=f"nav_{i}"):
                st.session_state.current_chapter = i

    st.markdown("---")
    if st.button("🔄 Load sample story"):
        st.session_state.story = load_sample_story()
        st.session_state.current_chapter = 0
        st.session_state.chapter_images = {}
        st.rerun()

    # Upload a custom story JSON file
    uploaded_story = st.file_uploader(
        "📂 Upload story JSON", type=["json"], key="story_upload"
    )
    if uploaded_story is not None:
        try:
            loaded = json.load(uploaded_story)
            st.session_state.story = loaded
            st.session_state.current_chapter = 0
            st.session_state.chapter_images = {}
            st.rerun()
        except json.JSONDecodeError:
            st.error("Invalid JSON file.")

# ---------------------------------------------------------------------------
# Main area — READ mode
# ---------------------------------------------------------------------------
if st.session_state.view_mode == "Read":
    # Story header
    cover_img = fetch_image(story.get("cover_image", ""))
    if cover_img:
        col_cover, col_meta = st.columns([2, 3])
        with col_cover:
            st.image(cover_img, use_container_width=True)
        with col_meta:
            st.markdown(
                f'<h1 class="story-title">{story.get("title", "Untitled Story")}</h1>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<p class="byline">by {story.get("author", "Unknown")}</p>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f'<h1 class="story-title">{story.get("title", "Untitled Story")}</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="byline">by {story.get("author", "Unknown")}</p>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    if not chapters:
        st.info("No chapters yet. Switch to **Edit Story** mode to add content.")
    else:
        idx = st.session_state.current_chapter
        chapter = chapters[idx]
        image_override = st.session_state.chapter_images.get(idx)
        display_chapter(chapter, image_override=image_override)

        # Chapter navigation
        col_prev, col_indicator, col_next = st.columns([1, 2, 1])
        with col_prev:
            if idx > 0 and st.button("← Previous"):
                st.session_state.current_chapter -= 1
                st.rerun()
        with col_indicator:
            st.markdown(
                f"<p style='text-align:center;color:#7a5c3e;'>"
                f"Chapter {idx + 1} of {len(chapters)}</p>",
                unsafe_allow_html=True,
            )
        with col_next:
            if idx < len(chapters) - 1 and st.button("Next →"):
                st.session_state.current_chapter += 1
                st.rerun()

        # Show all chapters toggle
        st.markdown("<br>", unsafe_allow_html=True)
        if st.checkbox("📜 Show all chapters on one page"):
            st.markdown("---")
            for i, ch in enumerate(chapters):
                display_chapter(ch, image_override=st.session_state.chapter_images.get(i))

# ---------------------------------------------------------------------------
# Main area — EDIT mode
# ---------------------------------------------------------------------------
else:
    st.markdown("## ✏️ Edit Your Story")

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
        with st.expander(f"📄 {ch['title']}", expanded=(i == st.session_state.current_chapter)):
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

            if st.button(f"🗑 Delete chapter {i + 1}", key=f"del_{i}"):
                chapters.pop(i)
                st.session_state.chapter_images = {
                    (k if k < i else k - 1): v
                    for k, v in st.session_state.chapter_images.items()
                    if k != i
                }
                # Keep current_chapter in bounds after deletion
                if st.session_state.current_chapter >= len(chapters):
                    st.session_state.current_chapter = max(0, len(chapters) - 1)
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
