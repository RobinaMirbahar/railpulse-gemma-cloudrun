# -*- coding: utf-8 -*-
"""
RailPulse AI — Live Azerbaijan Railways (ADY) Autonomous Dispatch Dashboard
Powered by Gemma, Google ADK (Agent Development Kit), Streamlit, and Google Cloud Run.
Workshop for DevFest Baku 2026.
"""

import json
import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from railpulse_agent.agent import run_railpulse_dispatch
from railpulse_agent.chat import answer_rail_chat_query
from railpulse_agent.tools import CORRIDOR_SIGNALS, LIVE_TRAINS

st.set_page_config(
    page_title="RailPulse AI • Live Dispatcher",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "active_train" not in st.session_state:
    st.session_state["active_train"] = "ADY-104"

if "lang" not in st.session_state:
    st.session_state["lang"] = "EN"

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {
            "role": "assistant",
            "content": "👋 **Hello! I am Gemma Rail Assistant.** Ask me about real-time train departures, airport-to-city transit, live schedules, delays, or Caspian weather conditions!",
        }
    ]

lang = st.session_state["lang"]
selected_train = st.session_state["active_train"]

TRAIN_GPS_INFO = {
    "ADY-104": {
        "lat": 40.4286,
        "lon": 49.8058,
        "coords_label": "40.4286° N, 49.8058° E",
        "current_station": "Bilajari Jn",
        "next_station": "Khirdalan",
        "distance_km": "5.4 km",
        "progress_pct": 55,
    },
    "ADY-702": {
        "lat": 40.6172,
        "lon": 47.1501,
        "coords_label": "40.6172° N, 47.1501° E",
        "current_station": "Yevlakh Jn",
        "next_station": "Ganja Central",
        "distance_km": "67 km",
        "progress_pct": 72,
    },
    "ADY-410": {
        "lat": 40.8297,
        "lon": 46.0178,
        "coords_label": "40.8297° N, 46.0178° E",
        "current_station": "Shamkir Stn",
        "next_station": "Agstafa Border",
        "distance_km": "52 km",
        "progress_pct": 48,
    },
}

# ---------------------------------------------------------
# Custom Styling: Graphical Cockpit, SVG Gauges, Blinking Beacons & Mobile Responsive
# ---------------------------------------------------------
st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --ground: #f1f5f9;
    --surface: #ffffff;
    --ink: #0f172a;
    --ink-muted: #64748b;
    --line: #e2e8f0;
    --caspian-blue: #2563eb;
    --electric-cyan: #06b6d4;
    --baku-amber: #f59e0b;
    --emerald-safe: #10b981;
    --rose-alert: #f43f5e;
    color-scheme: light;
}

html, body, [class*="css"], .stApp, .stMarkdown, h1, h2, h3, h4, h5, h6, p, span, div {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background-color: var(--ground) !important;
    color: var(--ink) !important;
}

h1, h2, h3, h4, h5, h6, .stMarkdown h5 {
    color: #0f172a !important;
}

.section-hdr {
    font-size: 15px;
    font-weight: 800;
    color: #0f172a !important;
    margin: 8px 0 6px 0;
    display: flex;
    align-items: center;
    gap: 6px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

/* Visual Cockpit Hero Banner with Animated SVG Train */
.cockpit-hero {
    background: linear-gradient(125deg, #0f172a 0%, #1e3a8a 55%, #0284c7 100%);
    border-radius: 16px;
    padding: 14px 20px;
    color: #ffffff !important;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 10px;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.16);
    position: relative;
    overflow: hidden;
}

.cockpit-hero * {
    color: #ffffff;
}

.hero-train-svg {
    flex-shrink: 0;
    display: flex;
    align-items: center;
}

@keyframes trainGlideGlow {
    0%, 100% { filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.6)); transform: translateX(0px); }
    50% { filter: drop-shadow(0 0 14px rgba(245, 158, 11, 0.95)); transform: translateX(4px); }
}

.svg-locomotive {
    animation: trainGlideGlow 2.4s infinite ease-in-out;
}

.live-badge-blink {
    background: rgba(245, 158, 11, 0.22);
    border: 1.5px solid #fbbf24;
    color: #fde68a !important;
    font-weight: 800;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 999px;
    animation: badgePulse 1.4s infinite;
}

@keyframes badgePulse {
    0%, 100% { opacity: 1.0; box-shadow: 0 0 0px rgba(245, 158, 11, 0); }
    50% { opacity: 0.78; box-shadow: 0 0 12px rgba(245, 158, 11, 0.7); }
}

/* Graphical Gauge KPI Cards */
.gauge-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 10px;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    min-height: 112px;
}

.gauge-info {
    flex: 1;
    min-width: 0;
}

.gauge-label {
    font-size: 10.5px;
    text-transform: uppercase;
    color: #64748b !important;
    font-weight: 800;
    letter-spacing: 0.4px;
}

.gauge-val {
    font-size: 20px;
    font-weight: 800;
    color: #0f172a !important;
    margin: 2px 0;
    line-height: 1.15;
}

.gauge-sub {
    font-size: 11.5px;
    font-weight: 700;
    margin-top: 3px;
}

