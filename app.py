"""RailPulse AI — Autonomous Rail Telemetry & Smart Dispatch Agent for Azerbaijan Railways (ADY).

Unique modern Caspian Indigo & Cyan transit identity.
Trilingual: English • Azerbaijani (Azərbaycan dili) • Russian (Русский язык).
Powered by Open-Weights Gemma, Google ADK Function Calling, Deterministic Guardrails, and Cloud Run.
Includes Live Departure, Timetable & Train Availability Chat Assistant.
"""

import json
import pandas as pd
import streamlit as st

from railpulse_agent.agent import run_railpulse_dispatch
from railpulse_agent.chat import answer_rail_chat_query
from railpulse_agent.tools import CORRIDOR_SIGNALS, LIVE_TRAINS

st.set_page_config(
    page_title="RailPulse AI · ADY Azerbaijan Railways",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state["lang"] = "EN"
if "active_train" not in st.session_state:
    st.session_state["active_train"] = "ADY-104"
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {
            "role": "assistant",
            "content": "👋 **Hello! I am Gemma Rail Copilot.** Ask me about real-time train departures, live schedules, delays, or Caspian weather conditions!",
        }
    ]

# ---------------------------------------------------------
# Modern Transit Design System Tokens & Styling
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
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--ink);
}

.stApp {
    background-color: var(--ground);
}

.timeline-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    padding: 24px 14px 12px 14px;
}

.timeline-line {
    position: absolute;
    top: 36px;
    left: 40px;
    right: 40px;
    height: 5px;
    background: #e2e8f0;
    border-radius: 999px;
    z-index: 1;
}

.timeline-fill {
    position: absolute;
    top: 36px;
    left: 40px;
    height: 5px;
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
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 800;
    margin-bottom: 6px;
    border: 2px solid white;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
}

.node-done {
    background: #10b981;
    color: white;
}

.node-active {
    background: #f59e0b;
    color: #ffffff;
    transform: scale(1.25);
    border: 2.5px solid #0284c7;
    animation: livePulse 1.5s infinite;
    box-shadow: 0 0 12px rgba(245, 158, 11, 0.6);
}

@keyframes livePulse {
    0% { transform: scale(1.15); box-shadow: 0 0 4px rgba(245, 158, 11, 0.4); }
    50% { transform: scale(1.32); box-shadow: 0 0 16px rgba(245, 158, 11, 0.85); }
    100% { transform: scale(1.15); box-shadow: 0 0 4px rgba(245, 158, 11, 0.4); }
}

.node-next {
    background: white;
    color: #94a3b8;
    border: 2px solid #cbd5e1;
}

.announcement-card {
    background: linear-gradient(135deg, #eff6ff 0%, #e0f2fe 100%);
    border: 1px solid #bfdbfe;
    border-left: 6px solid #2563eb;
    padding: 16px 20px;
    border-radius: 14px;
    color: #1e3a8a;
    font-size: 14.5px;
    line-height: 1.5;
    margin-bottom: 16px;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.06);
}

.audit-card-safe {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 6px solid #16a34a;
    padding: 14px 18px;
    border-radius: 14px;
    color: #14532d;
    font-size: 13.5px;
    margin-bottom: 16px;
}

.audit-card-warn {
    background: #fff1f2;
    border: 1px solid #fecdd3;
    border-left: 6px solid #e11d48;
    padding: 14px 18px;
    border-radius: 14px;
    color: #881337;
    font-size: 13.5px;
    margin-bottom: 16px;
}
</style>""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Top Navigation & Interactive Trilingual Language Selector
# ---------------------------------------------------------
nav_col1, nav_col2 = st.columns([2.0, 1.4])

with nav_col1:
    st.markdown(
        """<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
<span style="font-size: 26px;">🚆</span>
<span style="font-size: 24px; font-weight: 800; color: #0f172a; letter-spacing: -0.5px;">RailPulse AI</span>
<span style="background: #e0f2fe; color: #0369a1; font-weight: 700; font-size: 11px; padding: 4px 10px; border-radius: 999px;">ADY AZERBAIJAN</span>
<span style="background: #fef08a; color: #713f12; font-weight: 700; font-size: 11px; padding: 4px 10px; border-radius: 999px;">● LIVE DISPATCH</span>
</div>""",
        unsafe_allow_html=True,
    )

