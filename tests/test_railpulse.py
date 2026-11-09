"""Unit and integration tests for RailPulse AI tools, guardrails, and structured JSON schema."""

import pytest

from railpulse_agent.agent import run_railpulse_dispatch
from railpulse_agent.guardrails import (
    enforce_guardrails,
    enforce_railway_physics_limits,
    wind_at,
)
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
    assert recovery["stale_reason"] is None


@pytest.mark.parametrize(
    "age_s,expect_speed,expect_reason",
    [
        (15.000, 140, None),
        (15.001, 0, "expired"),
        (-0.500, 140, None),
        (-0.501, 0, "clock_skew"),
    ],
)
def test_wind_age_and_stale_reason(age_s: float, expect_speed: int, expect_reason: str | None) -> None:
    packet = wind_at(age_s)
    assert packet["corridor_state"]["corridor_id"] == "BTK-CORRIDOR"
    assert packet["corridor_state"]["wind_speed_kmh"] == 28
    res = enforce_guardrails(packet)
    assert (res.speed_kmh, res.stale_reason) == (expect_speed, expect_reason)
    assert res.age_used == max(0.0, age_s)
    assert res.guardrail_interlock_passed is (expect_reason is None)


def test_consumer_monotonic_ingest_and_producer_offset_telemetry() -> None:
    # Verify that a future-stamped wayside packet (producer_offset_s > 0.5s) triggers clock_skew
    # even when consumer residence time (now_monotonic - received_at_monotonic) is 0.05s.
    res = enforce_railway_physics_limits(
        train_id="ADY-702",
        requested_speed_kmh=140,
        use_passing_siding=False,
        corridor_state={
            "primary_block_id": "BLK-BILAJARI-B3",
            "primary_block_status": "FREE",
            "siding_block_id": "BLK-BILAJARI-SIDING-S1",
            "wind_speed_kmh": 28,
            "received_at_monotonic": 1000.000,
            "producer_offset_s": 0.501,
        },
        now_monotonic=1000.050,
    )
    assert res["approved_speed_kmh"] == 0
    assert res["stale_reason"] == "clock_skew"
    assert res["producer_offset_s"] == 0.501
    assert res["age_used"] == 0.05
    assert res["guardrail_interlock_passed"] is False


def test_wall_clock_read_exactly_once_at_ingress() -> None:
    # Verify that wall time (observed_at_wall) is captured once at ingress and never re-read
    # downstream by any helper in the schedule recovery or guardrail pipeline.
    wall_calls = 0

    def fake_wall_clock() -> float:
        nonlocal wall_calls
        wall_calls += 1
        return 1762680000.0

    recovery = calculate_schedule_recovery(
        train_id="ADY-410",
        target_speed_kmh=140,
        use_passing_siding=False,
        wall_clock=fake_wall_clock,
    )
    assert wall_calls == 1
    assert recovery["approved_speed_kmh"] == 140
    assert recovery["stale_reason"] is None


def test_structured_json_dispatch_advisory() -> None:
    advisory = run_railpulse_dispatch(train_id="ADY-702", requested_speed_kmh=145)
    assert isinstance(advisory, RailDispatchAdvisory)
    assert advisory.approved_speed_kmh <= 80
    assert advisory.assigned_block_id == "BLK-BILAJARI-SIDING-S1"
    assert advisory.stale_reason is None
    assert advisory.tools_invoked == [
        "get_live_train_telemetry",
        "check_corridor_signals_and_wind",
        "calculate_schedule_recovery",
    ]


def test_clear_corridor_btk_express() -> None:
    signals = check_corridor_signals_and_wind("BTK-CORRIDOR")
    assert signals["primary_block_status"] == "FREE"
    assert isinstance(signals["received_at_monotonic"], float)
    advisory = run_railpulse_dispatch(train_id="ADY-410", requested_speed_kmh=110)
    assert advisory.approved_speed_kmh == 110
    assert advisory.operational_status == "ON_TIME"
    assert advisory.stale_reason is None
