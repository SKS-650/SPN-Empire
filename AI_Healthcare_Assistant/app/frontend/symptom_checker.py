# Symptom Checker — redesigned with global theme
import os, sys
import streamlit as st
import requests

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

from styles import inject_global_css
inject_global_css()

BACKEND_URL = "http://localhost:8000/api/v1/disease"

COMMON_SYMPTOMS = [
    "Fever", "Cough", "Headache", "Fatigue", "Body Ache",
    "Nausea", "Vomiting", "Diarrhea", "Shortness of Breath", "Loss of Smell",
]

SEVERITY_CONFIG = {
    "High":   ("#FEE2E2", "#DC2626", "🔴", "badge-red"),
    "Medium": ("#FEF9C3", "#B45309", "🟡", "badge-yellow"),
    "Low":    ("#D1FAE5", "#065F46", "🟢", "badge-green"),
}

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hs-hero" style="padding:32px 36px">
  <h1 style="font-size:1.9rem;margin:0 0 8px">🩺 AI Symptom Checker</h1>
  <p style="margin:0;opacity:.85">
    Select your symptoms — our Random Forest model predicts possible conditions
    and gives actionable, localised guidance.
  </p>
</div>
""", unsafe_allow_html=True)


def run_local_fallback(symptoms):
    if "Shortness of Breath" in symptoms or ("Cough" in symptoms and "Fever" in symptoms):
        return {"condition": "Respiratory Infection", "confidence": 0.72, "severity": "High",
                "recommendations": ["Monitor oxygen levels.", "Visit nearest health post immediately."]}
    if any(s in symptoms for s in ["Nausea", "Vomiting", "Diarrhea"]):
        return {"condition": "Gastroenteritis", "confidence": 0.70, "severity": "Medium",
                "recommendations": ["Drink ORS (Jeevan Jal).", "Avoid solid food for 6 hours."]}
    if "Headache" in symptoms and "Nausea" in symptoms:
        return {"condition": "Migraine", "confidence": 0.65, "severity": "Low",
                "recommendations": ["Rest in a dark room.", "Apply cold compress to forehead."]}
    return {"condition": "Influenza / Viral Syndrome", "confidence": 0.68, "severity": "Medium",
            "recommendations": ["Rest and hydrate.", "Take Paracetamol if fever > 38°C.",
                                 "See health post if symptoms worsen after 48 h."]}


# ── Two-column layout ─────────────────────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

with left:
    st.markdown('<p class="hs-section-title">📋 Enter Symptoms</p>', unsafe_allow_html=True)

    selected = st.multiselect(
        "Select all that apply:",
        COMMON_SYMPTOMS,
        placeholder="Choose symptoms…",
    )

    # Visual chip display
    if selected:
        chips = "".join(
            f'<span class="badge badge-blue" style="margin:3px 4px 3px 0">{s}</span>'
            for s in selected
        )
        st.markdown(f"<div style='margin:4px 0 12px'>{chips}</div>", unsafe_allow_html=True)

    notes = st.text_area(
        "Additional description (optional):",
        placeholder="e.g., Chills during the night, pain worsens in the morning…",
        height=90,
    )
    lang = st.radio(
        "Response language:",
        ["🇬🇧 English", "🇳🇵 Nepali"],
        horizontal=True,
    )

    analyze_btn = st.button("🔍 Analyze Symptoms", type="primary", use_container_width=True)

    if analyze_btn:
        if not selected:
            st.warning("⚠️ Please select at least one symptom.")
        else:
            with st.spinner("Running diagnostic analysis…"):
                payload = {
                    "symptoms": selected,
                    "notes": notes,
                    "language": "np" if "Nepali" in lang else "en",
                }
                data = None
                try:
                    resp = requests.post(f"{BACKEND_URL}/predict", json=payload, timeout=8)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success("✅ Analysis complete — saved to Health History.")
                    else:
                        st.warning(f"Backend error {resp.status_code}. Using offline fallback.")
                except requests.exceptions.ConnectionError:
                    st.warning("Backend offline — using local fallback.")

                st.session_state["symptom_result"] = data or run_local_fallback(selected)
                st.session_state["symptom_selected"] = selected

with right:
    st.markdown('<p class="hs-section-title">📊 Results</p>', unsafe_allow_html=True)

    if "symptom_result" in st.session_state:
        res = st.session_state["symptom_result"]
        sev = res["severity"]
        bg, fg, icon, badge_cls = SEVERITY_CONFIG.get(sev, SEVERITY_CONFIG["Low"])
        conf_pct = int(res["confidence"] * 100)

        # Result card
        st.markdown(f"""
        <div class="hs-card" style="border-left:4px solid {fg}">
          <div style="font-size:.78rem;color:#64748B;font-weight:600;letter-spacing:.04em;
                      text-transform:uppercase;margin-bottom:6px">Suspected Condition</div>
          <div style="font-size:1.35rem;font-weight:700;color:#1E293B;margin-bottom:12px">
            {res['condition']}
          </div>

          <div style="display:flex;gap:10px;align-items:center;margin-bottom:14px">
            <span class="badge {badge_cls}">{icon} {sev} Severity</span>
            <span class="badge badge-blue">Confidence: {conf_pct}%</span>
          </div>

          <div style="margin-bottom:6px;font-size:.82rem;color:#64748B">Confidence</div>
          <div class="conf-bar-wrap">
            <div class="conf-bar-fill" style="width:{conf_pct}%;
              background:{'#EF4444' if sev=='High' else '#F59E0B' if sev=='Medium' else '#10B981'}">
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Recommendations
        recs_html = "".join(
            f'<li style="margin:7px 0;color:#475569;font-size:.9rem">{r}</li>'
            for r in res["recommendations"]
        )
        st.markdown(f"""
        <div class="hs-card hs-card-primary" style="margin-top:4px">
          <div style="font-weight:700;color:#1E293B;margin-bottom:10px">📋 Recommended Actions</div>
          <ul style="margin:0;padding-left:18px">{recs_html}</ul>
        </div>
        """, unsafe_allow_html=True)

        if sev == "High":
            st.markdown("""
            <div style="background:#FEE2E2;border:1.5px solid #FCA5A5;border-radius:10px;
                        padding:14px 16px;margin-top:8px">
              <b style="color:#DC2626">🚨 High Severity Warning</b><br>
              <span style="color:#7F1D1D;font-size:.88rem">
                Please visit the nearest health post or call emergency services
                immediately: <b>102</b> (Ambulance) · <b>112</b> (Emergency)
              </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hs-card" style="text-align:center;padding:40px 20px">
          <div style="font-size:2.5rem;margin-bottom:12px">🩺</div>
          <div style="color:#64748B;font-size:.95rem">
            Select symptoms on the left and click<br>
            <b>Analyze Symptoms</b> to see results here.
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Symptom guide ─────────────────────────────────────────────────────────────
with st.expander("📖 Common Disease Symptom Guide"):
    guide_cols = st.columns(2)
    guide = [
        ("Influenza (Flu)", "Fever, Cough, Body Ache, Fatigue, Headache"),
        ("Gastroenteritis", "Nausea, Vomiting, Diarrhea, Body Ache"),
        ("Respiratory Infection", "Cough, Shortness of Breath, Fever, Fatigue"),
        ("Migraine", "Headache (throbbing), Nausea, Light sensitivity"),
    ]
    for i, (dis, syms) in enumerate(guide):
        with guide_cols[i % 2]:
            st.markdown(f"**{dis}**  \n*{syms}*")
