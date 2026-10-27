"""Live Rail Time, Departure & Schedule Chat Engine for RailPulse AI.
Supports Context-Aware Intelligence (Active Train, Wind, Block Occupancy, ETA),
Baku & Azerbaijan Transit Knowledge, Onboard Amenities, Ticketing, and Trilingual Q&A (EN, AZ, RU).
"""

from typing import Any, Dict, Optional
import re
from railpulse_agent.tools import CORRIDOR_SIGNALS, LIVE_TRAINS


def answer_rail_chat_query(
    query: str,
    lang: str = "EN",
    selected_train: str = "ADY-104",
    advisory: Any = None,
) -> str:
    """Intelligently answers passenger and dispatcher queries with real-time rail telemetry context."""
    q = query.lower().strip()
    active_info = LIVE_TRAINS.get(selected_train, LIVE_TRAINS["ADY-104"])
    corridor_id = active_info.get("corridor_id", "ABSHERON-RING")
    signal_info = CORRIDOR_SIGNALS.get(corridor_id, {"wind_speed_kmh": 28, "primary_block_status": "FREE"})

    # Extract dynamic live advisory parameters
    approved_speed = getattr(advisory, "approved_speed_kmh", active_info["current_speed_kmh"]) if advisory else active_info["current_speed_kmh"]
    assigned_block = getattr(advisory, "assigned_block_id", "BLK-SUMGAYIT-A1") if advisory else "BLK-SUMGAYIT-A1"
    updated_eta = getattr(advisory, "updated_eta", active_info["scheduled_eta"]) if advisory else active_info["scheduled_eta"]
    delay_min = getattr(advisory, "delay_minutes_remaining", active_info["delay_minutes"]) if advisory else active_info["delay_minutes"]
    current_wind = signal_info.get("wind_speed_kmh", 28)
    block_status = signal_info.get("primary_block_status", "FREE")

    # -------------------------------------------------------------
    # 1. Natural Conversational Greetings (Hi, Hello, Salam, Privet)
    # -------------------------------------------------------------
    greeting_keywords = [
        "hi", "hello", "hey", "hola", "good morning", "good afternoon", "good evening",
        "salam", "sabahiniz xeyir", "sabahınız xeyir", "her vaxtiniz xeyir", "hər vaxtınız xeyir",
        "привет", "здравствуйте", "добрый день", "доброе утро", "добрый вечер", "хай"
    ]
    words = q.replace("!", "").replace(".", "").replace("?", "").split()
    if any(q == g or (len(words) <= 3 and g in words) for g in greeting_keywords):
        if lang == "AZ":
            return (
                "👋 **Salam! Mən Gemma Rail Assistant-am.**\n\n"
                "Azərbaycan Dəmir Yolları (ADY) şəbəkəsi üzrə real vaxt dispetçer və sərnişin köməkçisiyəm. Sizə necə kömək edə bilərəm?\n\n"
                f"📌 **Hazırkı Seçilmiş Qatar:** **{selected_train}** ({active_info['route_name']})\n"
                f"• Cari dayanacaq: `{active_info['current_station']}` ➔ `{active_info['next_station']}`\n"
                f"• Təsdiqlənmiş sürət: `{approved_speed} km/saat` | Çatma vaxtı: `{updated_eta}`\n\n"
                "Soruşa bilərsiniz:\n"
                "* ✈️ *Hava limanından Radisson və ya şəhər mərkəzinə necə gedim?*\n"
                "* 🕒 *Sumqayıt və ya Gəncəyə növbəti qatar nə vaxtdır?*\n"
                "* 💳 *Bilet qiymətləri və BakıKart qaydaları*\n"
                "* 🌬️ *Külək sürəti niyə qatarı yavaşladır?*\n"
                "* 📶 *Qatarda Wi-Fi və enerji yuvaları varmı?*"
            )
        elif lang == "RU":
            return (
                "👋 **Здравствуйте! Я цифровой помощник Gemma Rail Assistant.**\n\n"
                "Я предоставляю оперативную информацию о движении поездов Азербайджанских Железных Дорог (АЖД) в реальном времени. Чем могу помочь?\n\n"
                f"📌 **Активный выбранный поезд:** **{selected_train}** ({active_info['route_name']})\n"
                f"• Текущая станция: `{active_info['current_station']}` ➔ `{active_info['next_station']}`\n"
                f"• Безопасная скорость: `{approved_speed} км/ч` | Прибытие: `{updated_eta}`\n\n"
                "Вы можете спросить:\n"
                "* ✈️ *Как доехать из аэропорта до отеля Radisson или центра?*\n"
                "* 🕒 *Расписание поездов в Сумгаит и Гянджу*\n"
                "* 💳 *Стоимость билетов и оплата через BakıKart*\n"
                "* 🌬️ *Почему скорость ограничена из-за каспийского ветра?*\n"
                "* 📶 *Есть ли в поезде Wi-Fi и розетки?*"
            )
        else:
            return (
                "👋 **Hello! I am the Gemma Rail Assistant.**\n\n"
                "I provide real-time autonomous dispatch telemetry and passenger guidance for Azerbaijan Railways (ADY). How can I assist you?\n\n"
                f"📌 **Currently Active Train:** **{selected_train}** ({active_info['route_name']})\n"
                f"• Position: `{active_info['current_station']}` ➔ `{active_info['next_station']}`\n"
                f"• Approved Speed: `{approved_speed} km/h` | ETA: `{updated_eta}`\n\n"
                "Feel free to ask about:\n"
                "* ✈️ *How to travel from the Airport to Radisson Hotel / City Center*\n"
                "* 🕒 *Live schedules & next departures to Sumgayit or Ganja*\n"
                "* 💳 *Ticket fares, BakuCard, and contactless payments*\n"
                "* 🌬️ *Why Caspian crosswinds clamp train speed to 80 km/h*\n"
                "* 📶 *Onboard amenities (Wi-Fi, power outlets, double-decker cars)*"
            )

    # -------------------------------------------------------------
    # 2. Thank you / Polite closing
    # -------------------------------------------------------------
    thanks_keywords = ["thanks", "thank you", "thx", "təşəkkür", "tesekkur", "sag ol", "sağ ol", "спасибо", "благодарю"]
    if any(k in q for k in thanks_keywords):
        if lang == "AZ":
            return "Xoşdur! Azərbaycan Dəmir Yolları ilə səyahətiniz uğurlu, rahat və təhlükəsiz olsun! 🚆🇦🇿"
        elif lang == "RU":
            return "Пожалуйста! Приятной и безопасной поездки по Азербайджанским Железным Дорогам! 🚆"
        else:
            return "You are very welcome! Have a safe and comfortable journey with Azerbaijan Railways! 🚆"

    # -------------------------------------------------------------
    # 3. Airport Transit (GYD to Radisson, Boulevard, 28 May)
    # -------------------------------------------------------------
    airport_terms = ["airport", "aeroport", "hava liman", "havaliman", "аэропорт", "gyd", "heydar aliyev"]
    if any(k in q for k in airport_terms) or ("radisson" in q) or ("to airport" in q) or ("airport to" in q):
        if lang == "AZ":
            return (
                "✈️ **Heydər Əliyev Beynəlxalq Hava Limanı (GYD) ➔ Radisson Hotel Bakı / Şəhər Mərkəzi:**\n\n"
                "❌ **Birbaşa Dəmir Yolu Vəziyyəti:** Hazırda hava limanının birbaşa içərisində sərnişin qatarı stansiyası yoxdur *(ADY Hava Limanı dəmir yolu layihəsi inkişaf mərhələsindədir)*.\n\n"
                "💡 **Tövsiyə Olunan Ən Rahat Marşrut:**\n"
                "1. **BakuBus Aero Ekspres (H1 avtobusu):** Terminal 1 və 2-nin çıxışından **24/7 hər 30 dəqiqədən bir** hərəkət edir. Təxminən 30 dəqiqəyə **Bakı Dəmir Yolu Vağzalına (28 May)** çatır (Gediş haqqı: 1.30 AZN, BakıKart və ya təmassız kartla).\n"
                "2. **Radisson Otelinə Keçid:** **Radisson Hotel Bakı** (Azadlıq Meydanı / Neftçilər prospekti) Bakı Mərkəzi Vağzalından cəmi **7 dəqiqəlik piyada (təx. 700 metr)** Puşkin küçəsi ilə bulvar istiqamətində və ya 2 dəqiqəlik taksi məsafəsindədir!\n"
                "3. **Birbaşa Taksi:** Hava limanından rəsmi taksi və ya Bolt/Uber ilə Heydər Əliyev prospekti ilə 20–25 dəqiqəyə çatmaq mümkündür.\n\n"
                "🚆 *Qeyd: Bütün ADY qatarları (**ADY-104** Sumqayıt, **ADY-702** Gəncə, **ADY-410** Tbilisi) məhz Bakı Dəmir Yolu Vağzalından yola düşür!*"
            )
        elif lang == "RU":
            return (
                "✈️ **Международный Аэропорт Гейдар Алиев (GYD) ➔ Отель Radisson Baku / Центр города:**\n\n"
                "❌ **Прямой поезд:** На данный момент непосредственно внутри терминала аэропорта железнодорожной станции нет *(проект аэроэкспресса АЖД находится в разработке)*.\n\n"
                "💡 **Самый удобный и проверенный маршрут:**\n"
                "1. **Экспресс-автобус BakuBus Aero Express (H1):** Отправляется от выходов Терминалов 1 и 2 **круглосуточно каждые 30 минут** и за ~30 минут прибывает на **Бакинский Центральный Железнодорожный Вокзал (ст. метро 28 Мая)** (стоимость 1.30 AZN по BakıKart или банковской карте).\n"
                "2. **До отеля Radisson:** **Отель Radisson Baku** (пл. Свободы / проспект Нефтяников) находится всего в **7 минутах ходьбы (около 700 м)** от Бакинского вокзала вниз по улице Пушкина прямо к Приморскому бульвару!\n"
                "3. **Прямое такси:** Официальное такси аэропорта или через приложения Bolt / Uber довезет до отеля по проспекту Гейдара Алиева за 20–25 минут.\n\n"
                "🚆 *Если вы продолжаете путешествие по железной дороге, все поезда АЖД (**ADY-104** в Сумгаит, **ADY-702** в Гянджу, **ADY-410** в Тбилиси) отправляются с Бакинского Центрального Вокзала!*"
            )
        else:
            return (
                "✈️ **Heydar Aliyev International Airport (GYD) ➔ Radisson Hotel Baku / City Center:**\n\n"
                "❌ **Direct Train Status:** Currently, there is **no direct heavy-rail train station inside the airport terminal yet** *(the official Azerbaijan Railways Airport Rail Link project is in development)*.\n\n"
                "💡 **Recommended Fast & Seamless Route:**\n"
                "1. **BakuBus Aero Express (Line H1):** Board the direct express shuttle right outside Terminal 1/2. It operates **24/7 every 30 minutes**, reaching **Baku Central Railway Station (28 May)** in approximately 30 minutes (Fare: 1.30 AZN via BakuCard or contactless bank card).\n"
                "2. **To Radisson Hotel Baku:** **Radisson Hotel Baku** (located on Azadliq Square / Neftchilar Avenue overlooking Baku Boulevard) is just a **7-minute walk (approx. 700 meters)** down Pushkin Street or a 2-minute ride from Baku Central Railway Station!\n"
                "3. **Direct Airport Taxi:** An official airport taxi (or Bolt / Uber Azerbaijan) takes ~20–25 minutes directly to Radisson Hotel Baku via Heydar Aliyev Highway.\n\n"
                "🚆 *All Azerbaijan Railways trains (**ADY-104** to Sumgayit, **ADY-702** to Ganja, and **ADY-410** to Tbilisi) depart directly from **Baku Central Railway Station**!*"
            )

    # -------------------------------------------------------------
    # 4. Questions About the Active Selected Train / Delay / Speed
    # -------------------------------------------------------------
    current_status_terms = ["current", "active", "this train", "speed", "clamped", "why slow", "delay", "late", "eta", "status", "haradadır", "haradadir", "gecik", "ne vaxt", "hardadır", " hardadir", "где поезд", "почему медленно", "задержк", "опоздан"]
    if (any(k in q for k in current_status_terms) and not any(k in q for k in ["ticket", "wifi", "bilet"])) or ("why" in q and "speed" in q):
        is_clamped = approved_speed < 140 and current_wind > 65
        is_siding = "SIDING" in assigned_block
        if lang == "AZ":
            resp = [
                f"🚆 **Aktiv Qatar: {selected_train} ({active_info['route_name']}) Real Vaxt Məlumatı:**\n",
                f"• **Cari Mövqe:** `{active_info['current_station']}` ➔ `{active_info['next_station']}`",
                f"• **Təsdiqlənmiş Sürət:** `{approved_speed} km/saat`",
                f"• **Təyin Olunmuş Blok:** `{assigned_block}`" + (" *(⚠️ Yan Ehtiyat Xətt)*" if is_siding else " *(✓ Əsas Xətt)*"),
                f"• **Gözlənilən Çatma Vaxtı (ETA):** `{updated_eta}` ({delay_min} dəqiqə gecikmə bərpa olunur)",
                f"• **Külək Şəraiti:** `{current_wind} km/saat` Xəzər sahili küləyi",
            ]
            if is_clamped:
                resp.append(f"\n⚠️ **Təhlükəsizlik Bildirişi:** Küləyin sürəti təhlükəsizlik həddindən ({current_wind} > 65 km/saat) yüksək olduğu üçün Gemma dispetçer interlok sistemi sürəti **{approved_speed} km/saat** həddində məhdudlaşdırıb.")
            if is_siding:
                resp.append(f"\n🚧 **Xətt Bildirişi:** Əsas blok məşğul olduğundan qatar təhlükəsiz keçid üçün **{assigned_block}** yan xəttinə yönləndirilib.")
            return "\n".join(resp)
        elif lang == "RU":
            resp = [
                f"🚆 **Активный поезд: {selected_train} ({active_info['route_name']}) Онлайн-статус:**\n",
                f"• **Положение:** `{active_info['current_station']}` ➔ `{active_info['next_station']}`",
                f"• **Утвержденная скорость:** `{approved_speed} км/ч`",
                f"• **Блок пути:** `{assigned_block}`" + (" *(⚠️ Боковой разъезд)*" if is_siding else " *(✓ Главный путь)*"),
                f"• **Расчетное время прибытия (ETA):** `{updated_eta}` (остаточная задержка: {delay_min} мин)",
                f"• **Скорость ветра на побережье:** `{current_wind} км/ч`",
            ]
            if is_clamped:
                resp.append(f"\n⚠️ **Блокировка безопасности:** Из-за сильного каспийского ветра ({current_wind} > 65 км/ч) детерминированная система безопасности автоматически ограничила скорость до **{approved_speed} км/ч**.")
            if is_siding:
                resp.append(f"\n🚧 **Смена пути:** В связи с занятостью основного пути состав перенаправлен на разъезд **{assigned_block}**.")
            return "\n".join(resp)
        else:
            resp = [
                f"🚆 **Active Train: {selected_train} ({active_info['route_name']}) Real-Time Status:**\n",
                f"• **Current Position:** `{active_info['current_station']}` ➔ `{active_info['next_station']}`",
                f"• **Approved Safe Speed:** `{approved_speed} km/h`",
                f"• **Assigned Track Block:** `{assigned_block}`" + (" *(⚠️ Passing Siding Loop)*" if is_siding else " *(✓ Primary Clear Mainline)*"),
                f"• **Estimated Arrival (ETA):** `{updated_eta}` ({delay_min} min delay recovery active)",
                f"• **Caspian Crosswind:** `{current_wind} km/h`",
            ]
            if is_clamped:
                resp.append(f"\n⚠️ **Safety Interlock Explanation:** Because crosswinds exceed the critical railway safety threshold ({current_wind} > 65 km/h), the deterministic guardrail clamped requested speed down to **{approved_speed} km/h**.")
            if is_siding:
                resp.append(f"\n🚧 **Track Clearance:** The primary block is currently occupied; Gemma and Google ADK safely routed the train into **{assigned_block}**.")
            return "\n".join(resp)

    # -------------------------------------------------------------
    # 5. Tickets, BakuCard, Prices & Booking
    # -------------------------------------------------------------
    ticket_terms = ["ticket", "bilet", "buy", "fare", "cost", "price", "qiymət", "qiymet", "neçəyə", "neceye", "купить", "билет", "цена", "стоимость", "bakucard", "bakikart"]
    if any(k in q for k in ticket_terms):
        if lang == "AZ":
            return (
                "💳 **Azərbaycan Dəmir Yolları (ADY) Bilet və Ödəniş Bələdçisi:**\n\n"
                "* **Bakı ⇄ Sumqayıt Abşeron Dairəvi Xətti:**\n"
                "  - Gediş haqqı: **0.50 – 1.00 AZN** (məsafədən asılı olaraq).\n"
                "  - Ödəniş üsulu: Turniketlərdə birbaşa **BakıKart** və ya təmassız bank kartları (**Apple Pay / Google Pay / Visa / Mastercard**) keçərlidir.\n"
                "* **Bakı ⇄ Gəncə Sürət Qatarı:**\n"
                "  - Standart: ~10–15 AZN | Birinci sinif: ~20–25 AZN.\n"
                "  - Onlayn alış: Rəsmi [ady.az](https://ady.az) portalı və ya **ADY Mobile** tətbiqi vasitəsilə qabaqcadan alınması tövsiyə olunur.\n"
                "* **Bakı ⇄ Tbilisi Beynəlxalq Qatarı:**\n"
                "  - Beynəlxalq sərnişin daşımaları üçün biletlər xarici pasport təqdim olunmaqla rəsmi kassalardan və ya onlayn əldə edilir."
            )
        elif lang == "RU":
            return (
                "💳 **Билеты, тарифы и правила оплаты АЖД:**\n\n"
                "* **Абшеронское кольцо (Баку ⇄ Сумгаит):**\n"
                "  - Стоимость: **0.50 – 1.00 AZN** в зависимости от зоны.\n"
                "  - Оплата: Напрямую на турникетах картой **BakıKart** либо бесконтактными банковскими картами (**Apple Pay / Google Pay / Visa / Mastercard**).\n"
                "* **Скоростной поезд Баку ⇄ Гянджа:**\n"
                "  - Стандарт: ~10–15 AZN | Бизнес-класс: ~20–25 AZN.\n"
                "  - Покупка: Заранее на официальном сайте [ady.az](https://ady.az) или в приложении **ADY Mobile** по удостоверению личности.\n"
                "* **Баку ⇄ Тбилиси (Международный маршрут):**\n"
                "  - Билеты оформляются по заграничному паспорту онлайн или в кассах вокзалов."
            )
        else:
            return (
                "💳 **Azerbaijan Railways (ADY) Tickets & Fare Guide:**\n\n"
                "* **Baku ⇄ Sumgayit Absheron Commuter Ring:**\n"
                "  - Fare: **0.50 – 1.00 AZN** depending on the station distance.\n"
                "  - Payment: Tap directly at the turnstiles using **BakuCard** or contactless bank cards (**Apple Pay / Google Pay / Visa / Mastercard**).\n"
                "* **Baku ⇄ Ganja High-Speed Express:**\n"
                "  - Standard Class: ~10–15 AZN | First Class: ~20–25 AZN.\n"
                "  - Online Booking: Recommended in advance via [ady.az](https://ady.az) or the **ADY Mobile** app.\n"
                "* **Baku ⇄ Tbilisi Silk Road Express:**\n"
                "  - International reserved seating purchased via official portals or ticket desks with international passport identification."
            )

    # -------------------------------------------------------------
    # 6. Onboard Amenities (Wi-Fi, Power, Double-Decker, Luggage, Bike)
    # -------------------------------------------------------------
    amenity_terms = ["wifi", "wi-fi", "internet", "power", "charger", "plug", "socket", "outlet", "luggage", "baggage", "bike", "bicycle", "cafe", "food", "stadler", "baqaj", "velosiped", "qidalanma", "розетк", "багаж", "велосипед", "питание", "вайфай"]
    if any(k in q for k in amenity_terms):
        if lang == "AZ":
            return (
                "🚆 **ADY Qatarlarında Sərnişin Rahatlığı və Şərait:**\n\n"
                "* **Qatar Parkı:** Abşeron xəttində müasir ikimərtəbəli **Stadler KISS**, Gəncə xəttində isə **Stadler FLIRT** sürət qatarları fəaliyyət göstərir.\n"
                "* 📶 **Wi-Fi və Enerji:** Bütün vaqonlarda pulsuz Wi-Fi şəbəkəsi və oturacaqların altında 220V / USB enerji yuvaları mövcuddur.\n"
                "* 🧳 **Baqaj:** Hər sərnişin üçün 36 kq-dək əl baqajı pulsuzdur. Vaqonlarda xüsusi baqaj rəfləri vardır.\n"
                "* 🚲 **Velosipedlər:** İkimərtəbəli Stadler qatarlarının baş və son vaqonlarında velosipedlər üçün xüsusi bərkidici yerlər təchiz olunub.\n"
                "* ☕ **Kafe və İaşə:** Gəncə sürət qatarında kafe-bar vaqonu və qəlyanaltı xidməti fəaliyyət göstərir."
            )
        elif lang == "RU":
            return (
                "🚆 **Удобства и сервисы в поездах АЖД:**\n\n"
                "* **Подвижной состав:** На Абшеронском кольце курсируют двухэтажные электропоезда **Stadler KISS**, на маршруте в Гянджу — **Stadler FLIRT**.\n"
                "* 📶 **Wi-Fi и зарядка:** Бесплатный Wi-Fi во всех вагонах, розетки 220V и USB-порты под креслами.\n"
                "* 🧳 **Багаж:** Бесплатный провоз ручной клади до 36 кг. Имеются вместительные багажные полки.\n"
                "* 🚲 **Велосипеды:** В первом и последнем вагонах поездов Stadler предусмотрены специальные крепления для велосипедов.\n"
                "* ☕ **Кафе:** В скоростном экспрессе Баку-Гянджа работает вагон-бистро с напитками и свежей выпечкой."
            )
        else:
            return (
                "🚆 **Onboard Amenities & Services on Azerbaijan Railways:**\n\n"
                "* **Fleet:** Ultra-modern **Stadler KISS double-decker electric trains** (Absheron commuter) and **Stadler FLIRT high-speed trains** (Baku-Ganja).\n"
                "* 📶 **Wi-Fi & Charging:** Free high-speed Wi-Fi throughout all coaches, with individual 220V power outlets and USB ports under seats.\n"
                "* 🧳 **Luggage Policy:** Up to 36 kg of personal baggage is free of charge, with spacious overhead and vestibule luggage racks.\n"
                "* 🚲 **Bicycles:** Dedicated bike racks are available in the first and last carriages of Stadler commuter trains.\n"
                "* ☕ **Bistro & Refreshments:** Onboard bistro car with hot beverages and snacks is available on the Baku-Ganja corridor."
            )

    # -------------------------------------------------------------
    # 7. Baku-Sumgayit (ADY-104) Specific Inquiries
    # -------------------------------------------------------------
    if any(k in q for k in ["sumgayit", "sumqayıt", "sumqayit", "сумгаит", "104", "absheron", "abşeron", "абшерон"]):
        t = LIVE_TRAINS["ADY-104"]
        if lang == "AZ":
            return (
                f"🚆 **ADY-104 Abşeron Dairəvi Sürət Qatarı (Bakı ⇄ Sumqayıt):**\n\n"
                f"* **Marşrut:** Bakı Mərkəzi ➔ Keşlə ➔ Biləcəri ➔ Xırdalan ➔ Sumqayıt Sərnişin\n"
                f"* **Cari Mövqe:** `{t['current_station']}` ➔ `{t['next_station']}`\n"
                f"* **Sumqayıta Çatma Vaxtı (ETA):** `{t['scheduled_eta']}` ({t['delay_minutes']} dəq gecikmə bərpa olunur)\n"
                f"* **Sürət Həddi:** `{t['current_speed_kmh']} km/saat` (Xəzər sahili küləyinə uyğun olaraq tənzimlənib)\n"
                f"* **İnterval:** Pik saatlarda hər 15–20 dəqiqədən bir hərəkət edir."
            )
        elif lang == "RU":
            return (
                f"🚆 **ADY-104 Абшеронский экспресс (Баку ⇄ Сумгаит):**\n\n"
                f"* **Маршрут:** Баку-Пасс. ➔ Кешля ➔ Баладжары ➔ Хырдалан ➔ Сумгаит\n"
                f"* **Текущее положение:** `{t['current_station']}` ➔ `{t['next_station']}`\n"
                f"* **Время прибытия (ETA):** `{t['scheduled_eta']}` (задержка: {t['delay_minutes']} мин нагоняется)\n"
                f"* **Скорость:** `{t['current_speed_kmh']} км/ч` (скорректирована с учетом каспийского ветра)\n"
                f"* **Интервал:** В часы пик каждые 15–20 минут."
            )
        else:
            return (
                f"🚆 **ADY-104 Absheron Circular Express (Baku ⇄ Sumgayit):**\n\n"
                f"* **Corridor Route:** Baku Central ➔ Keshla ➔ Bilajari Junction ➔ Khirdalan ➔ Sumgayit Passenger\n"
                f"* **Current Location:** `{t['current_station']}` ➔ `{t['next_station']}`\n"
                f"* **Sumgayit Arrival (ETA):** `{t['scheduled_eta']}` ({t['delay_minutes']} min delay recovery active)\n"
                f"* **Approved Speed:** `{t['current_speed_kmh']} km/h`\n"
                f"* **Service Frequency:** Departs every 15–20 minutes during peak transit hours."
            )

    # -------------------------------------------------------------
    # 8. Baku-Ganja (ADY-702) Specific Inquiries
    # -------------------------------------------------------------
    if any(k in q for k in ["ganja", "gəncə", "gence", "гянджа", "702"]):
        t = LIVE_TRAINS["ADY-702"]
        if lang == "AZ":
            return (
                f"⚡ **ADY-702 Bakı ➔ Gəncə Sürət Qatarı:**\n\n"
                f"* **Marşrut:** Bakı Mərkəzi ➔ Biləcəri ➔ Kürdəmir ➔ Yevlax ➔ Gəncə Mərkəzi\n"
                f"* **Cari Mövqe:** `{t['current_station']}` ➔ `{t['next_station']}`\n"
                f"* **Gəncəyə Çatma (ETA):** `{t['scheduled_eta']}`\n"
                f"* **Sürət:** `{t['current_speed_kmh']} km/saat` (Goranboy-Yevlax düzənliyində 145 km/saat sürət həddi)\n"
                f"* **Status:** Əsas magistral xətt açıqdır, hərəkət qrafikə uyğundur."
            )
        elif lang == "RU":
            return (
                f"⚡ **ADY-702 Скоростной экспресс Баку ➔ Гянджа:**\n\n"
                f"* **Маршрут:** Баку-Пасс. ➔ Баладжары ➔ Кюрдамир ➔ Евлах ➔ Гянджа\n"
                f"* **Текущее положение:** `{t['current_station']}` ➔ `{t['next_station']}`\n"
                f"* **Прибытие в Гянджу (ETA):** `{t['scheduled_eta']}`\n"
                f"* **Скорость:** `{t['current_speed_kmh']} км/ч` (максимальная скорость на равнинном участке до 145 км/ч)\n"
                f"* **Статус:** Главный ход свободен, график соблюдается."
            )
        else:
            return (
                f"⚡ **ADY-702 Baku ➔ Ganja High-Speed Express:**\n\n"
                f"* **Corridor Route:** Baku Central ➔ Bilajari ➔ Kurdamir ➔ Yevlakh ➔ Ganja Central\n"
                f"* **Current Location:** `{t['current_station']}` ➔ `{t['next_station']}`\n"
                f"* **Ganja Arrival (ETA):** `{t['scheduled_eta']}`\n"
                f"* **Speed Profile:** `{t['current_speed_kmh']} km/h` (up to 145 km/h on central plains)\n"
                f"* **Status:** Main line clear and operating smoothly."
            )

    # -------------------------------------------------------------
    # 9. Baku-Tbilisi (ADY-410 Silk Road) Specific Inquiries
    # -------------------------------------------------------------
    if any(k in q for k in ["tbilisi", "tiflis", "тбилиси", "410", "silk road", "ipək yolu", "ipek yolu", "шелковый"]):
        t = LIVE_TRAINS["ADY-410"]
        if lang == "AZ":
            return (
                f"🌍 **ADY-410 İpək Yolu Beynəlxalq Ekspresi (Bakı ➔ Tbilisi):**\n\n"
                f"* **Marşrut:** Bakı ➔ Gəncə ➔ Şəmkir ➔ Tovuz ➔ Ağstafa ➔ Böyük Kəsik ➔ Tbilisi Mərkəzi\n"
                f"* **Cari Mövqe:** `{t['current_station']}` ➔ `{t['next_station']}`\n"
                f"* **Tbilisiyə Çatma (ETA):** `{t['scheduled_eta']}`\n"
                f"* **Sürət:** `{t['current_speed_kmh']} km/saat`\n"
                f"* **Status:** Sərhəd dəhlizində dəqiq qrafiklə hərəkət edir (Gecikmə: 0 dəqiqə)."
            )
        elif lang == "RU":
            return (
                f"🌍 **ADY-410 Экспресс Шёлковый Путь (Баку ➔ Тбилиси):**\n\n"
                f"* **Маршрут:** Баку ➔ Гянджа ➔ Шамкир ➔ Товуз ➔ Агстафа ➔ Беюк-Кясик ➔ Тбилиси\n"
                f"* **Текущее положение:** `{t['current_station']}` ➔ `{t['next_station']}`\n"
                f"* **Прибытие в Тбилиси (ETA):** `{t['scheduled_eta']}`\n"
                f"* **Скорость:** `{t['current_speed_kmh']} км/ч`\n"
                f"* **Статус:** Движение строго по расписанию через пограничный коридор (0 мин задержки)."
            )
        else:
            return (
                f"🌍 **ADY-410 Silk Road International Express (Baku ➔ Tbilisi):**\n\n"
                f"* **Corridor Route:** Baku ➔ Ganja ➔ Shamkir ➔ Tovuz ➔ Agstafa ➔ Boyuk Kasik ➔ Tbilisi Central\n"
                f"* **Current Location:** `{t['current_station']}` ➔ `{t['next_station']}`\n"
                f"* **Tbilisi Arrival (ETA):** `{t['scheduled_eta']}`\n"
                f"* **Operating Speed:** `{t['current_speed_kmh']} km/h`\n"
                f"* **Status:** On-Time nominal schedule across the western border."
            )

    # -------------------------------------------------------------
    # 10. Wind / Weather / Safety Limits Inquiries
    # -------------------------------------------------------------
    if any(k in q for k in ["wind", "weather", "külək", "kulek", "hava", "ветер", "погода", "xəzri", "xazri", "хазри"]):
        if lang == "AZ":
            return (
                "🌬️ **Xəzər Sahili Külək və Dəmir Yolu Təhlükəsizlik Rejimi:**\n\n"
                f"* **Abşeron Dəhlizi:** Külək sürəti `{CORRIDOR_SIGNALS['ABSHERON-RING']['wind_speed_kmh']} km/saat` (Xəzri küləyi).\n"
                "* **Təhlükəsizlik Qaydası:** Əgər külək > 65 km/saat olarsa, kontakt şəbəkəsi və yan külək təhlükəsizliyi üçün sürət **80 km/saat** həddində məhdudlaşdırılır.\n"
                f"* **Gəncə Düzənliyi:** Külək sürəti `{CORRIDOR_SIGNALS['BAKU-GANJA']['wind_speed_kmh']} km/saat` (Normal).\n"
                f"* **Qərb Sərhəd Dəhlizi:** Külək sürəti `{CORRIDOR_SIGNALS['SILK-ROAD']['wind_speed_kmh']} km/saat` (Açıq)."
            )
        elif lang == "RU":
            return (
                "🌬️ **Погодные условия на Каспийском побережье и железнодорожная безопасность:**\n\n"
                f"* **Абшеронский коридор:** Скорость ветра `{CORRIDOR_SIGNALS['ABSHERON-RING']['wind_speed_kmh']} км/ч` (ветер Хазри).\n"
                "* **Правило безопасности:** При скорости ветра свыше 65 км/ч система безопасности автоматически ограничивает скорость до **80 км/ч** во избежание повреждения контактной сети.\n"
                f"* **Гянджинский коридор:** Скорость ветра `{CORRIDOR_SIGNALS['BAKU-GANJA']['wind_speed_kmh']} км/ч` (В норме).\n"
                f"* **Западный коридор:** Скорость ветра `{CORRIDOR_SIGNALS['SILK-ROAD']['wind_speed_kmh']} км/ч` (Открыт)."
            )
        else:
            return (
                "🌬️ **Caspian Crosswind & Railway Safety Regulation:**\n\n"
                f"* **Absheron Corridor:** Wind speed `{CORRIDOR_SIGNALS['ABSHERON-RING']['wind_speed_kmh']} km/h` (*Khazri* gale).\n"
                "* **Safety Guardrail Rule:** If winds exceed 65 km/h on exposed coastal causeways, train speed is strictly clamped to **80 km/h** to protect overhead catenary wires and prevent lateral instability.\n"
                f"* **Baku-Ganja Corridor:** Wind speed `{CORRIDOR_SIGNALS['BAKU-GANJA']['wind_speed_kmh']} km/h` (Normal).\n"
                f"* **Western Silk Road Corridor:** Wind speed `{CORRIDOR_SIGNALS['SILK-ROAD']['wind_speed_kmh']} km/h` (Clear)."
            )

    # -------------------------------------------------------------
    # 11. Comprehensive Fallback with Live Context & Helpful Suggestions
    # -------------------------------------------------------------
    if lang == "AZ":
        return (
            f"ℹ️ **Sualınız üçün məlumat tapıldı:**\n\n"
            f"Hazırda seçilmiş qatar **{selected_train}** ({active_info['route_name']}) üzrə canlı vəziyyət:\n"
            f"• **Mövqe:** `{active_info['current_station']}` ➔ `{active_info['next_station']}`\n"
            f"• **Sürət:** `{approved_speed} km/saat` | **Çatma vaxtı:** `{updated_eta}` ({delay_min} dəq gecikmə)\n\n"
            "📋 **Gündəlik Sərnişin və Cədvəl Məlumatları:**\n"
            "1. **Bakı ⇄ Sumqayıt:** Stadler ikimərtəbəli qatarları hər 15–20 dəqiqədən bir çıxır (BakıKartla turniketdən ödəniş).\n"
            "2. **Bakı ⇄ Gəncə:** Sürət qatarları hər gün Bakı Mərkəzi Vağzalından yola düşür.\n"
            "3. **Hava Limanı:** Terminaldan H1 ekspres avtobusu ilə Bakı Mərkəzi Vağzalına (~30 dəq) çata bilərsiniz.\n\n"
            "💡 *Daha dəqiq məlumat üçün sualınızı 'Sumqayıt cədvəli', 'Bilet qiyməti', 'Aeroportdan otelə' və ya 'Wi-Fi' kimi qeyd edə bilərsiniz.*"
        )
    elif lang == "RU":
        return (
            f"ℹ️ **Информация по вашему запросу:**\n\n"
            f"Текущий выбранный поезд **{selected_train}** ({active_info['route_name']}):\n"
            f"• **Положение:** `{active_info['current_station']}` ➔ `{active_info['next_station']}`\n"
            f"• **Скорость:** `{approved_speed} км/ч` | **Прибытие (ETA):** `{updated_eta}` (задержка: {delay_min} мин)\n\n"
            "📋 **Часто запрашиваемая информация:**\n"
            "1. **Баку ⇄ Сумгаит:** Поезда Stadler отправляются каждые 15–20 минут (оплата через BakıKart).\n"
            "2. **Баку ⇄ Гянджа:** Ежедневные скоростные рейсы с Бакинского вокзала.\n"
            "3. **Аэропорт:** Автобус-экспресс H1 доставит из аэропорта до вокзала 28 Мая за ~30 минут.\n\n"
            "💡 *Для быстрого ответа попробуйте спросить: 'Расписание в Сумгаит', 'Цена билетов', 'Как доехать из аэропорта' или 'Wi-Fi в поезде'.*"
        )
    else:
        return (
            f"ℹ️ **Information regarding your inquiry:**\n\n"
            f"Currently active train **{selected_train}** ({active_info['route_name']}):\n"
            f"• **Location:** `{active_info['current_station']}` ➔ `{active_info['next_station']}`\n"
            f"• **Speed:** `{approved_speed} km/h` | **ETA:** `{updated_eta}` ({delay_min} min delay recovery active)\n\n"
            "📋 **Popular Passenger Information:**\n"
            "1. **Baku ⇄ Sumgayit Commuter:** High-frequency Stadler trains every 15–20 mins (tap turnstiles with BakuCard or Apple Pay).\n"
            "2. **Baku ⇄ Ganja High-Speed:** Daily express departures directly from Baku Central Station.\n"
            "3. **Airport Transit:** BakuBus Aero Express H1 runs 24/7 directly to Baku Central Station (30 mins).\n\n"
            "💡 *You can also ask: 'Next train to Sumgayit', 'Ticket fares', 'Airport to Radisson', or 'Is there Wi-Fi onboard?'*"
        )