with nav_col2:
    st.markdown("<div style='text-align: right; margin-bottom: 4px; font-size: 11px; font-weight: 700; color: #64748b;'>CLICK TO SWITCH LANGUAGE / DİL / ЯЗЫК:</div>", unsafe_allow_html=True)
    lang_btn1, lang_btn2, lang_btn3 = st.columns(3)
    with lang_btn1:
        if st.button("🇬🇧 EN", type="primary" if st.session_state["lang"] == "EN" else "secondary", use_container_width=True):
            st.session_state["lang"] = "EN"
            st.rerun()
    with lang_btn2:
        if st.button("🇦🇿 AZ", type="primary" if st.session_state["lang"] == "AZ" else "secondary", use_container_width=True):
            st.session_state["lang"] = "AZ"
            st.rerun()
    with lang_btn3:
        if st.button("🇷🇺 RU", type="primary" if st.session_state["lang"] == "RU" else "secondary", use_container_width=True):
            st.session_state["lang"] = "RU"
            st.rerun()

lang = st.session_state["lang"]

# ---------------------------------------------------------
# Sidebar: Live Corridor Simulator Controls
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
# Trilingual Localization Dictionary
# ---------------------------------------------------------
I18N = {
    "EN": {
        "tagline": "Azerbaijan Railways (ADY) High-Speed Corridor • Open-Weights Gemma • Google ADK • Cloud Run",
        "running_now": "ADY FLEET CORRIDORS (Click to Select)",
        "speed_clamped": f"↓ Clamped ({advisory.approved_speed_kmh - requested_speed} km/h)",
        "speed_clear": "✓ Normal Speed",
        "siding_alert": "⚠️ Passing Loop Siding",
        "main_line": "✓ Main Line",
        "timeline_title": f"STATION PROGRESSION · {LIVE_TRAINS[selected_train]['route_name']}",
        "announcement_hdr": "📢 Passenger Station Board Announcement (ADY Audio Synthesizer)",
        "announcement_body": advisory.passenger_announcement,
        "audit_hdr": "🛡️ Deterministic Railway Interlock Audit",
        "map_hdr": "🗺️ Live Azerbaijan Railways (ADY) Network Map",
        "chat_title": "💬 Gemma Rail Copilot (Live Departure & Schedule Q&A)",
        "chat_placeholder": "Ask about departure times, train availability, or weather...",
    },
    "AZ": {
        "tagline": "Azərbaycan Dəmir Yolları (ADY) • Açıq Gemma Modeli • Google ADK • Cloud Run",
        "running_now": "ADY QATAR MARŞRUTLARI (Seçmək üçün klikləyin)",
        "speed_clamped": f"↓ Məhdudlaşdırıldı ({advisory.approved_speed_kmh - requested_speed} km/s)",
        "speed_clear": "✓ Təhlükəsiz Sürət",
        "siding_alert": "⚠️ Ehtiyat Yan Xətt",
        "main_line": "✓ Əsas Xətt",
        "timeline_title": f"MARŞRUT VƏ STANSİYA HƏRƏKƏTİ · {LIVE_TRAINS[selected_train]['route_name']}",
        "announcement_hdr": "📢 Stansiya Sərnişin Məlumat Lövhəsi (ADY Səsli Bildiriş)",
        "announcement_body": f"Diqqət, sərnişinlərin nəzərinə! {LIVE_TRAINS[selected_train]['route_name']} qatarı ({advisory.train_id}) {advisory.assigned_block_id} blokuna təyin edildi. Təhlükəsiz sürət həddi: {advisory.approved_speed_kmh} km/saat. Yenilənmiş çatma vaxtı: {advisory.updated_eta}.",
        "audit_hdr": "🛡️ Deterministik Dəmiryolu Təhlükəsizlik Auditi",
        "map_hdr": "🗺️ Azərbaycan Dəmir Yolları (ADY) Canlı Şəbəkə Xəritəsi",
        "chat_title": "💬 Gemma Dəmiryolu Köməkçisi (Real Vaxt Çıxış və Cədvəl)",
        "chat_placeholder": "Çıxış vaxtları, qatar cədvəli və ya hava haqqında soruşun...",
    },
    "RU": {
        "tagline": "Азербайджанские Железные Дороги (ADY) • Open-Weights Gemma • Google ADK • Cloud Run",
        "running_now": "АКТИВНЫЕ МАРШРУТЫ ПОЕЗДОВ АЖД (Нажмите для выбора)",
        "speed_clamped": f"↓ Ограничено ({advisory.approved_speed_kmh - requested_speed} км/ч)",
        "speed_clear": "✓ В пределах нормы",
        "siding_alert": "⚠️ Боковой разъезд",
        "main_line": "✓ Главный путь",
        "timeline_title": f"МАРШРУТ И ПРОХОЖДЕНИЕ СТАНЦИЙ · {LIVE_TRAINS[selected_train]['route_name']}",
        "announcement_hdr": "📢 Вокзальное Табло и Оповещение Пассажиров (Аудиосинтезатор)",
        "announcement_body": f"Внимание пассажиров! Поезд {LIVE_TRAINS[selected_train]['route_name']} ({advisory.train_id}) направлен на блок {advisory.assigned_block_id}. Безопасная скорость: {advisory.approved_speed_kmh} км/ч. Новое время прибытия: {advisory.updated_eta}.",
        "audit_hdr": "🛡️ Аудит Детерминированных Блокировок Безопасности",
        "map_hdr": "🗺️ Интерактивная Карта Сети Азербайджанских Железных Дорог",
        "chat_title": "💬 Gemma Rail Copilot (Расписание и Отправления Онлайн)",
        "chat_placeholder": "Спросите о времени отправления, расписании или погоде...",
    },
}

