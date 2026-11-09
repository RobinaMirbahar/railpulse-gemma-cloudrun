"""Deterministic railway physics & block interlocking guardrails (Non-Security operational safety)."""

import math
import time
from typing import Any, Dict, Optional

from railpulse_agent.schemas import GuardrailDecision, StaleReason

MAX_HIGH_WIND_SPEED_KMH = 80
HIGH_WIND_THRESHOLD_KMH = 65
MAX_PASSENGER_RAIL_SPEED_KMH = 160
MAX_TELEMETRY_AGE_S = 15.0
MIN_CLOCK_SKEW_TOLERANCE_S = -0.5


def _parse_wind_kmh(raw: Any) -> Optional[float]:
    """Parse a wind reading, returning None when there is no usable number to act on."""
    if raw is None:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(value):
        return None
    return min(max(value, 0.0), 200.0)


def _normalize_block_status(raw: Any) -> str:
    """Normalise a block occupancy field. A missing or empty status is UNKNOWN, never FREE."""
    if raw is None:
        return "UNKNOWN"
    status = str(raw).strip().upper()
    return status or "UNKNOWN"


def _resolve_telemetry_freshness(
    corridor_state: Dict[str, Any],
    now_monotonic: Optional[float] = None,
) -> tuple[Optional[float], Optional[float], Optional[StaleReason]]:
    """Derive consumer-side monotonic age and check wayside producer clock skew.

    - Consumer age is derived from `now_monotonic - received_at_monotonic` when stamped at ingest.
    - Wayside producer clock drift (`producer_offset_s = observed_at - received_at`) is tracked as
      telemetry and triggers `stale_reason="clock_skew"` if the producer clock runs ahead by more
      than 0.500s (`age_s < -0.500` or `producer_offset_s > 0.500`).
    """
    producer_offset_s: Optional[float] = corridor_state.get("producer_offset_s")
    if producer_offset_s is not None:
        producer_offset_s = float(producer_offset_s)

    explicit_age = corridor_state.get("telemetry_age_s", corridor_state.get("age_s"))
    received_mono = corridor_state.get("received_at_monotonic")

    age_s: Optional[float] = None
    if explicit_age is not None:
        age_s = float(explicit_age)
    elif received_mono is not None:
        ref_mono = float(now_monotonic) if now_monotonic is not None else time.monotonic()
        age_s = round(ref_mono - float(received_mono), 6)

    # Check future-stamped wayside packet / negative effective age beyond -0.500s tolerance
    if producer_offset_s is not None and producer_offset_s > abs(MIN_CLOCK_SKEW_TOLERANCE_S):
        return age_s, producer_offset_s, "clock_skew"
    if age_s is not None:
        if age_s < MIN_CLOCK_SKEW_TOLERANCE_S:
            if producer_offset_s is None:
                producer_offset_s = -age_s
            return age_s, producer_offset_s, "clock_skew"
        if age_s > MAX_TELEMETRY_AGE_S:
            return age_s, producer_offset_s, "expired"

    return age_s, producer_offset_s, None


