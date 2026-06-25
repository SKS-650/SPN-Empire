# Voice Assistant — redesigned
import os, sys
import requests
import streamlit as st

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

from styles import inject_global_css
inject_global_css()

BACKEND_URL = "http://localhost:8000/api/v1/voice"

try:
    from streamlit_mic_recorder import mic_recorder
    _mic_ok = True
except ImportError:
    _mic_ok = False

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hs-hero" style="padding:32px 36px">
  <h1 style="font-size:1.9rem;margin:0 0 8px">🎙️ Nepali Voice Consultation</h1>
  <p style="margin:0;opacity:.85">
    Speak your symptoms in Nepali or English. The AI transcribes, analyses,
    and replies with a Nepali voice response — designed for rural patients.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Pipeline visual ───────────────────────────────────────────────────────────
p1, p2, p3, p4 = st.columns(4)
for col, step, icon, color in [
    (p1, "1. Record", "🎤", "#0EA5E9"),
    (p2, "2. Transcribe", "📝", "#8B5CF6"),
    (p3, "3. Analyse", "🧠", "#10B981"),
    (p4, "4. Respond", "🔊", "#F59E0B"),
]:
    with col:
        st.markdown(f"""
        <div class="hs-stat-pill">
          <div style="font-size:1.5rem">{icon}</div>
          <div style="font-size:.82rem;color:{color};font-weight:600;margin-top:4px">{step}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

left, right = st.columns(2, gap="large")

with left:
    st.markdown('<p class="hs-section-title">🎤 Input</p>', unsafe_allow_html=True)

    if not _mic_ok:
        st.markdown("""
        <div class="hs-card hs-card-warning">
          <b>Microphone not available</b><br>
          <span style="font-size:.88rem;color:#64748B">
            Install <code>streamlit-mic-recorder</code> for live recording:
          </span>
          <pre style="margin:8px 0 0;font-size:.82rem">pip install streamlit-mic-recorder</pre>
        </div>
        """, unsafe_allow_html=True)

    audio_bytes = None

    if _mic_ok:
        st.markdown("""
        <div style="background:#F0F9FF;border:1.5px solid #BAE6FD;border-radius:10px;
                    padding:14px 16px;margin-bottom:12px">
          <b style="color:#0369A1">निर्देशन (Instructions):</b><br>
          <span style="font-size:.88rem;color:#0C4A6E">
            रेकर्ड बटन थिच्नुहोस् र आफ्नो लक्षण बताउनुहोस्।<br>
            <i>Press Record and describe your symptoms.</i>
          </span>
        </div>
        """, unsafe_allow_html=True)

        audio = mic_recorder(
            start_prompt="▶️  Start Recording",
            stop_prompt="⏹️  Stop Recording",
            key="voice_recorder",
        )
        if audio:
            st.audio(audio["bytes"], format="audio/wav")
            audio_bytes = audio["bytes"]

    st.markdown("**Or upload an audio file:**")
    uploaded = st.file_uploader(
        "WAV / MP3 / OGG", type=["wav", "mp3", "ogg", "m4a"],
        label_visibility="collapsed",
    )
    if uploaded:
        st.audio(uploaded.getvalue(), format="audio/wav")
        audio_bytes = uploaded.getvalue()

    process_btn = st.button("⚙️ Process Query", type="primary", use_container_width=True)

    if process_btn:
        fname = getattr(uploaded, "name", "query.wav") if uploaded else "query.wav"
        with st.spinner("Running STT → NLP → TTS pipeline…"):
            try:
                files = {"file": (fname, audio_bytes or b"", "audio/wav")}
                resp = requests.post(f"{BACKEND_URL}/process", files=files, timeout=20)
                if resp.status_code == 200:
                    st.session_state["voice_result"] = resp.json()
                else:
                    st.error(f"Backend error {resp.status_code}")
                    st.session_state["voice_result"] = None
            except requests.exceptions.ConnectionError:
                st.warning("Backend offline — showing demo response.")
                st.session_state["voice_result"] = {
                    "transcription": "मलाई दुई दिन देखि टाउको दुखिरहेको छ र ज्वरो पनि छ।",
                    "translation": "I have had a headache and fever for two days.",
                    "ai_response": "तपाईंलाई भाइरल ज्वरो हुन सक्छ। प्रशस्त पानी पिउनुहोस्।",
                    "extracted_symptoms": ["Fever", "Headache"],
                    "audio_response_url": None,
                    "status": "Offline Demo",
                }

with right:
    st.markdown('<p class="hs-section-title">🤖 AI Response</p>', unsafe_allow_html=True)

    if "voice_result" in st.session_state and st.session_state["voice_result"]:
        r = st.session_state["voice_result"]

        steps = [
            ("1️⃣ Transcription (Speech → Text)", r.get("transcription", "—"), "#0EA5E9"),
            ("2️⃣ English Translation",           r.get("translation", "—"),   "#8B5CF6"),
        ]
        for label, value, color in steps:
            st.markdown(f"""
            <div class="hs-card" style="border-left:4px solid {color};padding:14px 18px">
              <div style="font-size:.8rem;font-weight:700;color:{color};
                          text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px">
                {label}
              </div>
              <div style="color:#1E293B;font-size:.95rem">{value}</div>
            </div>
            """, unsafe_allow_html=True)

        symptoms = r.get("extracted_symptoms", [])
        if symptoms:
            chips = "".join(
                f'<span class="badge badge-blue" style="margin:2px 4px 2px 0">{s}</span>'
                for s in symptoms
            )
            st.markdown(f"""
            <div class="hs-card" style="padding:14px 18px">
              <div style="font-size:.8rem;font-weight:700;color:#10B981;
                          text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">
                3️⃣ Detected Symptoms
              </div>
              {chips}
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="hs-card hs-card-success" style="padding:14px 18px">
          <div style="font-size:.8rem;font-weight:700;color:#10B981;
                      text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">
            4️⃣ AI Medical Advice (Nepali)
          </div>
          <div style="color:#1E293B;font-size:.95rem">{r.get("ai_response", "—")}</div>
        </div>
        """, unsafe_allow_html=True)

        audio_url = r.get("audio_response_url")
        if audio_url:
            st.markdown("**🔊 Audio Response:**")
            st.audio(audio_url, format="audio/mp3")
        else:
            st.info("Audio synthesis unavailable (gTTS not installed or network offline).")

        status = r.get("status", "")
        if status:
            st.caption(f"Pipeline status: {status}")
    else:
        st.markdown("""
        <div class="hs-card" style="text-align:center;padding:50px 20px">
          <div style="font-size:3rem;margin-bottom:12px">🎙️</div>
          <div style="color:#64748B">
            Record or upload audio, then click<br><b>Process Query</b>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Phrase guide ──────────────────────────────────────────────────────────────
with st.expander("📖 Common Nepali Health Phrases"):
    phrases = {
        "मलाई ज्वरो आएको छ।":    "I have a fever.",
        "टाउको दुखिरहेको छ।":    "I have a headache.",
        "पेट दुखेको छ।":          "My stomach hurts.",
        "सास फेर्न गाह्रो छ।":   "I have difficulty breathing.",
        "खोकी लागेको छ।":         "I have a cough.",
        "बान्ता भइरहेको छ।":      "I am vomiting.",
        "जीउ दुखेको छ।":          "My body aches.",
        "थकाइ लागेको छ।":         "I feel fatigued.",
    }
    cols = st.columns(2)
    for i, (nep, eng) in enumerate(phrases.items()):
        with cols[i % 2]:
            st.markdown(f"**{nep}**  \n*{eng}*")
