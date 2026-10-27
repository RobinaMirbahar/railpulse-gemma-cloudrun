"""Production Streamlit Dashboard for RailPulse AI.
Pixel-faithful architecture inspired by the iconic layout and design of Patri (patri.hataf.dev).
Powered by Open-Weights Gemma, Google ADK Function Calling, Deterministic Railway Interlocks, and Google Cloud Run.
"""

import json
import pandas as pd
import streamlit as st

from railpulse_agent.agent import run_railpulse_dispatch
from railpulse_agent.tools import CORRIDOR_SIGNALS, LIVE_TRAINS

st.set_page_config(
    page_title="RailPulse · Live Azerbaijan Railways (ADY)",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Exact Patri (patri.hataf.dev) Design System Tokens & CSS
# ---------------------------------------------------------
st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&family=Barlow+Condensed:wght@600;700;800&display=swap');

:root {
    --ground: #eef2ee;
    --surface: #ffffff;
    --ink: #0b1f17;
    --ink-muted: #56665d;
    --line: #d5ddd7;
    --line-soft: #e3e9e5;
    --sabz-700: #01411c;
    --sabz-800: #022c14;
    --sabz-900: #0b1f17;
    --sabz-100: #e3ede6;
    --zard-500: #f2c230;
    --zard-100: #fdf3d2;
    --red-alert: #d93829;
    --red-bg: #fdf0ee;
    --blue-bg: #e8f0fe;
    --blue-text: #1a73e8;
}

html, body, [class*="css"] {
    font-family: 'Barlow', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--ink);
}

.stApp {
    background-color: var(--ground);
}

/* Header Brand Bar matching Patri */
.patri-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    background: var(--surface);
    border-bottom: 2px solid var(--sabz-700);
    border-radius: 12px 12px 0 0;
    margin-bottom: 16px;
}

.brand-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-logo-text {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 32px;
    font-weight: 800;
    letter-spacing: 1.5px;
    color: var(--sabz-700);
    line-height: 1;
}

.brand-script {
    font-size: 20px;
    font-weight: 700;
    color: var(--sabz-700);
    border-left: 2px solid var(--line);
    padding-left: 10px;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 14px;
}

.live-badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-weight: 700;
    color: var(--sabz-700);
    letter-spacing: 0.5px;
}

.live-dot {
    width: 8px;
    height: 8px;
    background: #22c55e;
    border-radius: 50%;
    animation: livePulse 1.6s infinite;
}

@keyframes livePulse {
    0% { transform: scale(0.95); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.5; }
    100% { transform: scale(0.95); opacity: 1; }
}

.lang-switch {
    display: inline-flex;
    border: 1.5px solid var(--sabz-700);
    border-radius: 6px;
    overflow: hidden;
    font-size: 12px;
    font-weight: 700;
}

.lang-opt {
    padding: 4px 10px;
    background: var(--surface);
    color: var(--sabz-700);
}

.lang-active {
    background: var(--sabz-700);
    color: white;
}

/* Section Header */
.list-section-header {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 1px;
    color: var(--ink);
    text-transform: uppercase;
    margin: 16px 0 10px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Train Card Row matching Patri exactly */
.train-card-row {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: transform 0.12s ease, box-shadow 0.12s ease;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}

.train-card-active {
    border: 2px solid var(--sabz-700);
    background: #ffffff;
    box-shadow: 0 4px 14px rgba(1, 65, 28, 0.12);
}

.train-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.train-number-badge {
    background: var(--sabz-900);
    color: var(--zard-500);
    border-radius: 6px;
    padding: 6px 8px;
    min-width: 44px;
    text-align: center;
    line-height: 1.1;
}

.badge-num {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 19px;
    font-weight: 800;
}

.badge-type {
    font-size: 9px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.train-meta {
    display: flex;
    flex-direction: column;
}

.train-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--ink);
    line-height: 1.2;
}

.train-subroute {
    font-size: 13px;
    color: var(--ink-muted);
    font-weight: 500;
    margin-top: 2px;
}

.delay-pill {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.5px;
    padding: 6px 12px;
    border-radius: 6px;
    text-transform: uppercase;
    white-space: nowrap;
}

.delay-pill-red {
    background: var(--red-bg);
    color: var(--red-alert);
}

.delay-pill-blue {
    background: var(--blue-bg);
    color: var(--blue-text);
}

