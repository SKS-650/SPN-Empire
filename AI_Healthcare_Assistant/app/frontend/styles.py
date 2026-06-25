"""
Global CSS theme injected into every Streamlit page.
Import and call inject_global_css() at the top of each page file.
"""
import streamlit as st

THEME_CSS = """
<style>
/* ── Google Fonts ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root variables ──────────────────────────────────────────────────── */
:root {
  --primary:    #0EA5E9;
  --primary-dk: #0284C7;
  --accent:     #10B981;
  --danger:     #EF4444;
  --warn:       #F59E0B;
  --surface:    #F8FAFC;
  --surface2:   #F1F5F9;
  --border:     #E2E8F0;
  --text:       #1E293B;
  --text-muted: #64748B;
  --radius:     14px;
  --shadow:     0 4px 24px rgba(0,0,0,.07);
}

/* ── App shell ───────────────────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #F0F4F8; }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
  border-right: 1px solid #334155;
}
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] a { color: #94A3B8 !important; }
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a[aria-selected="true"] {
  background: rgba(14,165,233,.15) !important;
  border-radius: 8px;
  color: #38BDF8 !important;
}

/* ── Cards ───────────────────────────────────────────────────────────── */
.hs-card {
  background: #fff;
  border-radius: var(--radius);
  padding: 22px 26px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  margin-bottom: 18px;
  transition: transform .2s, box-shadow .2s;
}
.hs-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,.10); }

.hs-card-primary  { border-left: 4px solid var(--primary); }
.hs-card-success  { border-left: 4px solid var(--accent); }
.hs-card-danger   { border-left: 4px solid var(--danger); }
.hs-card-warning  { border-left: 4px solid var(--warn); }

/* ── Hero banner ─────────────────────────────────────────────────────── */
.hs-hero {
  background: linear-gradient(135deg, #0EA5E9 0%, #0F172A 100%);
  border-radius: var(--radius);
  padding: 48px 40px;
  color: #fff;
  margin-bottom: 28px;
  position: relative;
  overflow: hidden;
}
.hs-hero::before {
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Ccircle cx='30' cy='30' r='28'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.hs-hero h1 { font-size: 2.4rem; font-weight: 700; margin: 0 0 10px; }
.hs-hero p  { font-size: 1.1rem; opacity: .85; margin: 0; }

/* ── Stat pills ──────────────────────────────────────────────────────── */
.hs-stat-pill {
  background: #fff;
  border-radius: 12px;
  padding: 18px 20px;
  text-align: center;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}
.hs-stat-pill .val { font-size: 2rem; font-weight: 700; color: var(--primary); }
.hs-stat-pill .lbl { font-size: .82rem; color: var(--text-muted); margin-top: 4px; }

/* ── Section headings ────────────────────────────────────────────────── */
.hs-section-title {
  font-size: 1.25rem; font-weight: 600;
  color: var(--text); margin: 24px 0 12px;
  display: flex; align-items: center; gap: 8px;
}
.hs-section-title::after {
  content: ''; flex: 1; height: 1px;
  background: var(--border);
}

/* ── Badge chips ─────────────────────────────────────────────────────── */
.badge {
  display: inline-block; padding: 2px 10px;
  border-radius: 999px; font-size: .75rem; font-weight: 600;
}
.badge-red    { background: #FEE2E2; color: #DC2626; }
.badge-yellow { background: #FEF9C3; color: #B45309; }
.badge-green  { background: #D1FAE5; color: #065F46; }
.badge-blue   { background: #DBEAFE; color: #1D4ED8; }

/* ── Chat bubbles ────────────────────────────────────────────────────── */
.chat-user {
  background: var(--primary);
  color: #fff;
  border-radius: 18px 18px 4px 18px;
  padding: 12px 16px;
  max-width: 78%;
  margin: 8px 0 8px auto;
  font-size: .93rem;
  box-shadow: 0 2px 8px rgba(14,165,233,.25);
}
.chat-bot {
  background: #fff;
  color: var(--text);
  border-radius: 18px 18px 18px 4px;
  padding: 12px 16px;
  max-width: 85%;
  margin: 8px auto 8px 0;
  font-size: .93rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}
.chat-avatar-bot  { font-size: 1.4rem; margin-right: 8px; }
.chat-avatar-user { font-size: 1.4rem; margin-left: 8px; }

/* ── Streamlit overrides ─────────────────────────────────────────────── */
.stButton > button {
  border-radius: 10px !important;
  font-weight: 600 !important;
  transition: all .2s !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dk) 100%) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 4px 14px rgba(14,165,233,.35) !important;
}
.stButton > button[kind="primary"]:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(14,165,233,.45) !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
  border-radius: 10px !important;
  border: 1.5px solid var(--border) !important;
  background: #fff !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(14,165,233,.15) !important;
}
.stMetric {
  background: #fff;
  border-radius: 12px;
  padding: 14px 18px !important;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}
.stMetric label { color: var(--text-muted) !important; font-size: .82rem !important; }
.stMetric [data-testid="metric-container"] > div:first-child {
  font-size: 1.6rem !important; font-weight: 700 !important; color: var(--primary) !important;
}
div[data-testid="stExpander"] {
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
  background: #fff !important;
  box-shadow: var(--shadow) !important;
}
.stAlert { border-radius: 10px !important; }

/* ── Progress bar ────────────────────────────────────────────────────── */
.conf-bar-wrap { background: #E2E8F0; border-radius: 999px; height: 10px; }
.conf-bar-fill { height: 10px; border-radius: 999px;
  background: linear-gradient(90deg, var(--primary), var(--accent)); }

/* ── Page fade-in animation ──────────────────────────────────────────── */
@keyframes fadeUp { from { opacity:0; transform:translateY(16px); }
                    to   { opacity:1; transform:translateY(0); } }
.main .block-container { animation: fadeUp .35s ease; }

/* ── Scrollbar ───────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
</style>
"""


def inject_global_css():
    st.markdown(THEME_CSS, unsafe_allow_html=True)
