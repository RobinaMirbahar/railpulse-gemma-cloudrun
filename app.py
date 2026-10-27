"""Interactive Cute & Modern Streamlit Dashboard for RailPulse AI.
Inspired by the clean, friendly, and real-time design of Patri (patri.hataf.dev).
Powered by Open-Weights Gemma, Google ADK Function Calling, Deterministic Guardrails, and Cloud Run.
"""

import json
import pandas as pd
import streamlit as st

from railpulse_agent.agent import run_railpulse_dispatch
from railpulse_agent.tools import CORRIDOR_SIGNALS, LIVE_TRAINS

st.set_page_config(
    page_title="RailPulse AI · Live Rail Tracking (Baku)",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Cute Patri-Inspired Styling & Design System
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&family=Barlow+Condensed:wght@600;700&display=swap');

    :root {
        --ground: #f4f7f4;
        --surface: #ffffff;
        --ink: #0b1f17;
        --ink-muted: #56665d;
        --line: #dbe3dd;
        --sabz-primary: #01411c;
        --sabz-light: #e6efe8;
        --zard-gold: #f2c230;
        --zard-light: #fef7db;
        --red-alert: #d93829;
        --red-light: #fbeae8;
        --blue-tech: #1a73e8;
        --blue-light: #e8f0fe;
    }

    html, body, [class*="css"] {
        font-family: 'Barlow', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--ink);
    }

    /* Main Container background */
    .stApp {
        background-color: var(--ground);
    }

    /* Hero header banner */
    .patri-hero {
        background: linear-gradient(135deg, #01411c 0%, #063118 60%, #022010 100%);
        padding: 24px 28px;
        border-radius: 20px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(1, 65, 28, 0.18);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 16px;
    }

    .patri-hero h1 {
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .patri-hero p {
        color: #cde0d4;
        font-size: 14px;
        margin: 6px 0 0 0;
    }

    .live-badge {
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

    /* Cute cards */
    .patri-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .patri-card:hover {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.07);
    }

    /* Metric pill */
    .metric-pill-box {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
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
        color: var(--sabz-primary);
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

    /* Cute Station Timeline */
    .timeline-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
        padding: 24px 12px 12px 12px;
        margin: 10px 0 24px 0;
    }

    .timeline-track {
        position: absolute;
        top: 36px;
        left: 30px;
        right: 30px;
        height: 4px;
        background: #dbe3dd;
        z-index: 1;
    }

    .timeline-track-fill {
        position: absolute;
        top: 36px;
        left: 30px;
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
        width: 100px;
    }

    .node-dot {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
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
        transform: scale(1.25);
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

    /* Speaker Announcement Box */
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

    /* Interlock alert */
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

    /* Cute locomotive SVG icon */
    .loco-icon {
        display: inline-block;
        vertical-align: middle;
        margin-right: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar: Cute Interactive Simulator Controls
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ **Live Corridor Simulator**")
    st.caption("Adjust weather conditions & rail track block signals in real-time:")

    selected_train = st.selectbox(
        "Select Active ADY Train",
        options=["ADY-104", "ADY-702", "ADY-410"],
        format_func=lambda x: f"{x} — {LIVE_TRAINS[x]['route_name']}",
    )

    corridor_id = LIVE_TRAINS[selected_train]["corridor_id"]
    current_corridor = CORRIDOR_SIGNALS[corridor_id]

    st.markdown("---")
    st.markdown("#### ⚡ **Quick Scenario Presets**")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("🌪️ High Wind (78 km/h)", use_container_width=True):
            st.session_state["wind_slider"] = 78
            st.session_state["block_select"] = "FREE"
            st.session_state["speed_slider"] = 145
    with col_p2:
        if st.button("🚧 Blocked Track", use_container_width=True):
            st.session_state["block_select"] = "OCCUPIED"
            st.session_state["speed_slider"] = 110

    if st.button("☀️ Clear Sky Normal", use_container_width=True):
        st.session_state["wind_slider"] = 28
        st.session_state["block_select"] = "FREE"
        st.session_state["speed_slider"] = 120

    st.markdown("---")
    st.markdown("#### 🎚️ **Manual Parameter Adjustment**")

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
        help="Deterministic Guardrail prevents entering an OCCUPIED block and reroutes train to siding.",
    )

    default_speed = st.session_state.get("speed_slider", 145)
    requested_speed = st.slider(
        "⚡ LLM Requested Target Speed (km/h)",
        min_value=60,
        max_value=180,
        value=default_speed,
        step=5,
    )

# Apply simulation changes to live store
CORRIDOR_SIGNALS[corridor_id]["wind_speed_kmh"] = wind_speed
CORRIDOR_SIGNALS[corridor_id]["primary_block_status"] = block_status

# Execute Gemma + Google ADK Dispatch Agent Pipeline
advisory = run_railpulse_dispatch(
    train_id=selected_train,
    requested_speed_kmh=requested_speed,
)

# ---------------------------------------------------------
# Cute Hero Banner
# ---------------------------------------------------------
st.markdown(
    f"""
    <div class="patri-hero">
        <div>
            <h1>
                <svg class="loco-icon" width="34" height="22" viewBox="0 0 40 22" fill="none">
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
                RailPulse AI · Live Rail Tracking
            </h1>
            <p>Baku & Absheron High-Speed Corridor • Open-Weights Gemma • Google ADK • Cloud Run</p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
            <span class="live-badge">
                <span class="pulse-dot"></span>
                ADY LIVE DISPATCH
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Top Metric Cards (Cute Patri Cards)
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-pill-box">
            <div class="metric-title">Active Train</div>
            <div class="metric-value">{advisory.train_id}</div>
            <span class="metric-tag" style="background: var(--sabz-light); color: var(--sabz-primary);">
                🚆 {LIVE_TRAINS[selected_train]['route_name'].split(' ')[1]}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    is_clamped = advisory.approved_speed_kmh != requested_speed
    speed_tag_bg = "var(--red-light)" if is_clamped else "var(--sabz-light)"
    speed_tag_col = "var(--red-alert)" if is_clamped else "var(--sabz-primary)"
    speed_tag_text = f"↓ Clamped ({advisory.approved_speed_kmh - requested_speed} km/h)" if is_clamped else "✓ Clear"

    st.markdown(
        f"""
        <div class="metric-pill-box">
            <div class="metric-title">Guardrail Speed</div>
            <div class="metric-value">{advisory.approved_speed_kmh} <span style="font-size: 16px;">km/h</span></div>
            <span class="metric-tag" style="background: {speed_tag_bg}; color: {speed_tag_col};">
                {speed_tag_text}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    is_siding = "SIDING" in advisory.assigned_block_id
    block_tag_bg = "var(--zard-light)" if is_siding else "var(--sabz-light)"
    block_tag_col = "#996500" if is_siding else "var(--sabz-primary)"
    block_tag_text = "⚠️ Siding Loop" if is_siding else "✓ Main Line"

    st.markdown(
        f"""
        <div class="metric-pill-box">
            <div class="metric-title">Assigned Block</div>
            <div class="metric-value" style="font-size: 20px; padding-top: 4px;">{advisory.assigned_block_id}</div>
            <span class="metric-tag" style="background: {block_tag_bg}; color: {block_tag_col};">
                {block_tag_text} • Wind {wind_speed} km/h
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    recovered_min = LIVE_TRAINS[selected_train]["delay_minutes"] - advisory.delay_minutes_remaining
    st.markdown(
        f"""
        <div class="metric-pill-box">
            <div class="metric-title">Updated Station ETA</div>
            <div class="metric-value">{advisory.updated_eta}</div>
            <span class="metric-tag" style="background: var(--sabz-light); color: var(--sabz-primary);">
                ⚡ -{recovered_min}m recovered
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# Cute Station Journey Timeline (Signature Patri Feature!)
# ---------------------------------------------------------
st.markdown("### 🚉 **Journey Station Progress**")

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
    nodes_html.append(
        f"""
        <div class="station-node">
            <div class="node-dot {dot_class}">{icon}</div>
            <div class="node-name">{s['name']}</div>
            <div class="node-time">{s['time']}</div>
        </div>
        """
    )

progress_pct = 50 if selected_train == "ADY-104" else (70 if selected_train == "ADY-702" else 45)

st.markdown(
    f"""
    <div class="patri-card" style="padding-top: 10px;">
        <div class="timeline-container">
            <div class="timeline-track"></div>
            <div class="timeline-track-fill" style="width: {progress_pct}%;"></div>
            {''.join(nodes_html)}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Two-Column Layout: Live Map & AI Copilot Guardrails
# ---------------------------------------------------------
col_left, col_right = st.columns([1.25, 1.0])

with col_left:
    st.markdown("### 🗺️ **Live Azerbaijan Railways Corridor Map**")

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
    st.markdown("### 📢 **Passenger Station Broadcast**")
    st.markdown(
        f"""
        <div class="announcement-box">
            <div style="font-weight: 700; font-size: 13px; text-transform: uppercase; color: #7a5800; margin-bottom: 6px;">
                🔊 Station Master Voice Synthesizer
            </div>
            {advisory.passenger_announcement}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🛡️ **Deterministic Safety Interlock Audit**")
    if is_clamped or is_siding:
        audit_class = "interlock-badge-warn"
        audit_icon = "⚠️"
    else:
        audit_class = "interlock-badge-pass"
        audit_icon = "🛡️"

    st.markdown(
        f"""
        <div class="{audit_class}">
            <div style="font-size: 13px; text-transform: uppercase; margin-bottom: 4px;">
                {audit_icon} Physical Interlock Rule Verified
            </div>
            <code>{advisory.guardrail_intervention_summary}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("🤖 Ordered Google ADK Function Trajectory", expanded=True):
        for idx, tool_name in enumerate(advisory.tools_invoked, start=1):
            st.markdown(f"**Step {idx}:** `{tool_name}()`")

    with st.expander("📄 Validated Structured Output Schema (`RailDispatchAdvisory`)"):
        st.code(json.dumps(advisory.model_dump(), indent=2), language="json")
