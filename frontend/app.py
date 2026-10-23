import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import core  # noqa: E402
from backend.schemas import ChatMessage  # noqa: E402

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.png"

st.set_page_config(page_title="French Learning App", page_icon=str(LOGO_PATH), layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,500&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --ink: #121212;
        --muted: #5B5B52;
        --cream: #F8F3E4;
        --lime: #E6EFC0;
        --blue: #AEC2F0;
        --pink: #F4CFE3;
        --mustard: #F0C98A;
        --lavender: #DCCCF2;
    }

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: var(--cream);
    }
    [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 1040px;
        padding-top: 2.5rem;
    }
    html, body, p, span, label, div, li { font-family: 'Inter', sans-serif; color: var(--ink); }
    h1, h2, h3, h4 { font-family: 'Fraunces', Georgia, serif !important; font-weight: 600 !important; color: var(--ink) !important; }

    /* Buttons — exact .btn treatment from the design canvas */
    .stButton > button, .stFormSubmitButton > button, [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"] {
        background: var(--ink) !important;
        color: var(--cream) !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.6rem 1.6rem !important;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover { background: #2A2A24 !important; }
    .stButton > button p, .stButton > button span, .stButton > button div,
    .stFormSubmitButton > button p, .stFormSubmitButton > button span, .stFormSubmitButton > button div {
        color: var(--cream) !important;
    }

    /* Tabs — newer Streamlit renders these as React Aria tabs (data-testid="stTab"),
       not BaseWeb, so target that instead of [data-baseweb="tab"] */
    [role="tablist"] { gap: 10px; border-bottom: none !important; padding: 4px 0 18px; }
    [data-testid="stTab"] .react-aria-SelectionIndicator { display: none !important; }
    [data-testid="stTab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--ink) !important;
        background: #FFFFFF !important;
        border: 1.5px dashed var(--ink) !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        margin: 0 !important;
    }
    [data-testid="stTab"][aria-selected="true"] {
        background: var(--ink) !important;
        border-style: solid !important;
    }
    [data-testid="stTab"][aria-selected="true"] p,
    [data-testid="stTab"][aria-selected="true"] span,
    [data-testid="stTab"][aria-selected="true"] div {
        color: var(--cream) !important;
    }

    /* Inputs */
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
    [data-baseweb="select"] > div, [data-testid="stNumberInput"] input {
        border: 1.5px dashed var(--ink) !important;
        border-radius: 10px !important;
        background: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }
    /* Selectbox — newer Streamlit renders this as a React Aria combobox, not BaseWeb,
       so target the direct wrapper of the combobox input instead of [data-baseweb="select"] */
    [data-testid="stSelectbox"] div:has(> [role="combobox"]) {
        border: 1.5px dashed var(--ink) !important;
        border-radius: 10px !important;
        background: #FFFFFF !important;
    }
    [data-testid="stSelectbox"] [role="combobox"] {
        border: none !important;
        background: transparent !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Expander — same card treatment as the module cards */
    [data-testid="stExpander"] {
        border: 1.5px dashed var(--ink) !important;
        border-radius: 16px !important;
        background: #FFFFFF !important;
    }

    /* Alerts — soft pastel fills, no border */
    [data-testid="stAlertContentSuccess"], [data-testid="stSuccess"] { background: var(--lime) !important; border: none !important; border-radius: 14px !important; color: var(--ink) !important; }
    [data-testid="stAlertContentInfo"], [data-testid="stInfo"] { background: var(--blue) !important; border: none !important; border-radius: 14px !important; color: var(--ink) !important; }
    [data-testid="stAlertContentError"], [data-testid="stError"] { background: var(--pink) !important; border: none !important; border-radius: 14px !important; color: var(--ink) !important; }
    [data-testid="stAlertContentWarning"], [data-testid="stWarning"] { background: var(--mustard) !important; border: none !important; border-radius: 14px !important; color: var(--ink) !important; }

    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        border: 1.5px dashed var(--ink) !important;
        border-radius: 16px !important;
        background: #FFFFFF !important;
        padding: 0.5rem 0.75rem !important;
        margin-bottom: 0.6rem !important;
    }

    [data-testid="stCaptionContainer"] { color: var(--muted) !important; }

    /* Card containers — st.container(border=True), exact module-card treatment from the canvas */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1.5px dashed var(--ink) !important;
        border-radius: 16px !important;
        background: #FFFFFF !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stVerticalBlock"] {
        padding: 1.75rem 1.75rem 1.25rem;
        gap: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def module_header(icon_svg: str, bg: str, title: str, subtitle: str) -> None:
    html = f"""
        <div style="display:flex;align-items:center;gap:16px;margin:4px 0 22px;">
          <span style="flex:0 0 auto;width:56px;height:56px;border-radius:50%;background:{bg};
                       border:1.5px dashed #121212;display:flex;align-items:center;justify-content:center;">{icon_svg}</span>
          <div>
            <div style="font-family:'Fraunces',serif;font-weight:600;font-size:26px;color:#121212;line-height:1.2;">{title}</div>
            <div style="font-size:14.5px;color:#5B5B52;margin-top:2px;">{subtitle}</div>
          </div>
        </div>
        """
    st.markdown("\n".join(line.strip() for line in html.splitlines()), unsafe_allow_html=True)


_ICON_STROKE = 'fill="none" stroke="#121212" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
BOOK_ICON = (
    f'<svg width="24" height="24" viewBox="0 0 24 24" {_ICON_STROKE}>'
    '<path d="M4 5.5C4 4.67 4.67 4 5.5 4H12V20H5.5C4.67 20 4 19.33 4 18.5V5.5Z"/>'
    '<path d="M20 5.5C20 4.67 19.33 4 18.5 4H12V20H18.5C19.33 20 20 19.33 20 18.5V5.5Z"/></svg>'
)
PENCIL_ICON = (
    f'<svg width="24" height="24" viewBox="0 0 24 24" {_ICON_STROKE}>'
    '<path d="M4 20L4.8 16.2L15.5 5.5C16.1 4.9 17.1 4.9 17.7 5.5L18.5 6.3C19.1 6.9 19.1 7.9 18.5 8.5L7.8 19.2L4 20Z"/>'
    '<path d="M14 7L17 10"/></svg>'
)
ARCHIVE_ICON = (
    f'<svg width="24" height="24" viewBox="0 0 24 24" {_ICON_STROKE}>'
    '<path d="M4 7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2"/>'
    '<path d="M4 7h16v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7Z"/><path d="M9 12h6"/></svg>'
)
CHAT_ICON = (
    f'<svg width="24" height="24" viewBox="0 0 24 24" {_ICON_STROKE}>'
    '<path d="M21 11.5C21 16.75 16.97 21 12 21C10.86 21 9.77 20.78 8.77 20.38L3 21L4.4 16.5'
    'C3.52 15.08 3 13.35 3 11.5C3 6.25 7.03 2 12 2C16.97 2 21 6.25 21 11.5Z"/>'
    '<circle cx="8" cy="11.5" r="0.9" fill="#121212" stroke="none"/>'
    '<circle cx="12" cy="11.5" r="0.9" fill="#121212" stroke="none"/>'
    '<circle cx="16" cy="11.5" r="0.9" fill="#121212" stroke="none"/></svg>'
)

ACCENT = "#AEC2F0"

_hero_html = f"""
    <div style="display:flex;align-items:center;gap:10px;margin:0 0 18px;">
      <span style="width:34px;height:34px;border-radius:8px;border:1.5px dashed #121212;
                   display:flex;align-items:center;justify-content:center;">{BOOK_ICON}</span>
      <span style="font-family:'Fraunces',serif;font-size:22px;font-weight:600;color:#121212;">Bonjour</span>
      <span style="font-family:Inter,sans-serif;font-size:12px;font-weight:600;letter-spacing:0.16em;
                   text-transform:uppercase;color:#6B6B5E;margin-left:2px;">est. Paris</span>
    </div>

    <section style="background:#E6EFC0;border-radius:18px;padding:48px 44px;box-sizing:border-box;
                     position:relative;overflow:hidden;border:1.5px dashed #121212;">
      <div style="position:absolute;top:24px;right:30px;width:92px;height:92px;">
        <svg width="92" height="92" viewBox="0 0 104 104">
          <circle cx="52" cy="52" r="49" fill="none" stroke="#121212" stroke-width="1.2" stroke-dasharray="2.5 4"/>
          <circle cx="52" cy="52" r="38" fill="none" stroke="#121212" stroke-width="1"/>
          <path id="stampPath" d="M 52,52 m -38,0 a 38,38 0 1,1 76,0 a 38,38 0 1,1 -76,0" fill="none"/>
          <text font-size="7.5" letter-spacing="2.5" fill="#121212" font-family="Inter, sans-serif">
            <textPath href="#stampPath" startOffset="2%">BONJOUR • FRANÇAIS • A1–B2 •</textPath>
          </text>
          <text x="52" y="58" text-anchor="middle" font-family="Fraunces, serif" font-size="22" font-weight="600" fill="#121212">FR</text>
        </svg>
      </div>

      <div style="display:flex;flex-wrap:wrap;gap:40px;align-items:center;">
        <div style="flex:1 1 400px;min-width:280px;">
          <div style="font-family:Inter,sans-serif;font-size:12px;font-weight:600;letter-spacing:0.16em;
                      text-transform:uppercase;color:#6B6B5E;margin-bottom:12px;">Your Local French Tutor</div>
          <h1 style="font-family:'Fraunces',serif;font-size:46px;line-height:1.14;color:#121212;margin:0 0 16px;font-weight:600;">
            Speak
            <span style="border-radius:6px;padding:2px 12px;display:inline-block;background:#FFFFFF;
                         color:#121212;border:1.5px dashed #121212;">French</span>
            With
            <span style="border-radius:6px;padding:2px 12px;display:inline-block;background:{ACCENT};color:#121212;"><em>Real</em></span>
            <span style="border-radius:6px;padding:2px 12px;display:inline-block;background:#F4CFE3;color:#121212;"><em>Confidence</em></span>
          </h1>
          <p style="font-size:16px;line-height:1.6;color:#4A4A40;max-width:420px;margin:0 0 26px;">
            Learn to read, write and speak French with AI-generated stories, instant grammar
            corrections and real voice conversation practice — built for levels A1 through B2.
          </p>
          <div style="display:flex;flex-wrap:wrap;align-items:center;gap:16px;">
            <a href="#app-start" style="display:inline-flex;align-items:center;gap:8px;border-radius:10px;
               padding:13px 24px;font-weight:600;font-size:15px;background:#121212;color:#F8F3E4;
               text-decoration:none;font-family:Inter,sans-serif;">
              Start Learning
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F8F3E4" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12H19"/><path d="M13 6L19 12L13 18"/></svg>
            </a>
            <span style="display:flex;align-items:center;gap:8px;color:#4A4A40;font-size:14px;font-weight:600;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#121212" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3L19 6V11C19 15.5 16 19 12 21C8 19 5 15.5 5 11V6L12 3Z"/></svg>
              100% local &amp; private
            </span>
          </div>
        </div>

        <div style="flex:0 0 360px;min-width:260px;position:relative;height:320px;">
          <svg width="100%" height="100%" viewBox="0 0 420 380" style="position:absolute;inset:0;">
            <circle cx="210" cy="190" r="150" fill="#F8F3E4" opacity="0.6"/>
            <path d="M120 150 Q210 90 300 150 Q330 190 300 240 Q210 290 120 240 Q90 190 120 150 Z" fill="none" stroke="#121212" stroke-width="1" stroke-dasharray="3 5"/>
          </svg>
          <div style="position:absolute;top:24px;left:40px;transform:rotate(-3deg);">
            <span style="width:52px;height:52px;border-radius:50%;background:#F4CFE3;border:1.5px dashed #121212;
                         display:flex;align-items:center;justify-content:center;font-family:'Fraunces',serif;
                         font-weight:600;color:#121212;font-size:19px;">M</span>
          </div>
          <div style="position:absolute;top:6px;left:88px;background:#FFFFFF;border:1px solid #121212;
                      border-radius:6px;padding:2px 12px;color:#121212;font-size:13px;font-weight:600;transform:rotate(-2deg);">Bonjour !</div>

          <div style="position:absolute;top:66px;right:26px;transform:rotate(2deg);">
            <span style="width:60px;height:60px;border-radius:50%;background:{ACCENT};border:1.5px dashed #121212;
                         display:flex;align-items:center;justify-content:center;font-family:'Fraunces',serif;
                         font-weight:600;color:#121212;font-size:21px;">C</span>
          </div>
          <div style="position:absolute;top:46px;right:92px;background:#FFFFFF;border:1px solid #121212;
                      border-radius:6px;padding:2px 12px;color:#121212;font-size:13px;font-weight:600;transform:rotate(3deg);">Salut !</div>

          <div style="position:absolute;bottom:64px;left:62px;transform:rotate(3deg);">
            <span style="width:64px;height:64px;border-radius:50%;background:#F0C98A;border:1.5px dashed #121212;
                         display:flex;align-items:center;justify-content:center;font-family:'Fraunces',serif;
                         font-weight:600;color:#121212;font-size:22px;">S</span>
          </div>
          <div style="position:absolute;bottom:118px;left:0px;background:#FFFFFF;border:1px solid #121212;
                      border-radius:6px;padding:2px 12px;color:#121212;font-size:13px;font-weight:600;transform:rotate(-3deg);">Coucou !</div>

          <div style="position:absolute;bottom:22px;right:54px;transform:rotate(-2deg);">
            <span style="width:52px;height:52px;border-radius:50%;background:#FFFFFF;border:1.5px dashed #121212;
                         display:flex;align-items:center;justify-content:center;font-family:'Fraunces',serif;
                         font-weight:600;color:#121212;font-size:19px;">J</span>
          </div>
          <div style="position:absolute;bottom:76px;right:108px;background:#FFFFFF;border:1px solid #121212;
                      border-radius:6px;padding:2px 12px;color:#121212;font-size:13px;font-weight:600;transform:rotate(2deg);">Ça va ?</div>
        </div>
      </div>
    </section>

    <div style="text-align:center;max-width:580px;margin:44px auto 28px;">
      <div style="font-family:Inter,sans-serif;font-size:12px;font-weight:600;letter-spacing:0.16em;
                  text-transform:uppercase;color:#6B6B5E;margin-bottom:10px;">Learn By Doing</div>
      <h2 style="font-family:'Fraunces',serif;font-size:30px;margin:0 0 10px;color:#121212;">
        Three ways to <span style="border-radius:6px;padding:2px 12px;display:inline-block;background:#F4CFE3;"><em>practice</em></span> French
      </h2>
      <p style="font-size:15px;color:#5B5B52;line-height:1.6;margin:0;">
        Every module is built around your CEFR level, from first words at A1 to fluent conversation at B2.
      </p>
    </div>

    <div style="display:grid;grid-template-columns:repeat(3, minmax(0, 1fr));gap:20px;margin-bottom:12px;">
      <div style="background:#FFFFFF;border:1.5px dashed #121212;border-radius:16px;padding:26px;">
        <span style="width:48px;height:48px;border-radius:50%;background:#E6EFC0;display:flex;align-items:center;
                     justify-content:center;margin-bottom:16px;">{BOOK_ICON}</span>
        <h3 style="font-family:'Fraunces',serif;font-size:18px;margin:0 0 8px;color:#121212;">Reading</h3>
        <p style="font-size:13.5px;color:#5B5B52;line-height:1.6;margin:0;">
          Custom short stories at your level, with translation, vocabulary and grammar notes — plus narrated audio.
        </p>
      </div>
      <div style="background:#FFFFFF;border:1.5px dashed #121212;border-radius:16px;padding:26px;">
        <span style="width:48px;height:48px;border-radius:50%;background:#F4CFE3;display:flex;align-items:center;
                     justify-content:center;margin-bottom:16px;">{PENCIL_ICON}</span>
        <h3 style="font-family:'Fraunces',serif;font-size:18px;margin:0 0 8px;color:#121212;">Writing</h3>
        <p style="font-size:13.5px;color:#5B5B52;line-height:1.6;margin:0;">
          Submit anything you write in French and get clear grammar and spelling corrections.
        </p>
      </div>
      <div style="background:#FFFFFF;border:1.5px dashed #121212;border-radius:16px;padding:26px;">
        <span style="width:48px;height:48px;border-radius:50%;background:#DCCCF2;display:flex;align-items:center;
                     justify-content:center;margin-bottom:16px;">{CHAT_ICON}</span>
        <h3 style="font-family:'Fraunces',serif;font-size:18px;margin:0 0 8px;color:#121212;">Chat</h3>
        <p style="font-size:13.5px;color:#5B5B52;line-height:1.6;margin:0;">
          Type or speak with the tutor, hear a French reply, and read the transcript as you go.
        </p>
      </div>
    </div>
    <div id="app-start"></div>
    """

st.markdown("\n".join(line.strip() for line in _hero_html.splitlines()), unsafe_allow_html=True)

LEVELS = ["A1", "A2", "B1", "B2"]

tab_reading, tab_writing, tab_chat, tab_library = st.tabs(
    ["📖 Reading", "✍️ Writing", "💬 Chat", "📚 Library"]
)

with tab_reading:
    module_header(
        BOOK_ICON, "#E6EFC0", "Reading",
        "Custom short stories at your level, with vocabulary and grammar notes.",
    )

    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            level = st.selectbox("CEFR level", LEVELS, key="reading_level")
        with col2:
            theme = st.text_input("Theme", value="a trip to the market", key="reading_theme")
        with col3:
            length = st.selectbox(
                "Length", ["short", "medium", "long"], key="reading_length", format_func=str.capitalize
            )

        if st.button("Generate story", key="generate_story_btn"):
            with st.spinner("Writing your story..."):
                try:
                    st.session_state["story"] = core.generate_story(level, theme, length)
                except core.AppError as exc:
                    st.error(f"Error: {exc}")

    story = st.session_state.get("story")
    if story:
        with st.container(border=True):
            st.markdown(f"### {story['title_fr']}")
            st.audio(story["audio_path"], format="audio/mpeg")
            st.write(story["story_fr"])

            with st.expander("Show English translation (check your understanding first!)"):
                st.markdown(f"**{story['title_en']}**")
                st.write(story["story_en"])

            st.markdown("#### Vocabulary")
            for item in story["vocabulary"]:
                st.markdown(f"- **{item['french']}** — {item['english']}")

            st.markdown("#### Grammar notes")
            for note in story["grammar_notes"]:
                st.markdown(f"- {note}")

with tab_writing:
    module_header(
        PENCIL_ICON, "#F4CFE3", "Writing",
        "Submit anything you write in French and get clear grammar and spelling corrections.",
    )

    with st.container(border=True):
        writing_level = st.selectbox("Your level", LEVELS, index=2, key="writing_level")
        user_text = st.text_area("Write something in French", height=200, key="writing_text")

        if st.button("Check my writing", key="check_writing_btn"):
            with st.spinner("Analyzing..."):
                try:
                    st.session_state["correction"] = core.correct_writing(user_text, writing_level)
                except core.AppError as exc:
                    st.error(f"Error: {exc}")

    correction = st.session_state.get("correction")
    if correction:
        with st.container(border=True):
            st.markdown("#### Corrected text")
            st.success(correction["corrected_text"])

            st.markdown("#### Corrections")
            for item in correction["corrections"]:
                st.markdown(f"- ~~{item['original']}~~ → **{item['corrected']}**  \n  _{item['explanation_en']}_")

            st.markdown("#### Feedback")
            st.info(correction["overall_feedback_en"])

with tab_chat:
    module_header(
        CHAT_ICON, "#DCCCF2", "Chat",
        "Practice French by typing or speaking — get instant replies, with audio for voice messages.",
    )

    with st.container(border=True):
        chat_level = st.selectbox("Your level", LEVELS, index=0, key="chat_level")

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg.get("translation"):
                    st.caption(f"English: {msg['translation']}")
                if msg.get("audio_path"):
                    st.audio(msg["audio_path"], format="audio/mpeg")

        audio_value = st.audio_input("Record a message in French", key="chat_audio_input")
        if audio_value is not None and st.button("Send recording", key="send_chat_audio_btn"):
            history_payload = [
                ChatMessage(role=m["role"], content=m["content"]) for m in st.session_state["chat_history"]
            ]
            with st.spinner("Listening and replying..."):
                try:
                    result = core.chat_voice(chat_level, history_payload, audio_value.getvalue())
                    st.session_state["chat_history"].append({"role": "user", "content": result["transcript_fr"]})
                    st.session_state["chat_history"].append(
                        {
                            "role": "assistant",
                            "content": result["reply_fr"],
                            "translation": result["reply_en"],
                            "audio_path": result["audio_path"],
                        }
                    )
                    st.rerun()
                except core.AppError as exc:
                    st.error(f"Error: {exc}")

        user_message = st.chat_input("Or type a message in French...", key="chat_text_input")
        if user_message:
            st.session_state["chat_history"].append({"role": "user", "content": user_message})
            history_payload = [
                ChatMessage(role=m["role"], content=m["content"]) for m in st.session_state["chat_history"][:-1]
            ]
            with st.spinner("Thinking..."):
                try:
                    result = core.chat_text(chat_level, history_payload, user_message)
                    st.session_state["chat_history"].append(
                        {"role": "assistant", "content": result["reply_fr"], "translation": result["reply_en"]}
                    )
                except core.AppError as exc:
                    st.session_state["chat_history"].pop()
                    st.error(f"Error: {exc}")
            st.rerun()

        if st.button("Clear conversation", key="clear_chat_btn"):
            st.session_state["chat_history"] = []
            st.rerun()

with tab_library:
    module_header(
        ARCHIVE_ICON, "#F0C98A", "Library",
        "Every story you've generated or added, organized by level and length.",
    )

    if st.session_state.pop("story_loaded_notice", False):
        st.success("Loaded! Open the **📖 Reading** tab above to read it.")
    if st.session_state.pop("story_added_notice", False):
        st.success("Saved to your library!")

    with st.expander("➕ Add your own story"):
        with st.form("add_story_form", clear_on_submit=True):
            add_title_fr = st.text_input("Title (French)")
            add_col1, add_col2 = st.columns(2)
            with add_col1:
                add_level = st.selectbox("CEFR level", LEVELS, key="add_story_level")
            with add_col2:
                add_length = st.selectbox(
                    "Length", ["short", "medium", "long"], key="add_story_length", format_func=str.capitalize
                )
            add_theme = st.text_input("Theme / description (optional)")
            add_story_fr = st.text_area("Story text (French)", height=200)
            add_story_en = st.text_area("English translation (optional)", height=200)
            add_submitted = st.form_submit_button("Save to library")

        if add_submitted:
            if not add_title_fr.strip() or not add_story_fr.strip():
                st.error("Title and French story text are required.")
            else:
                with st.spinner("Saving..."):
                    core.add_story_to_library(
                        level=add_level,
                        length=add_length,
                        theme=add_theme,
                        title_fr=add_title_fr,
                        title_en="",
                        story_fr=add_story_fr,
                        story_en=add_story_en,
                    )
                st.session_state["story_added_notice"] = True
                st.rerun()

    library = core.list_story_library()

    if not library:
        st.info("No saved stories yet. Generate one in the Reading tab.")

    for lvl in LEVELS:
        level_items = [item for item in library if item["level"] == lvl]
        if not level_items:
            continue
        st.markdown(f"### {lvl}")
        for length_name in ["short", "medium", "long"]:
            length_items = [item for item in level_items if item["length"] == length_name]
            if not length_items:
                continue
            with st.expander(f"{length_name.capitalize()} ({len(length_items)})"):
                for item in length_items:
                    col_title, col_btn = st.columns([4, 1])
                    with col_title:
                        st.markdown(f"**{item['title_fr']}** — *{item['title_en']}*  \n{item['theme']}")
                    with col_btn:
                        if st.button("Open", key=f"open_{item['cache_key']}"):
                            with st.spinner("Loading..."):
                                try:
                                    st.session_state["story"] = core.get_library_story(item["cache_key"])
                                    st.session_state["story_loaded_notice"] = True
                                    st.rerun()
                                except core.AppError as exc:
                                    st.error(f"Error: {exc}")
