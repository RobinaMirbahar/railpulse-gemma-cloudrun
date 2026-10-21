"""Google ADK LlmAgent definition for RailPulse AI powered by open-weights Gemma on Cloud Run."""

import os
from typing import Any, Dict, Optional

from railpulse_agent.guardrails import railway_interlock_guardrail
from railpulse_agent.schemas import RailDispatchAdvisory
from railpulse_agent.tools import (
    calculate_schedule_recovery,
    check_corridor_signals_and_wind,
    get_live_train_telemetry,
)

DEFAULT_GEMMA_MODEL = os.environ.get("GEMMA_MODEL_NAME", "ollama_chat/gemma3:4b")
DEFAULT_OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")

SYSTEM_INSTRUCTION = """You are RailPulseDispatcher, an open-source AI Rail Operations & Smart Dispatch Agent
running on Google Cloud Run and powered by Google's open-weights Gemma model family.

For every train dispatch request, you MUST follow this exact 3-step operational sequence:
1. Call `get_live_train_telemetry(train_id)` to inspect the train's live GPS position, current speed, and delay.
2. Call `check_corridor_signals_and_wind(corridor_id)` to inspect track block occupancy ('FREE' vs 'OCCUPIED') and live Caspian crosswind speeds.
3. Call `calculate_schedule_recovery(train_id, target_speed_kmh, use_passing_siding)` to compute the guardrail-verified cruise speed, track block assignment, and updated station ETA.
4. Return your final dispatch advisory strictly conforming to the `RailDispatchAdvisory` JSON schema.
"""


def build_railpulse_agent(
    model_name: str = DEFAULT_GEMMA_MODEL,
    api_base: str = DEFAULT_OLLAMA_BASE,
) -> Any:
    """Construct the Google ADK LlmAgent wired to Gemma via LiteLLM, Python tools, guardrail, and JSON schema."""
    try:
        from google.adk.agents import LlmAgent
        from google.adk.models.lite_llm import LiteLlm

        gemma_llm = LiteLlm(model=model_name, api_base=api_base)
        return LlmAgent(
            name="RailPulseDispatcher",
            model=gemma_llm,
            instruction=SYSTEM_INSTRUCTION,
            tools=[
                get_live_train_telemetry,
                check_corridor_signals_and_wind,
                calculate_schedule_recovery,
            ],
            before_tool_callback=railway_interlock_guardrail,
            output_schema=RailDispatchAdvisory,
            output_key="rail_dispatch_advisory",
        )
    except Exception:
        # Fallback lightweight descriptor when running in minimal environments
        return {
            "name": "RailPulseDispatcher",
            "model": model_name,
            "api_base": api_base,
            "tools": [
                "get_live_train_telemetry",
                "check_corridor_signals_and_wind",
                "calculate_schedule_recovery",
            ],
            "output_schema": "RailDispatchAdvisory",
        }


def run_railpulse_dispatch(
    train_id: str = "ADY-702",
    requested_speed_kmh: int = 145,
    prefer_siding: Optional[bool] = None,
) -> RailDispatchAdvisory:
    """Execute the 3-step RailPulse tool trajectory with deterministic railway guardrails and return validated JSON."""
    # Step 1: Fetch live train GPS & delay telemetry
    telemetry = get_live_train_telemetry(train_id)

    # Step 2: Check corridor signals and Caspian wind speed
    signals = check_corridor_signals_and_wind(telemetry["corridor_id"])

    # Determine whether passing siding is needed
    use_siding = (
        prefer_siding
        if prefer_siding is not None
        else (signals["primary_block_status"] != "FREE")
    )

    # Invoke ADK before_tool_callback guardrail on the tool arguments
    tool_args: Dict[str, Any] = {
        "train_id": telemetry["train_id"],
        "target_speed_kmh": requested_speed_kmh,
        "use_passing_siding": use_siding,
    }
    railway_interlock_guardrail(calculate_schedule_recovery, tool_args, None)

    # Step 3: Compute deterministic schedule recovery & interlocking check
    recovery = calculate_schedule_recovery(**tool_args)

    # Classify operational badge
    if signals["wind_speed_kmh"] > 65:
        status_badge = "WIND_SPEED_RESTRICTED"
    elif signals["primary_block_status"] != "FREE":
        status_badge = "REROUTED_SIDING"
    elif recovery["remaining_delay_minutes"] > 0:
        status_badge = "DELAY_RECOVERY"
    else:
        status_badge = "ON_TIME"

    announcement = (
        f"Attention passengers on {telemetry['route_name']} ({telemetry['train_id']}) bound for "
        f"{telemetry['next_station']}: Assigned to block {recovery['assigned_track_block']} at "
        f"{recovery['approved_speed_kmh']} km/h. Updated arrival time is {recovery['updated_eta']} "
        f"({recovery['recovered_minutes']} min recovered)."
    )

    return RailDispatchAdvisory(
        train_id=telemetry["train_id"],
        route_name=telemetry["route_name"],
        operational_status=status_badge,
        approved_speed_kmh=recovery["approved_speed_kmh"],
        assigned_block_id=recovery["assigned_track_block"],
        updated_eta=recovery["updated_eta"],
        delay_minutes_remaining=recovery["remaining_delay_minutes"],
        tools_invoked=[
            "get_live_train_telemetry",
            "check_corridor_signals_and_wind",
            "calculate_schedule_recovery",
        ],
        guardrail_interlock_passed=recovery["guardrail_interlock_passed"],
        guardrail_intervention_summary=recovery["guardrail_note"],
        passenger_announcement=announcement,
    )
