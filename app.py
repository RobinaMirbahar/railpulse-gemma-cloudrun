"""Production Streamlit Dashboard for RailPulse AI — Azerbaijan Railways (ADY) Live Dispatch Agent.

Powered by Open-Weights Gemma, Google ADK Function Calling, Deterministic Railway Interlocks, and Google Cloud Run.
"""

import json
import pandas as pd
import streamlit as st

from railpulse_agent.agent import run_railpulse_dispatch
from railpulse_agent.tools import CORRIDOR_SIGNALS, LIVE_TRAINS

st.set_page_config(
    page_title="RailPulse AI — Live Rail Tracking & Smart Dispatch Agent (ADY)",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Enterprise Railway Operations Design System
# ---------------------------------------------------------
st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&family=Barlow+Condensed:wght@600;700&display=swap');

:root {
    --ground: #f4f7f4;
    --surface: #ffffff;
    --ink: #0b1f17;
    --ink-muted: #56665d;
    --line: #dbe3dd;
    --rail-primary: #01411c;
    --rail-light: #e6efe8;
    --gold-accent: #f2c230;
    --gold-light: #fef7db;
    --alert-red: #d93829;
    --alert-red-light: #fbeae8;
}

html, body, [class*="css"] {
    font-family: 'Barlow', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--ink);
}

.stApp {
    background-color: var(--ground);
}

.rail-hero {
    background: linear-gradient(135deg, #01411c 0%, #063118 60%, #022010 100%);
    padding: 24px 28px;
    border-radius: 18px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(1, 65, 28, 0.16);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
}

.rail-hero h1 {
    color: #ffffff;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.rail-hero p {
    color: #cde0d4;
    font-size: 14px;
    margin: 6px 0 0 0;
}

.live-status-pill {
    background: #f2c230;
    color: #0b1f17;
    font-weight: 700;
    font-size: 12px;
    padding: 6px 14px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 4px 12px rgba(242, 194, 48, 0.35);
}

.pulse-dot {
    width: 8px;
    height: 8px;
    background: #01411c;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { transform: scale(0.95); opacity: 1; }
    50% { transform: scale(1.35); opacity: 0.5; }
    100% { transform: scale(0.95); opacity: 1; }
}

.rail-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
    margin-bottom: 20px;
}

.metric-pill-box {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.metric-title {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--ink-muted);
    font-weight: 600;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 26px;
    font-weight: 800;
    color: var(--rail-primary);
    line-height: 1.1;
}

.metric-tag {
    display: inline-block;
    font-size: 12px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 6px;
    margin-top: 6px;
}

.timeline-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    padding: 24px 12px 12px 12px;
    margin: 10px 0 20px 0;
}

.timeline-track {
    position: absolute;
    top: 36px;
    left: 40px;
    right: 40px;
    height: 4px;
    background: #dbe3dd;
    z-index: 1;
}

.timeline-track-fill {
    position: absolute;
    top: 36px;
    left: 40px;
    height: 4px;
    background: #01411c;
    z-index: 2;
}

.station-node {
    position: relative;
    z-index: 3;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    min-width: 90px;
}

