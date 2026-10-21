"""Pure-Python function calling tools for live rail telemetry, signals, and schedule recovery."""

from typing import Any, Dict

# Live state store for Azerbaijan Railways (ADY) corridors (mutable via Streamlit simulator)
LIVE_TRAINS: Dict[str, Dict[str, Any]] = {
    "ADY-702": {
        "train_id": "ADY-702",
        "route_name": "Baku-Ganja High-Speed Express",
        "corridor_id": "BAKU-GANJA",
        "current_station": "Baku Central",
        "next_station": "Yevlakh Junction",
        "latitude": 40.4093,
        "longitude": 49.8671,
        "current_speed_kmh": 140,
        "delay_minutes": 18,
        "current_block_id": "BLK-BAKU-01",
        "scheduled_eta": "14:30",
    },
    "ADY-104": {
        "train_id": "ADY-104",
        "route_name": "Baku-Sumgayit Absheron Commuter",
        "corridor_id": "ABSHERON-RING",
        "current_station": "Bilajari Junction",
        "next_station": "Sumgayit Passenger",
        "latitude": 40.4985,
        "longitude": 49.7512,
        "current_speed_kmh": 95,
        "delay_minutes": 12,
        "current_block_id": "BLK-ABS-02",
        "scheduled_eta": "13:15",
    },
    "ADY-410": {
        "train_id": "ADY-410",
        "route_name": "Baku-Tbilisi Silk Road Express",
        "corridor_id": "BTK-CORRIDOR",
        "current_station": "Ganja Central",
        "next_station": "Agstafa Border Hub",
        "latitude": 40.6828,
        "longitude": 46.3606,
        "current_speed_kmh": 110,
        "delay_minutes": 0,
        "current_block_id": "BLK-BTK-04",
        "scheduled_eta": "16:45",
    },
}

CORRIDOR_SIGNALS: Dict[str, Dict[str, Any]] = {
    "BAKU-GANJA": {
        "corridor_id": "BAKU-GANJA",
        "primary_block_id": "BLK-BILAJARI-B3",
        "primary_block_status": "OCCUPIED",
        "siding_block_id": "BLK-BILAJARI-SIDING-S1",
        "siding_block_status": "FREE",
        "wind_speed_kmh": 72,
        "weather_alert": "HIGH_CASPIAN_CROSSWIND_72KMH",
    },
    "ABSHERON-RING": {
        "corridor_id": "ABSHERON-RING",
        "primary_block_id": "BLK-SUMGAYIT-A1",
        "primary_block_status": "FREE",
        "siding_block_id": "BLK-SUMGAYIT-SIDING-S2",
        "siding_block_status": "FREE",
        "wind_speed_kmh": 78,
        "weather_alert": "SEVERE_ABSHERON_GUSTS_78KMH",
    },
    "BTK-CORRIDOR": {
        "corridor_id": "BTK-CORRIDOR",
        "primary_block_id": "BLK-AGSTAFA-M1",
        "primary_block_status": "FREE",
        "siding_block_id": "BLK-AGSTAFA-SIDING-S1",
        "siding_block_status": "FREE",
        "wind_speed_kmh": 28,
        "weather_alert": "CLEAR_CORRIDOR",
    },
}


def get_live_train_telemetry(train_id: str) -> Dict[str, Any]:
    """Fetch live GPS coordinates, current speed (km/h), delay minutes, and active track block for a train.

    Args:
        train_id: Unique train identifier such as 'ADY-702', 'ADY-104', or 'ADY-410'.

    Returns:
        Dictionary containing the train's live GPS coordinates, speed, delay, and scheduled ETA.
    """
    normalized_id = train_id.strip().upper()
    train = LIVE_TRAINS.get(normalized_id, LIVE_TRAINS["ADY-702"])
    return dict(train)


def check_corridor_signals_and_wind(corridor_id: str) -> Dict[str, Any]:
    """Check railway block occupancy ('FREE', 'OCCUPIED', 'MAINTENANCE') and live Caspian wind speed.

    Args:
        corridor_id: Corridor identifier ('BAKU-GANJA', 'ABSHERON-RING', or 'BTK-CORRIDOR').

    Returns:
        Dictionary containing primary block status, passing siding status, and live wind speed in km/h.
    """
    normalized_corridor = corridor_id.strip().upper()
    signals = CORRIDOR_SIGNALS.get(normalized_corridor, CORRIDOR_SIGNALS["BAKU-GANJA"])
    return dict(signals)


def calculate_schedule_recovery(
    train_id: str,
    target_speed_kmh: int,
    use_passing_siding: bool = False,
) -> Dict[str, Any]:
    """Calculate updated station ETA and recovered delay minutes based on target speed and track selection.

    Args:
        train_id: Unique train identifier ('ADY-702', 'ADY-104', or 'ADY-410').
        target_speed_kmh: Requested cruise speed in km/h (subject to deterministic guardrail limits).
        use_passing_siding: True to route around an occupied primary block via the passing loop siding.

    Returns:
        Dictionary containing approved_speed_kmh, assigned_track_block, recovered_minutes, and updated_eta.
    """
    from railpulse_agent.guardrails import enforce_railway_physics_limits

    train = get_live_train_telemetry(train_id)
    corridor = check_corridor_signals_and_wind(train["corridor_id"])

    # Run deterministic railway interlocking & wind-speed guardrail check
    verified = enforce_railway_physics_limits(
        train_id=train["train_id"],
        requested_speed_kmh=target_speed_kmh,
        use_passing_siding=use_passing_siding,
        corridor_state=corridor,
    )

    approved_speed = verified["approved_speed_kmh"]
    assigned_block = verified["assigned_track_block"]

    # Deterministic ETA recovery calculation
    initial_delay = int(train["delay_minutes"])
    if initial_delay == 0:
        recovered_minutes = 0
    elif approved_speed >= 130:
        recovered_minutes = min(initial_delay, 12)
    elif approved_speed >= 95:
        recovered_minutes = min(initial_delay, 7)
    else:
        recovered_minutes = min(initial_delay, 4)

    remaining_delay = max(0, initial_delay - recovered_minutes)
    base_hour, base_min = [int(x) for x in train["scheduled_eta"].split(":")]
    total_mins = base_hour * 60 + base_min + remaining_delay
    updated_eta = f"{(total_mins // 60) % 24:02d}:{total_mins % 60:02d}"

    return {
        "train_id": train["train_id"],
        "approved_speed_kmh": approved_speed,
        "assigned_track_block": assigned_block,
        "recovered_minutes": recovered_minutes,
        "remaining_delay_minutes": remaining_delay,
        "updated_eta": updated_eta,
        "guardrail_interlock_passed": True,
        "guardrail_note": verified["guardrail_note"],
    }
