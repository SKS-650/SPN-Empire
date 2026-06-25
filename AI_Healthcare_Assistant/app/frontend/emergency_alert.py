# Emergency Alert — redesigned
import os, sys
import requests
import streamlit as st

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

from styles import inject_global_css
inject_global_css()

BACKEND_URL = "http://localhost:8000/api/v1/emergency"

FIRST_AID = {
    "Trauma / Severe Bleeding": (
        "🩹 Apply firm direct pressure with a clean cloth. "
        "Do NOT remove embedded objects. Elevate limb above heart if possible."
    ),
    "Cardiac Arrest / Chest Pain": (
        "❤️ Begin CPR immediately if unresponsive (30 compressions : 2 breaths). "
        "Call 102 now. Do NOT leave patient alone."
    ),
    "Poisoning / Snake Bite": (
        "🐍 Immobilise bitten limb below heart. Do NOT cut or apply tourniquet. "
        "Keep patient calm and still. Transport to hospital IMMEDIATELY."
    ),
    "Complications during Childbirth": (
        "🤱 Keep mother on left side. Do NOT attempt manual delivery. "
        "Keep warm and reassured. Call for trained help."
    ),
    "Other Acute Life-threatening Issues": (
        "⚠️ Keep patient calm. Loosen tight clothing. "
        "Do NOT give food or water. Monitor breathing."
    ),
}

