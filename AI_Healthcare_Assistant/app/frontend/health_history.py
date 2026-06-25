# Health History — redesigned
import os, sys
import streamlit as st

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

from styles import inject_global_css
inject_global_css()

from app.database.database import get_all_consultations

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hs-hero" style="padding:32px 36px">
  <h1 style="font-size:1.9rem;margin:0 0 8px">📜 Patient Health History</h1>
  <p style="margin:0;opacity:.85">
    All AI consultations from this device — stored locally in SQLite.
    No cloud upload. Full offline privacy.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
try:
    records = get_all_consultations()
except Exception as e:
    st.error(f"Could not read database: {e}")
    records = []

total    = len(records)
critical = sum(1 for r in records if r.get("urgency_level","").upper() == "CRITICAL")
urgent   = sum(1 for r in records if r.get("urgency_level","").upper() == "URGENT")
routine  = sum(1 for r in records if r.get("urgency_level","").upper() == "ROUTINE")

# ── Metrics row ───────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
for col, val, lbl, badge_cls in [
    (m1, total,    "Total Consultations", "badge-blue"),
    (m2, critical, "🔴 Critical",          "badge-red"),
    (m3, urgent,   "🟡 Urgent",            "badge-yellow"),
    (m4, routine,  "🟢 Routine",           "badge-green"),
]:
    with col:
        st.markdown(f"""
        <div class="hs-stat-pill">
          <div class="val" style="color:{'#DC2626' if '🔴' in lbl else '#B45309' if '�' in lbl else '#0EA5E9'}">
            {val}
          </div>
          <div class="lbl">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

if not records:
    st.markdown("""
    <div class="hs-card" style="text-align:center;padding:60px 20px">
      <div style="font-size:3rem;margin-bottom:12px">📋</div>
      <div style="color:#64748B;font-size:.95rem">
        No consultations yet.<br>
        Use <b>Symptom Checker</b> or <b>Voice Assistant</b> to get started.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Filters ───────────────────────────────────────────────────────────────────
st.markdown('<p class="hs-section-title">🔍 Filter Records</p>', unsafe_allow_html=True)

fc1, fc2 = st.columns([2, 1])
with fc1:
    urgency_filter = st.multiselect(
        "Filter by urgency:",
        ["CRITICAL", "URGENT", "ROUTINE"],
        default=["CRITICAL", "URGENT", "ROUTINE"],
        label_visibility="collapsed",
    )
with fc2:
    search_term = st.text_input(
        "Search condition:",
        placeholder="e.g., Influenza, Fever…",
        label_visibility="collapsed",
    )

filtered = [
    r for r in records
    if r.get("urgency_level", "ROUTINE").upper() in urgency_filter
    and (not search_term or search_term.lower() in r.get("ai_predicted_condition", "").lower())
]

st.markdown(
    f'<p class="hs-section-title">📅 Timeline — {len(filtered)} records</p>',
    unsafe_allow_html=True,
)

# ── Timeline entries ──────────────────────────────────────────────────────────
URGENCY_CFG = {
    "CRITICAL": ("#FEE2E2", "#DC2626", "🔴", "badge-red"),
    "URGENT":   ("#FEF9C3", "#B45309", "🟡", "badge-yellow"),
    "ROUTINE":  ("#D1FAE5", "#065F46", "🟢", "badge-green"),
}

for entry in filtered:
    urg = entry.get("urgency_level", "ROUTINE").upper()
    bg, fg, icon, badge_cls = URGENCY_CFG.get(urg, URGENCY_CFG["ROUTINE"])
    condition = entry.get("ai_predicted_condition", "Unknown")
    ts = entry.get("timestamp", "—")
    conf = entry.get("confidence_score") or 0.0
    conf_pct = int(conf * 100)

    expanded = urg == "CRITICAL"
    with st.expander(f"{icon} {ts}  ·  {condition}  ·  {urg}", expanded=expanded):
        d1, d2 = st.columns(2)
        with d1:
            st.markdown(f"""
            <div style="font-size:.9rem">
              <div style="margin-bottom:6px"><b>Condition:</b> {condition}</div>
              <div style="margin-bottom:6px">
                <b>Confidence:</b>
                <div class="conf-bar-wrap" style="margin-top:4px">
                  <div class="conf-bar-fill" style="width:{conf_pct}%;
                    background:{'#EF4444' if urg=='CRITICAL' else '#F59E0B' if urg=='URGENT' else '#10B981'}">
                  </div>
                </div>
                <span style="font-size:.8rem;color:#64748B">{conf_pct}%</span>
              </div>
              <div><b>Urgency:</b>
                <span class="badge {badge_cls}">{icon} {urg}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        with d2:
            syms = entry.get("translated_symptoms") or "—"
            notes = entry.get("input_transcript") or "—"
            st.markdown(f"""
            <div style="font-size:.9rem">
              <div style="margin-bottom:6px"><b>Symptoms:</b> {syms}</div>
              <div><b>Notes:</b> {notes}</div>
            </div>
            """, unsafe_allow_html=True)

        advice = entry.get("medical_advice") or "—"
        st.markdown(f"""
        <div style="background:#F8FAFC;border-radius:8px;padding:10px 14px;
                    margin-top:10px;font-size:.88rem;color:#475569">
          <b>💊 Advice:</b> {advice}
        </div>
        """, unsafe_allow_html=True)
        st.caption("🔒 Stored locally in healthcare.db — no data leaves this device.")
