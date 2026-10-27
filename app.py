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
# Cute, Fresh & Vibrant Transit Theme (Caspian Teal & Pastel Palette)
# ---------------------------------------------------------
st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Barlow+Condensed:wght@600;700&display=swap');

:root {
    --ground: #f8fafc;
    --surface: #ffffff;
    --ink: #0f172a;
    --ink-muted: #64748b;
    --line: #e2e8f0;
    --brand-teal: #0d9488;
    --brand-blue: #0284c7;
    --brand-mint: #10b981;
    --cute-peach: #ffedd5;
    --cute-yellow: #fef08a;
    --cute-pink: #ffe4e6;
    --cute-lavender: #ede9fe;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--ink);
}

.stApp {
    background-color: var(--ground);
}

/* Cute & Vibrant Hero Banner with Caspian Gradient */
.rail-hero {
    background: linear-gradient(135deg, #0284c7 0%, #0d9488 48%, #10b981 100%);
    padding: 26px 32px;
    border-radius: 24px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 12px 30px rgba(13, 148, 136, 0.22);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
    border: 1px solid rgba(255, 255, 255, 0.25);
}

.rail-hero h1 {
    color: #ffffff;
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -0.4px;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.rail-hero p {
    color: #e0f2fe;
    font-size: 14px;
    font-weight: 500;
    margin: 6px 0 0 0;
}

.live-status-pill {
    background: #fef08a;
    color: #854d0e;
    font-weight: 800;
    font-size: 12px;
    padding: 7px 16px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 4px 14px rgba(254, 240, 138, 0.45);
}

.pulse-dot {
    width: 9px;
    height: 9px;
    background: #eab308;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { transform: scale(0.95); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.6; }
    100% { transform: scale(0.95); opacity: 1; }
}

/* Cute Rounded Cards */
.rail-card {
    background: var(--surface);
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
    margin-bottom: 20px;
}

/* Cute Metric Pill Boxes */
.metric-pill-box {
    background: var(--surface);
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
    transition: transform 0.15s ease;
}
.metric-pill-box:hover {
    transform: translateY(-2px);
}

.metric-title {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    color: var(--ink-muted);
    font-weight: 700;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
}

.metric-tag {
    display: inline-block;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 999px;
    margin-top: 6px;
}

/* Cute Station Timeline */
.timeline-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    padding: 26px 16px 14px 16px;
    margin: 8px 0 18px 0;
}

.timeline-track {
    position: absolute;
    top: 38px;
    left: 45px;
    right: 45px;
    height: 6px;
    background: #e2e8f0;
    border-radius: 999px;
    z-index: 1;
}

.timeline-track-fill {
    position: absolute;
    top: 38px;
    left: 45px;
    height: 6px;
    background: linear-gradient(90deg, #0284c7 0%, #10b981 100%);
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
    min-width: 95px;
}

.node-dot {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 8px;
    border: 3px solid white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.12);
}

.node-passed {
    background: #10b981;
    color: white;
}

.node-current {
    background: #facc15;
    color: #713f12;
    transform: scale(1.22);
    border: 3px solid #0d9488;
    animation: pulse 1.8s infinite;
}

.node-upcoming {
    background: #ffffff;
    color: #94a3b8;
    border: 3px solid #cbd5e1;
}

.node-name {
    font-size: 13px;
    font-weight: 700;
    color: #1e293b;
}

.node-time {
    font-size: 11px;
    color: #64748b;
    font-weight: 600;
}

/* Cute Passenger Announcement Card */
.announcement-box {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    border: 1px solid #fde68a;
    border-left: 6px solid #f59e0b;
    padding: 18px 22px;
    border-radius: 16px;
    color: #78350f;
    font-size: 15px;
    line-height: 1.5;
    margin-bottom: 18px;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.08);
}

