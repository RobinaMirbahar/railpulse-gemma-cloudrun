"""Live Rail Time, Departure & Schedule Chat Engine for RailPulse AI.
Supports Natural Conversational Greetings and Trilingual Q&A (English, Azerbaijani, Russian).
"""

from typing import Any, Dict
from railpulse_agent.tools import CORRIDOR_SIGNALS, LIVE_TRAINS


def answer_rail_chat_query(query: str, lang: str = "EN") -> str:
    q = query.lower().strip()

    # 1. Natural Conversational Greetings (Hi, Hello, Salam, Привет)
    greeting_keywords = [
        "hi", "hello", "hey", "hola", "good morning", "good afternoon", "good evening",
        "salam", "sabahiniz xeyir", "sabahınız xeyir", "hər vaxtınız xeyir",
        "привет", "здравствуйте", "добрый день", "доброе утро", "добрый вечер", "хай"
    ]
    # Check if the query is just a greeting
    words = q.replace("!", "").replace(".", "").replace("?", "").split()
    if any(q == g or (len(words) <= 3 and g in words) for g in greeting_keywords):
        if lang == "AZ":
            return (
                "👋 **Salam! RailPulse AI-a xoş gəlmisiniz.**

"
                "Mən Azərbaycan Dəmir Yolları (ADY) üzrə Gemma rəqəmsal dispetçer köməkçisiyəm. Sizə necə kömək edə bilərəm?
"
                "* 🕒 **Çıxış və çatma vaxtları** (məs. *"Sumqayıta növbəti qatar nə vaxtdır?"*)
"
                "* ⚡ **Qatarların hərəkət vəziyyəti** (məs. *"Bakı-Gəncə qatarı gecikir?"*)
"
                "* 🌬️ **Xəzər küləyi və təhlükəsizlik hədləri**

"
                "Sualınızı yazın və ya aşağıdakı hazır düymələrdən birini seçin!"
            )
        elif lang == "RU":
            return (
                "👋 **Здравствуйте! Добро пожаловать в RailPulse AI.**

"
                "Я цифровой диспетчер Gemma по сети Азербайджанских Железных Дорог (АЖД). Чем я могу помочь?
"
                "* 🕒 **Расписание и время отправления** (напр. *"Когда следующий поезд в Сумгаит?"*)
"
                "* ⚡ **Статус рейсов и задержки** (напр. *"Опаздывает ли рейс в Гянджу?"*)
"
                "* 🌬️ **Погода на Каспийском побережье и скорость**

"
                "Задайте любой вопрос или нажмите быструю кнопку ниже!"
            )
        else:
            return (
                "👋 **Hello! Welcome to RailPulse AI.**

"
                "I am Gemma, your autonomous rail operations copilot for Azerbaijan Railways (ADY). How can I help you today?
"
                "* 🕒 **Live departures & arrivals** (e.g. *"When is the next train to Sumgayit?"*)
"
                "* ⚡ **Train status & schedule recovery** (e.g. *"Is Baku-Ganja on time?"*)
"
                "* 🌬️ **Caspian crosswinds & safety limits** (e.g. *"Check weather restrictions"*)

"
                "Feel free to ask a question or tap one of the suggestion buttons below!"
            )

    # 2. Thank you / Polite closing
    thanks_keywords = ["thanks", "thank you", "thx", "təşəkkür", "sag ol", "sağ ol", "спасибо", "благодарю"]
    if any(k in q for k in thanks_keywords):
        if lang == "AZ":
            return "Xoşdur! Azərbaycan Dəmir Yolları ilə səyahətiniz uğurlu və təhlükəsiz olsun! 🚆🇦🇿"
        elif lang == "RU":
            return "Пожалуйста! Приятной и безопасной поездки по Азербайджанским Железным Дорогам! 🚆"
        else:
            return "You are very welcome! Have a safe and comfortable journey with Azerbaijan Railways! 🚆"

    # 3. Sumgayit / Absheron Commuter
    if any(k in q for k in ["sumgayit", "sumqayıt", "сумгаит", "104", "absheron", "abşeron", "абшерон"]):
        t = LIVE_TRAINS["ADY-104"]
        c = CORRIDOR_SIGNALS["ABSHERON-RING"]
        wind = c["wind_speed_kmh"]
        if lang == "AZ":
            return (
                f"🚆 **ADY-104 Abşeron Dairəvi Qatarı (Bakı ➔ Sumqayıt)**

"
                f"* **Cari Mövqe:** {t['current_station']}
"
                f"* **Növbəti Dayanacaq:** {t['next_station']}
"
                f"* **Sumqayıta Çatma Vaxtı (ETA):** `{t['scheduled_eta']}` ({t['delay_minutes']} dəqiqə gecikmə)
"
                f"* **Hərəkət Sürəti:** {t['current_speed_kmh']} km/saat
"
                f"* **Külək Şəraiti:** Xəzər sahili külək {wind} km/saat (Təhlükəsizlik həddi tətbiq olunub)"
            )
        elif lang == "RU":
            return (
                f"🚆 **ADY-104 Абшеронский пригородный экспресс (Баку ➔ Сумгаит)**

"
                f"* **Текущая станция:** {t['current_station']}
"
                f"* **Следующая остановка:** {t['next_station']}
"
                f"* **Прибытие в Сумгаит (ETA):** `{t['scheduled_eta']}` (задержка {t['delay_minutes']} мин)
"
                f"* **Скорость:** {t['current_speed_kmh']} км/ч
"
                f"* **Ветер на Абшероне:** {wind} км/ч (активировано ограничение скорости)"
            )
        else:
            return (
                f"🚆 **ADY-104 Baku-Sumgayit Absheron Commuter**

"
                f"* **Current Location:** {t['current_station']}
"
                f"* **Next Station:** {t['next_station']}
"
                f"* **Scheduled Arrival (ETA):** `{t['scheduled_eta']}` ({t['delay_minutes']} min delay)
"
                f"* **Approved Speed:** {t['current_speed_kmh']} km/h
"
                f"* **Caspian Crosswind:** {wind} km/h (safety speed cap applied)"
            )

    # 4. Ganja / High-Speed Express
    if any(k in q for k in ["ganja", "gəncə", "гяндж", "702", "high-speed", "sürət", "скоростн"]):
        t = LIVE_TRAINS["ADY-702"]
        c = CORRIDOR_SIGNALS["BAKU-GANJA"]
        if lang == "AZ":
            return (
                f"⚡ **ADY-702 Bakı ➔ Gəncə Sürətli Sərnişin Qatarı**

"
                f"* **Bakıdan Çıxış:** 08:00 (Bakı Mərkəzi Vağzalı)
"
                f"* **Cari Stansiya:** {t['current_station']}
"
                f"* **Növbəti Qovşaq:** {t['next_station']}
"
                f"* **Gəncəyə Planlaşdırılan Çatma:** `{t['scheduled_eta']}`
"
                f"* **Hərəkət Vəziyyəti:** {t['delay_minutes']} dəqiqə gecikmə ilə hərəkət edir"
            )
        elif lang == "RU":
            return (
                f"⚡ **ADY-702 Скоростной экспресс Баку ➔ Гянджа**

"
                f"* **Отправление из Баку:** 08:00 (Баку-Пассажирский)
"
                f"* **Текущее положение:** {t['current_station']}
"
                f"* **Следующий узел:** {t['next_station']}
"
                f"* **Прибытие в Гянджу:** `{t['scheduled_eta']}`
"
                f"* **Статус рейса:** В пути с задержкой {t['delay_minutes']} мин"
            )
        else:
            return (
                f"⚡ **ADY-702 Baku-Ganja High-Speed Express**

"
                f"* **Departure Time:** 08:00 (Baku Central Station)
"
                f"* **Current Position:** {t['current_station']}
"
                f"* **Next Junction:** {t['next_station']}
"
                f"* **Estimated Arrival in Ganja:** `{t['scheduled_eta']}`
"
                f"* **Operating Status:** Running with {t['delay_minutes']} min delay (schedule recovery in progress)"
            )

    # 5. Tbilisi / Silk Road Express
    if any(k in q for k in ["tbilisi", "тбилиси", "410", "silk road", "ipək", "шелковый", "agstafa", "ağstafa"]):
        t = LIVE_TRAINS["ADY-410"]
        if lang == "AZ":
            return (
                f"🌍 **ADY-410 İpək Yolu Beynəlxalq Ekspresi (Bakı ➔ Tbilisi)**

"
                f"* **Bakıdan Çıxış Vaxtı:** 06:00
"
                f"* **Cari Mövqe:** {t['current_station']}
"
                f"* **Növbəti Sərhəd Qovşağı:** {t['next_station']}
"
                f"* **Tbilisi Mərkəzi Vağzalına Çatma:** `{t['scheduled_eta']}`
"
                f"* **Vəziyyət:** Qrafik üzrə tam vaxtında (0 dəqiqə gecikmə)"
            )
        elif lang == "RU":
            return (
                f"🌍 **ADY-410 Международный экспресс Шёлковый Путь (Баку ➔ Тбилиси)**

"
                f"* **Отправление из Баку:** 06:00
"
                f"* **Текущая станция:** {t['current_station']}
"
                f"* **Следующая пограничная станция:** {t['next_station']}
"
                f"* **Прибытие в Тбилиси:** `{t['scheduled_eta']}`
"
                f"* **Статус:** Строго по расписанию (без задержек)"
            )
        else:
            return (
                f"🌍 **ADY-410 Silk Road International Express (Baku ➔ Tbilisi)**

"
                f"* **Departure from Baku:** 06:00
"
                f"* **Current Station:** {t['current_station']}
"
                f"* **Next Hub:** {t['next_station']}
"
                f"* **Scheduled Arrival in Tbilisi:** `{t['scheduled_eta']}`
"
                f"* **Status:** On-Time (0 min delay, nominal clearance)"
            )

    # 6. Wind / Weather / Safety check
    if any(k in q for k in ["wind", "weather", "külək", "hava", "ветер", "погода", "speed", "sürət", "скорост"]):
        if lang == "AZ":
            return (
                f"🌬️ **Xəzər Sahili Külək və Təhlükəsizlik Vəziyyəti:**

"
                f"- **Abşeron Qovşağı (Bakı-Sumqayıt):** Külək 78 km/saat. Sürət avtomatik olaraq **80 km/saat** həddində saxlanılır.
"
                f"- **Bakı-Gəncə Dəhlizi:** Külək 72 km/saat. Sürət məhdudiyyəti aktivdir.
"
                f"- **BTK Dəhlizi (Ağstafa/Tbilisi):** Külək 22 km/saat. Normal sürət rejimi (110 km/saat)."
            )
        elif lang == "RU":
            return (
                f"🌬️ **Погодные условия на Каспийском побережье и безопасность:**

"
                f"- **Абшеронское кольцо (Баку-Сумгаит):** Ветер 78 км/ч. Скорость ограничена до **80 км/ч**.
"
                f"- **Коридор Баку-Гянджа:** Ветер 72 км/ч. Действует ограничение скорости.
"
                f"- **Коридор БТК (Агстафа/Тбилиси):** Ветер 22 км/ч. Скорость в норме (110 км/ч)."
            )
        else:
            return (
                f"🌬️ **Live Caspian Crosswind & Rail Safety Status:**

"
                f"- **Absheron Ring (Baku-Sumgayit):** Wind 78 km/h. Speed strictly clamped to **80 km/h**.
"
                f"- **Baku-Ganja Corridor:** Wind 72 km/h. High-wind speed interlock active.
"
                f"- **BTK Silk Road Corridor:** Wind 22 km/h. Clear normal speed (110 km/h)."
            )

    # 7. General departure timetable (fallback when asking for timetable/schedule)
    if lang == "AZ":
        lines = [
            "📋 **Azərbaycan Dəmir Yolları (ADY) Real Vaxt Cədvəli və Çıxış Vaxtları:**
",
            "1. **ADY-104 Abşeron Ekspresi (Bakı ➔ Sumqayıt)**",
            f"   - Cari dayanacaq: {LIVE_TRAINS['ADY-104']['current_station']} | Çatma vaxtı: `{LIVE_TRAINS['ADY-104']['scheduled_eta']}` (Gecikmə: {LIVE_TRAINS['ADY-104']['delay_minutes']} dəq)",
            "2. **ADY-702 Bakı ➔ Gəncə Sürət Qatarı**",
            f"   - Cari dayanacaq: {LIVE_TRAINS['ADY-702']['current_station']} | Çatma vaxtı: `{LIVE_TRAINS['ADY-702']['scheduled_eta']}` (Gecikmə: {LIVE_TRAINS['ADY-702']['delay_minutes']} dəq)",
            "3. **ADY-410 İpək Yolu (Bakı ➔ Tbilisi)**",
            f"   - Cari dayanacaq: {LIVE_TRAINS['ADY-410']['current_station']} | Çatma vaxtı: `{LIVE_TRAINS['ADY-410']['scheduled_eta']}` (Dəqiq qrafiklə)",
        ]
        return "
