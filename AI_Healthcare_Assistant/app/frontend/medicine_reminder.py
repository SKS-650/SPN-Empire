# Medicine Reminder Scheduler — redesigned
import os, sys
import requests
import streamlit as st
from datetime import datetime

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

from styles import inject_global_css
inject_global_css()

API_BASE_URL = "http://localhost:8000/api/v1/reminder"

FREQ_ICONS = {
    "Once daily": "🌅",
    "Twice a day": "🌅🌆",
    "Three times a day": "🌅🌆🌃",
    "Weekly": "📅",
    "As needed (PRN)": "🔔",
}

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hs-hero" style="padding:32px 36px">
  <h1 style="font-size:1.9rem;margin:0 0 8px">⏰ Medicine Reminder Scheduler</h1>
  <p style="margin:0;opacity:.85">
    Schedule and manage medication reminders for rural patients.
    Stored locally — works fully offline.
  </p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1, 1.3], gap="large")

# ── Add reminder form ─────────────────────────────────────────────────────────
with left:
    st.markdown('<p class="hs-section-title">➕ New Reminder</p>', unsafe_allow_html=True)

    with st.form("reminder_form", clear_on_submit=True):
        med_name = st.text_input(
            "💊 Medicine Name",
            placeholder="e.g., Paracetamol, Amoxicillin, ORS",
        ).strip()
        dosage = st.text_input(
            "📊 Dosage",
            placeholder="e.g., 1 Tablet, 5 ml, 2 Drops",
        ).strip()
        frequency = st.selectbox(
            "🔄 Frequency",
            ["Once daily", "Twice a day", "Three times a day", "Weekly", "As needed (PRN)"],
        )
        target_time = st.time_input("🕒 Time", datetime.now().time())
        formatted_time = target_time.strftime("%H:%M")

        submitted = st.form_submit_button("� Save Reminder", use_container_width=True)

        if submitted:
            if not med_name or not dosage:
                st.error("⚠️ Medicine name and dosage are required.")
            else:
                payload = {
                    "medicine_name": med_name,
                    "dosage_metric": dosage,
                    "frequency_interval": frequency,
                    "target_time": formatted_time,
                }
                try:
                    with st.spinner("Saving…"):
                        resp = requests.post(f"{API_BASE_URL}/", json=payload, timeout=8)
                    if resp.status_code in (200, 201):
                        st.success(f"✅ Reminder set for **{med_name}** at {formatted_time}")
                        st.rerun()
                    else:
                        st.error(f"Backend error {resp.status_code}: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend server.")

    # Quick-add common medicines
    st.markdown('<p class="hs-section-title" style="font-size:1rem">⚡ Quick Add</p>',
                unsafe_allow_html=True)
    quick = [("Paracetamol 500mg", "1 Tablet", "Twice a day"),
             ("ORS (Jeevan Jal)",  "1 Sachet", "Three times a day"),
             ("Vitamin C",         "1 Tablet", "Once daily")]
    for qname, qdose, qfreq in quick:
        if st.button(f"+ {qname}", key=f"quick_{qname}", use_container_width=True):
            payload = {"medicine_name": qname, "dosage_metric": qdose,
                       "frequency_interval": qfreq, "target_time": "08:00"}
            try:
                r = requests.post(f"{API_BASE_URL}/", json=payload, timeout=8)
                if r.status_code in (200, 201):
                    st.toast(f"Added {qname}!", icon="✅")
                    st.rerun()
            except Exception:
                st.warning("Backend offline.")

# ── Active reminders ──────────────────────────────────────────────────────────
with right:
    st.markdown('<p class="hs-section-title">📋 Active Schedules</p>', unsafe_allow_html=True)

    try:
        resp = requests.get(f"{API_BASE_URL}/", timeout=8)
        reminders = resp.json() if resp.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        st.markdown("""
        <div class="hs-card hs-card-warning" style="text-align:center;padding:30px">
          <div style="font-size:2rem">⚠️</div>
          <div style="color:#92400E;margin-top:8px">Backend offline — start the server first.</div>
        </div>
        """, unsafe_allow_html=True)
        reminders = []

    if not reminders:
        st.markdown("""
        <div class="hs-card" style="text-align:center;padding:40px">
          <div style="font-size:2.5rem;margin-bottom:10px">💊</div>
          <div style="color:#64748B">No reminders yet. Add one on the left.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Summary bar
        active_count = sum(1 for r in reminders if r.get("is_active"))
        st.markdown(f"""
        <div style="display:flex;gap:12px;margin-bottom:16px">
          <span class="badge badge-green">🟢 {active_count} Active</span>
          <span class="badge badge-blue">💊 {len(reminders)} Total</span>
        </div>
        """, unsafe_allow_html=True)

        for item in reminders:
            freq_icon = FREQ_ICONS.get(item.get("frequency_interval", ""), "�")
            active = item.get("is_active", 1)
            border_color = "#10B981" if active else "#94A3B8"

            c_info, c_del = st.columns([4, 1])
            with c_info:
                st.markdown(f"""
                <div class="hs-card" style="border-left:4px solid {border_color};
                                            padding:14px 18px;margin-bottom:8px">
                  <div style="font-weight:700;font-size:1rem;color:#1E293B">
                    💊 {item['medicine_name']}
                  </div>
                  <div style="display:flex;gap:16px;margin-top:8px;font-size:.88rem;color:#475569">
                    <span>📊 {item['dosage_metric']}</span>
                    <span>{freq_icon} {item['frequency_interval']}</span>
                    <span>⏱️ {item['target_time']}</span>
                  </div>
                  <div style="margin-top:6px;font-size:.78rem;color:#94A3B8">
                    Added: {item.get('created_at','—')}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with c_del:
                st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{item['id']}", help="Delete reminder"):
                    try:
                        dr = requests.delete(f"{API_BASE_URL}/{item['id']}", timeout=8)
                        if dr.status_code == 200:
                            st.toast(f"Removed {item['medicine_name']}", icon="✅")
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {dr.status_code}")
                    except Exception as e:
                        st.error(f"Network error: {e}")