.node-dot {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: bold;
    margin-bottom: 8px;
    border: 2px solid white;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.node-passed {
    background: #01411c;
    color: white;
}

.node-current {
    background: #f2c230;
    color: #0b1f17;
    transform: scale(1.2);
    border: 2px solid #01411c;
    animation: pulse 1.8s infinite;
}

.node-upcoming {
    background: #ffffff;
    color: #66736b;
    border: 2px solid #d5ddd7;
}

.node-name {
    font-size: 13px;
    font-weight: 700;
    color: var(--ink);
}

.node-time {
    font-size: 11px;
    color: var(--ink-muted);
    font-weight: 500;
}

.announcement-box {
    background: #fdf3d2;
    border-left: 5px solid #f2c230;
    padding: 16px 20px;
    border-radius: 12px;
    color: #0b1f17;
    font-size: 15px;
    line-height: 1.5;
    margin-bottom: 18px;
}

.interlock-badge-pass {
    background: #e3ede6;
    color: #01411c;
    border-left: 5px solid #01411c;
    padding: 14px 18px;
    border-radius: 12px;
    font-weight: 600;
    margin-bottom: 18px;
}

.interlock-badge-warn {
    background: #fbeae8;
    color: #b71c1c;
    border-left: 5px solid #d93829;
    padding: 14px 18px;
    border-radius: 12px;
    font-weight: 600;
    margin-bottom: 18px;
}

.train-badge-icon {
    display: inline-block;
    vertical-align: middle;
    margin-right: 6px;
}
</style>""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar: Live Corridor Simulator
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
        if st.button("🌪️ High Caspian Wind", use_container_width=True):
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
# Primary Dispatch Hero Banner
# ---------------------------------------------------------
hero_html = f"""<div class="rail-hero">
<div>
<h1>
<svg class="train-badge-icon" width="34" height="22" viewBox="0 0 40 22" fill="none">
<rect x="2" y="4" width="28" height="12" rx="3" fill="#ffffff"/>
<rect x="30" y="7" width="7" height="9" rx="2" fill="#ffffff"/>
<circle cx="8" cy="18" r="3" fill="#f2c230"/>
<circle cx="18" cy="18" r="3" fill="#f2c230"/>
<circle cx="28" cy="18" r="3" fill="#f2c230"/>
<circle cx="34" cy="18" r="2" fill="#f2c230"/>
<rect x="6" y="7" width="5" height="4" rx="1" fill="#01411c"/>
<rect x="14" y="7" width="5" height="4" rx="1" fill="#01411c"/>
<rect x="22" y="7" width="5" height="4" rx="1" fill="#01411c"/>
<line x1="2" y1="12" x2="30" y2="12" stroke="#f2c230" stroke-width="2"/>
</svg>
RailPulse AI — Live Rail Tracking & Smart Dispatch Agent
</h1>
<p>Azerbaijan Railways (ADY) High-Speed Corridor • Open-Weights Gemma • Google ADK • Cloud Run</p>
</div>
<div style="display: flex; gap: 10px; align-items: center;">
<span class="live-status-pill">
<span class="pulse-dot"></span>
ADY REAL-TIME DISPATCH
</span>
</div>
</div>"""
st.markdown(hero_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# Top Operational Metric Cards
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    train_route_short = LIVE_TRAINS[selected_train]['route_name'].split(' ')[1]
    card1_html = f"""<div class="metric-pill-box">
<div class="metric-title">Active Train</div>
<div class="metric-value">{advisory.train_id}</div>
<span class="metric-tag" style="background: var(--rail-light); color: var(--rail-primary);">
🚆 {train_route_short}
</span>
</div>"""
    st.markdown(card1_html, unsafe_allow_html=True)

with col2:
    is_clamped = advisory.approved_speed_kmh != requested_speed
    speed_tag_bg = "var(--alert-red-light)" if is_clamped else "var(--rail-light)"
    speed_tag_col = "var(--alert-red)" if is_clamped else "var(--rail-primary)"
    speed_tag_text = f"↓ Clamped ({advisory.approved_speed_kmh - requested_speed} km/h)" if is_clamped else "✓ Clear"

    card2_html = f"""<div class="metric-pill-box">
<div class="metric-title">Guardrail-Approved Speed</div>
<div class="metric-value">{advisory.approved_speed_kmh} <span style="font-size: 16px;">km/h</span></div>
<span class="metric-tag" style="background: {speed_tag_bg}; color: {speed_tag_col};">
{speed_tag_text}
</span>
</div>"""
    st.markdown(card2_html, unsafe_allow_html=True)

with col3:
    is_siding = "SIDING" in advisory.assigned_block_id
    block_tag_bg = "var(--gold-light)" if is_siding else "var(--rail-light)"
    block_tag_col = "#996500" if is_siding else "var(--rail-primary)"
    block_tag_text = "⚠️ Siding Loop" if is_siding else "✓ Main Line"

    card3_html = f"""<div class="metric-pill-box">
<div class="metric-title">Assigned Track Block</div>
<div class="metric-value" style="font-size: 20px; padding-top: 4px;">{advisory.assigned_block_id}</div>
<span class="metric-tag" style="background: {block_tag_bg}; color: {block_tag_col};">
{block_tag_text} • Wind {wind_speed} km/h
</span>
</div>"""
    st.markdown(card3_html, unsafe_allow_html=True)

with col4:
    recovered_min = LIVE_TRAINS[selected_train]["delay_minutes"] - advisory.delay_minutes_remaining
    card4_html = f"""<div class="metric-pill-box">
<div class="metric-title">Updated Station ETA</div>
<div class="metric-value">{advisory.updated_eta}</div>
<span class="metric-tag" style="background: var(--rail-light); color: var(--rail-primary);">
⚡ -{recovered_min}m delay recovered
</span>
</div>"""
    st.markdown(card4_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# Route Station Progression Timeline
# ---------------------------------------------------------
st.markdown("### 🚉 **Corridor Route & Station Progression**")

JOURNEY_STOPS = {
    "ADY-104": [
        {"name": "Baku Central", "time": "12:20", "status": "passed"},
        {"name": "Keshla Hub", "time": "12:35", "status": "passed"},
        {"name": "Bilajari Junction", "time": "12:50", "status": "current"},
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

timeline_full_html = f'<div class="rail-card" style="padding-top: 10px;"><div class="timeline-container"><div class="timeline-track"></div><div class="timeline-track-fill" style="width: {progress_pct}%;"></div>' + ''.join(nodes_html) + '</div></div>'
st.markdown(timeline_full_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# Two-Column Operations Layout
# ---------------------------------------------------------
col_left, col_right = st.columns([1.25, 1.0])

with col_left:
    st.markdown("### 🗺️ **Live Azerbaijan Railways (ADY) Corridor Telemetry**")

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
    st.map(df_trains, latitude="lat", longitude="lon", size=300, zoom=6)

    st.markdown("#### 📋 **Live Fleet Telemetry Table**")
    st.dataframe(
        df_trains.drop(columns=["lat", "lon"]),
        use_container_width=True,
        hide_index=True,
    )

with col_right:
    st.markdown("### 📢 **Passenger Station Board Announcement**")
    announcement_html = f"""<div class="announcement-box">
<div style="font-weight: 700; font-size: 13px; text-transform: uppercase; color: #7a5800; margin-bottom: 6px;">
🔊 Station Master Voice Synthesizer
</div>
{advisory.passenger_announcement}
</div>"""
    st.markdown(announcement_html, unsafe_allow_html=True)

    st.markdown("### 🛡️ **Deterministic Railway Interlock Audit**")
    if is_clamped or is_siding:
        audit_class = "interlock-badge-warn"
        audit_icon = "⚠️"
    else:
        audit_class = "interlock-badge-pass"
        audit_icon = "🛡️"

    audit_html = f"""<div class="{audit_class}">
<div style="font-size: 13px; text-transform: uppercase; margin-bottom: 4px;">
{audit_icon} Physical Interlock Rule Verified
</div>
<code>{advisory.guardrail_intervention_summary}</code>
</div>"""
    st.markdown(audit_html, unsafe_allow_html=True)

    with st.expander("🤖 Ordered Google ADK Function Trajectory", expanded=True):
        for idx, tool_name in enumerate(advisory.tools_invoked, start=1):
            st.markdown(f"**Step {idx}:** `{tool_name}()`")

    with st.expander("📄 Validated Structured JSON Output (`RailDispatchAdvisory`)"):
        st.code(json.dumps(advisory.model_dump(), indent=2), language="json")
