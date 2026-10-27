# -*- coding: utf-8 -*-
"""
RailPulse AI — Live Azerbaijan Railways (ADY) Visual Dispatch & Tracker
Powered by Gemma, Google ADK (Agent Development Kit), Streamlit, and Google Cloud Run.
Workshop for DevFest Baku 2026.
"""

import json
import os
import streamlit as st
import streamlit.components.v1 as components
from railpulse_agent.agent import run_railpulse_dispatch
from railpulse_agent.chat import answer_rail_chat_query
from railpulse_agent.tools import CORRIDOR_SIGNALS, LIVE_TRAINS

st.set_page_config(
    page_title="RailPulse AI • ADY Live Tracker",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_html(raw_html: str) -> None:
    """Render HTML via st.markdown without 4-space markdown code-block escaping."""
    compact = "".join(line.strip() for line in raw_html.splitlines() if line.strip())
    st.markdown(compact, unsafe_allow_html=True)


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
            "content": "👋 **Welcome to Gemma Rail Assistant!** Tap a quick button above or ask about airport transit, train times, or tickets.",
        }
    ]

lang = st.session_state["lang"]
selected_train = st.session_state["active_train"]

TRAIN_VISUAL_META = {
    "ADY-104": {
        "from_code": "BAK",
        "from_city": "Baku Central",
        "to_code": "SUM",
        "to_city": "Sumgayit",
        "dep_time": "12:20",
        "train_type": "Stadler KISS Double-Deck",
        "lat": 40.4286,
        "lon": 49.8058,
        "coords_label": "40.4286° N, 49.8058° E",
        "current_station": "Bilajari Jn",
        "next_station": "Khirdalan",
        "distance_km": "5.4 km",
        "progress_pct": 55,
    },
    "ADY-702": {
        "from_code": "BAK",
        "from_city": "Baku Central",
        "to_code": "GNJ",
        "to_city": "Ganja Express",
        "dep_time": "08:00",
        "train_type": "ADY High-Speed Express",
        "lat": 40.6172,
        "lon": 47.1501,
        "coords_label": "40.6172° N, 47.1501° E",
        "current_station": "Yevlakh Jn",
        "next_station": "Ganja Central",
        "distance_km": "67 km",
        "progress_pct": 72,
    },
    "ADY-410": {
        "from_code": "BAK",
        "from_city": "Baku Central",
        "to_code": "TBS",
        "to_city": "Tbilisi Central",
        "dep_time": "06:00",
        "train_type": "Silk Road Euro-Express",
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
# Sidebar: Clean Visual Simulator Controls
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ **Simulator Controls**")
    selected_train = st.selectbox(
        "Train Line",
        options=["ADY-104", "ADY-702", "ADY-410"],
        index=["ADY-104", "ADY-702", "ADY-410"].index(st.session_state["active_train"]),
        format_func=lambda x: f"{x} • {TRAIN_VISUAL_META[x]['from_city']} ➔ {TRAIN_VISUAL_META[x]['to_city']}",
    )
    st.session_state["active_train"] = selected_train

    corridor_id = LIVE_TRAINS[selected_train]["corridor_id"]
    current_corridor = CORRIDOR_SIGNALS[corridor_id]

    st.markdown("#### ⚡ **1-Tap Weather & Track Presets**")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("🌪️ High Wind", use_container_width=True):
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
    default_wind = st.session_state.get("wind_slider", int(current_corridor["wind_speed_kmh"]))
    wind_speed = st.slider("🌬️ Wind Speed (km/h)", 10, 110, default_wind, 2)

    default_block = st.session_state.get("block_select", current_corridor["primary_block_status"])
    block_status = st.selectbox(
        "🚦 Track Status",
        options=["FREE", "OCCUPIED", "MAINTENANCE"],
        index=["FREE", "OCCUPIED", "MAINTENANCE"].index(default_block),
    )

    default_speed = st.session_state.get("speed_slider", 145)
    requested_speed = st.slider("⚡ Target Speed (km/h)", 60, 180, default_speed, 5)

CORRIDOR_SIGNALS[corridor_id]["wind_speed_kmh"] = wind_speed
CORRIDOR_SIGNALS[corridor_id]["primary_block_status"] = block_status

advisory = run_railpulse_dispatch(
    train_id=selected_train,
    requested_speed_kmh=requested_speed,
)

I18N = {
    "EN": {
        "hero_sub": "Azerbaijan Railways (ADY) • Live High-Speed GPS & AI Safety",
        "running_now": "🚄 SELECT ACTIVE ADY CORRIDOR",
        "kpi_active_train": "ACTIVE CORRIDOR",
        "kpi_approved_speed": "SPEEDOMETER GAUGE",
        "kpi_track_block": "SIGNAL & WIND SENSOR",
        "kpi_station_eta": "ARRIVAL & RECOVERY",
        "status_safe": "ON SCHEDULE",
        "status_wind": "WIND SPEED CAP",
        "status_reroute": "SIDING REROUTE",
        "announcement_hdr": "LIVE STATION AUDIO BOARD",
        "announcement_body": advisory.passenger_announcement,
        "audit_hdr": "🛡️ SAFETY INTERLOCK TELEMETRY MATRIX",
        "chat_hdr": "💬 Gemma Rail Assistant",
        "chat_placeholder": "Ask about airport bus, train times, or tickets...",
    },
    "AZ": {
        "hero_sub": "Azərbaycan Dəmir Yolları (ADY) • Canlı GPS və Süni İntellekt",
        "running_now": "🚄 AKTİV ADY MARŞRUTUNU SEÇİN",
        "kpi_active_train": "AKTİV MARŞRUT",
        "kpi_approved_speed": "SÜRƏT ÖLÇƏN",
        "kpi_track_block": "SİQNAL VƏ KÜLƏK",
        "kpi_station_eta": "ÇATMA VAXTI",
        "status_safe": "CƏDVƏL ÜZRƏ",
        "status_wind": "KÜLƏK LİMİTİ",
        "status_reroute": "EHTİYAT XƏTT",
        "announcement_hdr": "CANLI STANSİYA SƏSLİ LÖVHƏSİ",
        "announcement_body": f"Diqqət! {LIVE_TRAINS[selected_train]['route_name']} ({advisory.train_id}) → {advisory.assigned_block_id} ({advisory.approved_speed_kmh} km/s). ETA: {advisory.updated_eta}.",
        "audit_hdr": "🛡️ TƏHLÜKƏSİZLİK İNTERLOK MATRİSİ",
        "chat_hdr": "💬 Gemma Dəmiryolu Köməkçisi",
        "chat_placeholder": "Hava limanı, qatar vaxtları və ya biletlər...",
    },
    "RU": {
        "hero_sub": "Азербайджанские ЖД (ADY) • Онлайн GPS-трекер и ИИ",
        "running_now": "🚄 ВЫБЕРИТЕ МАРШРУТ АЖД",
        "kpi_active_train": "МАРШРУТ",
        "kpi_approved_speed": "СПИДОМЕТР",
        "kpi_track_block": "СИГНАЛ И ВЕТЕР",
        "kpi_station_eta": "ПРИБЫТИЕ",
        "status_safe": "ПО РАСПИСАНИЮ",
        "status_wind": "ЛИМИТ ВЕТРА",
        "status_reroute": "БОКОВОЙ ПУТЬ",
        "announcement_hdr": "ЦИФРОВОЕ ТАБЛО ВОКЗАЛА",
        "announcement_body": f"Внимание! Поезд {advisory.train_id} направлен на блок {advisory.assigned_block_id} ({advisory.approved_speed_kmh} км/ч). Прибытие: {advisory.updated_eta}.",
        "audit_hdr": "🛡️ МАТРИЦА БЛОКИРОВОК БЕЗОПАСНОСТИ",
        "chat_hdr": "💬 Gemma Rail Assistant",
        "chat_placeholder": "Спросите об аэропорте, расписании или билетах...",
    },
}

t = I18N[lang]
meta = TRAIN_VISUAL_META[selected_train]
is_clamped = advisory.approved_speed_kmh != requested_speed
is_siding = "SIDING" in advisory.assigned_block_id

# ---------------------------------------------------------
# Visual Styling (4 SVG Gauge Cards + Clean Boarding Pass + No Code-Block Escaping)
# ---------------------------------------------------------
render_html(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
:root { color-scheme: light; }
html, body, [class*="css"], .stApp, .stMarkdown, h1, h2, h3, h4, h5, h6, p, span, div {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}
.stApp { background-color: #f1f5f9 !important; color: #0f172a !important; }
.block-container { padding-top: 2.9rem !important; padding-bottom: 1.5rem !important; }
div[data-testid="stButton"] > button { white-space: nowrap !important; padding-left: 8px !important; padding-right: 8px !important; }
.section-hdr {
    font-size: 13.5px;
    font-weight: 800;
    color: #0f172a !important;
    margin: 6px 0 6px 0;
    letter-spacing: 0.4px;
}
.rail-hero {
    background: linear-gradient(135deg, #090d16 0%, #0f2942 50%, #0284c7 100%);
    border-radius: 18px;
    padding: 15px 22px;
    color: #ffffff !important;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 10px;
    box-shadow: 0 10px 25px rgba(2, 132, 199, 0.18);
    overflow: hidden;
}
.rail-hero * { color: #ffffff; }
@keyframes bulletGlide {
    0%, 100% { filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.7)); }
    50% { filter: drop-shadow(0 0 14px rgba(250, 204, 21, 0.95)); }
}
.bullet-svg { animation: bulletGlide 2.2s infinite ease-in-out; flex-shrink: 0; }
.gauge-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 16px;
    padding: 14px 16px;
    margin-top: 4px;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    height: 134px;
}
.gauge-info { flex: 1; min-width: 0; }
.gauge-label {
    font-size: 10px;
    text-transform: uppercase;
    color: #64748b !important;
    font-weight: 800;
    letter-spacing: 0.3px;
    white-space: nowrap;
}
.gauge-val {
    font-size: 22px;
    font-weight: 800;
    color: #0f172a !important;
    margin: 3px 0;
    line-height: 1.15;
}
.gauge-sub { font-size: 11.5px; font-weight: 700; margin-top: 3px; }
@keyframes spinTurbine { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.wind-rotor { transform-origin: 28px 28px; animation: spinTurbine 1.6s linear infinite; }
.boarding-pass {
    background: #ffffff;
    border-radius: 18px;
    border: 1.5px solid #e2e8f0;
    padding: 14px 22px;
    margin-bottom: 14px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
}
.pass-route-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}
.city-code { font-size: 26px; font-weight: 800; color: #0f172a !important; letter-spacing: -1px; line-height: 1.0; }
.city-name { font-size: 12px; font-weight: 700; color: #64748b !important; margin-top: 2px; }
.city-time { font-size: 13.5px; font-weight: 800; color: #0284c7 !important; margin-top: 2px; }
.visual-track-center { flex: 1; padding: 0 12px; overflow-x: auto; }
.timeline-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    padding: 16px 14px 4px 14px;
    min-width: 300px;
}
.timeline-line {
    position: absolute;
    top: 30px;
    left: 36px;
    right: 36px;
    height: 6px;
    background: #e2e8f0;
    border-radius: 999px;
    z-index: 1;
}
.timeline-fill {
    position: absolute;
    top: 30px;
    left: 36px;
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
    min-width: 58px;
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
    margin-bottom: 4px;
    border: 2.5px solid white;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
}
.node-done { background: #10b981; color: white !important; }
.node-active {
    background: #f59e0b;
    color: #ffffff !important;
    transform: scale(1.25);
    border: 2.5px solid #0284c7;
    animation: livePulse 1.3s infinite ease-in-out;
    box-shadow: 0 0 16px rgba(245, 158, 11, 0.9);
}
@keyframes livePulse {
    0%, 100% { transform: scale(1.12); box-shadow: 0 0 6px rgba(245, 158, 11, 0.45); }
    50% { transform: scale(1.38); box-shadow: 0 0 22px rgba(245, 158, 11, 1.0); }
}
.node-next { background: white; color: #94a3b8 !important; border: 2px solid #cbd5e1; }
.interlock-visual-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.interlock-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px; }
.interlock-tile { border-radius: 10px; padding: 10px 12px; display: flex; align-items: center; gap: 10px; }
.led-board-card {
    background: #0f172a;
    border: 1.5px solid #1e293b;
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 12px;
    color: #f8fafc !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
}
.led-board-card * { color: #f8fafc; }
@keyframes eqBar1 { 0%, 100% { height: 5px; } 50% { height: 16px; } }
@keyframes eqBar2 { 0%, 100% { height: 15px; } 50% { height: 5px; } }
.eq-bars { display: inline-flex; align-items: flex-end; gap: 2.5px; height: 16px; flex-shrink: 0; }
.eq-bar { width: 3px; background: #38bdf8; border-radius: 2px; }
.eq-bar:nth-child(1) { animation: eqBar1 0.7s infinite; }
.eq-bar:nth-child(2) { animation: eqBar2 0.6s infinite; }
.eq-bar:nth-child(3) { animation: eqBar1 0.8s infinite; }
.ticket-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px; }
.mini-ticket { background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 10px 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.03); }
.mini-ticket-active { background: #eff6ff; border: 2px solid #2563eb; }
@media (max-width: 768px) {
    .rail-hero { flex-direction: column; align-items: flex-start; padding: 14px; }
    .gauge-card { height: auto; min-height: 116px; }
    .pass-route-row { flex-direction: column; align-items: stretch; gap: 10px; }
    .interlock-grid { grid-template-columns: 1fr; }
    .ticket-strip { grid-template-columns: 1fr; }
}
</style>"""
)

# ---------------------------------------------------------
# 1. Top Visual Hero + Wide Language Buttons (Never Truncated)
# ---------------------------------------------------------
c_top_l, c_top_r = st.columns([2.5, 1.5])
with c_top_l:
    render_html(
        f"""<div class="rail-hero">
<div>
  <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
    <span style="font-size:24px; font-weight:800; letter-spacing:-0.5px;">🚄 RailPulse AI</span>
    <span style="background:#10b981; color:#ffffff !important; font-size:10.5px; font-weight:800; padding:3px 10px; border-radius:999px;">● LIVE ADY TRACKER</span>
  </div>
  <div style="font-size:12.5px; color:#bae6fd !important; margin-top:4px;">{t['hero_sub']}</div>
</div>
<svg class="bullet-svg" width="215" height="48" viewBox="0 0 240 52" fill="none">
  <path d="M18 38 C22 20 26 20 28 38" stroke="#38bdf8" stroke-width="1.5" opacity="0.45" fill="none"/>
  <path d="M32 38 C36 16 40 16 42 38" stroke="#38bdf8" stroke-width="1.5" opacity="0.45" fill="none"/>
  <line x1="2" y1="45" x2="238" y2="45" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M25 18 H172 C198 18 216 28 224 38 C226 40 223 41 219 41 H25 V18 Z" fill="#ffffff"/>
  <path d="M25 32 H218 L223 38 H25 V32 Z" fill="#2563eb"/>
  <path d="M25 30 H214" stroke="#f59e0b" stroke-width="2.5"/>
  <path d="M174 21 H194 C204 23 211 28 214 31 H174 V21 Z" fill="#0f172a"/>
  <rect x="38" y="22" width="16" height="6" rx="2" fill="#0284c7"/>
  <rect x="60" y="22" width="16" height="6" rx="2" fill="#0284c7"/>
  <rect x="82" y="22" width="16" height="6" rx="2" fill="#0284c7"/>
  <rect x="104" y="22" width="16" height="6" rx="2" fill="#0284c7"/>
  <rect x="126" y="22" width="16" height="6" rx="2" fill="#0284c7"/>
  <rect x="148" y="22" width="16" height="6" rx="2" fill="#0284c7"/>
  <polygon points="224,36 240,30 240,42" fill="#fef08a" opacity="0.75"/>
</svg>
</div>"""
    )

with c_top_r:
    render_html("<div style='font-size:11px;font-weight:800;color:#475569;margin-bottom:4px;text-align:right;'>CLICK TO SWITCH LANGUAGE / DİL / ЯЗЫК:</div>")
    l1, l2, l3 = st.columns(3)
    with l1:
        if st.button("🇬🇧 EN", type="primary" if lang == "EN" else "secondary", use_container_width=True):
            st.session_state["lang"] = "EN"
            st.rerun()
    with l2:
        if st.button("🇦🇿 AZ", type="primary" if lang == "AZ" else "secondary", use_container_width=True):
            st.session_state["lang"] = "AZ"
            st.rerun()
    with l3:
        if st.button("🇷🇺 RU", type="primary" if lang == "RU" else "secondary", use_container_width=True):
            st.session_state["lang"] = "RU"
            st.rerun()

# ---------------------------------------------------------
# 2. Clean 3-Button Corridor Selector
# ---------------------------------------------------------
render_html(f'<div class="section-hdr">{t["running_now"]}</div>')
b1, b2, b3 = st.columns(3)
with b1:
    if st.button("🚆 ADY-104 • Baku ⇄ Sumgayit", type="primary" if selected_train == "ADY-104" else "secondary", use_container_width=True):
        st.session_state["active_train"] = "ADY-104"
        st.rerun()
with b2:
    if st.button("⚡ ADY-702 • Baku ⇄ Ganja Express", type="primary" if selected_train == "ADY-702" else "secondary", use_container_width=True):
        st.session_state["active_train"] = "ADY-702"
        st.rerun()
with b3:
    if st.button("🌍 ADY-410 • Baku ⇄ Tbilisi Silk Road", type="primary" if selected_train == "ADY-410" else "secondary", use_container_width=True):
        st.session_state["active_train"] = "ADY-410"
        st.rerun()

# ---------------------------------------------------------
# 3. The 4 Cute SVG Gauge & Signal Instrument Cards (Equal Height!)
# ---------------------------------------------------------
speed_ratio = min(max(advisory.approved_speed_kmh / 180.0, 0.05), 1.0)
arc_offset = round(110 * (1.0 - speed_ratio), 1)
gauge_stroke = "#f59e0b" if is_clamped else "#10b981"
wind_color = "#ea580c" if wind_speed > 65 else "#0284c7"

sig_red = "#ef4444" if block_status != "FREE" else "#334155"
sig_amber = "#f59e0b" if (is_clamped and block_status == "FREE") else "#334155"
sig_green = "#10b981" if (not is_clamped and block_status == "FREE") else "#334155"

k1, k2, k3, k4 = st.columns(4)

with k1:
    render_html(
        f"""<div class="gauge-card">
<div class="gauge-info">
  <div class="gauge-label">{t['kpi_active_train']}</div>
  <div style="font-size: 16px; font-weight: 800; color: #0f172a; margin: 4px 0;">{selected_train} • {meta['current_station']}</div>
  <div style="width:100%; background:#e2e8f0; height:7px; border-radius:999px; margin: 6px 0; overflow:hidden;">
    <div style="width:{meta['progress_pct']}%; background:linear-gradient(90deg,#2563eb,#06b6d4); height:100%; border-radius:999px;"></div>
  </div>
  <div class="gauge-sub" style="color: #0284c7;">⏭️ {meta['next_station']} ({meta['distance_km']})</div>
</div>
<svg width="54" height="54" viewBox="0 0 54 54" fill="none">
  <circle cx="27" cy="27" r="25" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.5"/>
  <rect x="15" y="13" width="24" height="24" rx="5" fill="#2563eb"/>
  <rect x="19" y="17" width="16" height="8" rx="2" fill="#bae6fd"/>
  <circle cx="21" cy="31" r="2.2" fill="#fde047"/>
  <circle cx="33" cy="31" r="2.2" fill="#fde047"/>
  <path d="M18 41 L22 37 M36 41 L32 37" stroke="#475569" stroke-width="2.2" stroke-linecap="round"/>
</svg>
</div>"""
    )

with k2:
    speed_badge_txt = f"Clamped from {requested_speed} km/h" if is_clamped else f"Target {requested_speed} km/h"
    render_html(
        f"""<div class="gauge-card">
<div class="gauge-info">
  <div class="gauge-label">{t['kpi_approved_speed']}</div>
  <div class="gauge-val">{advisory.approved_speed_kmh} <span style="font-size: 12px; color: #64748b;">km/h</span></div>
  <div class="gauge-sub" style="color: {gauge_stroke};">{'⚠️ ' + speed_badge_txt if is_clamped else '✓ ' + speed_badge_txt}</div>
</div>
<svg width="76" height="54" viewBox="0 0 76 54">
  <path d="M 8 44 A 30 30 0 0 1 68 44" fill="none" stroke="#e2e8f0" stroke-width="7" stroke-linecap="round"/>
  <path d="M 8 44 A 30 30 0 0 1 68 44" fill="none" stroke="{gauge_stroke}" stroke-width="7" stroke-linecap="round" stroke-dasharray="110" stroke-dashoffset="{arc_offset}"/>
  <text x="38" y="42" text-anchor="middle" font-size="11" font-weight="800" fill="#0f172a">{int(speed_ratio*100)}%</text>
</svg>
</div>"""
    )

with k3:
    render_html(
        f"""<div class="gauge-card">
<div class="gauge-info">
  <div class="gauge-label">{t['kpi_track_block']}</div>
  <div style="font-size: 13.5px; font-weight: 800; color: #0f172a; margin: 4px 0;"><code>{advisory.assigned_block_id}</code></div>
  <div class="gauge-sub" style="color: {wind_color};">🌬️ {wind_speed} km/h Wind • {'Siding' if is_siding else 'Main Line'}</div>
</div>
<div style="display:flex; align-items:center; gap:6px;">
  <svg width="24" height="54" viewBox="0 0 24 54">
    <rect x="3" y="2" width="18" height="44" rx="9" fill="#0f172a" stroke="#475569" stroke-width="1.5"/>
    <circle cx="12" cy="12" r="4.5" fill="{sig_red}"/>
    <circle cx="12" cy="24" r="4.5" fill="{sig_amber}"/>
    <circle cx="12" cy="36" r="4.5" fill="{sig_green}"/>
  </svg>
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
</div>"""
    )

with k4:
    render_html(
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
</div>"""
    )

# ---------------------------------------------------------
# 4. Visual Origin (BAK) ➔ Blinking 5-Station Track ➔ Destination (SUM) Boarding Card
# ---------------------------------------------------------
JOURNEY_STOPS = {
    "ADY-104": [
        {"name": "Baku", "status": "passed"},
        {"name": "Keshla", "status": "passed"},
        {"name": "Bilajari", "status": "current"},
        {"name": "Khirdalan", "status": "upcoming"},
        {"name": "Sumgayit", "status": "upcoming"},
    ],
    "ADY-702": [
        {"name": "Baku", "status": "passed"},
        {"name": "Bilajari", "status": "passed"},
        {"name": "Kurdamir", "status": "passed"},
        {"name": "Yevlakh", "status": "current"},
        {"name": "Ganja", "status": "upcoming"},
    ],
    "ADY-410": [
        {"name": "Baku", "status": "passed"},
        {"name": "Ganja", "status": "passed"},
        {"name": "Shamkir", "status": "current"},
        {"name": "Agstafa", "status": "upcoming"},
        {"name": "Tbilisi", "status": "upcoming"},
    ],
}

nodes_html = []
for idx, s in enumerate(JOURNEY_STOPS[selected_train], start=1):
    dot_class = "node-done" if s["status"] == "passed" else ("node-active" if s["status"] == "current" else "node-next")
    icon = "✓" if s["status"] == "passed" else ("🚄" if s["status"] == "current" else str(idx))
    nodes_html.append(
        f'<div class="station-node"><div class="node-circle {dot_class}">{icon}</div><div style="font-size:11.5px;font-weight:800;color:#0f172a;">{s["name"]}</div></div>'
    )

status_badge_txt = t["status_reroute"] if is_siding else (t["status_wind"] if is_clamped else t["status_safe"])
status_badge_bg = "#fef3c7" if (is_clamped or is_siding) else "#dcfce7"
status_badge_col = "#b45309" if (is_clamped or is_siding) else "#15803d"

render_html(
    f"""<div class="boarding-pass">
<div class="pass-route-row">
  <div style="min-width:105px;">
    <div style="font-size:10px;font-weight:800;color:#64748b;text-transform:uppercase;">ORIGIN</div>
    <div class="city-code">{meta['from_code']}</div>
    <div class="city-name">{meta['from_city']}</div>
    <div class="city-time">{meta['dep_time']}</div>
  </div>
  <div class="visual-track-center">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px;">
      <span style="font-size:11px;font-weight:800;color:#2563eb;">🚄 {selected_train} • {meta['train_type']}</span>
      <span style="background:{status_badge_bg};color:{status_badge_col};font-size:10.5px;font-weight:800;padding:3px 10px;border-radius:999px;">● {status_badge_txt}</span>
    </div>
    <div class="timeline-box">
      <div class="timeline-line"></div>
      <div class="timeline-fill" style="width:{meta['progress_pct']}%;"></div>
      {''.join(nodes_html)}
    </div>
  </div>
  <div style="min-width:105px;text-align:right;">
    <div style="font-size:10px;font-weight:800;color:#64748b;text-transform:uppercase;">DESTINATION</div>
    <div class="city-code">{meta['to_code']}</div>
    <div class="city-name">{meta['to_city']}</div>
    <div class="city-time">{advisory.updated_eta}</div>
  </div>
</div>
</div>"""
)

# ---------------------------------------------------------
# 5. Balanced Two-Column Visual Grid
# ---------------------------------------------------------
col_left, col_right = st.columns([1.0, 1.05], gap="medium")

with col_left:
    # 1. Digital LED Station Audio Board with Animated Sound Equalizer Bars
    render_html(
        f"""<div class="led-board-card">
<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
  <span style="font-size:11px; font-weight:800; color:#38bdf8 !important; letter-spacing:0.6px;">📢 {t['announcement_hdr']}</span>
  <div class="eq-bars"><div class="eq-bar"></div><div class="eq-bar"></div><div class="eq-bar"></div></div>
</div>
<div style="font-size:12.5px; font-weight:600; color:#f8fafc !important; line-height:1.45;">{t['announcement_body']}</div>
</div>"""
    )

    # 2. Graphical 2-Channel Safety Interlock Matrix
    wind_pct = min(int((wind_speed / 110.0) * 100), 100)
    wind_tile_bg = "#fffbeb" if wind_speed > 65 else "#ecfdf5"
    wind_tile_bdr = "#fde68a" if wind_speed > 65 else "#a7f3d0"
    wind_bar_col = "#f59e0b" if wind_speed > 65 else "#10b981"
    wind_status_lbl = f"CLAMPED → {advisory.approved_speed_kmh} km/h" if is_clamped else "PASS (SAFE)"

    blk_tile_bg = "#fffbeb" if is_siding else "#ecfdf5"
    blk_tile_bdr = "#fde68a" if is_siding else "#a7f3d0"
    blk_col = "#f59e0b" if is_siding else "#10b981"
    blk_status_lbl = "SIDING REROUTE" if is_siding else "PRIMARY LOCKED"

    render_html(
        f"""<div class="interlock-visual-card">
<div style="font-size:11.5px; font-weight:800; color:#0f172a; text-transform:uppercase;">{t['audit_hdr']}</div>
<div class="interlock-grid">
  <div class="interlock-tile" style="background:{wind_tile_bg}; border:1.5px solid {wind_tile_bdr};">
    <div style="width:100%;">
      <div style="display:flex; justify-content:space-between; font-size:11px; font-weight:800; color:#0f172a;">
        <span>🌬️ WIND INTERLOCK</span><span>{wind_speed}/65 km/h</span>
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
        <code style="font-size:11px; font-weight:800; color:#0f172a;">{advisory.assigned_block_id}</code>
      </div>
      <div style="font-size:11px; font-weight:800; color:{'#b45309' if is_siding else '#047857'};">{blk_status_lbl}</div>
    </div>
  </div>
</div>
</div>"""
    )

    # 3. Gemma Rail Assistant Chat
    render_html(f"<div style='font-size:14px;font-weight:800;color:#0f172a;margin-bottom:6px;'>{t['chat_hdr']}</div>")

    q1, q2, q3 = st.columns(3)
    user_prompt = None
    with q1:
        if st.button("✈️ Airport", use_container_width=True):
            user_prompt = "Is there any train from Heydar Aliyev Airport to Radisson Hotel Baku?"
    with q2:
        if st.button("🕒 Schedule", use_container_width=True):
            user_prompt = "Show all available train departures"
    with q3:
        if st.button("🎫 Tickets", use_container_width=True):
            user_prompt = "How much are tickets and BakuCard fares?"

    text_input = st.chat_input(t["chat_placeholder"])
    if text_input:
        user_prompt = text_input

    if user_prompt:
        st.session_state["chat_history"].append({"role": "user", "content": user_prompt})
        response = answer_rail_chat_query(user_prompt, lang=lang, selected_train=selected_train, advisory=advisory)
        st.session_state["chat_history"].append({"role": "assistant", "content": response})

    chat_container = st.container(height=270)
    with chat_container:
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    with st.expander("🤖 Google ADK Tool Trajectory & Structured JSON"):
        st.markdown("**ADK Tool Execution Order:** " + " ➔ ".join([f"`{fn}()`" for fn in advisory.tools_invoked]))
        st.code(json.dumps(advisory.model_dump(), indent=2), language="json")

with col_right:
    leaflet_map_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; padding: 0; background: transparent; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    #map-wrapper {{ position: relative; width: 100%; height: 420px; border-radius: 16px; overflow: hidden; border: 1.5px solid #cbd5e1; box-shadow: 0 4px 14px rgba(0,0,0,0.05); }}
    #railmap {{ width: 100%; height: 100%; }}
    .live-gps-hud {{
      position: absolute; top: 10px; left: 50px; right: 10px; z-index: 1000;
      background: rgba(15, 23, 42, 0.90); color: #f8fafc; backdrop-filter: blur(6px);
      padding: 6px 12px; border-radius: 999px; font-size: 11px; font-weight: 700;
      display: flex; align-items: center; justify-content: space-between;
      border: 1px solid rgba(56, 189, 248, 0.45);
    }}
    .blink-dot {{
      display: inline-block; width: 8px; height: 8px; background: #10b981;
      border-radius: 50%; margin-right: 6px; animation: dotBlink 1s infinite;
    }}
    @keyframes dotBlink {{ 0%, 100% {{ opacity: 1; box-shadow: 0 0 8px #10b981; }} 50% {{ opacity: 0.3; }} }}
    .station-node-icon {{ background: #ffffff; border: 2.5px solid #0284c7; border-radius: 50%; width: 10px; height: 10px; }}
    .station-active-icon {{
      background: #f59e0b; border: 2.5px solid #ffffff; border-radius: 50%;
      width: 14px; height: 14px; animation: stPulse 1.2s infinite ease-in-out;
    }}
    @keyframes stPulse {{
      0%, 100% {{ transform: scale(1.0); box-shadow: 0 0 6px rgba(245, 158, 11, 0.6); }}
      50% {{ transform: scale(1.45); box-shadow: 0 0 18px rgba(245, 158, 11, 1.0); }}
    }}
    .train-pin-wrapper {{ position: relative; width: 20px; height: 20px; }}
    .train-gps-dot {{
      width: 14px; height: 14px; border-radius: 50%; background: #0284c7;
      border: 2.5px solid #ffffff; position: absolute; top: 3px; left: 3px; z-index: 5;
    }}
    .train-gps-dot-active {{
      width: 16px; height: 16px; border-radius: 50%; background: #f59e0b;
      border: 3px solid #ffffff; position: absolute; top: 2px; left: 2px; z-index: 10;
    }}
    .ping-circle {{
      position: absolute; width: 36px; height: 36px; border-radius: 50%;
      background: rgba(37, 99, 235, 0.55); top: -8px; left: -8px; z-index: 1;
      animation: radarRing 1.5s infinite;
    }}
    @keyframes radarRing {{ 0% {{ transform: scale(0.5); opacity: 0.95; }} 100% {{ transform: scale(2.2); opacity: 0; }} }}
    .train-tag {{
      position: absolute; bottom: 22px; left: 50%; transform: translateX(-50%);
      background: #0f172a; color: #38bdf8; border: 1.5px solid #38bdf8;
      border-radius: 999px; padding: 3px 8px; font-size: 10.5px; font-weight: 800;
      white-space: nowrap; z-index: 20;
    }}
    .train-tag-active {{
      background: #2563eb; color: #ffffff; border: 2px solid #ffffff;
      padding: 4px 10px; font-size: 11px; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.8); z-index: 30;
    }}
    .map-controls {{
      position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 1000;
      display: flex; justify-content: space-between; pointer-events: none;
    }}
    .map-btn {{
      pointer-events: auto; background: #0f172a; color: #ffffff;
      border: 1.5px solid #38bdf8; border-radius: 999px; padding: 6px 12px;
      font-size: 11px; font-weight: 800; cursor: pointer;
    }}
  </style>
</head>
<body>
  <div id="map-wrapper">
    <div id="railmap"></div>
    <div class="live-gps-hud">
      <div><span class="blink-dot"></span><b>{selected_train}</b> • {meta['current_station']} ➔ {meta['next_station']}</div>
      <div style="color:#38bdf8;font-family:monospace;" id="hud-coords">{meta['coords_label']}</div>
    </div>
    <div class="map-controls">
      <button class="map-btn" onclick="focusActiveTrain()">🎯 Zoom to {selected_train}</button>
      <button class="map-btn" onclick="resetAzerbaijanBounds()">🇦🇿 Full Map</button>
    </div>
  </div>
  <script>
    var map = L.map('railmap', {{ zoomControl: true, attributionControl: false, minZoom: 6, maxZoom: 15 }});
    L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ maxZoom: 19 }}).addTo(map);
    var azBounds = [[38.4, 44.8], [41.9, 50.6]];
    map.fitBounds(azBounds, {{ padding: [14, 14] }});
    var azerbaijanBorder = [
      [38.40, 44.78], [38.75, 45.45], [38.92, 46.02], [38.85, 48.05],
      [38.42, 48.88], [39.15, 49.32], [39.75, 49.38], [40.25, 49.85],
      [40.45, 50.35], [40.75, 49.95], [41.05, 49.25], [41.52, 48.80],
      [41.90, 48.55], [41.92, 46.50], [41.35, 45.15], [41.10, 45.02],
      [40.85, 45.40], [40.35, 45.65], [39.72, 46.05], [39.22, 46.52],
      [38.40, 44.78]
    ];
    L.polygon(azerbaijanBorder, {{ color: '#0284c7', weight: 2.5, fillColor: '#0284c7', fillOpacity: 0.07, dashArray: '5, 5' }}).addTo(map);
    var absheronTrack = [[40.3798, 49.8488], [40.3953, 49.8912], [40.4286, 49.8058], [40.4503, 49.7547], [40.5897, 49.6686]];
    var bakuGanjaTrack = [[40.3798, 49.8488], [40.4286, 49.8058], [40.0167, 49.4000], [40.0389, 48.9328], [40.3436, 48.1608], [40.5194, 47.6542], [40.6172, 47.1501], [40.6272, 46.7778], [40.6828, 46.3606]];
    var silkRoadTrack = [[40.6828, 46.3606], [40.8297, 46.0178], [40.9922, 45.6289], [41.1189, 45.4539], [41.2056, 45.1861], [41.5495, 45.0006], [41.7225, 44.7986]];
    var activeTrainId = "{selected_train}";
    var is104Active = activeTrainId === "ADY-104";
    var is702Active = activeTrainId === "ADY-702";
    var is410Active = activeTrainId === "ADY-410";
    L.polyline(absheronTrack, {{ color: is104Active ? '#2563eb' : '#64748b', weight: is104Active ? 5 : 3 }}).addTo(map);
    L.polyline(bakuGanjaTrack, {{ color: is702Active ? '#2563eb' : '#64748b', weight: is702Active ? 5 : 3 }}).addTo(map);
    L.polyline(silkRoadTrack, {{ color: is410Active ? '#2563eb' : '#64748b', weight: is410Active ? 5 : 3 }}).addTo(map);
    var stations = [
      {{ name: "Baku Central", lat: 40.3798, lon: 49.8488, isLive: false }},
      {{ name: "Bilajari Jn", lat: 40.4286, lon: 49.8058, isLive: is104Active }},
      {{ name: "Sumgayit", lat: 40.5897, lon: 49.6686, isLive: false }},
      {{ name: "Yevlakh Jn", lat: 40.6172, lon: 47.1501, isLive: is702Active }},
      {{ name: "Ganja Central", lat: 40.6828, lon: 46.3606, isLive: false }},
      {{ name: "Shamkir Stn", lat: 40.8297, lon: 46.0178, isLive: is410Active }},
      {{ name: "Agstafa", lat: 41.1189, lon: 45.4539, isLive: false }}
    ];
    stations.forEach(function(st) {{
      var iconHtml = st.isLive ? '<div class="station-active-icon"></div>' : '<div class="station-node-icon"></div>';
      var stIcon = L.divIcon({{ className: '', html: iconHtml, iconSize: [14, 14], iconAnchor: [7, 7] }});
      L.marker([st.lat, st.lon], {{ icon: stIcon }}).addTo(map).bindPopup("<b>🚉 " + st.name + "</b>");
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
    var marker104 = L.marker([40.4286, 49.8058], {{ icon: buildTrainIcon('ADY-104', '🚆', speedVal104, is104Active), zIndexOffset: is104Active ? 1000 : 100 }}).addTo(map);
    var marker702 = L.marker([40.6172, 47.1501], {{ icon: buildTrainIcon('ADY-702', '⚡', speedVal702, is702Active), zIndexOffset: is702Active ? 1000 : 100 }}).addTo(map);
    var marker410 = L.marker([40.8297, 46.0178], {{ icon: buildTrainIcon('ADY-410', '🌍', speedVal410, is410Active), zIndexOffset: is410Active ? 1000 : 100 }}).addTo(map);
    var currentActiveLat = {meta['lat']};
    var currentActiveLon = {meta['lon']};
    function focusActiveTrain() {{ map.flyTo([currentActiveLat, currentActiveLon], 11, {{ duration: 0.8 }}); }}
    function resetAzerbaijanBounds() {{ map.flyToBounds(azBounds, {{ padding: [14, 14], duration: 0.8 }}); }}
  </script>
</body>
</html>"""

    components.html(leaflet_map_html, height=430)

    sp104 = advisory.approved_speed_kmh if selected_train == "ADY-104" else 80
    sp702 = advisory.approved_speed_kmh if selected_train == "ADY-702" else 145
    sp410 = advisory.approved_speed_kmh if selected_train == "ADY-410" else 110

    render_html(
        f"""<div class="ticket-strip">
<div class="mini-ticket {'mini-ticket-active' if selected_train == 'ADY-104' else ''}">
  <div style="display:flex;justify-content:space-between;font-size:12px;font-weight:800;color:#0f172a;">
    <span>🚆 ADY-104</span><span style="color:#2563eb;">{sp104} km/h</span>
  </div>
  <div style="font-size:11px;color:#64748b;margin:3px 0;">BAK ➔ SUM • <b>13:23</b></div>
  <div style="width:100%;background:#e2e8f0;height:5px;border-radius:99px;"><div style="width:55%;background:#2563eb;height:100%;border-radius:99px;"></div></div>
</div>
<div class="mini-ticket {'mini-ticket-active' if selected_train == 'ADY-702' else ''}">
  <div style="display:flex;justify-content:space-between;font-size:12px;font-weight:800;color:#0f172a;">
    <span>⚡ ADY-702</span><span style="color:#10b981;">{sp702} km/h</span>
  </div>
  <div style="font-size:11px;color:#64748b;margin:3px 0;">BAK ➔ GNJ • <b>14:30</b></div>
  <div style="width:100%;background:#e2e8f0;height:5px;border-radius:99px;"><div style="width:72%;background:#10b981;height:100%;border-radius:99px;"></div></div>
</div>
<div class="mini-ticket {'mini-ticket-active' if selected_train == 'ADY-410' else ''}">
  <div style="display:flex;justify-content:space-between;font-size:12px;font-weight:800;color:#0f172a;">
    <span>🌍 ADY-410</span><span style="color:#0d9488;">{sp410} km/h</span>
  </div>
  <div style="font-size:11px;color:#64748b;margin:3px 0;">BAK ➔ TBS • <b>16:45</b></div>
  <div style="width:100%;background:#e2e8f0;height:5px;border-radius:99px;"><div style="width:48%;background:#0d9488;height:100%;border-radius:99px;"></div></div>
</div>
</div>"""
    )