.delay-pill-green {
    background: var(--sabz-100);
    color: var(--sabz-700);
}

/* Timeline component */
.timeline-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 16px 18px 20px 18px;
    margin-bottom: 16px;
}

.timeline-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    padding: 24px 10px 10px 10px;
}

.timeline-track {
    position: absolute;
    top: 36px;
    left: 35px;
    right: 35px;
    height: 5px;
    background: #dbe3dd;
    border-radius: 999px;
    z-index: 1;
}

.timeline-track-fill {
    position: absolute;
    top: 36px;
    left: 35px;
    height: 5px;
    background: var(--sabz-700);
    border-radius: 999px;
    z-index: 2;
}

.station-node {
    position: relative;
    z-index: 3;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    min-width: 80px;
}

.node-dot {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 800;
    margin-bottom: 8px;
    border: 2px solid white;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.node-passed {
    background: var(--sabz-700);
    color: white;
}

.node-current {
    background: var(--zard-500);
    color: var(--sabz-900);
    transform: scale(1.22);
    border: 2px solid var(--sabz-700);
    animation: livePulse 1.8s infinite;
}

.node-upcoming {
    background: #ffffff;
    color: #66736b;
    border: 2px solid var(--line);
}

.node-name {
    font-size: 13px;
    font-weight: 700;
    color: var(--ink);
}

.node-time {
    font-size: 11px;
    color: var(--ink-muted);
    font-weight: 600;
}

/* Dispatch announcement card */
.announcement-card {
    background: var(--zard-100);
    border-left: 5px solid var(--zard-500);
    border-radius: 10px;
    padding: 14px 18px;
    color: var(--sabz-900);
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 14px;
}

.audit-card {
    background: var(--sabz-100);
    border-left: 5px solid var(--sabz-700);
    border-radius: 10px;
    padding: 14px 18px;
    color: var(--sabz-900);
    font-size: 13px;
    margin-bottom: 14px;
}

.audit-card-warn {
    background: var(--red-bg);
    border-left: 5px solid var(--red-alert);
    border-radius: 10px;
    padding: 14px 18px;
    color: #991b1b;
    font-size: 13px;
    margin-bottom: 14px;
}
</style>""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar: Live Corridor Simulator Controls
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ **Live Corridor Simulator**")
    st.caption("Inject live environmental and track occupancy conditions:")

    selected_train = st.selectbox(
        "Select Active ADY Train",
        options=["ADY-104", "ADY-702", "ADY-410"],
        format_func=lambda x: f"{x} — {LIVE_TRAINS[x]['route_name']}",
    )

    corridor_id = LIVE_TRAINS[selected_train]["corridor_id"]
    current_corridor = CORRIDOR_SIGNALS[corridor_id]

    st.markdown("---")
    st.markdown("#### ⚡ **Operating Scenario Presets**")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("🌪️ High Wind (78 km/h)", use_container_width=True):
            st.session_state["wind_slider"] = 78
            st.session_state["block_select"] = "FREE"
            st.session_state["speed_slider"] = 145
    with col_p2:
        if st.button("🚧 Track Blockage", use_container_width=True):
            st.session_state["block_select"] = "OCCUPIED"
            st.session_state["speed_slider"] = 110

    if st.button("☀️ Clear Corridor Nominal", use_container_width=True):
        st.session_state["wind_slider"] = 28
        st.session_state["block_select"] = "FREE"
        st.session_state["speed_slider"] = 120

    st.markdown("---")
    st.markdown("#### 🎚️ **Manual Corridor Controls**")

    default_wind = st.session_state.get("wind_slider", int(current_corridor["wind_speed_kmh"]))
    wind_speed = st.slider(
        "🌬️ Caspian Crosswind Speed (km/h)",
        min_value=10,
        max_value=110,
        value=default_wind,
        step=2,
        help="Deterministic Guardrail clamps train speed to <= 80 km/h when wind > 65 km/h.",
    )

    default_block = st.session_state.get("block_select", current_corridor["primary_block_status"])
    block_status = st.selectbox(
        f"🚦 Primary Block ({current_corridor['primary_block_id']}) Status",
        options=["FREE", "OCCUPIED", "MAINTENANCE"],
        index=["FREE", "OCCUPIED", "MAINTENANCE"].index(default_block),
        help="Deterministic Guardrail prevents entering an OCCUPIED block and reroutes train to passing siding.",
    )

    default_speed = st.session_state.get("speed_slider", 145)
    requested_speed = st.slider(
        "⚡ LLM Requested Target Speed (km/h)",
        min_value=60,
        max_value=180,
        value=default_speed,
        step=5,
    )

# Apply simulation changes to live state
CORRIDOR_SIGNALS[corridor_id]["wind_speed_kmh"] = wind_speed
CORRIDOR_SIGNALS[corridor_id]["primary_block_status"] = block_status

# Execute Gemma + Google ADK Dispatch Agent Pipeline
advisory = run_railpulse_dispatch(
    train_id=selected_train,
    requested_speed_kmh=requested_speed,
)

# ---------------------------------------------------------
# Top Bar: Patri-Authentic Brand Header
# ---------------------------------------------------------
topbar_html = """<div class="patri-header">
<div class="brand-wrap">
<div class="brand-logo-text">RAILPULSE</div>
<div class="brand-script">DƏMİRYOLU · ADY</div>
</div>
<div class="header-right">
<div class="live-badge-pill">
<span class="live-dot"></span>
LIVE DISPATCH
</div>
<div class="lang-switch">
<span class="lang-opt lang-active">EN</span>
<span class="lang-opt">AZ</span>
</div>
</div>
</div>"""
st.markdown(topbar_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# Two-Column Layout: Left Train Cards (Running Now) & Right Map/Details
# ---------------------------------------------------------
col_left, col_right = st.columns([1.05, 1.35])

with col_left:
    st.markdown('<div class="list-section-header">RUNNING NOW · 3 ADY FLEET TRAINS</div>', unsafe_allow_html=True)

    # 1. ADY-104 Card
    card_104_active = "train-card-active" if selected_train == "ADY-104" else ""
    advisory_speed_104 = f"{advisory.approved_speed_kmh} KM/H" if selected_train == "ADY-104" else "95 KM/H"
    card_104 = f"""<div class="train-card-row {card_104_active}">
<div class="train-left">
<div class="train-number-badge">
<div class="badge-num">104</div>
<div class="badge-type">ABS</div>
</div>
<div class="train-meta">
<div class="train-title">Absheron Commuter</div>
<div class="train-subroute">Bilajari Jn → Sumgayit Pass.</div>
</div>
</div>
<div class="delay-pill delay-pill-red">12 MIN LATE</div>
</div>"""
    st.markdown(card_104, unsafe_allow_html=True)

    # 2. ADY-702 Card
    card_702_active = "train-card-active" if selected_train == "ADY-702" else ""
    card_702 = f"""<div class="train-card-row {card_702_active}">
<div class="train-left">
<div class="train-number-badge">
<div class="badge-num">702</div>
<div class="badge-type">EXP</div>
</div>
<div class="train-meta">
<div class="train-title">Baku-Ganja High-Speed</div>
<div class="train-subroute">Yevlakh Jn → Ganja Central</div>
</div>
</div>
<div class="delay-pill delay-pill-red">18 MIN LATE</div>
</div>"""
    st.markdown(card_702, unsafe_allow_html=True)

    # 3. ADY-410 Card
    card_410_active = "train-card-active" if selected_train == "ADY-410" else ""
    card_410 = f"""<div class="train-card-row {card_410_active}">
<div class="train-left">
<div class="train-number-badge">
<div class="badge-num">410</div>
<div class="badge-type">SLK</div>
</div>
<div class="train-meta">
<div class="train-title">Silk Road Express</div>
<div class="train-subroute">Shamkir → Agstafa Border Hub</div>
</div>
</div>
<div class="delay-pill delay-pill-blue">ON TIME</div>
</div>"""
    st.markdown(card_410, unsafe_allow_html=True)

    st.markdown('<div class="list-section-header">🤖 GEMMA AI DISPATCH & GUARDRAIL CO-PILOT</div>', unsafe_allow_html=True)

    is_clamped = advisory.approved_speed_kmh != requested_speed
    is_siding = "SIDING" in advisory.assigned_block_id

    announcement_html = f"""<div class="announcement-card">
<div style="font-weight: 800; font-size: 11px; text-transform: uppercase; color: #854d0e; margin-bottom: 4px;">
📢 Passenger Station Board Announcement (ADY Audio Synthesizer)
</div>
{advisory.passenger_announcement}
</div>"""
    st.markdown(announcement_html, unsafe_allow_html=True)

    audit_class = "audit-card-warn" if (is_clamped or is_siding) else "audit-card"
    audit_icon = "⚠️" if (is_clamped or is_siding) else "🛡️"
    audit_html = f"""<div class="{audit_class}">
<div style="font-weight: 800; font-size: 11px; text-transform: uppercase; margin-bottom: 4px;">
{audit_icon} Deterministic Railway Interlock Audit
</div>
<code>{advisory.guardrail_intervention_summary}</code>
</div>"""
    st.markdown(audit_html, unsafe_allow_html=True)

    with st.expander("🤖 Ordered Google ADK Function Trajectory"):
        for idx, tool_name in enumerate(advisory.tools_invoked, start=1):
            st.markdown(f"**Step {idx}:** `{tool_name}()`")

    with st.expander("📄 Validated Structured JSON (`RailDispatchAdvisory`)"):
        st.code(json.dumps(advisory.model_dump(), indent=2), language="json")

with col_right:
    st.markdown(f'<div class="list-section-header">STATION TIMELINE · {LIVE_TRAINS[selected_train]["route_name"]}</div>', unsafe_allow_html=True)

    JOURNEY_STOPS = {
        "ADY-104": [
            {"name": "Baku Central", "time": "12:20", "status": "passed"},
            {"name": "Keshla Hub", "time": "12:35", "status": "passed"},
            {"name": "Bilajari Jn", "time": "12:50", "status": "current"},
            {"name": "Khirdalan", "time": "13:05", "status": "upcoming"},
            {"name": "Sumgayit Pass.", "time": advisory.updated_eta, "status": "upcoming"},
        ],
        "ADY-702": [
            {"name": "Baku Central", "time": "08:00", "status": "passed"},
            {"name": "Bilajari", "time": "08:35", "status": "passed"},
            {"name": "Kurdamir", "time": "10:45", "status": "passed"},
            {"name": "Yevlakh", "time": "12:15", "status": "current"},
            {"name": "Ganja Central", "time": advisory.updated_eta, "status": "upcoming"},
        ],
        "ADY-410": [
            {"name": "Baku Central", "time": "06:00", "status": "passed"},
            {"name": "Ganja Central", "time": "11:15", "status": "passed"},
            {"name": "Shamkir", "time": "13:00", "status": "current"},
            {"name": "Agstafa Border", "time": "14:45", "status": "upcoming"},
            {"name": "Tbilisi Central", "time": advisory.updated_eta, "status": "upcoming"},
        ],
    }

    stops = JOURNEY_STOPS[selected_train]
    nodes_html = []
    for idx, s in enumerate(stops, start=1):
        dot_class = f"node-{s['status']}"
        icon = "✓" if s["status"] == "passed" else ("🚆" if s["status"] == "current" else str(idx))
        node_str = f'<div class="station-node"><div class="node-dot {dot_class}">{icon}</div><div class="node-name">{s["name"]}</div><div class="node-time">{s["time"]}</div></div>'
        nodes_html.append(node_str)

    progress_pct = 50 if selected_train == "ADY-104" else (70 if selected_train == "ADY-702" else 45)

    timeline_full_html = f'<div class="timeline-card"><div class="timeline-container"><div class="timeline-track"></div><div class="timeline-track-fill" style="width: {progress_pct}%;"></div>' + ''.join(nodes_html) + '</div></div>'
    st.markdown(timeline_full_html, unsafe_allow_html=True)

    st.markdown('<div class="list-section-header">LIVE AZERBAIJAN RAILWAYS (ADY) NETWORK MAP</div>', unsafe_allow_html=True)

    map_rows = []
    for t_id, t_info in LIVE_TRAINS.items():
        map_rows.append(
            {
                "Train ID": t_id,
                "Route": t_info["route_name"],
                "Current Station": t_info["current_station"],
                "Next Station": t_info["next_station"],
                "lat": t_info["latitude"],
                "lon": t_info["longitude"],
                "Speed (km/h)": advisory.approved_speed_kmh if t_id == selected_train else t_info["current_speed_kmh"],
                "Delay (min)": advisory.delay_minutes_remaining if t_id == selected_train else t_info["delay_minutes"],
                "ETA": advisory.updated_eta if t_id == selected_train else t_info["scheduled_eta"],
            }
        )
    df_trains = pd.DataFrame(map_rows)
    st.map(df_trains, latitude="lat", longitude="lon", size=320, zoom=6)
