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
    initial_sidebar_state="collapsed",
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

# Exact GPS Telemetry Metadata for Each ADY Train
TRAIN_GPS_INFO = {
    "ADY-104": {
        "lat": 40.4286,
        "lon": 49.8058,
        "coords_label": "40.4286° N, 49.8058° E",
        "current_station": "Bilajari Junction",
        "next_station": "Khirdalan (5.4 km ahead)",
        "corridor_label": "Baku ⇄ Sumgayit Absheron Circular",
    },
    "ADY-702": {
        "lat": 40.6172,
        "lon": 47.1501,
        "coords_label": "40.6172° N, 47.1501° E",
        "current_station": "Yevlakh Junction",
        "next_station": "Ganja Central (67 km ahead)",
        "corridor_label": "Baku ⇄ Ganja High-Speed Express",
    },
    "ADY-410": {
        "lat": 40.8297,
        "lon": 46.0178,
        "coords_label": "40.8297° N, 46.0178° E",
        "current_station": "Shamkir Station",
        "next_station": "Agstafa Border (52 km ahead)",
        "corridor_label": "Baku ⇄ Tbilisi Silk Road International",
    },
}

# ---------------------------------------------------------
# Custom Styling: Mobile-Responsive & High-Contrast Light Mode
# ---------------------------------------------------------
st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --ground: #f8fafc;
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
    font-size: 16px;
    font-weight: 800;
    color: #0f172a !important;
    margin: 10px 0 8px 0;
    display: flex;
    align-items: center;
    gap: 6px;
}

.timeline-wrapper {
    background: white;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 14px 20px;
    margin-bottom: 18px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.timeline-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    padding: 20px 16px 10px 16px;
    min-width: 420px;
}

.timeline-line {
    position: absolute;
    top: 34px;
    left: 48px;
    right: 48px;
    height: 6px;
    background: #e2e8f0;
    border-radius: 999px;
    z-index: 1;
}

.timeline-fill {
    position: absolute;
    top: 34px;
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
    min-width: 78px;
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
    margin-bottom: 6px;
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
    transform: scale(1.18);
    border: 2.5px solid #0284c7;
    box-shadow: 0 0 12px rgba(245, 158, 11, 0.65);
}

.node-next {
    background: white;
    color: #64748b !important;
    border: 2px solid #cbd5e1;
}

