"""
AI Health Chat — GPT-powered conversational health assistant.
Supports English and Nepali. Falls back to a rule-based engine offline.
"""
import os
import sys
import requests
import streamlit as st

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

from styles import inject_global_css
inject_global_css()

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hs-hero" style="padding:32px 36px">
  <h1 style="font-size:1.9rem;margin:0 0 8px">💬 AI Health Chat</h1>
  <p style="margin:0;opacity:.85">
    Ask anything about health, symptoms, medicines or first-aid —
    powered by GPT with a Nepali-aware medical context.
  </p>
</div>
""", unsafe_allow_html=True)

BACKEND_URL = "http://localhost:8000/api/v1/chat"

# ── Suggested questions ───────────────────────────────────────────────────────
SUGGESTIONS = [
    "What are symptoms of typhoid fever?",
    "मलाई ज्वरो र खोकी छ, के गर्ने?",
    "How to treat snake bite before hospital?",
    "What foods help recover from diarrhea?",
    "मेरो बच्चालाई धेरै ज्वरो आएको छ",
    "Difference between viral and bacterial infection?",
    "How much paracetamol is safe per day?",
    "Signs of dehydration in children",
]

# ── Session state init ────────────────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "नमस्ते! 👋 I'm your AI Health Assistant.\n\n"
                "I can help with:\n"
                "- **Symptom explanations** and possible causes\n"
                "- **First-aid guidance** for emergencies\n"
                "- **Medicine information** and dosage queries\n"
                "- **Health tips** for rural conditions\n\n"
                "You can ask me in **Nepali or English** — I understand both! 🇳🇵"
            ),
        }
    ]

if "chat_lang" not in st.session_state:
    st.session_state.chat_lang = "Auto-detect"

# ── Layout ────────────────────────────────────────────────────────────────────
chat_col, ctrl_col = st.columns([3, 1])

# ── Control panel ─────────────────────────────────────────────────────────────
with ctrl_col:
    st.markdown("""
    <div class="hs-card hs-card-primary" style="padding:16px 18px">
      <div style="font-weight:700;font-size:.95rem;color:#1E293B;margin-bottom:12px">
        ⚙️ Chat Settings
      </div>
    """, unsafe_allow_html=True)

    lang = st.selectbox(
        "Response language",
        ["Auto-detect", "English", "नेपाली (Nepali)"],
        key="chat_lang_select",
        label_visibility="collapsed",
    )
    st.session_state.chat_lang = lang

    mode = st.selectbox(
        "AI Model",
        ["GPT-4o (Best)", "GPT-3.5 Turbo (Fast)", "Offline Fallback"],
        key="chat_model_select",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_messages = [st.session_state.chat_messages[0]]
        st.rerun()

    st.markdown("")
    st.markdown("""
    <div class="hs-card" style="padding:14px 16px">
      <div style="font-weight:600;font-size:.88rem;color:#1E293B;margin-bottom:8px">
        💡 Suggested Questions
      </div>
    """, unsafe_allow_html=True)

    for suggestion in SUGGESTIONS:
        if st.button(suggestion, key=f"sug_{suggestion[:20]}", use_container_width=True):
            st.session_state["_pending_message"] = suggestion
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="hs-card hs-card-warning" style="padding:12px 14px;font-size:.78rem;color:#92400E">
      ⚠️ <b>Disclaimer:</b> AI responses are for informational purposes only.
      Always consult a qualified healthcare professional for medical decisions.
    </div>
    """, unsafe_allow_html=True)

# ── Chat window ───────────────────────────────────────────────────────────────
with chat_col:
    # Render history
    chat_container = st.container(height=480)
    with chat_container:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div style="display:flex;justify-content:flex-end;align-items:flex-end;gap:6px;margin:6px 0">'
                    f'<div class="chat-user">{msg["content"]}</div>'
                    f'<div class="chat-avatar-user">👤</div></div>',
                    unsafe_allow_html=True,
                )
            else:
                content_html = msg["content"].replace("\n", "<br>")
                st.markdown(
                    f'<div style="display:flex;align-items:flex-end;gap:6px;margin:6px 0">'
                    f'<div class="chat-avatar-bot">🏥</div>'
                    f'<div class="chat-bot">{content_html}</div></div>',
                    unsafe_allow_html=True,
                )

    # ── Input row ─────────────────────────────────────────────────────────
    input_col, btn_col = st.columns([5, 1])
    with input_col:
        user_input = st.chat_input(
            "Ask a health question in English or Nepali…",
            key="chat_input_field",
        )
    # Handle suggestion button clicks
    if "_pending_message" in st.session_state:
        user_input = st.session_state.pop("_pending_message")

    # ── Send message ──────────────────────────────────────────────────────
    if user_input and user_input.strip():
        user_text = user_input.strip()
        st.session_state.chat_messages.append({"role": "user", "content": user_text})

        with st.spinner("Thinking…"):
            model_map = {
                "GPT-4o (Best)":       "gpt-4o",
                "GPT-3.5 Turbo (Fast)": "gpt-3.5-turbo",
                "Offline Fallback":    "offline",
            }
            payload = {
                "message": user_text,
                "history": st.session_state.chat_messages[:-1],  # exclude current
                "language": st.session_state.chat_lang,
                "model": model_map.get(mode, "gpt-4o"),
            }
            try:
                resp = requests.post(BACKEND_URL, json=payload, timeout=30)
                if resp.status_code == 200:
                    reply = resp.json().get("reply", "Sorry, no response received.")
                else:
                    reply = f"⚠️ Backend error {resp.status_code}. Using offline fallback."
                    # Try offline anyway
                    payload["model"] = "offline"
                    resp2 = requests.post(BACKEND_URL, json=payload, timeout=10)
                    if resp2.status_code == 200:
                        reply = resp2.json().get("reply", reply)
            except requests.exceptions.ConnectionError:
                reply = _offline_reply(user_text)

        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()


def _offline_reply(text: str) -> str:
    """Very simple keyword-based fallback when backend is down."""
    t = text.lower()
    if any(w in t for w in ["fever", "ज्वरो", "temperature"]):
        return ("**Fever (ज्वरो):** Stay hydrated, rest, and take Paracetamol 500mg if above 38°C. "
                "See a doctor if fever exceeds 39°C or lasts more than 3 days.")
    if any(w in t for w in ["cough", "खोकी"]):
        return ("**Cough (खोकी):** Drink warm fluids, use honey with ginger tea. "
                "Avoid cold drinks. See a doctor if coughing blood or lasts >2 weeks.")
    if any(w in t for w in ["headache", "टाउको"]):
        return ("**Headache:** Rest in a quiet place, drink water, and take Paracetamol if needed. "
                "Seek help immediately if headache is sudden and severe.")
    if any(w in t for w in ["snake", "साप", "bite"]):
        return ("**Snake Bite 🚨:** Keep limb immobile below heart. Do NOT cut, suck, or apply tourniquet. "
                "Go to hospital immediately. Call 102.")
    if any(w in t for w in ["diarrhea", "पखाला", "loose stool"]):
        return ("**Diarrhea:** Drink ORS (Jeevan Jal) frequently. Avoid dairy and greasy food. "
                "If bloody or lasting >2 days, seek medical help.")
    return ("I'm currently in offline mode. Please start the backend server (`python run.py`) "
            "for full GPT-powered responses. For emergencies, call **102** (Nepal Ambulance).")
