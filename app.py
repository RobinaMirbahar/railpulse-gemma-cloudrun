"""RailPulse AI — Autonomous Rail Telemetry & Smart Dispatch Agent for Azerbaijan Railways (ADY).

Built with Open-Weights Gemma, Google ADK Function Calling, Deterministic Railway Interlocks, and Google Cloud Run.
Trilingual: English • Azerbaijani (Azərbaycan dili) • Russian (Русский язык).
"""

import json
import pandas as pd
import streamlit as st

from railpulse_agent.agent import run_railpulse_dispatch
from railpulse_agent.tools import CORRIDOR_SIGNALS, LIVE_TRAINS

st.set_page_config(
    page_title="RailPulse AI · ADY Azerbaijan Railways",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Custom Modern Transit Design System (Caspian Teal & Sky Palette)
# ---------------------------------------------------------
st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Barlow+Condensed:wght@600;700;800&display=swap');

:root {
    --ground: #f6f8fb;
    --surface: #ffffff;
    --ink: #0f172a;
    --ink-muted: #64748b;
    --line: #e2e8f0;
    --caspian-blue: #0284c7;
    --baku-teal: #0d9488;
    --baku-gold: #f59e0b;
    --emerald-green: #10b981;
    --alert-rose: #f43f5e;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--ink);
}

.stApp {
    background-color: var(--ground);
}

/* Unique RailPulse Header */
.rp-header {
    background: linear-gradient(135deg, #0284c7 0%, #0d9488 50%, #059669 100%);
    padding: 22px 28px;
    border-radius: 20px;
    color: white;
    margin-bottom: 22px;
    box-shadow: 0 10px 28px rgba(2, 132, 199, 0.2);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
    border: 1px solid rgba(255, 255, 255, 0.25);
}

.rp-header h1 {
    color: #ffffff;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.3px;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.rp-header p {
    color: #e0f2fe;
    font-size: 13.5px;
    font-weight: 500;
    margin: 4px 0 0 0;
}

.live-pill {
    background: #fef08a;
    color: #854d0e;
    font-weight: 800;
    font-size: 11.5px;
    padding: 6px 14px;
    border-radius: 999px;
    letter-spacing: 0.6px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.live-dot {
    width: 8px;
    height: 8px;
    background: #eab308;
    border-radius: 50%;
    animation: livePulse 1.5s infinite;
}

@keyframes livePulse {
    0% { transform: scale(0.95); opacity: 1; }
    50% { transform: scale(1.35); opacity: 0.6; }
    100% { transform: scale(0.95); opacity: 1; }
}

/* Clean Cards */
.rp-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.03);
    margin-bottom: 18px;
}

/* Fleet Mini-Cards */
.fleet-card {
    background: var(--surface);
    border: 1.5px solid var(--line);
    border-radius: 14px;
    padding: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    transition: all 0.15s ease;
}

.fleet-card-active {
    border-color: #0284c7;
    background: #f0f9ff;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.12);
}

.fleet-badge {
    background: #0f172a;
    color: #facc15;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 17px;
    font-weight: 800;
    padding: 4px 8px;
    border-radius: 8px;
    min-width: 42px;
    text-align: center;
}

.status-badge {
    font-size: 11.5px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 999px;
    text-transform: uppercase;
}

.status-late {
    background: #ffe4e6;
    color: #e11d48;
}

.status-ontime {
    background: #e0f2fe;
    color: #0284c7;
}

.status-recovered {
    background: #dcfce7;
    color: #15803d;
}

/* Timeline */
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
    background: linear-gradient(90deg, #0284c7, #10b981);
    border-radius: 999px;
    z-index: 2;
}

.station-item {
    position: relative;
    z-index: 3;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    min-width: 85px;
}

.station-circle {
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

.circle-passed {
    background: #10b981;
    color: white;
}

.circle-current {
    background: #facc15;
    color: #713f12;
    transform: scale(1.22);
    border: 2px solid #0d9488;
    animation: livePulse 1.8s infinite;
}

.circle-upcoming {
    background: white;
    color: #94a3b8;
    border: 2px solid #cbd5e1;
}

/* Announcements & Audits */
.announcement-box {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    border: 1px solid #fde68a;
    border-left: 5px solid #f59e0b;
    padding: 16px 20px;
    border-radius: 14px;
    color: #78350f;
    font-size: 14.5px;
    line-height: 1.5;
    margin-bottom: 16px;
}

.audit-box-pass {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 5px solid #22c55e;
    padding: 14px 18px;
    border-radius: 14px;
    color: #166534;
    font-size: 13.5px;
    margin-bottom: 16px;
}

.audit-box-warn {
    background: #fff1f2;
    border: 1px solid #fecdd3;
    border-left: 5px solid #f43f5e;
    padding: 14px 18px;
    border-radius: 14px;
    color: #9f1239;
    font-size: 13.5px;
    margin-bottom: 16px;
}
</style>""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar: Trilingual Selector & Live Corridor Simulator
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌐 **Language / Dil / Язык**")
    lang = st.radio(
        "Choose Display Language",
        options=["EN", "AZ", "RU"],
        format_func=lambda x: {"EN": "🇬🇧 English", "AZ": "🇦🇿 Azərbaycan", "RU": "🇷🇺 Русский"}[x],
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### 🎛️ **Live Corridor Simulator**")
    st.caption(
        "Simulate live weather conditions and track occupancy in real-time:"
        if lang == "EN"
        else ("Hava şəraiti və xətt məşğulluğunu real vaxtda simulyasiya edin:" if lang == "AZ" else "Симуляция погодных условий и занятости путей в реальном времени:")
    )

    selected_train = st.selectbox(
        "Select Active ADY Train" if lang == "EN" else ("Aktiv ADY Qatarını Seçin" if lang == "AZ" else "Выберите поезд АЖД"),
        options=["ADY-104", "ADY-702", "ADY-410"],
        format_func=lambda x: f"{x} — {LIVE_TRAINS[x]['route_name']}",
    )

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
    with col_p2:
        if st.button("🚧 Track Blocked", use_container_width=True):
            st.session_state["block_select"] = "OCCUPIED"
            st.session_state["speed_slider"] = 110

    if st.button("☀️ Clear Sky Normal", use_container_width=True):
        st.session_state["wind_slider"] = 28
        st.session_state["block_select"] = "FREE"
        st.session_state["speed_slider"] = 120

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
# Trilingual Translation Dictionary
# ---------------------------------------------------------
I18N = {
    "EN": {
        "title": "RailPulse AI — Live Rail Tracking & Smart Dispatch Agent",
        "subtitle": "Azerbaijan Railways (ADY) High-Speed Corridor • Open-Weights Gemma • Google ADK • Cloud Run",
        "live_badge": "ADY REAL-TIME DISPATCH",
        "running_now": "ACTIVE ADY FLEET CORRIDORS",
        "speed_clamped": f"↓ Clamped ({advisory.approved_speed_kmh - requested_speed} km/h)",
        "speed_clear": "✓ Normal Speed",
        "siding_alert": "⚠️ Passing Loop Siding",
        "main_line": "✓ Main Line",
        "timeline_title": f"ROUTE & STATION PROGRESSION · {LIVE_TRAINS[selected_train]['route_name']}",
        "announcement_hdr": "📢 Passenger Station Board Announcement (ADY Audio Synthesizer)",
        "announcement_body": advisory.passenger_announcement,
        "audit_hdr": "🛡️ Deterministic Railway Interlock Audit",
        "map_hdr": "🗺️ Live Azerbaijan Railways (ADY) Network Map",
    },
    "AZ": {
        "title": "RailPulse AI — Dəmiryolu İzləmə və Ağıllı Dispetçer Agenti",
        "subtitle": "Azərbaycan Dəmir Yolları (ADY) • Açıq Gemma Modeli • Google ADK • Cloud Run",
        "live_badge": "ADY CANLI DİSPETÇER",
        "running_now": "AKTİV ADY QATAR MARŞRUTLARI",
        "speed_clamped": f"↓ Məhdudlaşdırıldı ({advisory.approved_speed_kmh - requested_speed} km/s)",
        "speed_clear": "✓ Təhlükəsiz Sürət",
        "siding_alert": "⚠️ Ehtiyat Yan Xətt",
        "main_line": "✓ Əsas Yol",
        "timeline_title": f"MARŞRUT VƏ STANSİYA HƏRƏKƏTİ · {LIVE_TRAINS[selected_train]['route_name']}",
        "announcement_hdr": "📢 Stansiya Sərnişin Məlumat Lövhəsi (ADY Səsli Bildiriş)",
        "announcement_body": f"Diqqət, sərnişinlərin nəzərinə! {LIVE_TRAINS[selected_train]['route_name']} qatarı ({advisory.train_id}) {advisory.assigned_block_id} blokuna təyin edildi. Sürət həddi: {advisory.approved_speed_kmh} km/saat. Yenilənmiş çatma vaxtı: {advisory.updated_eta}.",
        "audit_hdr": "🛡️ Deterministik Dəmiryolu Təhlükəsizlik Auditi",
        "map_hdr": "🗺️ Azərbaycan Dəmir Yolları (ADY) Canlı Xəritəsi",
    },
    "RU": {
        "title": "RailPulse AI — Мониторинг Путей и Умный Диспетчер АЖД",
        "subtitle": "Азербайджанские Железные Дороги (ADY) • Open-Weights Gemma • Google ADK • Cloud Run",
        "live_badge": "АЖД ОНЛАЙН ДИСПЕТЧЕР",
        "running_now": "АКТИВНЫЕ МАРШРУТЫ ПОЕЗДОВ АЖД",
        "speed_clamped": f"↓ Ограничено ({advisory.approved_speed_kmh - requested_speed} км/ч)",
        "speed_clear": "✓ В пределах нормы",
        "siding_alert": "⚠️ Боковой путь разъезда",
        "main_line": "✓ Главный путь",
        "timeline_title": f"МАРШРУТ И ПРОХОЖДЕНИЕ СТАНЦИЙ · {LIVE_TRAINS[selected_train]['route_name']}",
        "announcement_hdr": "📢 Вокзальное Табло и Оповещение Пассажиров (Аудиосинтезатор)",
        "announcement_body": f"Внимание пассажиров! Поезд {LIVE_TRAINS[selected_train]['route_name']} ({advisory.train_id}) направлен на блок {advisory.assigned_block_id}. Утвержденная скорость: {advisory.approved_speed_kmh} км/ч. Новое время прибытия: {advisory.updated_eta}.",
        "audit_hdr": "🛡️ Аудит Детерминированных Блокировок Безопасности",
        "map_hdr": "🗺️ Интерактивная Карта Сети Азербайджанских Железных Дорог",
    },
}

t = I18N[lang]

# ---------------------------------------------------------
# Custom Modern Header Banner
# ---------------------------------------------------------
header_html = f"""<div class="rp-header">
<div>
<h1>
<svg width="32" height="22" viewBox="0 0 40 22" fill="none">
<rect x="2" y="4" width="28" height="12" rx="3" fill="#ffffff"/>
<rect x="30" y="7" width="7" height="9" rx="2" fill="#ffffff"/>
<circle cx="8" cy="18" r="3" fill="#fef08a"/>
<circle cx="18" cy="18" r="3" fill="#fef08a"/>
<circle cx="28" cy="18" r="3" fill="#fef08a"/>
<circle cx="34" cy="18" r="2" fill="#fef08a"/>
<rect x="6" y="7" width="5" height="4" rx="1" fill="#0284c7"/>
<rect x="14" y="7" width="5" height="4" rx="1" fill="#0284c7"/>
<rect x="22" y="7" width="5" height="4" rx="1" fill="#0284c7"/>
<line x1="2" y1="12" x2="30" y2="12" stroke="#fef08a" stroke-width="2"/>
</svg>
{t['title']}
</h1>
<p>{t['subtitle']}</p>
</div>
<div style="display: flex; gap: 10px; align-items: center;">
<span class="live-pill">
<span class="live-dot"></span>
{t['live_badge']}
</span>
</div>
</div>"""
st.markdown(header_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# Two-Column Layout: Left Fleet & AI Dispatch, Right Route Timeline & Map
# ---------------------------------------------------------
col_left, col_right = st.columns([1.05, 1.35])

with col_left:
    st.markdown(f"#### 🚄 **{t['running_now']}**")

    # ADY-104 Card
    c104_active = "fleet-card-active" if selected_train == "ADY-104" else ""
    st.markdown(
        f"""<div class="fleet-card {c104_active}">
<div style="display: flex; align-items: center; gap: 12px;">
<div class="fleet-badge">104</div>
<div>
<div style="font-weight: 700; font-size: 15px;">Baku-Sumgayit Absheron</div>
<div style="font-size: 12px; color: #64748b;">Bilajari Jn → Sumgayit Pass.</div>
</div>
</div>
<span class="status-badge status-late">12m delay</span>
</div>""",
        unsafe_allow_html=True,
    )

    # ADY-702 Card
    c702_active = "fleet-card-active" if selected_train == "ADY-702" else ""
    st.markdown(
        f"""<div class="fleet-card {c702_active}">
<div style="display: flex; align-items: center; gap: 12px;">
<div class="fleet-badge">702</div>
<div>
<div style="font-weight: 700; font-size: 15px;">Baku-Ganja High-Speed</div>
<div style="font-size: 12px; color: #64748b;">Yevlakh Jn → Ganja Central</div>
</div>
</div>
<span class="status-badge status-late">18m delay</span>
</div>""",
        unsafe_allow_html=True,
    )

    # ADY-410 Card
    c410_active = "fleet-card-active" if selected_train == "ADY-410" else ""
    st.markdown(
        f"""<div class="fleet-card {c410_active}">
<div style="display: flex; align-items: center; gap: 12px;">
<div class="fleet-badge">410</div>
<div>
<div style="font-weight: 700; font-size: 15px;">Silk Road Express (BTK)</div>
<div style="font-size: 12px; color: #64748b;">Shamkir → Agstafa Border Hub</div>
</div>
</div>
<span class="status-badge status-ontime">On Time</span>
</div>""",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Announcement Box
    st.markdown(
        f"""<div class="announcement-box">
<div style="font-weight: 800; font-size: 11.5px; text-transform: uppercase; color: #b45309; margin-bottom: 5px;">
{t['announcement_hdr']}
</div>
{t['announcement_body']}
</div>""",
        unsafe_allow_html=True,
    )

    # Guardrail Audit Box
    is_clamped = advisory.approved_speed_kmh != requested_speed
    is_siding = "SIDING" in advisory.assigned_block_id
    audit_class = "audit-box-warn" if (is_clamped or is_siding) else "audit-box-pass"
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
        dot_class = f"circle-{s['status']}"
        icon = "✓" if s["status"] == "passed" else ("🚆" if s["status"] == "current" else str(idx))
        node_str = f'<div class="station-item"><div class="station-circle {dot_class}">{icon}</div><div style="font-size: 13px; font-weight: 700;">{s["name"]}</div><div style="font-size: 11px; color: #64748b;">{s["time"]}</div></div>'
        nodes_html.append(node_str)

    progress_pct = 50 if selected_train == "ADY-104" else (70 if selected_train == "ADY-702" else 45)

    timeline_full_html = f'<div class="rp-card" style="padding: 12px 16px;"><div class="timeline-box"><div class="timeline-line"></div><div class="timeline-fill" style="width: {progress_pct}%;"></div>' + ''.join(nodes_html) + '</div></div>'
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