.kpi-card {
    background: white;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

.gps-banner {
    background: #0f172a;
    color: #f8fafc !important;
    border: 1.5px solid #1e293b;
    border-left: 5px solid #38bdf8;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 10px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    font-size: 12.5px;
}

.gps-banner span, .gps-banner b, .gps-banner code {
    color: #f8fafc !important;
}

.announcement-card {
    background: linear-gradient(135deg, #eff6ff 0%, #e0f2fe 100%);
    border: 1px solid #bfdbfe;
    border-left: 6px solid #2563eb;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 12px;
    color: #0f172a !important;
}

.audit-card-warn {
    background: #fffbeb;
    border: 1px solid #fef3c7;
    border-left: 6px solid #f59e0b;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 12px;
    color: #0f172a !important;
}

.audit-card-safe {
    background: #ecfdf5;
    border: 1px solid #d1fae5;
    border-left: 6px solid #10b981;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 12px;
    color: #0f172a !important;
}

.telemetry-table-container {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 10px 12px;
    margin-top: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

/* Mobile Responsive Refinements */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
    .kpi-card {
        padding: 10px 12px;
        margin-bottom: 8px;
    }
    .timeline-wrapper {
        padding: 10px 10px;
    }
    .timeline-box {
        min-width: 340px;
        padding: 14px 6px 6px 6px;
    }
    .station-node {
        min-width: 62px;
    }
    .gps-banner {
        font-size: 11.5px;
        padding: 8px 10px;
    }
    .telemetry-table-container table {
        font-size: 11.5px !important;
        min-width: 480px;
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
# Trilingual Localization Dictionary (Clean, No Duplicate Emojis)
# ---------------------------------------------------------
I18N = {
    "EN": {
        "tagline": "Azerbaijan Railways (ADY) High-Speed Corridor • Open-Weights Gemma • Google ADK • Cloud Run",
        "running_now": "🚄 ADY FLEET CORRIDORS (Tap to Select Active Train)",
        "kpi_active_train": "Active Train & Route",
        "kpi_approved_speed": "Approved Safe Speed",
        "kpi_track_block": "Assigned Track Block",
        "kpi_station_eta": "Station Arrival ETA",
        "speed_clamped": f"↓ Clamped ({advisory.approved_speed_kmh - requested_speed} km/h)",
        "speed_clear": "✓ Normal Approved Speed",
        "siding_alert": "⚠️ Passing Loop Siding",
        "main_line": "✓ Clear Primary Line",
        "timeline_title": f"🚉 STATION PROGRESSION · {LIVE_TRAINS[selected_train]['route_name']}",
        "announcement_hdr": "📢 Passenger Station Board Announcement (ADY Audio Synthesizer)",
        "announcement_body": advisory.passenger_announcement,
        "audit_hdr": "Deterministic Railway Interlock Audit",
        "map_hdr": "🗺️ Live Azerbaijan Railways (ADY) High-Speed Network & Exact GPS",
        "chat_title": "💬 Gemma Rail Assistant (Live Departure & Schedule Q&A)",
        "chat_placeholder": "Ask about airport transit, departure times, schedules, or weather...",
        "telemetry_hdr": "📊 Live ADY Fleet Telemetry & Block Clearance",
    },
    "AZ": {
        "tagline": "Azərbaycan Dəmir Yolları (ADY) • Açıq Gemma Modeli • Google ADK • Cloud Run",
        "running_now": "🚄 ADY QATAR MARŞRUTLARI (Aktiv qatarı seçmək üçün toxunun)",
        "kpi_active_train": "Aktiv Qatar və Marşrut",
        "kpi_approved_speed": "Təsdiqlənmiş Təhlükəsiz Sürət",
        "kpi_track_block": "Təyin Olunmuş Yol Bloku",
        "kpi_station_eta": "Stansiyaya Çatma Vaxtı",
        "speed_clamped": f"↓ Məhdudlaşdırıldı ({advisory.approved_speed_kmh - requested_speed} km/s)",
        "speed_clear": "✓ Təhlükəsiz Sürət Rejimi",
        "siding_alert": "⚠️ Ehtiyat Yan Xətt",
        "main_line": "✓ Əsas Xətt Açıqdır",
        "timeline_title": f"🚉 MARŞRUT VƏ STANSİYA HƏRƏKƏTİ · {LIVE_TRAINS[selected_train]['route_name']}",
        "announcement_hdr": "📢 Stansiya Sərnişin Məlumat Lövhəsi (ADY Səsli Bildiriş)",
        "announcement_body": f"Diqqət, sərnişinlərin nəzərinə! {LIVE_TRAINS[selected_train]['route_name']} qatarı ({advisory.train_id}) {advisory.assigned_block_id} blokuna təyin edildi. Təhlükəsiz sürət həddi: {advisory.approved_speed_kmh} km/saat. Yenilənmiş çatma vaxtı: {advisory.updated_eta}.",
        "audit_hdr": "Deterministik Dəmiryolu Təhlükəsizlik Auditi",
        "map_hdr": "🗺️ Azərbaycan Dəmir Yolları (ADY) Canlı Xəritə və GPS Mövqeyi",
        "chat_title": "💬 Gemma Dəmiryolu Köməkçisi (Real Vaxt Çıxış və Cədvəl)",
        "chat_placeholder": "Hava limanı nəqliyyatı, çıxış vaxtları və ya hava haqqında soruşun...",
        "telemetry_hdr": "📊 ADY Qatar Parkının Canlı Telemetriyası və Yol Təhlükəsizliyi",
    },
    "RU": {
        "tagline": "Азербайджанские Железные Дороги (ADY) • Open-Weights Gemma • Google ADK • Cloud Run",
        "running_now": "🚄 АКТИВНЫЕ МАРШРУТЫ ПОЕЗДОВ АЖД (Нажмите для выбора поезда)",
        "kpi_active_train": "Активный поезд и маршрут",
        "kpi_approved_speed": "Безопасная скорость",
        "kpi_track_block": "Назначенный блок пути",
        "kpi_station_eta": "Время прибытия (ETA)",
        "speed_clamped": f"↓ Ограничено ({advisory.approved_speed_kmh - requested_speed} км/ч)",
        "speed_clear": "✓ В пределах нормы",
        "siding_alert": "⚠️ Боковой разъезд",
        "main_line": "✓ Главный путь свободен",
        "timeline_title": f"🚉 МАРШРУТ И ПРОХОЖДЕНИЕ СТАНЦИЙ · {LIVE_TRAINS[selected_train]['route_name']}",
        "announcement_hdr": "📢 Вокзальное Табло и Оповещение Пассажиров (Аудиосинтезатор)",
        "announcement_body": f"Внимание пассажиров! Поезд {LIVE_TRAINS[selected_train]['route_name']} ({advisory.train_id}) направлен на блок {advisory.assigned_block_id}. Безопасная скорость: {advisory.approved_speed_kmh} км/ч. Новое время прибытия: {advisory.updated_eta}.",
        "audit_hdr": "Аудит Детерминированных Блокировок Безопасности",
        "map_hdr": "🗺️ Карта Железнодорожной Сети Азербайджана и Точные GPS Координаты",
        "chat_title": "💬 Gemma Rail Assistant (Расписание и Отправления Онлайн)",
        "chat_placeholder": "Спросите о трансфере из аэропорта, расписании или погоде...",
        "telemetry_hdr": "📊 Телеметрия Парка Поездов АЖД и Статус Путей",
    },
}

t = I18N[lang]

# ---------------------------------------------------------
# Top Header Row: Branding & Clickable Language Switcher
# ---------------------------------------------------------
col_head_left, col_head_right = st.columns([2.6, 1.4])
with col_head_left:
    st.markdown(
        """<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-top: 2px;">
<span style="font-size: 26px;">🚄</span>
<span style="font-size: 22px; font-weight: 800; color: #0f172a; letter-spacing: -0.5px;">RailPulse AI</span>
<span style="background: #e0f2fe; color: #0369a1; font-weight: 800; font-size: 11px; padding: 4px 9px; border-radius: 6px; letter-spacing: 0.5px;">ADY AZERBAIJAN</span>
<span style="background: #fef3c7; color: #b45309; font-weight: 800; font-size: 11px; padding: 4px 9px; border-radius: 6px;">● LIVE DISPATCH</span>
</div>""",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div style='font-size: 12.5px; color: #475569; margin-bottom: 6px;'>{t['tagline']}</div>", unsafe_allow_html=True)

with col_head_right:
    st.markdown("<div style='font-size: 11px; color: #475569; font-weight: 700; margin-bottom: 4px;'>LANGUAGE / DİL / ЯЗЫК:</div>", unsafe_allow_html=True)
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
# Full-Width Section 2: Four Key Telemetry & KPI Cards
# ---------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        f"""<div class="kpi-card">
<div style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700;">{t['kpi_active_train']}</div>
<div style="font-size: 16px; font-weight: 800; color: #0f172a; margin: 4px 0;">{LIVE_TRAINS[selected_train]['route_name']}</div>
<div style="font-size: 12px; color: #0284c7; font-weight: 700;">📍 {TRAIN_GPS_INFO[selected_train]['current_station']} ({TRAIN_GPS_INFO[selected_train]['coords_label']})</div>
</div>""",
        unsafe_allow_html=True,
    )

with k2:
    is_clamped = advisory.approved_speed_kmh != requested_speed
    speed_sub = t["speed_clamped"] if is_clamped else t["speed_clear"]
    speed_color = "#ea580c" if is_clamped else "#10b981"
    st.markdown(
        f"""<div class="kpi-card">
<div style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700;">{t['kpi_approved_speed']}</div>
<div style="font-size: 21px; font-weight: 800; color: #0f172a; margin: 2px 0;">{advisory.approved_speed_kmh} <span style="font-size: 13px; font-weight: 600; color: #64748b;">km/h</span></div>
<div style="font-size: 12px; color: {speed_color}; font-weight: 700;">{speed_sub}</div>
</div>""",
        unsafe_allow_html=True,
    )

with k3:
    is_siding = "SIDING" in advisory.assigned_block_id
    block_sub = t["siding_alert"] if is_siding else t["main_line"]
    block_color = "#b45309" if is_siding else "#0284c7"
    st.markdown(
        f"""<div class="kpi-card">
<div style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700;">{t['kpi_track_block']}</div>
<div style="font-size: 15px; font-weight: 800; color: #0f172a; margin: 5px 0;"><code>{advisory.assigned_block_id}</code></div>
<div style="font-size: 12px; color: {block_color}; font-weight: 700;">{block_sub}</div>
</div>""",
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        f"""<div class="kpi-card">
<div style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700;">{t['kpi_station_eta']}</div>
<div style="font-size: 21px; font-weight: 800; color: #0284c7; margin: 2px 0;">{advisory.updated_eta}</div>
<div style="font-size: 12px; color: #10b981; font-weight: 700;">✓ {advisory.delay_minutes_remaining} min delay remaining</div>
</div>""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# Full-Width Section 3: Prominent Station Progression Timeline
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
# Two-Column Balanced Grid: Left Safety & Assistant | Right Network Map & Telemetry
# ---------------------------------------------------------
col_left, col_right = st.columns([1.0, 1.0], gap="medium")

with col_left:
    # 1. Passenger Announcement Card
    st.markdown(
        f"""<div class="announcement-card">
<div style="font-weight: 800; font-size: 11.5px; text-transform: uppercase; color: #1e40af; margin-bottom: 5px;">
{t['announcement_hdr']}
</div>
<div style="font-size: 13.5px; line-height: 1.5; color: #0f172a;">{t['announcement_body']}</div>
</div>""",
        unsafe_allow_html=True,
    )

    # 2. Guardrail Audit Card
    audit_class = "audit-card-warn" if (is_clamped or is_siding) else "audit-card-safe"
    audit_icon = "⚠️" if (is_clamped or is_siding) else "🛡️"
    st.markdown(
        f"""<div class="{audit_class}">
<div style="font-weight: 800; font-size: 11.5px; text-transform: uppercase; margin-bottom: 4px; color: #0f172a;">
{audit_icon} {t['audit_hdr']}
</div>
<div style="font-size: 12.5px; font-family: monospace; color: #0f172a;">{advisory.guardrail_intervention_summary}</div>
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

    chat_container = st.container(height=290)
    with chat_container:
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    with st.expander("🤖 Ordered Google ADK Function Trajectory"):
        for idx, tool_name in enumerate(advisory.tools_invoked, start=1):
            st.markdown(f"**Step {idx}:** `{tool_name}()`")

    with st.expander("📄 Validated Structured JSON (`RailDispatchAdvisory`)"):
        st.code(json.dumps(advisory.model_dump(), indent=2), language="json")

with col_right:
    # 1. Section Header (Single Emoji, Explicit Dark Contrast)
    st.markdown(f'<div class="section-hdr">{t["map_hdr"]}</div>', unsafe_allow_html=True)

    # 2. Dedicated Exact GPS Location Banner Above Map
    active_gps = TRAIN_GPS_INFO[selected_train]
    st.markdown(
        f"""<div class="gps-banner">
<div>🎯 <b>Exact Location ({selected_train}):</b> {active_gps['current_station']} &nbsp;|&nbsp; 🧭 <code>{active_gps['coords_label']}</code></div>
<div>⏭️ <b>Next:</b> {active_gps['next_station']}</div>
</div>""",
        unsafe_allow_html=True,
    )

    # 3. Interactive Leaflet Map:
    # - Zero fast back-and-forth movement! Trains are pinned accurately at their real-time GPS coordinates.
    # - Elevated pointer callout badge positioned ABOVE the pin so station dots never cover text.
    # - Built-in "🎯 Zoom to Active Train" and "🇦🇿 Full Azerbaijan Map" buttons for instant mobile navigation.
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
    #map-wrapper {{ position: relative; width: 100%; height: 395px; border-radius: 12px; overflow: hidden; border: 1.5px solid #cbd5e1; }}
    #railmap {{ width: 100%; height: 100%; }}

    .station-dot {{
      background: #ffffff;
      border: 2.5px solid #0284c7;
      border-radius: 50%;
      width: 10px;
      height: 10px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.35);
    }}

    /* Crisp GPS Pin & Elevated Callout so Pin NEVER Overlaps Badge Text */
    .train-pin-wrapper {{
      position: relative;
      width: 22px;
      height: 22px;
    }}
    .train-gps-dot {{
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: #334155;
      border: 2.5px solid #ffffff;
      box-shadow: 0 2px 6px rgba(0,0,0,0.45);
      position: absolute;
      top: 3px;
      left: 3px;
      z-index: 5;
    }}
    .train-gps-dot-active {{
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: #f59e0b;
      border: 3px solid #ffffff;
      box-shadow: 0 0 12px rgba(245, 158, 11, 0.95);
      position: absolute;
      top: 2px;
      left: 2px;
      z-index: 10;
    }}
    .radar-pulse {{
      position: absolute;
      width: 34px;
      height: 34px;
      border-radius: 50%;
      background: rgba(245, 158, 11, 0.45);
      top: -6px;
      left: -6px;
      z-index: 2;
      animation: pulseRing 2s infinite;
    }}
    @keyframes pulseRing {{
      0% {{ transform: scale(0.55); opacity: 0.95; }}
      100% {{ transform: scale(1.9); opacity: 0; }}
    }}

    /* Elevated Callout Badge Positioned Cleanly Above GPS Pin */
    .train-callout {{
      position: absolute;
      bottom: 26px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.92);
      color: #f8fafc;
      border: 1.5px solid #38bdf8;
      border-radius: 8px;
      padding: 3px 8px;
      font-size: 10.5px;
      font-weight: 800;
      white-space: nowrap;
      box-shadow: 0 4px 10px rgba(0,0,0,0.3);
      pointer-events: auto;
      z-index: 20;
    }}
    .train-callout-active {{
      background: #2563eb;
      color: #ffffff;
      border: 2px solid #ffffff;
      padding: 4px 10px;
      font-size: 11px;
      box-shadow: 0 6px 16px rgba(37, 99, 235, 0.65);
      z-index: 30;
    }}
    .train-callout::after {{
      content: "";
      position: absolute;
      top: 100%;
      left: 50%;
      margin-left: -5px;
      border-width: 5px;
      border-style: solid;
      border-color: #2563eb transparent transparent transparent;
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
    .overlay-badge {{
      position: absolute;
      top: 10px;
      right: 10px;
      z-index: 1000;
      background: rgba(15, 23, 42, 0.90);
      color: #38bdf8;
      padding: 4px 10px;
      border-radius: 7px;
      font-size: 10.5px;
      font-weight: 800;
      border: 1px solid rgba(56, 189, 248, 0.45);
    }}
  </style>
</head>
<body>
  <div id="map-wrapper">
    <div id="railmap"></div>
    <div class="overlay-badge">🇦🇿 ADY LIVE GPS TRACKER</div>
    <div class="map-controls">
      <button class="map-btn" onclick="focusActiveTrain()">🎯 Pin Exact Location ({selected_train})</button>
      <button class="map-btn" onclick="resetAzerbaijanBounds()">🇦🇿 Full Azerbaijan View</button>
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
    map.fitBounds(azBounds, {{ padding: [16, 16] }});

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
      weight: 2.5,
      opacity: 0.9,
      fillColor: '#0284c7',
      fillOpacity: 0.06,
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
      {{ name: "Baku Central (28 May)", lat: 40.3798, lon: 49.8488 }},
      {{ name: "Keshla Hub", lat: 40.3953, lon: 49.8912 }},
      {{ name: "Bilajari Junction", lat: 40.4286, lon: 49.8058 }},
      {{ name: "Khirdalan", lat: 40.4503, lon: 49.7547 }},
      {{ name: "Sumgayit Passenger", lat: 40.5897, lon: 49.6686 }},
      {{ name: "Kurdamir", lat: 40.3436, lon: 48.1608 }},
      {{ name: "Yevlakh Junction", lat: 40.6172, lon: 47.1501 }},
      {{ name: "Ganja Central", lat: 40.6828, lon: 46.3606 }},
      {{ name: "Shamkir Station", lat: 40.8297, lon: 46.0178 }},
      {{ name: "Agstafa Border", lat: 41.1189, lon: 45.4539 }}
    ];

    stations.forEach(function(st) {{
      var stIcon = L.divIcon({{
        className: '',
        html: '<div class="station-dot"></div>',
        iconSize: [10, 10],
        iconAnchor: [5, 5]
      }});
      L.marker([st.lat, st.lon], {{ icon: stIcon }})
        .addTo(map)
        .bindPopup("<b>🚉 " + st.name + "</b><br><small>GPS: " + st.lat.toFixed(4) + "° N, " + st.lon.toFixed(4) + "° E</small>");
    }});

    var trainData = {{
      "ADY-104": {{
        lat: 40.4286,
        lon: 49.8058,
        station: "Bilajari Junction",
        next: "Khirdalan",
        speed: is104Active ? "{advisory.approved_speed_kmh} km/h" : "80 km/h",
        block: is104Active ? "{advisory.assigned_block_id}" : "BLK-SUMGAYIT-A1",
        icon: "🚆"
      }},
      "ADY-702": {{
        lat: 40.6172,
        lon: 47.1501,
        station: "Yevlakh Junction",
        next: "Ganja Central",
        speed: is702Active ? "{advisory.approved_speed_kmh} km/h" : "145 km/h",
        block: is702Active ? "{advisory.assigned_block_id}" : "BLK-GANJA-EXPR",
        icon: "⚡"
      }},
      "ADY-410": {{
        lat: 40.8297,
        lon: 46.0178,
        station: "Shamkir Station",
        next: "Agstafa Border",
        speed: is410Active ? "{advisory.approved_speed_kmh} km/h" : "110 km/h",
        block: is410Active ? "{advisory.assigned_block_id}" : "BLK-SILKROAD-04",
        icon: "🌍"
      }}
    }};

    var trainMarkers = {{}};
    Object.keys(trainData).forEach(function(tid) {{
      var td = trainData[tid];
      var isActive = (tid === activeTrainId);
      var calloutHtml = isActive
        ? '<div class="train-callout train-callout-active">' + td.icon + ' ' + tid + ' • ' + td.speed + ' 📍 ' + td.station + '</div>'
        : '<div class="train-callout">' + td.icon + ' ' + tid + '</div>';

      var pinHtml = '<div class="train-pin-wrapper">' +
        (isActive ? '<div class="radar-pulse"></div>' : '') +
        '<div class="' + (isActive ? 'train-gps-dot-active' : 'train-gps-dot') + '"></div>' +
        calloutHtml +
        '</div>';

      var divIcon = L.divIcon({{
        className: '',
        html: pinHtml,
        iconSize: [22, 22],
        iconAnchor: [11, 11]
      }});

      var popupContent = '<div style="font-size:12px;line-height:1.45;">' +
        '<b>' + td.icon + ' ' + tid + ' Exact Telemetry</b><br>' +
        '📍 <b>Current Station:</b> ' + td.station + '<br>' +
        '⏭️ <b>Next Stop:</b> ' + td.next + '<br>' +
        '🧭 <b>Exact GPS:</b> <code>' + td.lat.toFixed(4) + '° N, ' + td.lon.toFixed(4) + '° E</code><br>' +
        '⚡ <b>Approved Speed:</b> ' + td.speed + '<br>' +
        '🚦 <b>Track Block:</b> <code>' + td.block + '</code>' +
        '</div>';

      var m = L.marker([td.lat, td.lon], {{ icon: divIcon, zIndexOffset: isActive ? 1000 : 100 }})
        .addTo(map)
        .bindPopup(popupContent);

      trainMarkers[tid] = m;
    }});

    function focusActiveTrain() {{
      var td = trainData[activeTrainId];
      map.flyTo([td.lat, td.lon], 11, {{ duration: 0.8 }});
      trainMarkers[activeTrainId].openPopup();
    }}

    function resetAzerbaijanBounds() {{
      map.closePopup();
      map.flyToBounds(azBounds, {{ padding: [16, 16], duration: 0.8 }});
    }}
  </script>
</body>
</html>"""

    components.html(leaflet_map_html, height=405)

    # 4. Live Fleet Telemetry & Block Status Table (Responsive Horizontal Scroll on Mobile)
    st.markdown(f'<div class="section-hdr">{t["telemetry_hdr"]}</div>', unsafe_allow_html=True)

    telemetry_html = f"""<div class="telemetry-table-container">
<table style="width: 100%; border-collapse: collapse; font-size: 12.5px; color: #0f172a;">
<thead>
<tr style="background: #f8fafc; border-bottom: 2px solid #e2e8f0; text-align: left; color: #475569;">
<th style="padding: 8px 10px;">Train</th>
<th style="padding: 8px 10px;">Exact Station & GPS</th>
<th style="padding: 8px 10px;">Speed</th>
<th style="padding: 8px 10px;">Active Block</th>
<th style="padding: 8px 10px;">Status</th>
<th style="padding: 8px 10px;">ETA</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom: 1px solid #f1f5f9; background: {'#eff6ff' if selected_train == 'ADY-104' else 'white'};">
<td style="padding: 9px 10px; font-weight: 700;">🚆 ADY-104</td>
<td style="padding: 9px 10px;"><b>Bilajari Jn</b><br><span style="font-size:11px;color:#64748b;">40.4286°N, 49.8058°E</span></td>
<td style="padding: 9px 10px; font-weight: 700;">{advisory.approved_speed_kmh if selected_train == 'ADY-104' else '80'} km/h</td>
<td style="padding: 9px 10px;"><code>{advisory.assigned_block_id if selected_train == 'ADY-104' else 'BLK-SUMGAYIT-A1'}</code></td>
<td style="padding: 9px 10px;"><span style="background: #fef3c7; color: #b45309; padding: 2px 7px; border-radius: 4px; font-weight: 700; font-size: 11px;">⚠️ High Wind Clamped</span></td>
<td style="padding: 9px 10px; font-weight: 700; color: #0284c7;">{advisory.updated_eta if selected_train == 'ADY-104' else '13:23'}</td>
</tr>
<tr style="border-bottom: 1px solid #f1f5f9; background: {'#eff6ff' if selected_train == 'ADY-702' else 'white'};">
<td style="padding: 9px 10px; font-weight: 700;">⚡ ADY-702</td>
<td style="padding: 9px 10px;"><b>Yevlakh Jn</b><br><span style="font-size:11px;color:#64748b;">40.6172°N, 47.1501°E</span></td>
<td style="padding: 9px 10px; font-weight: 700;">{advisory.approved_speed_kmh if selected_train == 'ADY-702' else '145'} km/h</td>
<td style="padding: 9px 10px;"><code>{advisory.assigned_block_id if selected_train == 'ADY-702' else 'BLK-GANJA-EXPR'}</code></td>
<td style="padding: 9px 10px;"><span style="background: #ecfdf5; color: #047857; padding: 2px 7px; border-radius: 4px; font-weight: 700; font-size: 11px;">✓ On Schedule</span></td>
<td style="padding: 9px 10px; font-weight: 700; color: #0284c7;">{advisory.updated_eta if selected_train == 'ADY-702' else '14:30'}</td>
</tr>
<tr style="background: {'#eff6ff' if selected_train == 'ADY-410' else 'white'};">
<td style="padding: 9px 10px; font-weight: 700;">🌍 ADY-410</td>
<td style="padding: 9px 10px;"><b>Shamkir Stn</b><br><span style="font-size:11px;color:#64748b;">40.8297°N, 46.0178°E</span></td>
<td style="padding: 9px 10px; font-weight: 700;">{advisory.approved_speed_kmh if selected_train == 'ADY-410' else '110'} km/h</td>
<td style="padding: 9px 10px;"><code>{advisory.assigned_block_id if selected_train == 'ADY-410' else 'BLK-SILKROAD-04'}</code></td>
<td style="padding: 9px 10px;"><span style="background: #ecfdf5; color: #047857; padding: 2px 7px; border-radius: 4px; font-weight: 700; font-size: 11px;">✓ Border Route Clear</span></td>
<td style="padding: 9px 10px; font-weight: 700; color: #0284c7;">{advisory.updated_eta if selected_train == 'ADY-410' else '16:45'}</td>
</tr>
</tbody>
</table>
</div>"""
    st.markdown(telemetry_html, unsafe_allow_html=True)