t = I18N[lang]

# ---------------------------------------------------------
# Two-Column Layout: Left Fleet & AI Dispatch, Right Route Timeline & Map
# ---------------------------------------------------------
col_left, col_right = st.columns([1.05, 1.35])

with col_left:
    st.markdown(f"#### 🚄 **{t['running_now']}**")

    # Interactive Clickable Train Selection Buttons
    btn_104_col, btn_702_col, btn_410_col = st.columns(3)
    with btn_104_col:
        style_104 = "primary" if selected_train == "ADY-104" else "secondary"
        if st.button("🚆 ADY-104\nAbsheron", type=style_104, use_container_width=True):
            st.session_state["active_train"] = "ADY-104"
            st.rerun()
    with btn_702_col:
        style_702 = "primary" if selected_train == "ADY-702" else "secondary"
        if st.button("⚡ ADY-702\nBaku-Ganja", type=style_702, use_container_width=True):
            st.session_state["active_train"] = "ADY-702"
            st.rerun()
    with btn_410_col:
        style_410 = "primary" if selected_train == "ADY-410" else "secondary"
        if st.button("🌍 ADY-410\nSilk Road", type=style_410, use_container_width=True):
            st.session_state["active_train"] = "ADY-410"
            st.rerun()

    # Active Train Summary Card
    st.markdown(
        f"""<div style="background: white; border: 1.5px solid #0284c7; border-radius: 14px; padding: 14px 18px; margin: 12px 0 16px 0; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.08);">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<div style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700;">Selected Active Train</div>
<div style="font-size: 18px; font-weight: 800; color: #0f172a;">{LIVE_TRAINS[selected_train]['route_name']}</div>
<div style="font-size: 13px; color: #0284c7; font-weight: 600;">{LIVE_TRAINS[selected_train]['current_station']} → {LIVE_TRAINS[selected_train]['next_station']}</div>
</div>
<div style="text-align: right;">
<div style="font-size: 22px; font-weight: 800; color: #0f172a;">{advisory.approved_speed_kmh} <span style="font-size: 13px;">km/h</span></div>
<span style="font-size: 11px; font-weight: 700; background: #e0f2fe; color: #0369a1; padding: 3px 8px; border-radius: 6px;">ETA {advisory.updated_eta}</span>
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # Interactive Gemma Rail Copilot Chat Assistant
    # -----------------------------------------------------
    st.markdown(f"#### {t['chat_title']}")
    
    # Quick prompt suggestion pills
    q_col1, q_col2, q_col3 = st.columns(3)
    user_prompt = None
    with q_col1:
        if st.button("🕒 Sumgayit Next?", use_container_width=True):
            user_prompt = "When is the next train to Sumgayit?"
    with q_col2:
        if st.button("⚡ Ganja Schedule?", use_container_width=True):
            user_prompt = "What is the schedule for Baku-Ganja?"
    with q_col3:
        if st.button("📋 All Departures", use_container_width=True):
            user_prompt = "Show all available train departures"

    # Chat Input field
    text_input = st.chat_input(t["chat_placeholder"])
    if text_input:
        user_prompt = text_input

    # Process chat query
    if user_prompt:
        st.session_state["chat_history"].append({"role": "user", "content": user_prompt})
        response = answer_rail_chat_query(user_prompt, lang=lang)
        st.session_state["chat_history"].append({"role": "assistant", "content": response})

    # Render recent chat messages (scrollable container)
    chat_container = st.container(height=260)
    with chat_container:
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    st.markdown("---")

    # Announcement Card
    st.markdown(
        f"""<div class="announcement-card">
<div style="font-weight: 800; font-size: 11.5px; text-transform: uppercase; color: #1e40af; margin-bottom: 5px;">
{t['announcement_hdr']}
</div>
{t['announcement_body']}
</div>""",
        unsafe_allow_html=True,
    )

    # Guardrail Audit Card
    is_clamped = advisory.approved_speed_kmh != requested_speed
    is_siding = "SIDING" in advisory.assigned_block_id
    audit_class = "audit-card-warn" if (is_clamped or is_siding) else "audit-card-safe"
    audit_icon = "⚠️" if (is_clamped or is_siding) else "🛡️"

    st.markdown(
        f"""<div class="{audit_class}">
<div style="font-weight: 800; font-size: 11.5px; text-transform: uppercase; margin-bottom: 4px;">
{audit_icon} {t['audit_hdr']}
</div>
<code>{advisory.guardrail_intervention_summary}</code>
</div>""",
        unsafe_allow_html=True,
    )

    with st.expander("🤖 Ordered Google ADK Function Trajectory"):
        for idx, tool_name in enumerate(advisory.tools_invoked, start=1):
            st.markdown(f"**Step {idx}:** `{tool_name}()`")

    with st.expander("📄 Validated Structured JSON (`RailDispatchAdvisory`)"):
        st.code(json.dumps(advisory.model_dump(), indent=2), language="json")

with col_right:
    st.markdown(f"#### 🚉 **{t['timeline_title']}**")

    # Multilingual Station Names
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
        node_str = f'<div class="station-node"><div class="node-circle {dot_class}">{icon}</div><div style="font-size: 13px; font-weight: 700;">{s["name"]}</div><div style="font-size: 11px; color: #64748b;">{s["time"]}</div></div>'
        nodes_html.append(node_str)

    progress_pct = 50 if selected_train == "ADY-104" else (70 if selected_train == "ADY-702" else 45)

    timeline_full_html = f'<div class="rp-card" style="padding: 14px 16px;"><div class="timeline-box"><div class="timeline-line"></div><div class="timeline-fill" style="width: {progress_pct}%;"></div>' + ''.join(nodes_html) + '</div></div>'
    st.markdown(timeline_full_html, unsafe_allow_html=True)

    st.markdown(f"#### 🗺️ **{t['map_hdr']}**")

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