@keyframes spinTurbine {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.wind-rotor {
    transform-origin: 28px 28px;
    animation: spinTurbine 1.8s linear infinite;
}

/* Station Timeline with Blinking Active Node */
.timeline-wrapper {
    background: white;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 12px 18px;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.timeline-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    padding: 18px 18px 8px 18px;
    min-width: 420px;
}

.timeline-line {
    position: absolute;
    top: 32px;
    left: 48px;
    right: 48px;
    height: 6px;
    background: #e2e8f0;
    border-radius: 999px;
    z-index: 1;
}

.timeline-fill {
    position: absolute;
    top: 32px;
    left: 48px;
    height: 6px;
    background: linear-gradient(90deg, #2563eb, #06b6d4, #10b981);
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

.node-circle {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 800;
    margin-bottom: 5px;
    border: 2.5px solid white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}

.node-done {
    background: #10b981;
    color: white !important;
}

.node-active {
    background: #f59e0b;
    color: #ffffff !important;
    transform: scale(1.22);
    border: 2.5px solid #0284c7;
    animation: livePulse 1.3s infinite ease-in-out;
    box-shadow: 0 0 16px rgba(245, 158, 11, 0.85);
}

@keyframes livePulse {
    0% { transform: scale(1.12); box-shadow: 0 0 6px rgba(245, 158, 11, 0.45); }
    50% { transform: scale(1.36); box-shadow: 0 0 22px rgba(245, 158, 11, 1.0); }
    100% { transform: scale(1.12); box-shadow: 0 0 6px rgba(245, 158, 11, 0.45); }
}

.node-next {
    background: white;
    color: #64748b !important;
    border: 2px solid #cbd5e1;
}

/* Visual Interlock & Digital LED Board Cards (Concise Text + Rich Graphics) */
.interlock-visual-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.interlock-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 8px;
}

.interlock-tile {
    border-radius: 10px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.led-board-card {
    background: #0f172a;
    border: 1.5px solid #1e293b;
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 12px;
    color: #f8fafc !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
}

.led-board-card * {
    color: #f8fafc;
}

@keyframes eqBar1 { 0%, 100% { height: 6px; } 50% { height: 18px; } }
@keyframes eqBar2 { 0%, 100% { height: 16px; } 50% { height: 5px; } }
@keyframes eqBar3 { 0%, 100% { height: 9px; } 50% { height: 20px; } }

.eq-bars {
    display: inline-flex;
    align-items: flex-end;
    gap: 3px;
    height: 20px;
}
.eq-bar {
    width: 3.5px;
    background: #38bdf8;
    border-radius: 2px;
}
.eq-bar:nth-child(1) { animation: eqBar1 0.8s infinite; }
.eq-bar:nth-child(2) { animation: eqBar2 0.7s infinite; }
.eq-bar:nth-child(3) { animation: eqBar3 0.9s infinite; }
.eq-bar:nth-child(4) { animation: eqBar1 0.6s infinite; }

/* Fleet Visual Speed Bars Card */
.fleet-visual-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 12px 16px;
    margin-top: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 1.2rem !important;
        padding-left: 0.65rem !important;
        padding-right: 0.65rem !important;
    }
    .cockpit-hero {
        flex-direction: column;
        align-items: flex-start;
        padding: 12px 14px;
    }
    .hero-train-svg {
        width: 100%;
        justify-content: center;
    }
    .interlock-grid {
        grid-template-columns: 1fr;
    }
    .timeline-box {
        min-width: 340px;
        padding: 14px 6px 6px 6px;
    }
    .station-node {
        min-width: 62px;
    }
}
</style>""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar: Real-Time Corridor Simulator
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ **Live Corridor Simulator**")
    st.caption(
        "Simulate live weather conditions and track occupancy in real-time:"
        if lang == "EN"
        else ("Hava şəraiti və xətt məşğulluğunu real vaxtda simulyasiya edin:" if lang == "AZ" else "Симуляция погодных условий и занятости путей в реальном времени:")
    )

    selected_train = st.selectbox(
        "Active ADY Train" if lang == "EN" else ("Aktiv ADY Qatarı" if lang == "AZ" else "Активный поезд АЖД"),
        options=["ADY-104", "ADY-702", "ADY-410"],
        index=["ADY-104", "ADY-702", "ADY-410"].index(st.session_state["active_train"]),
        format_func=lambda x: f"{x} — {LIVE_TRAINS[x]['route_name']}",
    )
    st.session_state["active_train"] = selected_train

    corridor_id = LIVE_TRAINS[selected_train]["corridor_id"]
    current_corridor = CORRIDOR_SIGNALS[corridor_id]

    st.markdown("---")
    st.markdown("#### ⚡ **Quick Scenario Presets**" if lang == "EN" else ("#### ⚡ **Ssenari Seçimləri**" if lang == "AZ" else "#### ⚡ **Быстрые сценарии**"))
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("🌪️ High Wind (78 km/h)", use_container_width=True):
            st.session_state["wind_slider"] = 78
            st.session_state["block_select"] = "FREE"
            st.session_state["speed_slider"] = 145
            st.rerun()
    with col_p2:
        if st.button("🚧 Track Blocked", use_container_width=True):
            st.session_state["block_select"] = "OCCUPIED"
            st.session_state["speed_slider"] = 110
            st.rerun()

    if st.button("☀️ Clear Sky Normal", use_container_width=True):
        st.session_state["wind_slider"] = 28
        st.session_state["block_select"] = "FREE"
        st.session_state["speed_slider"] = 120
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🎚️ **Manual Parameter Adjustment**" if lang == "EN" else ("#### 🎚️ **Əl ilə İdarəetmə**" if lang == "AZ" else "#### 🎚️ **Ручные настройки**"))

    default_wind = st.session_state.get("wind_slider", int(current_corridor["wind_speed_kmh"]))
    wind_speed = st.slider(
        "🌬️ Caspian Crosswind Speed (km/h)",
        min_value=10,
        max_value=110,
        value=default_wind,
        step=2,
    )

    default_block = st.session_state.get("block_select", current_corridor["primary_block_status"])
    block_status = st.selectbox(
        f"🚦 Primary Block ({current_corridor['primary_block_id']}) Status",
        options=["FREE", "OCCUPIED", "MAINTENANCE"],
        index=["FREE", "OCCUPIED", "MAINTENANCE"].index(default_block),
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
# Trilingual Localization Dictionary (Concise & Visual-First)
# ---------------------------------------------------------
I18N = {
    "EN": {
        "tagline": "Azerbaijan Railways (ADY) Autonomous Dispatch • Gemma + Google ADK • Cloud Run",
        "running_now": "🚄 SELECT ACTIVE ADY CORRIDOR",
        "kpi_active_train": "Active Corridor",
        "kpi_approved_speed": "Speedometer Gauge",
        "kpi_track_block": "Signal & Wind Sensor",
        "kpi_station_eta": "Arrival & Recovery",
        "timeline_title": f"🚉 LIVE STATION PROGRESSION · {LIVE_TRAINS[selected_train]['route_name']}",
        "announcement_hdr": "LIVE STATION AUDIO BOARD",
        "announcement_body": advisory.passenger_announcement,
        "audit_hdr": "🛡️ SAFETY INTERLOCK TELEMETRY MATRIX",
        "map_hdr": "🗺️ LIVE AZERBAIJAN (ADY) GPS RADAR MAP",
        "chat_title": "💬 GEMMA RAIL ASSISTANT",
        "chat_placeholder": "Ask about airport transit, departure times, schedules, or weather...",
        "telemetry_hdr": "📊 FLEET SPEED & CORRIDOR VISUAL TELEMETRY",
    },
    "AZ": {
        "tagline": "Azərbaycan Dəmir Yolları (ADY) • Gemma + Google ADK • Cloud Run",
        "running_now": "🚄 AKTİV ADY QATARINI SEÇİN",
        "kpi_active_train": "Aktiv Marşrut",
        "kpi_approved_speed": "Sürət Ölçən (Spidometr)",
        "kpi_track_block": "Siqnal və Külək Sensoru",
        "kpi_station_eta": "Çatma Vaxtı (ETA)",
        "timeline_title": f"🚉 CANLI STANSİYA HƏRƏKƏTİ · {LIVE_TRAINS[selected_train]['route_name']}",
        "announcement_hdr": "CANLI STANSİYA SƏSLİ MƏLUMAT LÖVHƏSİ",
        "announcement_body": f"Diqqət! {LIVE_TRAINS[selected_train]['route_name']} ({advisory.train_id}) → {advisory.assigned_block_id} ({advisory.approved_speed_kmh} km/s). ETA: {advisory.updated_eta}.",
        "audit_hdr": "🛡️ TƏHLÜKƏSİZLİK İNTERLOK MATRİSİ",
        "map_hdr": "🗺️ AZƏRBAYCAN DƏMİR YOLLARI (ADY) CANLI GPS XƏRİTƏSİ",
        "chat_title": "💬 GEMMA DƏMİRYOLU KÖMƏKÇİSİ",
        "chat_placeholder": "Hava limanı nəqliyyatı, çıxış vaxtları və ya hava haqqında soruşun...",
        "telemetry_hdr": "📊 QATAR PARKININ VİZUAL TELEMETRİYASI",
    },
    "RU": {
        "tagline": "Азербайджанские Железные Дороги (ADY) • Gemma + Google ADK • Cloud Run",
        "running_now": "🚄 ВЫБЕРИТЕ АКТИВНЫЙ МАРШРУТ АЖД",
        "kpi_active_train": "Активный маршрут",
        "kpi_approved_speed": "Спидометр поезда",
        "kpi_track_block": "Сигнал и датчик ветра",
        "kpi_station_eta": "Прибытие (ETA)",
        "timeline_title": f"🚉 ПРОХОЖДЕНИЕ СТАНЦИЙ · {LIVE_TRAINS[selected_train]['route_name']}",
        "announcement_hdr": "ЦИФРОВОЕ ТАБЛО ВОКЗАЛА",
        "announcement_body": f"Внимание! Поезд {advisory.train_id} направлен на блок {advisory.assigned_block_id} ({advisory.approved_speed_kmh} км/ч). Прибытие: {advisory.updated_eta}.",
        "audit_hdr": "🛡️ МАТРИЦА БЛОКИРОВОК БЕЗОПАСНОСТИ",
        "map_hdr": "🗺️ КАРТА СЕТИ АЖД И GPS РАДАР",
        "chat_title": "💬 GEMMA RAIL ASSISTANT",
        "chat_placeholder": "Спросите о трансфере из аэропорта, расписании или погоде...",
        "telemetry_hdr": "📊 ВИЗУАЛЬНАЯ ТЕЛЕМЕТРИЯ ПАРКА АЖД",
    },
}

t = I18N[lang]

# ---------------------------------------------------------
# Top Graphical Cockpit Banner with Animated SVG Stadler Train & Language Switcher
# ---------------------------------------------------------
col_head_left, col_head_right = st.columns([3.0, 1.1])
with col_head_left:
    st.markdown(
        f"""<div class="cockpit-hero">
<div>
  <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px;">
    <span style="font-size: 22px; font-weight: 800; letter-spacing: -0.4px;">🚄 RailPulse AI</span>
    <span style="background: rgba(56, 189, 248, 0.2); border: 1px solid #38bdf8; color: #7dd3fc !important; font-weight: 800; font-size: 10.5px; padding: 3px 9px; border-radius: 999px;">🇦🇿 ADY MISSION CONTROL</span>
    <span class="live-badge-blink">● LIVE TELEMETRY</span>
  </div>
  <div style="font-size: 12px; color: #cbd5e1 !important; margin-top: 4px;">{t['tagline']}</div>
</div>
<div class="hero-train-svg">
  <svg class="svg-locomotive" width="210" height="48" viewBox="0 0 210 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- Electrified Catenary Wire & Track -->
    <line x1="4" y1="6" x2="206" y2="6" stroke="#38bdf8" stroke-width="1.2" stroke-dasharray="4 3" opacity="0.7"/>
    <line x1="2" y1="43" x2="208" y2="43" stroke="#94a3b8" stroke-width="2.5"/>
    <!-- Pantograph -->
    <path d="M55 15 L63 7 L71 15" stroke="#fbbf24" stroke-width="1.8" fill="none"/>
    <!-- Coach 1 -->
    <rect x="12" y="15" width="66" height="23" rx="4" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
    <rect x="18" y="19" width="12" height="8" rx="1.5" fill="#38bdf8" opacity="0.85"/>
    <rect x="34" y="19" width="12" height="8" rx="1.5" fill="#38bdf8" opacity="0.85"/>
    <rect x="50" y="19" width="12" height="8" rx="1.5" fill="#38bdf8" opacity="0.85"/>
    <line x1="12" y1="31" x2="78" y2="31" stroke="#f59e0b" stroke-width="2.2"/>
    <!-- Aerodynamic Stadler High-Speed Nose -->
    <path d="M82 15 H165 C182 15 194 25 198 35 C199 37 197 38 194 38 H82 V15 Z" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"/>
    <path d="M162 18 H177 C185 20 190 25 192 29 H162 V18 Z" fill="#fef08a"/>
    <rect x="90" y="19" width="14" height="8" rx="1.5" fill="#bae6fd"/>
    <rect x="108" y="19" width="14" height="8" rx="1.5" fill="#bae6fd"/>
    <rect x="126" y="19" width="14" height="8" rx="1.5" fill="#bae6fd"/>
    <rect x="144" y="19" width="12" height="8" rx="1.5" fill="#bae6fd"/>
    <line x1="82" y1="32" x2="195" y2="32" stroke="#fbbf24" stroke-width="2.5"/>
    <!-- Headlight Beam -->
    <polygon points="198,33 210,28 210,39" fill="#fde047" opacity="0.65"/>
    <!-- Wheels -->
    <circle cx="24" cy="40" r="3.2" fill="#e2e8f0"/><circle cx="64" cy="40" r="3.2" fill="#e2e8f0"/>
    <circle cx="98" cy="40" r="3.2" fill="#e2e8f0"/><circle cx="138" cy="40" r="3.2" fill="#e2e8f0"/><circle cx="176" cy="40" r="3.2" fill="#e2e8f0"/>
  </svg>
</div>
</div>""",
        unsafe_allow_html=True,
    )

with col_head_right:
    st.markdown("<div style='font-size: 10.5px; color: #475569; font-weight: 800; margin-bottom: 4px;'>LANGUAGE / DİL / ЯЗЫК:</div>", unsafe_allow_html=True)
    lang_c1, lang_c2, lang_c3 = st.columns(3)
    with lang_c1:
        btn_en_type = "primary" if lang == "EN" else "secondary"
        if st.button("🇬🇧 EN", type=btn_en_type, use_container_width=True, key="hdr_lang_en"):
            st.session_state["lang"] = "EN"
            st.rerun()
    with lang_c2:
        btn_az_type = "primary" if lang == "AZ" else "secondary"
        if st.button("🇦🇿 AZ", type=btn_az_type, use_container_width=True, key="hdr_lang_az"):
            st.session_state["lang"] = "AZ"
            st.rerun()
    with lang_c3:
        btn_ru_type = "primary" if lang == "RU" else "secondary"
        if st.button("🇷🇺 RU", type=btn_ru_type, use_container_width=True, key="hdr_lang_ru"):
            st.session_state["lang"] = "RU"
            st.rerun()

# ---------------------------------------------------------
# Full-Width Section 1: Fleet Corridor Selector
# ---------------------------------------------------------
st.markdown(f'<div class="section-hdr">{t["running_now"]}</div>', unsafe_allow_html=True)
c_train1, c_train2, c_train3 = st.columns(3)
with c_train1:
    s104 = "primary" if selected_train == "ADY-104" else "secondary"
    lbl104 = "🚆 ADY-104 • Baku ⇄ Sumgayit" if lang == "EN" else ("🚆 ADY-104 • Bakı ⇄ Sumqayıt" if lang == "AZ" else "🚆 ADY-104 • Баку ⇄ Сумгаит")
    if st.button(lbl104, type=s104, use_container_width=True, key="train_btn_104"):
        st.session_state["active_train"] = "ADY-104"
        st.rerun()

with c_train2:
    s702 = "primary" if selected_train == "ADY-702" else "secondary"
    lbl702 = "⚡ ADY-702 • Baku ⇄ Ganja Express" if lang == "EN" else ("⚡ ADY-702 • Bakı ⇄ Gəncə Ekspres" if lang == "AZ" else "⚡ ADY-702 • Баку ⇄ Гянджа Экспресс")
    if st.button(lbl702, type=s702, use_container_width=True, key="train_btn_702"):
        st.session_state["active_train"] = "ADY-702"
        st.rerun()

with c_train3:
    s410 = "primary" if selected_train == "ADY-410" else "secondary"
    lbl410 = "🌍 ADY-410 • Baku ⇄ Tbilisi Silk Road" if lang == "EN" else ("🌍 ADY-410 • Bakı ⇄ Tbilisi İpək Yolu" if lang == "AZ" else "🌍 ADY-410 • Баку ⇄ Тбилиси Шелковый путь")
    if st.button(lbl410, type=s410, use_container_width=True, key="train_btn_410"):
        st.session_state["active_train"] = "ADY-410"
        st.rerun()

# ---------------------------------------------------------
# Full-Width Section 2: 4 Graphical SVG Gauge & Signal Cards
# ---------------------------------------------------------
is_clamped = advisory.approved_speed_kmh != requested_speed
is_siding = "SIDING" in advisory.assigned_block_id
gps_meta = TRAIN_GPS_INFO[selected_train]

# Calculate SVG Speedometer arc dashoffset (max 180 km/h -> arc length 110)
speed_ratio = min(max(advisory.approved_speed_kmh / 180.0, 0.05), 1.0)
arc_offset = round(110 * (1.0 - speed_ratio), 1)
gauge_stroke = "#f59e0b" if is_clamped else "#10b981"

# Signal lamp colors (Red / Amber / Green)
sig_red = "#ef4444" if block_status != "FREE" else "#334155"
sig_amber = "#f59e0b" if (is_clamped and block_status == "FREE") else "#334155"
sig_green = "#10b981" if (not is_clamped and block_status == "FREE") else "#334155"

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f"""<div class="gauge-card">
<div class="gauge-info">
  <div class="gauge-label">{t['kpi_active_train']}</div>
  <div style="font-size: 15.5px; font-weight: 800; color: #0f172a; margin: 3px 0;">{selected_train} • {gps_meta['current_station']}</div>
  <div style="width:100%; background:#e2e8f0; height:7px; border-radius:999px; margin: 6px 0; overflow:hidden;">
    <div style="width:{gps_meta['progress_pct']}%; background:linear-gradient(90deg,#2563eb,#06b6d4); height:100%; border-radius:999px;"></div>
  </div>
  <div class="gauge-sub" style="color: #0284c7;">⏭️ {gps_meta['next_station']} ({gps_meta['distance_km']})</div>
</div>
<svg width="54" height="54" viewBox="0 0 54 54" fill="none">
  <circle cx="27" cy="27" r="25" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.5"/>
  <rect x="15" y="13" width="24" height="24" rx="5" fill="#2563eb"/>
  <rect x="19" y="17" width="16" height="8" rx="2" fill="#bae6fd"/>
  <circle cx="21" cy="31" r="2.2" fill="#fde047"/>
  <circle cx="33" cy="31" r="2.2" fill="#fde047"/>
  <path d="M18 41 L22 37 M36 41 L32 37" stroke="#475569" stroke-width="2.2" stroke-linecap="round"/>
</svg>
</div>""",
        unsafe_allow_html=True,
    )

with k2:
    speed_badge_txt = f"Clamped from {requested_speed} km/h" if is_clamped else f"Target {requested_speed} km/h Clear"
    st.markdown(
        f"""<div class="gauge-card">
<div class="gauge-info">
  <div class="gauge-label">{t['kpi_approved_speed']}</div>
  <div class="gauge-val">{advisory.approved_speed_kmh} <span style="font-size: 12px; color: #64748b;">km/h</span></div>
  <div class="gauge-sub" style="color: {gauge_stroke};">{'⚠️ ' + speed_badge_txt if is_clamped else '✓ ' + speed_badge_txt}</div>
</div>
<svg width="76" height="54" viewBox="0 0 76 54">
  <path d="M 8 44 A 30 30 0 0 1 68 44" fill="none" stroke="#e2e8f0" stroke-width="7" stroke-linecap="round"/>
  <path d="M 8 44 A 30 30 0 0 1 68 44" fill="none" stroke="{gauge_stroke}" stroke-width="7" stroke-linecap="round"
        stroke-dasharray="110" stroke-dashoffset="{arc_offset}"/>
  <text x="38" y="42" text-anchor="middle" font-size="11" font-weight="800" fill="#0f172a">{int(speed_ratio*100)}%</text>
</svg>
</div>""",
        unsafe_allow_html=True,
    )

with k3:
    wind_color = "#ea580c" if wind_speed > 65 else "#0284c7"
    st.markdown(
        f"""<div class="gauge-card">
<div class="gauge-info">
  <div class="gauge-label">{t['kpi_track_block']}</div>
  <div style="font-size: 14px; font-weight: 800; color: #0f172a; margin: 3px 0;"><code>{advisory.assigned_block_id}</code></div>
  <div class="gauge-sub" style="color: {wind_color};">🌬️ {wind_speed} km/h Wind • {'Siding' if is_siding else 'Main Line'}</div>
</div>
<div style="display:flex; align-items:center; gap:6px;">
  <!-- 3-Aspect Railway Signal Graphic -->
  <svg width="24" height="54" viewBox="0 0 24 54">
    <rect x="3" y="2" width="18" height="44" rx="9" fill="#0f172a" stroke="#475569" stroke-width="1.5"/>
    <circle cx="12" cy="12" r="4.5" fill="{sig_red}"/>
    <circle cx="12" cy="24" r="4.5" fill="{sig_amber}"/>
    <circle cx="12" cy="36" r="4.5" fill="{sig_green}"/>
  </svg>
  <!-- Spinning Wind Anemometer Graphic -->
  <svg width="46" height="54" viewBox="0 0 56 56">
    <line x1="28" y1="28" x2="28" y2="52" stroke="#64748b" stroke-width="3" stroke-linecap="round"/>
    <g class="wind-rotor">
      <circle cx="28" cy="28" r="4" fill="#0284c7"/>
      <path d="M28 28 L25 8 C28 5 31 5 31 8 Z" fill="{wind_color}"/>
      <path d="M28 28 L46 37 C48 40 45 42 42 40 Z" fill="{wind_color}"/>
      <path d="M28 28 L10 37 C8 40 11 42 14 40 Z" fill="{wind_color}"/>
    </g>
  </svg>
</div>
</div>""",
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        f"""<div class="gauge-card">
<div class="gauge-info">
  <div class="gauge-label">{t['kpi_station_eta']}</div>
  <div class="gauge-val" style="color: #0284c7 !important;">{advisory.updated_eta}</div>
  <div class="gauge-sub" style="color: #10b981;">✓ {advisory.delay_minutes_remaining} min delay left</div>
</div>
<svg width="54" height="54" viewBox="0 0 54 54">
  <circle cx="27" cy="27" r="23" fill="#ecfdf5" stroke="#10b981" stroke-width="2.5" stroke-dasharray="105 35"/>
  <line x1="27" y1="27" x2="27" y2="14" stroke="#0f172a" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="27" y1="27" x2="37" y2="27" stroke="#0284c7" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="27" cy="27" r="3" fill="#10b981"/>
</svg>
</div>""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# Full-Width Section 3: Prominent Station Progression Timeline (with Blinking Active Node)
# ---------------------------------------------------------
st.markdown(f'<div class="section-hdr">{t["timeline_title"]}</div>', unsafe_allow_html=True)

JOURNEY_STOPS = {
    "ADY-104": [
        {"name": "Baku Central" if lang != "RU" else "Баку-Пасс.", "time": "12:20", "status": "passed"},
        {"name": "Keshla Hub" if lang != "RU" else "Кешля", "time": "12:35", "status": "passed"},
        {"name": "Bilajari Jn" if lang != "RU" else "Баладжары", "time": "12:50", "status": "current"},
        {"name": "Khirdalan" if lang != "RU" else "Хырдалан", "time": "13:05", "status": "upcoming"},
        {"name": "Sumgayit Pass." if lang != "RU" else "Сумгаит", "time": advisory.updated_eta, "status": "upcoming"},
    ],
    "ADY-702": [
        {"name": "Baku Central" if lang != "RU" else "Баку-Пасс.", "time": "08:00", "status": "passed"},
        {"name": "Bilajari" if lang != "RU" else "Баладжары", "time": "08:35", "status": "passed"},
        {"name": "Kurdamir" if lang != "RU" else "Кюрдамир", "time": "10:45", "status": "passed"},
        {"name": "Yevlakh" if lang != "RU" else "Евлах", "time": "12:15", "status": "current"},
        {"name": "Ganja Central" if lang != "RU" else "Гянджа", "time": advisory.updated_eta, "status": "upcoming"},
    ],
    "ADY-410": [
        {"name": "Baku Central" if lang != "RU" else "Баку-Пасс.", "time": "06:00", "status": "passed"},
        {"name": "Ganja Central" if lang != "RU" else "Гянджа", "time": "11:15", "status": "passed"},
        {"name": "Shamkir" if lang != "RU" else "Шамкир", "time": "13:00", "status": "current"},
        {"name": "Agstafa Border" if lang != "RU" else "Агстафа", "time": "14:45", "status": "upcoming"},
        {"name": "Tbilisi Central" if lang != "RU" else "Тбилиси", "time": advisory.updated_eta, "status": "upcoming"},
    ],
}

stops = JOURNEY_STOPS[selected_train]
nodes_html = []
for idx, s in enumerate(stops, start=1):
    dot_class = "node-done" if s["status"] == "passed" else ("node-active" if s["status"] == "current" else "node-next")
    icon = "✓" if s["status"] == "passed" else ("🚆" if s["status"] == "current" else str(idx))
    node_str = f'<div class="station-node"><div class="node-circle {dot_class}">{icon}</div><div style="font-size: 12px; font-weight: 700; color: #0f172a;">{s["name"]}</div><div style="font-size: 11px; color: #64748b;">{s["time"]}</div></div>'
    nodes_html.append(node_str)

progress_pct = 50 if selected_train == "ADY-104" else (70 if selected_train == "ADY-702" else 45)

timeline_full_html = f'<div class="timeline-wrapper"><div class="timeline-box"><div class="timeline-line"></div><div class="timeline-fill" style="width: {progress_pct}%;"></div>' + ''.join(nodes_html) + '</div></div>'
st.markdown(timeline_full_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# Two-Column Balanced Visual Grid
# ---------------------------------------------------------
col_left, col_right = st.columns([1.0, 1.0], gap="medium")

with col_left:
    # 1. Digital LED Station Audio Board with Animated Sound Equalizer Bars
    st.markdown(
        f"""<div class="led-board-card">
<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
  <span style="font-size:11px; font-weight:800; color:#38bdf8 !important; letter-spacing:0.6px;">📢 {t['announcement_hdr']}</span>
  <div class="eq-bars"><div class="eq-bar"></div><div class="eq-bar"></div><div class="eq-bar"></div><div class="eq-bar"></div></div>
</div>
<div style="font-size:13px; font-weight:600; color:#f8fafc !important; line-height:1.45;">{t['announcement_body']}</div>
</div>""",
        unsafe_allow_html=True,
    )

    # 2. Graphical 2-Channel Safety Interlock Matrix (Replaces Wall of Text!)
    wind_pct = min(int((wind_speed / 110.0) * 100), 100)
    wind_tile_bg = "#fffbeb" if wind_speed > 65 else "#ecfdf5"
    wind_tile_bdr = "#fde68a" if wind_speed > 65 else "#a7f3d0"
    wind_bar_col = "#f59e0b" if wind_speed > 65 else "#10b981"
    wind_status_lbl = f"CLAMPED → {advisory.approved_speed_kmh} km/h" if is_clamped else "PASS (WITHIN ENVELOPE)"

    blk_tile_bg = "#fffbeb" if is_siding else "#ecfdf5"
    blk_tile_bdr = "#fde68a" if is_siding else "#a7f3d0"
    blk_col = "#f59e0b" if is_siding else "#10b981"
    blk_status_lbl = "REROUTED TO SIDING" if is_siding else "PRIMARY TRACK LOCKED"

    st.markdown(
        f"""<div class="interlock-visual-card">
<div style="font-size:11.5px; font-weight:800; color:#0f172a; text-transform:uppercase;">{t['audit_hdr']}</div>
<div class="interlock-grid">
  <div class="interlock-tile" style="background:{wind_tile_bg}; border:1.5px solid {wind_tile_bdr};">
    <div style="width:100%;">
      <div style="display:flex; justify-content:space-between; font-size:11px; font-weight:800; color:#0f172a;">
        <span>🌬️ WIND INTERLOCK</span><span>{wind_speed} / 65 km/h</span>
      </div>
      <div style="width:100%; background:#e2e8f0; height:7px; border-radius:999px; margin:6px 0; overflow:hidden;">
        <div style="width:{wind_pct}%; background:{wind_bar_col}; height:100%; border-radius:999px;"></div>
      </div>
      <div style="font-size:11px; font-weight:800; color:{'#b45309' if is_clamped else '#047857'};">{wind_status_lbl}</div>
    </div>
  </div>
  <div class="interlock-tile" style="background:{blk_tile_bg}; border:1.5px solid {blk_tile_bdr};">
    <div style="width:100%;">
      <div style="display:flex; justify-content:space-between; font-size:11px; font-weight:800; color:#0f172a;">
        <span>🚦 TRACK INTERLOCK</span><span>{block_status}</span>
      </div>
      <div style="margin:6px 0; display:flex; align-items:center; gap:6px;">
        <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:{blk_col};"></span>
        <code style="font-size:11.5px; font-weight:800; color:#0f172a;">{advisory.assigned_block_id}</code>
      </div>
      <div style="font-size:11px; font-weight:800; color:{'#b45309' if is_siding else '#047857'};">{blk_status_lbl}</div>
    </div>
  </div>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # 3. Interactive Gemma Rail Assistant Chat
    st.markdown(f'<div class="section-hdr">{t["chat_title"]}</div>', unsafe_allow_html=True)

    q_col1, q_col2, q_col3 = st.columns(3)
    user_prompt = None
    with q_col1:
        if st.button("🕒 Sumgayit Next?", use_container_width=True, key="chat_quick_sumgayit"):
            user_prompt = "When is the next train to Sumgayit?"
    with q_col2:
        if st.button("✈️ Airport to Hotel?", use_container_width=True, key="chat_quick_airport"):
            user_prompt = "Is there any train from Heydar Aliyev Airport to Radisson Hotel Baku?"
    with q_col3:
        if st.button("📋 All Departures", use_container_width=True, key="chat_quick_all"):
            user_prompt = "Show all available train departures"

    text_input = st.chat_input(t["chat_placeholder"])
    if text_input:
        user_prompt = text_input

    if user_prompt:
        st.session_state["chat_history"].append({"role": "user", "content": user_prompt})
        response = answer_rail_chat_query(user_prompt, lang=lang, selected_train=selected_train, advisory=advisory)
        st.session_state["chat_history"].append({"role": "assistant", "content": response})

    chat_container = st.container(height=280)
    with chat_container:
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    with st.expander("🤖 Google ADK Tool Trajectory & Structured JSON"):
        st.markdown(" **ADK Tool Execution Order:** " + " ➔ ".join([f"`{fn}()`" for fn in advisory.tools_invoked]))
        st.code(json.dumps(advisory.model_dump(), indent=2), language="json")

with col_right:
    # 1. Section Header
    st.markdown(f'<div class="section-hdr">{t["map_hdr"]}</div>', unsafe_allow_html=True)

    # 2. Interactive Leaflet Map with Blinking Beacons & Smooth Forward Train Glide
    leaflet_map_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; padding: 0; background: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    #map-wrapper {{ position: relative; width: 100%; height: 410px; border-radius: 14px; overflow: hidden; border: 1.5px solid #cbd5e1; }}
    #railmap {{ width: 100%; height: 100%; }}

    .live-gps-hud {{
      position: absolute;
      top: 10px;
      left: 50px;
      right: 10px;
      z-index: 1000;
      background: rgba(15, 23, 42, 0.92);
      color: #f8fafc;
      backdrop-filter: blur(6px);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 11px;
      font-weight: 700;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      border: 1px solid rgba(56, 189, 248, 0.45);
      box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }}
    .blink-dot {{
      display: inline-block;
      width: 8px;
      height: 8px;
      background: #10b981;
      border-radius: 50%;
      margin-right: 5px;
      animation: dotBlink 1s infinite;
    }}
    @keyframes dotBlink {{
      0%, 100% {{ opacity: 1; transform: scale(1); box-shadow: 0 0 8px #10b981; }}
      50% {{ opacity: 0.3; transform: scale(0.8); }}
    }}

    .station-node-icon {{
      background: #ffffff;
      border: 2.5px solid #0284c7;
      border-radius: 50%;
      width: 10px;
      height: 10px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.3);
    }}
    .station-active-icon {{
      background: #f59e0b;
      border: 2.5px solid #ffffff;
      border-radius: 50%;
      width: 14px;
      height: 14px;
      box-shadow: 0 0 14px rgba(245, 158, 11, 0.95);
      animation: stPulse 1.2s infinite ease-in-out;
    }}
    @keyframes stPulse {{
      0%, 100% {{ transform: scale(1.0); box-shadow: 0 0 6px rgba(245, 158, 11, 0.6); }}
      50% {{ transform: scale(1.45); box-shadow: 0 0 18px rgba(245, 158, 11, 1.0); }}
    }}

    .train-pin-wrapper {{
      position: relative;
      width: 20px;
      height: 20px;
    }}
    .train-gps-dot {{
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: #0284c7;
      border: 2.5px solid #ffffff;
      box-shadow: 0 2px 6px rgba(0,0,0,0.45);
      position: absolute;
      top: 3px;
      left: 3px;
      z-index: 5;
    }}
    .train-gps-dot-active {{
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: #f59e0b;
      border: 3px solid #ffffff;
      box-shadow: 0 0 14px rgba(245, 158, 11, 1.0);
      position: absolute;
      top: 2px;
      left: 2px;
      z-index: 10;
    }}
    .ping-circle {{
      position: absolute;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: rgba(37, 99, 235, 0.55);
      top: -8px;
      left: -8px;
      z-index: 1;
      animation: radarRing 1.5s infinite;
    }}
    @keyframes radarRing {{
      0% {{ transform: scale(0.5); opacity: 0.95; }}
      100% {{ transform: scale(2.2); opacity: 0; }}
    }}

    .train-tag {{
      position: absolute;
      bottom: 22px;
      left: 50%;
      transform: translateX(-50%);
      background: #0f172a;
      color: #38bdf8;
      border: 1.5px solid #38bdf8;
      border-radius: 14px;
      padding: 3px 8px;
      font-size: 10.5px;
      font-weight: 800;
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      box-shadow: 0 4px 10px rgba(15, 23, 42, 0.4);
      z-index: 20;
    }}
    .train-tag-active {{
      background: #2563eb;
      color: #ffffff;
      border: 2px solid #ffffff;
      padding: 4px 10px;
      font-size: 11px;
      box-shadow: 0 0 16px rgba(37, 99, 235, 0.9);
      z-index: 30;
    }}

    .map-controls {{
      position: absolute;
      bottom: 10px;
      left: 10px;
      right: 10px;
      z-index: 1000;
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      justify-content: space-between;
      pointer-events: none;
    }}
    .map-btn {{
      pointer-events: auto;
      background: #0f172a;
      color: #ffffff;
      border: 1.5px solid #38bdf8;
      border-radius: 8px;
      padding: 6px 10px;
      font-size: 11px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 3px 10px rgba(0,0,0,0.25);
    }}
    .map-btn:hover {{
      background: #2563eb;
      border-color: #ffffff;
    }}
  </style>
</head>
<body>
  <div id="map-wrapper">
    <div id="railmap"></div>
    <div class="live-gps-hud">
      <div><span class="blink-dot"></span><b>LIVE GPS ({selected_train}):</b> <span>{gps_meta['current_station']} ➔ {gps_meta['next_station']}</span></div>
      <div style="color:#38bdf8;font-family:monospace;" id="hud-coords">{gps_meta['coords_label']}</div>
    </div>
    <div class="map-controls">
      <button class="map-btn" onclick="focusActiveTrain()">🎯 Locate Active Train ({selected_train})</button>
      <button class="map-btn" onclick="resetAzerbaijanBounds()">🇦🇿 Full Azerbaijan Map</button>
    </div>
  </div>

  <script>
    var map = L.map('railmap', {{
      zoomControl: true,
      attributionControl: false,
      minZoom: 6,
      maxZoom: 15
    }});

    L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      maxZoom: 19
    }}).addTo(map);

    var azBounds = [
      [38.4, 44.8],
      [41.9, 50.6]
    ];
    map.fitBounds(azBounds, {{ padding: [14, 14] }});

    var azerbaijanBorder = [
      [38.40, 44.78], [38.75, 45.45], [38.92, 46.02], [38.85, 48.05],
      [38.42, 48.88], [39.15, 49.32], [39.75, 49.38], [40.25, 49.85],
      [40.45, 50.35], [40.75, 49.95], [41.05, 49.25], [41.52, 48.80],
      [41.90, 48.55], [41.92, 46.50], [41.35, 45.15], [41.10, 45.02],
      [40.85, 45.40], [40.35, 45.65], [39.72, 46.05], [39.22, 46.52],
      [38.40, 44.78]
    ];

    L.polygon(azerbaijanBorder, {{
      color: '#0284c7',
      weight: 3,
      opacity: 0.95,
      fillColor: '#0284c7',
      fillOpacity: 0.08,
      dashArray: '5, 5'
    }}).addTo(map);

    var absheronTrack = [
      [40.3798, 49.8488],
      [40.3953, 49.8912],
      [40.4286, 49.8058],
      [40.4503, 49.7547],
      [40.5897, 49.6686]
    ];

    var bakuGanjaTrack = [
      [40.3798, 49.8488],
      [40.4286, 49.8058],
      [40.0167, 49.4000],
      [40.0389, 48.9328],
      [40.3436, 48.1608],
      [40.5194, 47.6542],
      [40.6172, 47.1501],
      [40.6272, 46.7778],
      [40.6828, 46.3606]
    ];

    var silkRoadTrack = [
      [40.6828, 46.3606],
      [40.8297, 46.0178],
      [40.9922, 45.6289],
      [41.1189, 45.4539],
      [41.2056, 45.1861],
      [41.5495, 45.0006],
      [41.7225, 44.7986]
    ];

    var activeTrainId = "{selected_train}";
    var is104Active = activeTrainId === "ADY-104";
    var is702Active = activeTrainId === "ADY-702";
    var is410Active = activeTrainId === "ADY-410";

    L.polyline(absheronTrack, {{
      color: is104Active ? '#2563eb' : '#64748b',
      weight: is104Active ? 5 : 3,
      opacity: is104Active ? 1.0 : 0.65
    }}).addTo(map);

    L.polyline(bakuGanjaTrack, {{
      color: is702Active ? '#2563eb' : '#64748b',
      weight: is702Active ? 5 : 3,
      opacity: is702Active ? 1.0 : 0.65
    }}).addTo(map);

    L.polyline(silkRoadTrack, {{
      color: is410Active ? '#2563eb' : '#64748b',
      weight: is410Active ? 5 : 3,
      opacity: is410Active ? 1.0 : 0.65
    }}).addTo(map);

    var stations = [
      {{ name: "Baku Central (28 May)", lat: 40.3798, lon: 49.8488, isLive: false }},
      {{ name: "Keshla Hub", lat: 40.3953, lon: 49.8912, isLive: false }},
      {{ name: "Bilajari Junction", lat: 40.4286, lon: 49.8058, isLive: is104Active }},
      {{ name: "Khirdalan", lat: 40.4503, lon: 49.7547, isLive: false }},
      {{ name: "Sumgayit Passenger", lat: 40.5897, lon: 49.6686, isLive: false }},
      {{ name: "Kurdamir", lat: 40.3436, lon: 48.1608, isLive: false }},
      {{ name: "Yevlakh Junction", lat: 40.6172, lon: 47.1501, isLive: is702Active }},
      {{ name: "Ganja Central", lat: 40.6828, lon: 46.3606, isLive: false }},
      {{ name: "Shamkir Station", lat: 40.8297, lon: 46.0178, isLive: is410Active }},
      {{ name: "Agstafa Border", lat: 41.1189, lon: 45.4539, isLive: false }}
    ];

    stations.forEach(function(st) {{
      var iconHtml = st.isLive ? '<div class="station-active-icon"></div>' : '<div class="station-node-icon"></div>';
      var stIcon = L.divIcon({{ className: '', html: iconHtml, iconSize: [14, 14], iconAnchor: [7, 7] }});
      L.marker([st.lat, st.lon], {{ icon: stIcon }})
        .addTo(map)
        .bindPopup("<b>🚉 " + st.name + "</b><br><small>Exact GPS: " + st.lat.toFixed(4) + "° N, " + st.lon.toFixed(4) + "° E</small>");
    }});

    var speedVal104 = is104Active ? "{advisory.approved_speed_kmh} km/h" : "80 km/h";
    var speedVal702 = is702Active ? "{advisory.approved_speed_kmh} km/h" : "145 km/h";
    var speedVal410 = is410Active ? "{advisory.approved_speed_kmh} km/h" : "110 km/h";

    function buildTrainIcon(tid, iconEmoji, speedText, isActive) {{
      var html = '<div class="train-pin-wrapper">' +
        (isActive ? '<div class="ping-circle"></div>' : '') +
        '<div class="' + (isActive ? 'train-gps-dot-active' : 'train-gps-dot') + '"></div>' +
        '<div class="train-tag ' + (isActive ? 'train-tag-active' : '') + '">' +
        iconEmoji + ' ' + tid + ' • ' + speedText +
        '</div></div>';
      return L.divIcon({{ className: '', html: html, iconSize: [20, 20], iconAnchor: [10, 10] }});
    }}

    var marker104 = L.marker([40.4286, 49.8058], {{
      icon: buildTrainIcon('ADY-104', '🚆', speedVal104, is104Active),
      zIndexOffset: is104Active ? 1000 : 100
    }}).addTo(map);

    var marker702 = L.marker([40.6172, 47.1501], {{
      icon: buildTrainIcon('ADY-702', '⚡', speedVal702, is702Active),
      zIndexOffset: is702Active ? 1000 : 100
    }}).addTo(map);

    var marker410 = L.marker([40.8297, 46.0178], {{
      icon: buildTrainIcon('ADY-410', '🌍', speedVal410, is410Active),
      zIndexOffset: is410Active ? 1000 : 100
    }}).addTo(map);

    var progress = 0.0;
    var hudCoordsEl = document.getElementById('hud-coords');
    var currentActiveLat = {gps_meta['lat']};
    var currentActiveLon = {gps_meta['lon']};

    function animateTrainsForward() {{
      progress += 0.00075;
      if (progress > 1.0) {{
        progress = 0.0;
      }}

      var lat104 = 40.4286 + (40.5897 - 40.4286) * progress;
      var lon104 = 49.8058 + (49.6686 - 49.8058) * progress;
      marker104.setLatLng([lat104, lon104]);

      var lat702 = 40.6172 + (40.6828 - 40.6172) * progress;
      var lon702 = 47.1501 + (46.3606 - 47.1501) * progress;
      marker702.setLatLng([lat702, lon702]);

      var lat410 = 40.8297 + (41.1189 - 40.8297) * progress;
      var lon410 = 46.0178 + (45.4539 - 46.0178) * progress;
      marker410.setLatLng([lat410, lon410]);

      if (is104Active) {{ currentActiveLat = lat104; currentActiveLon = lon104; }}
      else if (is702Active) {{ currentActiveLat = lat702; currentActiveLon = lon702; }}
      else {{ currentActiveLat = lat410; currentActiveLon = lon410; }}

      if (hudCoordsEl) {{
        hudCoordsEl.textContent = currentActiveLat.toFixed(4) + "° N, " + currentActiveLon.toFixed(4) + "° E";
      }}

      requestAnimationFrame(animateTrainsForward);
    }}

    requestAnimationFrame(animateTrainsForward);

    function focusActiveTrain() {{
      map.flyTo([currentActiveLat, currentActiveLon], 11, {{ duration: 0.8 }});
    }}

    function resetAzerbaijanBounds() {{
      map.flyToBounds(azBounds, {{ padding: [14, 14], duration: 0.8 }});
    }}
  </script>
