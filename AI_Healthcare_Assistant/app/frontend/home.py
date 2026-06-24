# ── Hamro Swasthya AI — Multi-page root ──────────────────────────────────────
import streamlit as st

st.set_page_config(
    page_title="Hamro Swasthya AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

from styles import inject_global_css          # noqa: E402
inject_global_css()

# ── Sidebar branding ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:18px 0 24px; text-align:center;'>
      <div style='font-size:2.6rem;'>🏥</div>
      <div style='color:#38BDF8;font-size:1.1rem;font-weight:700;margin-top:6px;'>
        Hamro Swasthya AI
      </div>
      <div style='color:#64748B;font-size:.75rem;margin-top:4px;'>
        Rural Healthcare • Nepal
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Multi-page navigation ─────────────────────────────────────────────────────
pages = {
    "🏠 Dashboard": [
        st.Page("home.py",           title="Home",                   icon="🏠"),
        st.Page("health_history.py", title="Health History",         icon="📜"),
    ],
    "🤖 AI Diagnostics": [
        st.Page("symptom_checker.py", title="Symptom Checker",       icon="🩺"),
        st.Page("skin_detector.py",   title="Skin Disease Analyzer", icon="🔬"),
        st.Page("ai_chat.py",         title="AI Health Chat",        icon="💬"),
    ],
    "🩺 Care & Assistance": [
        st.Page("voice_assistant.py",   title="Voice Assistant",     icon="🎙️"),
        st.Page("medicine_reminder.py", title="Medicine Reminders",  icon="⏰"),
    ],
    "🚨 Emergency": [
        st.Page("emergency_alert.py", title="Emergency SOS",         icon="🚨"),
    ],
}

pg = st.navigation(pages)
pg.run()

# ── Home page content (only renders on this page) ─────────────────────────────

# Hero banner
st.markdown("""
<div class="hs-hero">
  <h1>🏥 Hamro Swasthya AI</h1>
  <p>Empowering Rural Nepal with Intelligent, Localized Healthcare — available offline, in Nepali.</p>
</div>
""", unsafe_allow_html=True)

# ── Quick-stats row ───────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
for col, val, lbl in [
    (c1, "4",  "Disease Classes"),
    (c2, "19", "Skin Categories"),
    (c3, "2",  "Voice Languages"),
    (c4, "✅", "Offline Ready"),
    (c5, "GPT", "AI Chat Engine"),
]:
    with col:
        st.markdown(f"""
        <div class="hs-stat-pill">
          <div class="val">{val}</div>
          <div class="lbl">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

# ── Feature cards ─────────────────────────────────────────────────────────────
st.markdown('<p class="hs-section-title">✨ Features</p>', unsafe_allow_html=True)

row1_cols = st.columns(3)
features = [
    ("🩺", "AI Symptom Checker", "primary",
     "Describe symptoms in Nepali or English. Our Random Forest model predicts conditions and gives actionable advice."),
    ("🔬", "Skin Disease Analyzer", "success",
     "Upload or capture a photo. MobileNetV3 classifies 19 skin conditions including Melanoma, Eczema, and Fungal infections."),
    ("💬", "AI Health Chat", "primary",
     "Ask anything health-related — powered by GPT. Understands Nepali. Get evidence-based answers in seconds."),
    ("🎙️", "Voice Assistant", "success",
     "Speak in Nepali. The system transcribes, translates, analyses, and replies with a Nepali voice response."),
    ("⏰", "Medicine Reminders", "warning",
     "Schedule daily medication reminders. Stored locally in SQLite — no cloud, no privacy concerns."),
    ("🚨", "Emergency SOS", "danger",
     "One-click broadcast to nearby health posts. AI triage engine assesses severity before alerting."),
]

for i, (icon, title, card_type, desc) in enumerate(features):
    with row1_cols[i % 3]:
        st.markdown(f"""
        <div class="hs-card hs-card-{card_type}">
          <div style="font-size:1.8rem">{icon}</div>
          <div style="font-weight:700;font-size:1rem;margin:8px 0 6px;color:#1E293B">{title}</div>
          <div style="font-size:.87rem;color:#64748B;line-height:1.55">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Mission + How it works ────────────────────────────────────────────────────
st.markdown('<p class="hs-section-title">🎯 Mission & Approach</p>', unsafe_allow_html=True)

m1, m2 = st.columns(2)
with m1:
    st.markdown("""
    <div class="hs-card hs-card-primary">
      <h4 style="margin:0 0 10px;color:#0EA5E9">🌏 The Problem</h4>
      <p style="color:#475569;font-size:.9rem;line-height:1.6;margin:0">
        Over 80% of Nepal's population lives in rural areas with limited access to doctors,
        diagnostic labs, or timely medical advice. Language barriers make the situation worse
        for those who only speak Nepali or local dialects.
      </p>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="hs-card hs-card-success">
      <h4 style="margin:0 0 10px;color:#10B981">🤖 Our Solution</h4>
      <p style="color:#475569;font-size:.9rem;line-height:1.6;margin:0">
        An offline-first AI assistant combining classical ML (Random Forest), computer vision
        (MobileNetV3), GPT-based conversational AI, Nepali TTS/STT, and a local SQLite health
        record — all accessible on a single low-cost device with no internet required for core features.
      </p>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#94A3B8;font-size:.8rem;padding:8px 0 16px'>
  Hamro Swasthya AI &nbsp;·&nbsp; National AI Hackathon 2026 &nbsp;·&nbsp;
  SPN Empire Team &nbsp;·&nbsp; Built for Rural Healthcare in Nepal 🇳🇵
</div>
""", unsafe_allow_html=True)
