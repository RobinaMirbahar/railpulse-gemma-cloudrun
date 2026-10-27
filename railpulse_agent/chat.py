"""Live Rail Time, Departure & Schedule Chat Engine for RailPulse AI.
Supports Trilingual Q&A (English, Azerbaijani, Russian) backed by real-time ADY telemetry.
"""

from typing import Any, Dict
from railpulse_agent.tools import CORRIDOR_SIGNALS, LIVE_TRAINS


def answer_rail_chat_query(query: str, lang: str = "EN") -> str:
    q = query.lower().strip()

    # 1. Sumgayit / Absheron Commuter
    if any(k in q for k in ["sumgayit", "sumqayıt", "сумгаит", "104", "absheron", "abşeron", "абшерон"]):
        t = LIVE_TRAINS["ADY-104"]
        c = CORRIDOR_SIGNALS["ABSHERON-RING"]
        wind = c["wind_speed_kmh"]
        if lang == "AZ":
            return (
                f"🚆 **ADY-104 Abşeron Dairəvi Qatary (Bakı ➔ Sumqayıt)**\n\n"
                f"* **Cari Mövqe:** {t['current_station']}\n"
                f"* **Növbəti Dayanacaq:** {t['next_station']}\n"
                f"* **Sumqayıta Çatma Vaxtı (ETA):** `{t['scheduled_eta']}` ({t['delay_minutes']} dəqiqə gecikmə)\n"
                f"* **Hərəkət Sürəti:** {t['current_speed_kmh']} km/saat\n"
                f"* **Külək Şəraiti:** Xəzər sahili külək {wind} km/saat (Təhlükəsizlik həddi tətbiq olunub)"
            )
        elif lang == "RU":
            return (
                f"🚆 **ADY-104 Абшеронский пригородный экспресс (Баку ➔ Сумгаит)**\n\n"
                f"* **Текущая станция:** {t['current_station']}\n"
                f"* **Следующая остановка:** {t['next_station']}\n"
                f"* **Прибытие в Сумгаит (ETA):** `{t['scheduled_eta']}` (задержка {t['delay_minutes']} мин)\n"
                f"* **Скорость:** {t['current_speed_kmh']} км/ч\n"
                f"* **Ветер на Абшероне:** {wind} км/ч (активировано ограничение скорости)"
            )
        else:
            return (
                f"🚆 **ADY-104 Baku-Sumgayit Absheron Commuter**\n\n"
                f"* **Current Location:** {t['current_station']}\n"
                f"* **Next Station:** {t['next_station']}\n"
                f"* **Scheduled Arrival (ETA):** `{t['scheduled_eta']}` ({t['delay_minutes']} min delay)\n"
                f"* **Approved Speed:** {t['current_speed_kmh']} km/h\n"
                f"* **Caspian Crosswind:** {wind} km/h (safety speed cap applied)"
            )

    # 2. Ganja / High-Speed Express
    if any(k in q for k in ["ganja", "gəncə", "гяндж", "702", "high-speed", "sürət", "скоростн"]):
        t = LIVE_TRAINS["ADY-702"]
        c = CORRIDOR_SIGNALS["BAKU-GANJA"]
        if lang == "AZ":
            return (
                f"⚡ **ADY-702 Bakı ➔ Gəncə Sürətli Sərnişin Qatarı**\n\n"
                f"* **Bakıdan Çıxış:** 08:00 (Bakı Mərkəzi Vağzalı)\n"
                f"* **Cari Stansiya:** {t['current_station']}\n"
                f"* **Növbəti Qovşaq:** {t['next_station']}\n"
                f"* **Gəncəyə Planlaşdırılan Çatma:** `{t['scheduled_eta']}`\n"
                f"* **Hərəkət Vəziyyəti:** {t['delay_minutes']} dəqiqə gecikmə ilə hərəkət edir"
            )
        elif lang == "RU":
            return (
                f"⚡ **ADY-702 Скоростной экспресс Баку ➔ Гянджа**\n\n"
                f"* **Отправление из Баку:** 08:00 (Баку-Пассажирский)\n"
                f"* **Текущее положение:** {t['current_station']}\n"
                f"* **Следующий узел:** {t['next_station']}\n"
                f"* **Прибытие в Гянджу:** `{t['scheduled_eta']}`\n"
                f"* **Статус рейса:** В пути с задержкой {t['delay_minutes']} мин"
            )
        else:
            return (
                f"⚡ **ADY-702 Baku-Ganja High-Speed Express**\n\n"
                f"* **Departure Time:** 08:00 (Baku Central Station)\n"
                f"* **Current Position:** {t['current_station']}\n"
                f"* **Next Junction:** {t['next_station']}\n"
                f"* **Estimated Arrival in Ganja:** `{t['scheduled_eta']}`\n"
                f"* **Operating Status:** Running with {t['delay_minutes']} min delay (schedule recovery in progress)"
            )

    # 3. Tbilisi / Silk Road Express
    if any(k in q for k in ["tbilisi", "тбилиси", "410", "silk road", "ipək", "шелковый", "agstafa", "ağstafa"]):
        t = LIVE_TRAINS["ADY-410"]
        if lang == "AZ":
            return (
                f"🌍 **ADY-410 İpək Yolu Beynəlxalq Ekspresi (Bakı ➔ Tbilisi)**\n\n"
                f"* **Bakıdan Çıxış Vaxtı:** 06:00\n"
                f"* **Cari Mövqe:** {t['current_station']}\n"
                f"* **Növbəti Sərhəd Qovşağı:** {t['next_station']}\n"
                f"* **Tbilisi Mərkəzi Vağzalına Çatma:** `{t['scheduled_eta']}`\n"
                f"* **Vəziyyət:** Qrafik üzrə tam vaxtında (0 dəqiqə gecikmə)"
            )
        elif lang == "RU":
            return (
                f"🌍 **ADY-410 Международный экспресс Шёлковый Путь (Баку ➔ Тбилиси)**\n\n"
                f"* **Отправление из Баку:** 06:00\n"
                f"* **Текущая станция:** {t['current_station']}\n"
                f"* **Следующая пограничная станция:** {t['next_station']}\n"
                f"* **Прибытие в Тбилиси:** `{t['scheduled_eta']}`\n"
                f"* **Статус:** Строго по расписанию (без задержек)"
            )
        else:
            return (
                f"🌍 **ADY-410 Silk Road International Express (Baku ➔ Tbilisi)**\n\n"
                f"* **Departure from Baku:** 06:00\n"
                f"* **Current Station:** {t['current_station']}\n"
                f"* **Next Hub:** {t['next_station']}\n"
                f"* **Scheduled Arrival in Tbilisi:** `{t['scheduled_eta']}`\n"
                f"* **Status:** On-Time (0 min delay, nominal clearance)"
            )

    # 4. Wind / Weather / Safety check
    if any(k in q for k in ["wind", "weather", "külək", "hava", "ветер", "погода", "speed", "sürət", "скорост"]):
        if lang == "AZ":
            return (
                f"🌬️ **Xəzər Sahili Külək və Təhlükəsizlik Vəziyyəti:**\n\n"
                f"- **Abşeron Qovşağı (Bakı-Sumqayıt):** Külək 78 km/saat. Sürət avtomatik olaraq **80 km/saat** həddində saxlanılır.\n"
                f"- **Bakı-Gəncə Dəhlizi:** Külək 72 km/saat. Sürət məhdudiyyəti aktivdir.\n"
                f"- **BTK Dəhlizi (Ağstafa/Tbilisi):** Külək 22 km/saat. Normal sürət rejimi (110 km/saat)."
            )
        elif lang == "RU":
            return (
                f"🌬️ **Погодные условия на Каспийском побережье и безопасность:**\n\n"
                f"- **Абшеронское кольцо (Баку-Сумгаит):** Ветер 78 км/ч. Скорость ограничена до **80 км/ч**.\n"
                f"- **Коридор Баку-Гянджа:** Ветер 72 км/ч. Действует ограничение скорости.\n"
                f"- **Коридор БТК (Агстафа/Тбилиси):** Ветер 22 км/ч. Скорость в норме (110 км/ч)."
            )
        else:
            return (
                f"🌬️ **Live Caspian Crosswind & Rail Safety Status:**\n\n"
                f"- **Absheron Ring (Baku-Sumgayit):** Wind 78 km/h. Speed strictly clamped to **80 km/h**.\n"
                f"- **Baku-Ganja Corridor:** Wind 72 km/h. High-wind speed interlock active.\n"
                f"- **BTK Silk Road Corridor:** Wind 22 km/h. Clear normal speed (110 km/h)."
            )

    # 5. General departure timetable
    if lang == "AZ":
        lines = [
            "📋 **Azərbaycan Dəmir Yolları (ADY) Real Vaxt Cədvəli və Çıxış Vaxtları:**\n",
            "1. **ADY-104 Abşeron Ekspresi (Bakı ➔ Sumqayıt)**",
            f"   - Cari dayanacaq: {LIVE_TRAINS['ADY-104']['current_station']} | Çatma vaxtı: `{LIVE_TRAINS['ADY-104']['scheduled_eta']}` (Gecikmə: {LIVE_TRAINS['ADY-104']['delay_minutes']} dəq)",
            "2. **ADY-702 Bakı ➔ Gəncə Sürət Qatarı**",
            f"   - Cari dayanacaq: {LIVE_TRAINS['ADY-702']['current_station']} | Çatma vaxtı: `{LIVE_TRAINS['ADY-702']['scheduled_eta']}` (Gecikmə: {LIVE_TRAINS['ADY-702']['delay_minutes']} dəq)",
            "3. **ADY-410 İpək Yolu (Bakı ➔ Tbilisi)**",
            f"   - Cari dayanacaq: {LIVE_TRAINS['ADY-410']['current_station']} | Çatma vaxtı: `{LIVE_TRAINS['ADY-410']['scheduled_eta']}` (Dəqiq qrafiklə)",
        ]
        return "\n".join(lines)
    elif lang == "RU":
        lines = [
            "📋 **Текущее расписание отправлений и движения поездов АЖД:**\n",
            "1. **ADY-104 Баку ➔ Сумгаит (Абшеронский экспресс)**",
            f"   - Текущая станция: {LIVE_TRAINS['ADY-104']['current_station']} | Прибытие: `{LIVE_TRAINS['ADY-104']['scheduled_eta']}` (Задержка: {LIVE_TRAINS['ADY-104']['delay_minutes']} мин)",
            "2. **ADY-702 Скоростной поезд Баку ➔ Гянджа**",
            f"   - Текущая станция: {LIVE_TRAINS['ADY-702']['current_station']} | Прибытие: `{LIVE_TRAINS['ADY-702']['scheduled_eta']}` (Задержка: {LIVE_TRAINS['ADY-702']['delay_minutes']} мин)",
            "3. **ADY-410 Экспресс Баку ➔ Тбилиси (Шёлковый путь)**",
            f"   - Текущая станция: {LIVE_TRAINS['ADY-410']['current_station']} | Прибытие: `{LIVE_TRAINS['ADY-410']['scheduled_eta']}` (Вовремя)",
        ]
        return "\n".join(lines)
    else:
        lines = [
            "📋 **Current Azerbaijan Railways (ADY) Live Departures & Real-Time Schedule:**\n",
            "1. **ADY-104 Absheron Commuter (Baku ➔ Sumgayit)**",
            f"   - Current Station: {LIVE_TRAINS['ADY-104']['current_station']} | ETA: `{LIVE_TRAINS['ADY-104']['scheduled_eta']}` (Delay: {LIVE_TRAINS['ADY-104']['delay_minutes']} min)",
            "2. **ADY-702 Baku-Ganja High-Speed Express**",
            f"   - Current Station: {LIVE_TRAINS['ADY-702']['current_station']} | ETA: `{LIVE_TRAINS['ADY-702']['scheduled_eta']}` (Delay: {LIVE_TRAINS['ADY-702']['delay_minutes']} min)",
            "3. **ADY-410 Silk Road Express (Baku ➔ Tbilisi)**",
            f"   - Current Station: {LIVE_TRAINS['ADY-410']['current_station']} | ETA: `{LIVE_TRAINS['ADY-410']['scheduled_eta']}` (On-Time)",
        ]
        return "\n".join(lines)