</body>
</html>"""

    components.html(leaflet_map_html, height=418)

    # 3. Graphical Fleet Speed & Block Telemetry Bars (Replaces Dense Text Table!)
    st.markdown(f'<div class="section-hdr">{t["telemetry_hdr"]}</div>', unsafe_allow_html=True)

    sp104 = advisory.approved_speed_kmh if selected_train == "ADY-104" else 80
    sp702 = advisory.approved_speed_kmh if selected_train == "ADY-702" else 145
    sp410 = advisory.approved_speed_kmh if selected_train == "ADY-410" else 110

    pct104 = min(int((sp104 / 180.0) * 100), 100)
    pct702 = min(int((sp702 / 180.0) * 100), 100)
    pct410 = min(int((sp410 / 180.0) * 100), 100)

    fleet_visual_html = f"""<div class="fleet-visual-card">
<!-- ADY-104 Visual Bar Row -->
<div style="padding: 8px 10px; border-radius: 10px; margin-bottom: 8px; background: {'#eff6ff' if selected_train == 'ADY-104' else '#f8fafc'}; border: 1.5px solid {'#93c5fd' if selected_train == 'ADY-104' else '#e2e8f0'};">
  <div style="display:flex; justify-content:space-between; align-items:center; font-size:12px; font-weight:800; color:#0f172a;">
    <span>🚆 ADY-104 • Baku ➔ Sumgayit <span style="color:#0284c7;font-weight:700;">(📍 Bilajari Jn)</span></span>
    <span><code style="font-size:11px;">{advisory.assigned_block_id if selected_train == 'ADY-104' else 'BLK-SUMGAYIT-A1'}</code> • <b>{sp104} km/h</b> • ETA {advisory.updated_eta if selected_train == 'ADY-104' else '13:23'}</span>
  </div>
  <div style="width:100%; background:#e2e8f0; height:8px; border-radius:999px; margin-top:6px; overflow:hidden;">
    <div style="width:{pct104}%; background:linear-gradient(90deg,#f59e0b,#2563eb); height:100%; border-radius:999px;"></div>
  </div>