".join(lines)
    elif lang == "RU":
        lines = [
            "📋 **Текущее расписание отправлений и движения поездов АЖД:**
",
            "1. **ADY-104 Баку ➔ Сумгаит (Абшеронский экспресс)**",
            f"   - Текущая станция: {LIVE_TRAINS['ADY-104']['current_station']} | Прибытие: `{LIVE_TRAINS['ADY-104']['scheduled_eta']}` (Задержка: {LIVE_TRAINS['ADY-104']['delay_minutes']} мин)",
            "2. **ADY-702 Скоростной поезд Баку ➔ Гянджа**",
            f"   - Текущая станция: {LIVE_TRAINS['ADY-702']['current_station']} | Прибытие: `{LIVE_TRAINS['ADY-702']['scheduled_eta']}` (Задержка: {LIVE_TRAINS['ADY-702']['delay_minutes']} мин)",
            "3. **ADY-410 Экспресс Баку ➔ Тбилиси (Шёлковый путь)**",
            f"   - Текущая станция: {LIVE_TRAINS['ADY-410']['current_station']} | Прибытие: `{LIVE_TRAINS['ADY-410']['scheduled_eta']}` (Вовремя)",
        ]
        return "
".join(lines)
    else:
        lines = [
            "📋 **Current Azerbaijan Railways (ADY) Live Departures & Real-Time Schedule:**
",
            "1. **ADY-104 Absheron Commuter (Baku ➔ Sumgayit)**",
            f"   - Current Station: {LIVE_TRAINS['ADY-104']['current_station']} | ETA: `{LIVE_TRAINS['ADY-104']['scheduled_eta']}` (Delay: {LIVE_TRAINS['ADY-104']['delay_minutes']} min)",
            "2. **ADY-702 Baku-Ganja High-Speed Express**",
            f"   - Current Station: {LIVE_TRAINS['ADY-702']['current_station']} | ETA: `{LIVE_TRAINS['ADY-702']['scheduled_eta']}` (Delay: {LIVE_TRAINS['ADY-702']['delay_minutes']} min)",
            "3. **ADY-410 Silk Road Express (Baku ➔ Tbilisi)**",
            f"   - Current Station: {LIVE_TRAINS['ADY-410']['current_station']} | ETA: `{LIVE_TRAINS['ADY-410']['scheduled_eta']}` (On-Time)",
        ]
        return "
".join(lines)