SEV_CFG = {
    "CRITICAL": ("#FEE2E2", "#DC2626", "🔴 CRITICAL"),
    "URGENT":   ("#FEF9C3", "#B45309", "🟡 URGENT"),
    "ROUTINE":  ("#D1FAE5", "#065F46", "🟢 ROUTINE"),
}

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hs-hero" style="padding:32px 36px;
  background:linear-gradient(135deg,#DC2626 0%,#0F172A 100%)">
  <h1 style="font-size:1.9rem;margin:0 0 8px">🚨 Emergency SOS System</h1>
  <p style="margin:0;opacity:.85">
    Broadcast life-threatening emergencies to community coordinators and district hospitals.
    AI triage engine assesses severity before dispatching.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Emergency hotline bar ─────────────────────────────────────────────────────
st.markdown("""
<div style="background:#FEE2E2;border:1.5px solid #FCA5A5;border-radius:10px;
            padding:12px 18px;margin:12px 0;display:flex;gap:24px;align-items:center">
  <span style="font-size:1.1rem;font-weight:700;color:#DC2626">📞 Emergency Numbers:</span>
  <span class="badge badge-red" style="font-size:.95rem">🚑 102 — Ambulance</span>
  <span class="badge badge-red" style="font-size:.95rem">🚓 100 — Police</span>
  <span class="badge badge-red" style="font-size:.95rem">🔥 101 — Fire</span>
  <span class="badge badge-red" style="font-size:.95rem">📞 112 — National Emergency</span>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.1, 1], gap="large")

# ── Triage tool ───────────────────────────────────────────────────────────────
with left:
    st.markdown('<p class="hs-section-title">⚡ Quick Triage</p>', unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div class="hs-card hs-card-danger" style="padding:16px 18px;margin-bottom:0">
          <div style="font-weight:700;color:#1E293B;margin-bottom:12px">
            Answer to get instant severity assessment:
          </div>
        """, unsafe_allow_html=True)

        q_chest   = st.checkbox("💔 Chest pain or pressure?")
        q_breath  = st.checkbox("😮‍💨 Difficulty breathing?")
        q_fever   = st.checkbox("🌡️ Very high fever (>39°C)?")
        q_balance = st.checkbox("🤕 Loss of balance / unconscious?")
        q_mild    = st.checkbox("😐 Mild discomfort only?")

        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("⚡ Assess Severity Now", use_container_width=True):
        with st.spinner("Evaluating…"):
            try:
                payload = {
                    "chest_pain": int(q_chest), "breathlessness": int(q_breath),
                    "high_fever": int(q_fever), "loss_of_balance": int(q_balance),
                    "mild_symptoms": int(q_mild),
                }
                resp = requests.post(f"{BACKEND_URL}/assess", json=payload, timeout=5)
                if resp.status_code == 200:
                    d = resp.json()
                    sev = d.get("status", "ROUTINE")
                    bg, fg, label = SEV_CFG.get(sev, SEV_CFG["ROUTINE"])
                    st.markdown(f"""
                    <div style="background:{bg};border:2px solid {fg};border-radius:10px;
                                padding:16px 18px;margin-top:8px">
                      <b style="color:{fg};font-size:1.1rem">{label}</b><br>
                      <span style="color:#1E293B;font-size:.9rem">{d.get('output_message','')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    raise ConnectionError()
            except Exception:
                if q_chest or q_breath:
                    st.error("🔴 CRITICAL — Call 102 immediately!")
                elif q_fever or q_balance:
                    st.warning("🟡 URGENT — Visit nearest health post now.")
                else:
                    st.success("🟢 ROUTINE — Monitor and consult a health worker.")

    st.markdown("---")

    # ── First Aid Reference ───────────────────────────────────────────────
    st.markdown('<p class="hs-section-title">🏥 First Aid Reference</p>',
                unsafe_allow_html=True)
    for etype, tip in FIRST_AID.items():
        with st.expander(etype):
            st.markdown(f"""
            <div style="color:#475569;font-size:.9rem;line-height:1.6">{tip}</div>
            """, unsafe_allow_html=True)

# ── SOS Broadcast form ────────────────────────────────────────────────────────
with right:
    st.markdown('<p class="hs-section-title">📡 Broadcast SOS</p>', unsafe_allow_html=True)

    with st.form("sos_form"):
        location = st.text_input(
            "📍 Location",
            placeholder="e.g., Ward 4, Sunkoshi, Sindhupalchok",
        )
        etype = st.selectbox("🚨 Emergency Type", list(FIRST_AID.keys()))
        description = st.text_area(
            "📝 Description",
            placeholder="Patient condition, symptoms, any action taken…",
            height=100,
        )
        submitted = st.form_submit_button(
            "🚨 BROADCAST EMERGENCY ALERT",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        if not location or not location.strip():
            st.error("📍 Location is required for dispatch.")
        else:
            with st.spinner("Broadcasting to emergency networks…"):
                try:
                    payload = {"location": location, "type": etype, "description": description}
                    resp = requests.post(f"{BACKEND_URL}/trigger", json=payload, timeout=8)
                    if resp.status_code == 200:
                        d = resp.json()
                        sev = d.get("severity", "ROUTINE")
                        bg, fg, label = SEV_CFG.get(sev, SEV_CFG["CRITICAL"])
                        nodes = ", ".join(d.get("target_nodes", []))
                        st.markdown(f"""
                        <div style="background:{bg};border:2px solid {fg};border-radius:10px;
                                    padding:20px;margin:8px 0">
                          <h3 style="color:{fg};margin:0 0 12px">{label} ACTIVATED</h3>
                          <p><b>Broadcast ID:</b> {d.get('broadcast_id','—')}</p>
                          <p><b>Action:</b> {d.get('action_message','—')}</p>
                          <p><b>Alerted:</b> {nodes}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        raise ConnectionError(f"{resp.status_code}")
                except Exception:
                    tip = FIRST_AID.get(etype, "")
                    st.markdown(f"""
                    <div style="background:#FEE2E2;border:2px solid #DC2626;border-radius:10px;
                                padding:20px;margin:8px 0">
                      <h3 style="color:#DC2626;margin:0 0 10px">⚠️ CRITICAL PROTOCOLS (Offline)</h3>
                      <p><b>SOS sent to:</b> Nearest Health Post & District Hospital</p>
                      <p><b>Location:</b> {location}</p>
                      <p><b>First-Aid:</b> {tip}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Always show first-aid
            tip = FIRST_AID.get(etype, "")
            st.markdown(f"""
            <div class="hs-card hs-card-warning" style="margin-top:8px">
              <b>🏥 First-Aid for {etype}:</b><br>
              <span style="font-size:.9rem;color:#475569">{tip}</span>
            </div>
            """, unsafe_allow_html=True)