</div>

<!-- ADY-702 Visual Bar Row -->
<div style="padding: 8px 10px; border-radius: 10px; margin-bottom: 8px; background: {'#eff6ff' if selected_train == 'ADY-702' else '#f8fafc'}; border: 1.5px solid {'#93c5fd' if selected_train == 'ADY-702' else '#e2e8f0'};">
  <div style="display:flex; justify-content:space-between; align-items:center; font-size:12px; font-weight:800; color:#0f172a;">
    <span>⚡ ADY-702 • Baku ➔ Ganja Express <span style="color:#0284c7;font-weight:700;">(📍 Yevlakh Jn)</span></span>
    <span><code style="font-size:11px;">{advisory.assigned_block_id if selected_train == 'ADY-702' else 'BLK-GANJA-EXPR'}</code> • <b>{sp702} km/h</b> • ETA {advisory.updated_eta if selected_train == 'ADY-702' else '14:30'}</span>
  </div>
  <div style="width:100%; background:#e2e8f0; height:8px; border-radius:999px; margin-top:6px; overflow:hidden;">
    <div style="width:{pct702}%; background:linear-gradient(90deg,#2563eb,#10b981); height:100%; border-radius:999px;"></div>
  </div>
</div>

<!-- ADY-410 Visual Bar Row -->
<div style="padding: 8px 10px; border-radius: 10px; background: {'#eff6ff' if selected_train == 'ADY-410' else '#f8fafc'}; border: 1.5px solid {'#93c5fd' if selected_train == 'ADY-410' else '#e2e8f0'};">
  <div style="display:flex; justify-content:space-between; align-items:center; font-size:12px; font-weight:800; color:#0f172a;">
    <span>🌍 ADY-410 • Baku ➔ Tbilisi Silk Road <span style="color:#0284c7;font-weight:700;">(📍 Shamkir Stn)</span></span>
    <span><code style="font-size:11px;">{advisory.assigned_block_id if selected_train == 'ADY-410' else 'BLK-SILKROAD-04'}</code> • <b>{sp410} km/h</b> • ETA {advisory.updated_eta if selected_train == 'ADY-410' else '16:45'}</span>
  </div>
  <div style="width:100%; background:#e2e8f0; height:8px; border-radius:999px; margin-top:6px; overflow:hidden;">
    <div style="width:{pct410}%; background:linear-gradient(90deg,#06b6d4,#10b981); height:100%; border-radius:999px;"></div>
  </div>
</div>
</div>"""
    st.markdown(fleet_visual_html, unsafe_allow_html=True)
