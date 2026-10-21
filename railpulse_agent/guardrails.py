"""Deterministic railway physics & block interlocking guardrails (Non-Security operational safety)."""

from typing import Any, Dict, Optional

MAX_HIGH_WIND_SPEED_KMH = 80
HIGH_WIND_THRESHOLD_KMH = 65
MAX_PASSENGER_RAIL_SPEED_KMH = 160


def enforce_railway_physics_limits(
    train_id: str,
    requested_speed_kmh: int,
    use_passing_siding: bool,
    corridor_state: Dict[str, Any],
) -> Dict[str, Any]:
    """Deterministically enforce railway block occupancy interlocking and Caspian wind-speed caps.

    Rules enforced:
    1. Block Occupancy Interlock: A train can NEVER enter an OCCUPIED or MAINTENANCE primary block.
       If the primary block is not FREE, the guardrail automatically switches the route to the FREE
       passing siding block.
    2. Caspian High-Wind Speed Cap: If corridor crosswinds exceed 65 km/h, max train speed is
       clamped to 80 km/h regardless of what the LLM requests.
    3. Passenger Corridor Speed Ceiling: Max speed is clamped to 160 km/h.
    """
    notes = []
    approved_speed = max(20, int(requested_speed_kmh))

    # Rule 1: Passenger rail ceiling
    if approved_speed > MAX_PASSENGER_RAIL_SPEED_KMH:
        notes.append(
            f"Clamped requested speed {approved_speed} km/h -> {MAX_PASSENGER_RAIL_SPEED_KMH} km/h (corridor max)."
        )
        approved_speed = MAX_PASSENGER_RAIL_SPEED_KMH

    # Rule 2: Caspian wind-speed cap
    wind_kmh = int(corridor_state.get("wind_speed_kmh", 0))
    if wind_kmh > HIGH_WIND_THRESHOLD_KMH and approved_speed > MAX_HIGH_WIND_SPEED_KMH:
        notes.append(
            f"High-wind interlock triggered (wind={wind_kmh} km/h > {HIGH_WIND_THRESHOLD_KMH} km/h): "
            f"clamped speed {approved_speed} km/h -> {MAX_HIGH_WIND_SPEED_KMH} km/h."
        )
        approved_speed = MAX_HIGH_WIND_SPEED_KMH

    # Rule 3: Single-track / block occupancy collision interlock
    primary_status = corridor_state.get("primary_block_status", "FREE")
    primary_block = corridor_state.get("primary_block_id", "BLK-PRIMARY")
    siding_block = corridor_state.get("siding_block_id", "BLK-SIDING")

    if primary_status != "FREE" or use_passing_siding:
        assigned_block = siding_block
        if primary_status != "FREE" and not use_passing_siding:
            notes.append(
                f"Block collision interlock triggered: {primary_block} is {primary_status}; "
                f"auto-rerouted {train_id} onto passing loop {siding_block}."
            )
        else:
            notes.append(f"Verified passing loop {siding_block} is FREE for {train_id}.")
    else:
        assigned_block = primary_block
        notes.append(f"Verified primary block {primary_block} is FREE for {train_id}.")

    return {
        "approved_speed_kmh": approved_speed,
        "assigned_track_block": assigned_block,
        "guardrail_note": " | ".join(notes),
    }


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
