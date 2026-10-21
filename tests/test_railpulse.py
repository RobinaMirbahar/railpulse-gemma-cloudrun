"""Unit and integration tests for RailPulse AI tools, guardrails, and structured JSON schema."""

from railpulse_agent.agent import run_railpulse_dispatch
from railpulse_agent.schemas import RailDispatchAdvisory
from railpulse_agent.tools import (
    calculate_schedule_recovery,
    check_corridor_signals_and_wind,
    get_live_train_telemetry,
)


def test_get_live_train_telemetry() -> None:
    telemetry = get_live_train_telemetry("ADY-702")
    assert telemetry["train_id"] == "ADY-702"
    assert telemetry["corridor_id"] == "BAKU-GANJA"
    assert telemetry["delay_minutes"] >= 0


def test_deterministic_wind_and_block_interlock_guardrail() -> None:
    # ADY-702 is on BAKU-GANJA where primary block BLK-BILAJARI-B3 is OCCUPIED and wind is 72 km/h (>65 km/h)
    recovery = calculate_schedule_recovery(
        train_id="ADY-702",
        target_speed_kmh=150,
        use_passing_siding=False,
    )
    # Must clamp speed from 150 -> 80 km/h due to 72 km/h Caspian wind
    assert recovery["approved_speed_kmh"] == 80
    # Must automatically reroute away from OCCUPIED primary block onto FREE passing loop siding
    assert recovery["assigned_track_block"] == "BLK-BILAJARI-SIDING-S1"
    assert recovery["guardrail_interlock_passed"] is True


def test_structured_json_dispatch_advisory() -> None:
    advisory = run_railpulse_dispatch(train_id="ADY-702", requested_speed_kmh=145)
    assert isinstance(advisory, RailDispatchAdvisory)
    assert advisory.approved_speed_kmh <= 80
    assert advisory.assigned_block_id == "BLK-BILAJARI-SIDING-S1"
    assert advisory.tools_invoked == [
        "get_live_train_telemetry",
        "check_corridor_signals_and_wind",
        "calculate_schedule_recovery",
    ]


def test_clear_corridor_btk_express() -> None:
    signals = check_corridor_signals_and_wind("BTK-CORRIDOR")
    assert signals["primary_block_status"] == "FREE"
    advisory = run_railpulse_dispatch(train_id="ADY-410", requested_speed_kmh=110)
    assert advisory.approved_speed_kmh == 110
    assert advisory.operational_status == "ON_TIME"
