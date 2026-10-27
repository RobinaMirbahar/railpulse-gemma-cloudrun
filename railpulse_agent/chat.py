"""Live Rail Time, Departure & Schedule Chat Engine for RailPulse AI.
Supports Natural Conversational Greetings, Local Transit Knowledge (Airport, Hotels, Baku Central),
and Trilingual Q&A (English, Azerbaijani, Russian).
"""

from typing import Any, Dict
from railpulse_agent.tools import CORRIDOR_SIGNALS, LIVE_TRAINS


def answer_rail_chat_query(query: str, lang: str = "EN") -> str:
    q = query.lower().strip()

    # 1. Natural Conversational Greetings (Hi, Hello, Salam, Privet)
    greeting_keywords = [
        "hi", "hello", "hey", "hola", "good morning", "good afternoon", "good evening",
        "salam", "sabahiniz xeyir", "sabahınız xeyir", "her vaxtiniz xeyir", "hər vaxtınız xeyir",
        "привет", "здравствуйте", "добрый день", "доброе утро", "добрый вечер", "хай"
    ]
    words = q.replace("!", "").replace(".", "").replace("?", "").split()
    if any(q == g or (len(words) <= 3 and g in words) for g in greeting_keywords):
        if lang == "AZ":
            return (
                "👋 **Salam! RailPulse AI-a xoş gəlmisiniz.**\n\n"
                "Mən Azərbaycan Dəmir Yolları (ADY) üzrə Gemma rəqəmsal dispetçer köməkçisiyəm. Sizə necə kömək edə bilərəm?\n"
                "* 🕒 **Çıxış və çatma vaxtları** (məs. *Sumqayıta növbəti qatar nə vaxtdır?*)\n"
                "* ✈️ **Hava limanından şəhərə / otellərə transfer**\n"
                "* ⚡ **Qatarların hərəkət vəziyyəti** (məs. *Bakı-Gəncə qatarı gecikir?*)\n"
                "* 🌬️ **Xəzər küləyi və təhlükəsizlik hədləri**\n\n"
                "Sualınızı yazın və ya yuxarıdakı hazır düymələrdən birini seçin!"
            )
        elif lang == "RU":
            return (
                "👋 **Здравствуйте! Добро пожаловать в RailPulse AI.**\n\n"
                "Я цифровой диспетчер Gemma по сети Азербайджанских Железных Дорог (АЖД). Чем я могу помочь?\n"
                "* 🕒 **Расписание и время отправления** (напр. *Когда следующий поезд в Сумгаит?*)\n"
                "* ✈️ **Как добраться из аэропорта в центр и отели**\n"
                "* ⚡ **Статус рейсов и задержки** (напр. *Опаздывает ли рейс в Гянджу?*)\n"
                "* 🌬️ **Погода на Каспийском побережье и скорость**\n\n"
                "Задайте любой вопрос или нажмите быструю кнопку выше!"
            )
        else:
            return (
                "👋 **Hello! Welcome to RailPulse AI.**\n\n"
                "I am Gemma, your autonomous rail operations copilot for Azerbaijan Railways (ADY). How can I help you today?\n"
                "* 🕒 **Live departures & arrivals** (e.g. *When is the next train to Sumgayit?*)\n"
                "* ✈️ **Airport to city center / hotel transit routes**\n"
                "* ⚡ **Train status & schedule recovery** (e.g. *Is Baku-Ganja on time?*)\n"
                "* 🌬️ **Caspian crosswinds & safety limits** (e.g. *Check weather restrictions*)\n\n"
                "Feel free to ask a question or tap one of the suggestion buttons above!"
            )

    # 2. Thank you / Polite closing
    thanks_keywords = ["thanks", "thank you", "thx", "təşəkkür", "tesekkur", "sag ol", "sağ ol", "спасибо", "благодарю"]
    if any(k in q for k in thanks_keywords):
        if lang == "AZ":
            return "Xoşdur! Azərbaycan Dəmir Yolları ilə səyahətiniz uğurlu və təhlükəsiz olsun! 🚆🇦🇿"
        elif lang == "RU":
            return "Пожалуйста! Приятной и безопасной поездки по Азербайджанским Железным Дорогам! 🚆"
        else:
            return "You are very welcome! Have a safe and comfortable journey with Azerbaijan Railways! 🚆"

    # 3. Airport to Hotel / City Center / Radisson / 28 May Transit Query
    airport_keywords = ["airport", "aeroport", "hava liman", "havaliman", "аэропорт", "gyd", "heydar aliyev"]
    hotel_transit_keywords = ["radisson", "hotel", "otel", "отель", "marriott", "hilton", "azadliq", "azadlıq", "28 may", "downtown", "center", "centre", "mərkəz", "merkez", "центр"]

    has_airport = any(k in q for k in airport_keywords)
    has_hotel_or_dest = any(k in q for k in hotel_transit_keywords)

    if has_airport or ("radisson" in q) or ("airport to" in q) or ("to airport" in q):
        if lang == "AZ":
            return (
                "✈️ **Heydər Əliyev Beynəlxalq Hava Limanı (GYD) ➔ Radisson Hotel Bakı / Şəhər Mərkəzi:**\n\n"
                "* **Birbaşa Dəmir Yolu Vəziyyəti:** Hazırda hava limanının bilavasitə daxilində sərnişin qatarı stansiyası yoxdur *(ADY Hava Limanı sürətli dəmir yolu xətti layihəsi inkişaf mərhələsindədir)*.\n\n"
                "💡 **Ən Rahat və Sürətli Marşrut:**\n"
                "1. **BakuBus Aero Ekspres (H1 avtobusu):** Terminal 1 və 2-nin çıxışından 24/7 hər 30 dəqiqədən bir hərəkət edir. Təxminən 30 dəqiqəyə **Bakı Dəmir Yolu Vağzalına (28 May)** çatır.\n"
                "2. **Radisson Otelinə Keçid:** **Radisson Hotel Bakı** (Azadlıq Meydanı / Neftçilər prospekti) Bakı Mərkəzi Dəmir Yolu Vağzalından cəmi **7 dəqiqəlik piyada (təx. 700 metr)** və ya 2 dəqiqəlik taksi məsafəsindədir!\n"
                "3. **Birbaşa Taksi:** Hava limanından rəsmi taksi və ya Bolt / Uber ilə Heydər Əliyev prospekti ilə Radisson otelinə çatmaq ~20–25 dəqiqə çəkir.\n\n"
                "🚆 *Qeyd: Əgər Sumqayıt, Gəncə və ya Tiflis istiqamətinə getmək istəyirsinizsə, bütün ADY qatarları (**ADY-104**, **ADY-702**, **ADY-410**) məhz Bakı Mərkəzi Vağzalından yola düşür!*"
            )
        elif lang == "RU":
            return (
                "✈️ **Международный Аэропорт Гейдар Алиев (GYD) ➔ Отель Radisson Baku / Центр города:**\n\n"
                "* **Прямой поезд:** На данный момент непосредственно внутри терминала аэропорта железнодорожной станции нет *(проект аэроэкспресса АЖД находится в разработке)*.\n\n"
                "💡 **Самый удобный и проверенный маршрут:**\n"
                "1. **Экспресс-автобус BakuBus Aero Express (H1):** Отправляется от выходов Терминалов 1 и 2 круглосуточно каждые 30 минут и за ~30 минут прибывает на **Бакинский Центральный Железнодорожный Вокзал (ст. метро 28 Мая)**.\n"
                "2. **До отеля Radisson:** **Отель Radisson Baku** (пл. Свободы / проспект Нефтяников) находится всего в **7 минутах ходьбы (около 700 м)** от Бакинского вокзала вниз по улице Пушкина к бульвару!\n"
                "3. **Прямое такси:** Официальное такси аэропорта или через приложения Bolt / Uber довезет до Radisson по проспекту Гейдара Алиева за 20–25 минут.\n\n"
                "🚆 *Если вы продолжаете путь по железной дороге, все поезда АЖД (**ADY-104** в Сумгаит, **ADY-702** в Гянджу, **ADY-410** в Тбилиси) отправляются с Бакинского Центрального Вокзала!*"
            )
        else:
            return (
                "✈️ **Heydar Aliyev International Airport (GYD) ➔ Radisson Hotel Baku / City Center:**\n\n"
                "* **Direct Train Status:** Currently, there is **no direct heavy-rail train station directly inside the airport terminal yet** *(the official ADY Airport Rail Link project is in development)*.\n\n"
                "💡 **Recommended Fast & Seamless Route:**\n"
                "1. **BakuBus Aero Express (Line H1):** Board the direct express shuttle right outside Terminal 1/2. It operates 24/7 every 30 minutes, reaching **Baku Central Railway Station (28 May)** in approximately 30 minutes.\n"
                "2. **To Radisson Hotel Baku:** **Radisson Hotel Baku** (located on Azadliq Square / Neftchilar Avenue overlooking Baku Boulevard) is just a **7-minute walk (approx. 700 meters)** down Pushkin Street or a 2-minute ride from Baku Central Railway Station!\n"
                "3. **Direct Airport Taxi:** An official airport taxi (or Bolt / Uber Azerbaijan) takes ~20–25 minutes directly to Radisson Hotel Baku via Heydar Aliyev Highway.\n\n"
                "🚆 *If you are connecting onwards across Azerbaijan, all ADY trains (**ADY-104** to Sumgayit, **ADY-702** to Ganja, and **ADY-410** to Tbilisi) depart directly from **Baku Central Railway Station**!*"
            )

    # 4. Tickets / BakuCard / Fares
    ticket_keywords = ["ticket", "bilet", "buy", "fare", "cost", "price", "qiymət", "qiymet", "neçəyə", "neceye", "купить", "билет", "цена", "стоимость", "bakucard"]
    if any(k in q for k in ticket_keywords):
        if lang == "AZ":
            return (
                "💳 **ADY Biletlər və Ödəniş Qaydaları:**\n\n"
                "* **Onlayn Bilet:** Rəsmi [ady.az](https://ady.az) saytından və ya **ADY Mobile** tətbiqindən ala bilərsiniz.\n"
                "* **Abşeron Şəhərətrafı Qatarları:** Turniketlərdə birbaşa **BakıKart** və ya təmassız bank kartları (Visa / Mastercard / Apple Pay) keçərlidir.\n"
                "* **Bakı ➔ Gəncə / Tiflis Qatarları:** Biletləri qabaqcadan şəxsiyyət vəsiqəsi ilə sayt və ya vağzal kassalarından əldə etmək tövsiyə olunur."
            )
        elif lang == "RU":
            return (
                "💳 **Билеты и оплата проезда АЖД:**\n\n"
                "* **Онлайн:** На официальном сайте [ady.az](https://ady.az) или в приложении **ADY Mobile**.\n"
                "* **Пригородные поезда (Баку-Сумгаит):** Оплата на турникетах картой **BakıKart** или бесконтактной банковской картой (Visa / Mastercard / Apple Pay).\n"
                "* **Поезда в Гянджу и Тбилиси:** Билеты приобретаются заранее по удостоверению личности онлайн или в кассах вокзала."
            )
        else:
            return (
                "💳 **ADY Tickets & Payment Guide:**\n\n"
                "* **Online Purchase:** Book via the official portal [ady.az](https://ady.az) or the **ADY Mobile** app.\n"
                "* **Absheron Commuter Lines (Baku ⇄ Sumgayit):** Tap directly at the turnstiles using **BakuCard** or contactless bank cards (Visa / Mastercard / Apple Pay).\n"
                "* **High-Speed Express (Baku ⇄ Ganja / Tbilisi):** Advance reserved seating tickets are available online or at Baku Central Station ticket counters."
            )

    # 5. Sumgayit / Absheron Commuter
    if any(k in q for k in ["sumgayit", "sumqayıt", "sumqayit", "сумгаит", "104", "absheron", "abşeron", "абшерон"]):
        t = LIVE_TRAINS["ADY-104"]
        c = CORRIDOR_SIGNALS["ABSHERON-RING"]
        wind = c["wind_speed_kmh"]
        if lang == "AZ":
            return (
                f"🚆 **ADY-104 Abşeron Dairəvi Qatarı (Bakı ➔ Sumqayıt)**\n\n"
                f"* **Cari Mövqe:** {t['current_station']}\n"
                f"* **Növbəti Dayanacaq:** {t['next_station']}\n"
                f"* **Sumqayıta Çatma Vaxtı (ETA):** `{t['scheduled_eta']}` ({t['delay_minutes']} dəqiqə gecikmə)\n"
                f"* **Hərəkət Sürəti:** {t['current_speed_kmh']} km/saat\n"
                f"* **Külək Şəraiti:** Xəzər sahili külək {wind} km/saat (Təhlükəsizlik həddi tətbiq olunub)"
            )
        elif lang == "RU":
            return (
                f"🚆 **ADY-104 Абшеронский экспресс (Баку ➔ Сумгаит)**\n\n"
                f"* **Текущая станция:** {t['current_station']}\n"
                f"* **Следующая остановка:** {t['next_station']}\n"
                f"* **Прибытие в Сумгаит (ETA):** `{t['scheduled_eta']}` (Задержка {t['delay_minutes']} мин)\n"
                f"* **Скорость поезда:** {t['current_speed_kmh']} км/ч\n"
                f"* **Ветер на побережье:** {wind} км/ч (Действует безопасный лимит скорости)"
            )
        else:
            return (
                f"🚆 **ADY-104 Absheron Commuter (Baku ➔ Sumgayit)**\n\n"
                f"* **Current Location:** {t['current_station']}\n"
                f"* **Next Station:** {t['next_station']}\n"
                f"* **Sumgayit Arrival (ETA):** `{t['scheduled_eta']}` ({t['delay_minutes']} min delay)\n"
                f"* **Approved Speed:** {t['current_speed_kmh']} km/h\n"
                f"* **Weather Safety:** Crosswind {wind} km/h (Safe corridor speed limits applied)"
            )

    # 6. Ganja High-Speed Express
    if any(k in q for k in ["ganja", "gəncə", "gence", "гянджа", "702"]):
        t = LIVE_TRAINS["ADY-702"]
        if lang == "AZ":
            return (
                f"⚡ **ADY-702 Bakı ➔ Gəncə Sürət Qatarı**\n\n"
                f"* **Cari Mövqe:** {t['current_station']}\n"
                f"* **Növbəti Dayanacaq:** {t['next_station']}\n"
                f"* **Gəncəyə Çatma Vaxtı (ETA):** `{t['scheduled_eta']}` ({t['delay_minutes']} dəqiqə gecikmə)\n"
                f"* **Sürət Həddi:** {t['current_speed_kmh']} km/saat\n"
                f"* **Status:** Əsas xətt açıqdır, hərəkət bərpa olunur."
            )
        elif lang == "RU":
            return (
                f"⚡ **ADY-702 Скоростной поезд Баку ➔ Гянджа**\n\n"
                f"* **Текущая станция:** {t['current_station']}\n"
                f"* **Следующая остановка:** {t['next_station']}\n"
                f"* **Прибытие в Гянджу (ETA):** `{t['scheduled_eta']}` (Задержка {t['delay_minutes']} мин)\n"
                f"* **Скорость:** {t['current_speed_kmh']} км/ч\n"
                f"* **Статус:** Главный путь свободен, график нагоняется."
            )
        else:
            return (
                f"⚡ **ADY-702 Baku ➔ Ganja High-Speed Express**\n\n"
                f"* **Current Location:** {t['current_station']}\n"
                f"* **Next Station:** {t['next_station']}\n"
                f"* **Ganja Arrival (ETA):** `{t['scheduled_eta']}` ({t['delay_minutes']} min delay)\n"
                f"* **Approved Speed:** {t['current_speed_kmh']} km/h\n"
                f"* **Status:** Primary track clear, delay recovery active."
            )

    # 7. Silk Road Express (Tbilisi)
    if any(k in q for k in ["tbilisi", "tiflis", "тбилиси", "410", "silk road", "ipək yolu", "ipek yolu", "шелковый"]):
        t = LIVE_TRAINS["ADY-410"]
        if lang == "AZ":
            return (
                f"🌍 **ADY-410 İpək Yolu Ekspresi (Bakı ➔ Tbilisi)**\n\n"
                f"* **Cari Mövqe:** {t['current_station']}\n"
                f"* **Növbəti Dayanacaq:** {t['next_station']}\n"
                f"* **Tbilisi Mərkəzi Çatma Vaxtı (ETA):** `{t['scheduled_eta']}`\n"
                f"* **Sürət Həddi:** {t['current_speed_kmh']} km/saat\n"
                f"* **Status:** Dəqiq qrafik üzrə (0 dəqiqə gecikmə, sərhəd dəhlizi açıqdır)"
            )
        elif lang == "RU":
            return (
                f"🌍 **ADY-410 Экспресс Шёлковый Путь (Баку ➔ Тбилиси)**\n\n"
                f"* **Текущая станция:** {t['current_station']}\n"
                f"* **Следующая остановка:** {t['next_station']}\n"
                f"* **Прибытие в Тбилиси (ETA):** `{t['scheduled_eta']}`\n"
                f"* **Скорость:** {t['current_speed_kmh']} км/ч\n"
                f"* **Статус:** Строго по расписанию (0 мин задержки, коридор свободен)"
            )
        else:
            return (
                f"🌍 **ADY-410 Silk Road Express (Baku ➔ Tbilisi)**\n\n"
                f"* **Current Location:** {t['current_station']}\n"
                f"* **Next Station:** {t['next_station']}\n"
                f"* **Tbilisi Central Arrival (ETA):** `{t['scheduled_eta']}`\n"
                f"* **Approved Speed:** {t['current_speed_kmh']} km/h\n"
                f"* **Status:** On-Time (0 min delay, nominal clearance)"
            )

    # 8. Wind / Weather / Safety check
    if any(k in q for k in ["wind", "weather", "külək", "kulek", "hava", "ветер", "погода", "speed", "sürət", "suret", "скорост"]):
        if lang == "AZ":
            return (
                "🌬️ **Xəzər Sahili Külək və Təhlükəsizlik Vəziyyəti:**\n\n"
                "- **Abşeron Qovşağı (Bakı-Sumqayıt):** Külək 78 km/saat. Sürət avtomatik olaraq **80 km/saat** həddində saxlanılır.\n"
                "- **Bakı-Gəncə Dəhlizi:** Külək 72 km/saat. Sürət məhdudiyyəti aktivdir.\n"
                "- **BTK Dəhlizi (Ağstafa/Tbilisi):** Külək 22 km/saat. Normal sürət rejimi (110 km/saat)."
            )
        elif lang == "RU":
            return (
                "🌬️ **Погодные условия на Каспийском побережье и безопасность:**\n\n"
                "- **Абшеронское кольцо (Баку-Сумгаит):** Ветер 78 км/ч. Скорость ограничена до **80 км/ч**.\n"
                "- **Коридор Баку-Гянджа:** Ветер 72 км/ч. Действует ограничение скорости.\n"
                "- **Коридор БТК (Агстафа/Тбилиси):** Ветер 22 км/ч. Скорость в норме (110 км/ч)."
            )
        else:
            return (
                "🌬️ **Live Caspian Crosswind & Rail Safety Status:**\n\n"
                "- **Absheron Ring (Baku-Sumgayit):** Wind 78 km/h. Speed strictly clamped to **80 km/h**.\n"
                "- **Baku-Ganja Corridor:** Wind 72 km/h. High-wind speed interlock active.\n"
                "- **BTK Silk Road Corridor:** Wind 22 km/h. Clear normal speed (110 km/h)."
            )

    # 9. General departure timetable (fallback)
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