def enforce_railway_physics_limits(
    train_id: str,
    requested_speed_kmh: int,
    use_passing_siding: bool,
    corridor_state: Dict[str, Any],
    now_monotonic: Optional[float] = None,
) -> Dict[str, Any]:
    """Deterministically enforce telemetry freshness, railway block occupancy, and Caspian wind caps.

    Rules enforced:
    0. Telemetry Freshness & Clock-Skew Interlock:
       - If telemetry is future-stamped beyond 0.500s (`age_s < -0.500` or `producer_offset_s > 0.500`),
         clamp speed to 0 km/h with `stale_reason="clock_skew"`.
       - If consumer monotonic age exceeds 15.000s (`age_s > 15.000`), clamp speed to 0 km/h with
         `stale_reason="expired"`.
    1. Block Occupancy Interlock: A train can NEVER enter an OCCUPIED or MAINTENANCE primary block.
       If the primary block is not FREE, the guardrail automatically switches the route to the FREE
       passing siding block.
    2. Caspian High-Wind Speed Cap: If corridor crosswinds exceed 65 km/h, max train speed is
       clamped to 80 km/h regardless of what the LLM requests.
    3. Passenger Corridor Speed Ceiling: Max speed is clamped to 160 km/h.
    """
    notes = []
    age_s, producer_offset_s, stale_reason = _resolve_telemetry_freshness(
        corridor_state, now_monotonic=now_monotonic
    )

    if stale_reason == "clock_skew":
        approved_speed = 0
        notes.append(
            f"Clock-skew interlock triggered (age_s={age_s}, producer_offset_s={producer_offset_s}): "
            "clamped speed to 0 km/h (stale_reason='clock_skew')."
        )
    elif stale_reason == "expired":
        approved_speed = 0
        notes.append(
            f"Stale telemetry interlock triggered (age_s={age_s}s > {MAX_TELEMETRY_AGE_S}s): "
            "clamped speed to 0 km/h (stale_reason='expired')."
        )
    else:
        approved_speed = max(20, int(requested_speed_kmh))

        # Rule 1: Passenger rail ceiling
        if approved_speed > MAX_PASSENGER_RAIL_SPEED_KMH:
            notes.append(
                f"Clamped requested speed {approved_speed} km/h -> {MAX_PASSENGER_RAIL_SPEED_KMH} km/h (corridor max)."
            )
            approved_speed = MAX_PASSENGER_RAIL_SPEED_KMH

        # Rule 2: Caspian wind-speed cap. An unreadable sensor is not calm weather: a missing,
        # non-numeric or NaN reading is capped exactly like a high-wind reading until data arrives.
        wind_kmh = _parse_wind_kmh(corridor_state.get("wind_speed_kmh"))
        if wind_kmh is None:
            if approved_speed > MAX_HIGH_WIND_SPEED_KMH:
                notes.append(
                    f"Wind reading unavailable (raw={corridor_state.get('wind_speed_kmh')!r}): "
                    f"clamped speed {approved_speed} km/h -> {MAX_HIGH_WIND_SPEED_KMH} km/h (wind_unknown)."
                )
                approved_speed = MAX_HIGH_WIND_SPEED_KMH
        elif wind_kmh > HIGH_WIND_THRESHOLD_KMH and approved_speed > MAX_HIGH_WIND_SPEED_KMH:
            notes.append(
                f"High-wind interlock triggered (wind={wind_kmh:g} km/h > {HIGH_WIND_THRESHOLD_KMH} km/h): "
                f"clamped speed {approved_speed} km/h -> {MAX_HIGH_WIND_SPEED_KMH} km/h."
            )
            approved_speed = MAX_HIGH_WIND_SPEED_KMH

    # Rule 3: Single-track / block occupancy collision interlock. An unknown status is never
    # treated as FREE: a missing field routes the train to the loop exactly like an OCCUPIED one.
    primary_status = _normalize_block_status(corridor_state.get("primary_block_status"))
    primary_block = corridor_state.get("primary_block_id", "BLK-PRIMARY")
    siding_block = corridor_state.get("siding_block_id", "BLK-SIDING")
    interlock_passed = True

    if primary_status != "FREE" or use_passing_siding:
        assigned_block = siding_block
        if primary_status != "FREE":
            notes.append(
                f"Block collision interlock triggered: {primary_block} is {primary_status}; "
                f"auto-rerouted {train_id} onto passing loop {siding_block}."
            )

        # The loop itself still has to be verified FREE, otherwise there is no safe block at all.
        siding_status = _normalize_block_status(corridor_state.get("siding_block_status"))
        if siding_status != "FREE":
            interlock_passed = False
            approved_speed = 0
            notes.append(
                f"Passing loop {siding_block} is {siding_status}: no verified block for {train_id}, "
                "held at 0 km/h at the signal."
            )
        else:
            notes.append(f"Verified passing loop {siding_block} is FREE for {train_id}.")
    else:
        assigned_block = primary_block
        notes.append(f"Verified primary block {primary_block} is FREE for {train_id}.")

    return {
        "speed_kmh": approved_speed,
        "approved_speed_kmh": approved_speed,
        "assigned_track_block": assigned_block,
        "guardrail_interlock_passed": interlock_passed,
        "stale_reason": stale_reason,
        "producer_offset_s": producer_offset_s,
        "guardrail_note": " | ".join(notes),
    }


def wind_at(
    age_s: float,
    wind_speed_kmh: int = 28,
    requested_speed_kmh: int = 140,
    train_id: str = "ADY-702",
) -> Dict[str, Any]:
    """Construct a corridor wind telemetry packet at a target age or clock-skew offset for testing."""
    now_mono = time.monotonic()
    return {
        "train_id": train_id,
        "requested_speed_kmh": requested_speed_kmh,
        "use_passing_siding": False,
        "now_monotonic": now_mono,
        "corridor_state": {
            "corridor_id": "BAKU-GANJA",
            "primary_block_id": "BLK-BILAJARI-B3",
            "primary_block_status": "FREE",
            "siding_block_id": "BLK-BILAJARI-SIDING-S1",
            "siding_block_status": "FREE",
            "wind_speed_kmh": wind_speed_kmh,
            "received_at_monotonic": now_mono - float(age_s),
            "producer_offset_s": -float(age_s) if age_s < 0 else 0.0,
            "telemetry_age_s": float(age_s),
        },
    }


def enforce_guardrails(packet: Dict[str, Any]) -> GuardrailDecision:
    """Evaluate a telemetry packet through `enforce_railway_physics_limits` and return a `GuardrailDecision`."""
    corridor_state = packet.get("corridor_state", packet)
    res = enforce_railway_physics_limits(
        train_id=str(packet.get("train_id", "ADY-702")),
        requested_speed_kmh=int(packet.get("requested_speed_kmh", 140)),
        use_passing_siding=bool(packet.get("use_passing_siding", False)),
        corridor_state=corridor_state,
        now_monotonic=packet.get("now_monotonic"),
    )
    return GuardrailDecision(**res)


def railway_interlock_guardrail(
    tool: Any,
    args: Dict[str, Any],
    tool_context: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    """Google ADK before_tool_callback that deterministically sanitizes tool arguments before execution."""
    tool_name = getattr(tool, "name", None) or getattr(tool, "__name__", str(tool))

    if tool_name == "calculate_schedule_recovery":
        raw_speed = int(args.get("target_speed_kmh", 120))
        if raw_speed < 0:
            args["target_speed_kmh"] = 60
        elif raw_speed > MAX_PASSENGER_RAIL_SPEED_KMH:
            args["target_speed_kmh"] = MAX_PASSENGER_RAIL_SPEED_KMH

    # Returning None allows ADK to proceed with the sanitized tool arguments
    return None