/* Cute Interlock Badges */
.interlock-badge-pass {
    background: #f0fdf4;
    color: #166534;
    border: 1px solid #bbf7d0;
    border-left: 6px solid #22c55e;
    padding: 16px 20px;
    border-radius: 16px;
    font-weight: 600;
    margin-bottom: 18px;
}
.interlock-badge-warn {
    background: #fff1f2;
    color: #9f1239;
    border: 1px solid #fecdd3;
    border-left: 6px solid #f43f5e;
    padding: 16px 20px;
    border-radius: 16px;
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
        if st.button("🌪️ High Wind (78 km/h)", use_container_width=True):
            st.session_state["wind_slider"] = 78
            st.session_state["block_select"] = "FREE"
            st.session_state["speed_slider"] = 145
    with col_p2:
        if st.button("🚧 Track Blocked", use_container_width=True):
            st.session_state["block_select"] = "OCCUPIED"
            st.session_state["speed_slider"] = 110

    if st.button("☀️ Clear Sky Normal", use_container_width=True):
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
# Cute Caspian Hero Banner
# ---------------------------------------------------------
hero_html = f"""<div class="rail-hero">
<div>
<h1>
<svg class="train-badge-icon" width="34" height="22" viewBox="0 0 40 22" fill="none">
<rect x="2" y="4" width="28" height="12" rx="3" fill="#ffffff"/>
<rect x="30" y="7" width="7" height="9" rx="2" fill="#ffffff"/>
<circle cx="8" cy="18" r="3" fill="#fef08a"/>
<circle cx="18" cy="18" r="3" fill="#fef08a"/>
<circle cx="28" cy="18" r="3" fill="#fef08a"/>
<circle cx="34" cy="18" r="2" fill="#fef08a"/>
<rect x="6" y="7" width="5" height="4" rx="1" fill="#0d9488"/>
<rect x="14" y="7" width="5" height="4" rx="1" fill="#0d9488"/>
<rect x="22" y="7" width="5" height="4" rx="1" fill="#0d9488"/>
<line x1="2" y1="12" x2="30" y2="12" stroke="#fef08a" stroke-width="2"/>
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
# Top Operational Metric Cards (Cute Pastel Badges)
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    train_route_short = LIVE_TRAINS[selected_train]['route_name'].split(' ')[1]
    card1_html = f"""<div class="metric-pill-box">
<div class="metric-title">Active Train</div>
<div class="metric-value" style="color: #0284c7;">{advisory.train_id}</div>
<span class="metric-tag" style="background: #e0f2fe; color: #0369a1;">
🚆 {train_route_short}
</span>
</div>"""
    st.markdown(card1_html, unsafe_allow_html=True)

with col2:
    is_clamped = advisory.approved_speed_kmh != requested_speed
    speed_tag_bg = "#ffe4e6" if is_clamped else "#dcfce7"
    speed_tag_col = "#e11d48" if is_clamped else "#15803d"
    speed_val_col = "#e11d48" if is_clamped else "#10b981"
    speed_tag_text = f"↓ Clamped ({advisory.approved_speed_kmh - requested_speed} km/h)" if is_clamped else "✓ Clear Speed"

    card2_html = f"""<div class="metric-pill-box">
<div class="metric-title">Guardrail-Approved Speed</div>
<div class="metric-value" style="color: {speed_val_col};">{advisory.approved_speed_kmh} <span style="font-size: 16px;">km/h</span></div>
<span class="metric-tag" style="background: {speed_tag_bg}; color: {speed_tag_col};">
{speed_tag_text}
</span>
</div>"""
    st.markdown(card2_html, unsafe_allow_html=True)

with col3:
    is_siding = "SIDING" in advisory.assigned_block_id
    block_tag_bg = "#fef9c3" if is_siding else "#e0f2fe"
    block_tag_col = "#a16207" if is_siding else "#0284c7"
    block_tag_text = "⚠️ Siding Loop" if is_siding else "✓ Main Line"

    card3_html = f"""<div class="metric-pill-box">
<div class="metric-title">Assigned Track Block</div>
<div class="metric-value" style="font-size: 21px; padding-top: 3px; color: #0d9488;">{advisory.assigned_block_id}</div>
<span class="metric-tag" style="background: {block_tag_bg}; color: {block_tag_col};">
{block_tag_text} • Wind {wind_speed} km/h
</span>
</div>"""
    st.markdown(card3_html, unsafe_allow_html=True)

with col4:
    recovered_min = LIVE_TRAINS[selected_train]["delay_minutes"] - advisory.delay_minutes_remaining
    card4_html = f"""<div class="metric-pill-box">
<div class="metric-title">Updated Station ETA</div>
<div class="metric-value" style="color: #7c3aed;">{advisory.updated_eta}</div>
<span class="metric-tag" style="background: #f3e8ff; color: #6d28d9;">
⚡ -{recovered_min}m delay recovered
</span>
</div>"""
    st.markdown(card4_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# Cute Route Station Progression Timeline
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

timeline_full_html = f'<div class="rail-card" style="padding-top: 14px;"><div class="timeline-container"><div class="timeline-track"></div><div class="timeline-track-fill" style="width: {progress_pct}%;"></div>' + ''.join(nodes_html) + '</div></div>'
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
<div style="font-weight: 800; font-size: 13px; text-transform: uppercase; color: #b45309; margin-bottom: 6px;">
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
