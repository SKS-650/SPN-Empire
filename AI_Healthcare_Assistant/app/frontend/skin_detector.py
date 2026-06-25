# Skin Disease Detector — redesigned
import os, sys
import requests
import streamlit as st

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

from styles import inject_global_css
inject_global_css()

BACKEND_URL = "http://localhost:8000/api/v1/skin"

URGENCY_CFG = {
    "High":   ("#FEE2E2", "#DC2626", "🔴", "badge-red"),
    "Medium": ("#FEF9C3", "#B45309", "🟡", "badge-yellow"),
    "Low":    ("#D1FAE5", "#065F46", "🟢", "badge-green"),
}

DEMO_CLASSES = [
    "Acne and Rosacea Photos",
    "Eczema Photos",
    "Tinea Ringworm Candidiasis and other Fungal Infections",
    "Melanoma Skin Cancer Nevi and Moles",
]

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hs-hero" style="padding:32px 36px">
  <h1 style="font-size:1.9rem;margin:0 0 8px">🔬 Skin Disease Analyzer</h1>
  <p style="margin:0;opacity:.85">
    Upload a photo or use your camera. MobileNetV3 classifies 19 skin conditions
    including Melanoma, Eczema, Fungal infections, and more.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
upload_col, result_col = st.columns([1, 1], gap="large")

with upload_col:
    st.markdown('<p class="hs-section-title">📸 Upload or Capture</p>', unsafe_allow_html=True)

    input_mode = st.radio(
        "Input method:",
        ["📁 Upload Image", "📷 Camera"],
        horizontal=True,
    )

    uploaded_file = None
    if "Upload" in input_mode:
        uploaded_file = st.file_uploader(
            "Select a skin image:",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )
        st.caption("💡 Best results with a well-lit, close-up photo of the affected area.")
    else:
        uploaded_file = st.camera_input("Capture skin region", label_visibility="collapsed")

    if uploaded_file:
        st.image(uploaded_file, use_column_width=True, caption="Preview")

        run_btn = st.button("✨ Run AI Analysis", type="primary", use_container_width=True)

        if run_btn:
            with st.spinner("Running deep-learning inference…"):
                file_bytes = uploaded_file.getvalue()
                fname = getattr(uploaded_file, "name", "capture.jpg")
                files = {"file": (fname, file_bytes, "image/jpeg")}
                data = None
                try:
                    resp = requests.post(f"{BACKEND_URL}/analyze", files=files, timeout=30)
                    if resp.status_code == 200:
                        data = resp.json()
                    else:
                        st.error(f"Backend error {resp.status_code}: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.warning("Backend offline — showing demo result.")
                    data = {
                        "condition": DEMO_CLASSES[len(file_bytes) % len(DEMO_CLASSES)],
                        "confidence": 0.74,
                        "urgency": "Medium",
                        "care_steps": ["Keep area clean and dry.",
                                       "Consult a primary health centre for treatment."],
                        "status": "Offline Demo",
                    }
                st.session_state["skin_result"] = data

with result_col:
    st.markdown('<p class="hs-section-title">📊 Analysis Result</p>', unsafe_allow_html=True)

    if "skin_result" in st.session_state and st.session_state["skin_result"]:
        d = st.session_state["skin_result"]
        urg = d.get("urgency", "Medium")
        bg, fg, icon, badge_cls = URGENCY_CFG.get(urg, URGENCY_CFG["Medium"])
        conf_pct = int(d.get("confidence", 0) * 100)
        condition = d.get("condition", "—").replace("_", " ").title()

        st.markdown(f"""
        <div class="hs-card" style="border-left:4px solid {fg}">
          <div style="font-size:.78rem;color:#64748B;font-weight:600;letter-spacing:.04em;
                      text-transform:uppercase;margin-bottom:6px">Detected Condition</div>
          <div style="font-size:1.25rem;font-weight:700;color:#1E293B;margin-bottom:12px">
            {condition}
          </div>
          <div style="display:flex;gap:10px;align-items:center;margin-bottom:14px">
            <span class="badge {badge_cls}">{icon} {urg} Urgency</span>
            <span class="badge badge-blue">Confidence: {conf_pct}%</span>
          </div>
          <div style="font-size:.82rem;color:#64748B;margin-bottom:5px">Confidence</div>
          <div class="conf-bar-wrap">
            <div class="conf-bar-fill" style="width:{conf_pct}%;
              background:{'#EF4444' if urg=='High' else '#F59E0B' if urg=='Medium' else '#10B981'}">
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        steps_html = "".join(
            f'<li style="margin:7px 0;color:#475569;font-size:.9rem">{s}</li>'
            for s in d.get("care_steps", [])
        )
        st.markdown(f"""
        <div class="hs-card hs-card-primary">
          <div style="font-weight:700;color:#1E293B;margin-bottom:10px">📋 Care Recommendations</div>
          <ul style="margin:0;padding-left:18px">{steps_html}</ul>
        </div>
        """, unsafe_allow_html=True)

        if urg == "High":
            st.markdown("""
            <div style="background:#FEE2E2;border:1.5px solid #FCA5A5;border-radius:10px;
                        padding:14px 16px">
              <b style="color:#DC2626">🚨 High-Urgency Detected</b><br>
              <span style="color:#7F1D1D;font-size:.88rem">
                Please visit a dermatologist or district hospital as soon as possible.
              </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hs-card" style="text-align:center;padding:60px 20px">
          <div style="font-size:3rem;margin-bottom:12px">🔬</div>
          <div style="color:#64748B">
            Upload or capture a skin image, then click<br><b>Run AI Analysis</b>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Model info ────────────────────────────────────────────────────────────────
with st.expander("ℹ️ About the Skin AI Model"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Architecture:** MobileNetV3-Large")
        st.markdown("**Classes:** 19 skin condition categories")
        st.markdown("**Inference:** Runs fully offline (CPU/GPU)")
    with c2:
        st.markdown("**Input size:** 224 × 224 px")
        st.markdown("**Normalisation:** ImageNet standard")
        st.markdown("**Training dataset:** Curated dermoscopy images")
    st.caption("⚠️ Preliminary screening only — not a substitute for professional diagnosis.")
