"""Interactive Streamlit Dashboard for RailPulse AI — Open-Source Gemma + Google ADK on Cloud Run."""

import json
import pandas as pd
import streamlit as st

from railpulse_agent.agent import run_railpulse_dispatch
from railpulse_agent.tools import CORRIDOR_SIGNALS, LIVE_TRAINS

st.set_page_config(
    page_title="RailPulse AI — Gemma + ADK Rail Tracker (DevFest Baku 2026)",
    page_icon="🚆",
    layout="wide",
)

st.title("🚆 RailPulse AI — Live Rail Tracking & Smart Dispatch Agent")
st.caption(
    "Powered by **Open-Weights Gemma** • **Google ADK Function Calling** • "
    "**Deterministic Railway Interlock Guardrails** • **Google Cloud Run (Scale-to-Zero)**"
)

# Sidebar: Interactive Disruption & Weather Simulator
st.sidebar.header("🎛️ Live Corridor Simulator")
selected_train = st.sidebar.selectbox(
    "Select Active ADY Train",
    options=["ADY-702", "ADY-104", "ADY-410"],
    format_func=lambda x: f"{x} — {LIVE_TRAINS[x]['route_name']}",
)

corridor_id = LIVE_TRAINS[selected_train]["corridor_id"]
current_corridor = CORRIDOR_SIGNALS[corridor_id]

wind_speed = st.sidebar.slider(
    "🌬️ Caspian Crosswind Speed (km/h)",
    min_value=10,
    max_value=110,
    value=int(current_corridor["wind_speed_kmh"]),
    step=2,
    help="Deterministic Guardrail clamps train speed to <= 80 km/h when wind > 65 km/h.",
)

block_status = st.sidebar.selectbox(
    f"🚦 Primary Block ({current_corridor['primary_block_id']}) Status",
    options=["FREE", "OCCUPIED", "MAINTENANCE"],
    index=["FREE", "OCCUPIED", "MAINTENANCE"].index(current_corridor["primary_block_status"]),
    help="Deterministic Guardrail prevents entering an OCCUPIED block and reroutes to the passing loop siding.",
)

requested_speed = st.sidebar.slider(
    "⚡ LLM Requested Target Speed (km/h)",
    min_value=60,
    max_value=180,
    value=145,
    step=5,
)

# Apply live simulation adjustments
CORRIDOR_SIGNALS[corridor_id]["wind_speed_kmh"] = wind_speed
CORRIDOR_SIGNALS[corridor_id]["primary_block_status"] = block_status

# Execute Gemma + ADK Dispatch Pipeline
advisory = run_railpulse_dispatch(
    train_id=selected_train,
    requested_speed_kmh=requested_speed,
)

# Top KPI Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Train", advisory.train_id, advisory.operational_status)
col2.metric(
    "Guardrail-Approved Speed",
    f"{advisory.approved_speed_kmh} km/h",
    delta=f"{advisory.approved_speed_kmh - requested_speed} km/h vs requested"
    if advisory.approved_speed_kmh != requested_speed
    else "Within limits",
)
col3.metric("Assigned Track Block", advisory.assigned_block_id, f"Wind: {wind_speed} km/h")
col4.metric(
    "Updated Station ETA",
    advisory.updated_eta,
    delta=f"-{LIVE_TRAINS[selected_train]['delay_minutes'] - advisory.delay_minutes_remaining} min delay recovered",
)

st.divider()

# Middle Row: Live Corridor Map + Station Departure Board
left_col, right_col = st.columns([1.25, 1.0])

with left_col:
    st.subheader("🗺️ Live Azerbaijan Railways (ADY) Corridor Telemetry")
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
    st.map(df_trains, latitude="lat", longitude="lon", size=250, zoom=6)
    st.dataframe(
        df_trains.drop(columns=["lat", "lon"]),
        use_container_width=True,
        hide_index=True,
    )

with right_col:
    st.subheader("🛡️ Deterministic Guardrail & Tool-Call Inspector")
    st.info(f"**Passenger Station Board Announcement:**\n\n📢 {advisory.passenger_announcement}")
    st.success(f"**Railway Interlock Audit:**\n\n`{advisory.guardrail_intervention_summary}`")
    st.markdown("**Ordered ADK Function Calling Trajectory:**")
    for idx, tool_name in enumerate(advisory.tools_invoked, start=1):
        st.code(f"{idx}. {tool_name}()", language="python")

    st.markdown("**Validated Structured JSON Output (`RailDispatchAdvisory`):**")
    st.code(json.dumps(advisory.model_dump(), indent=2), language="json")
