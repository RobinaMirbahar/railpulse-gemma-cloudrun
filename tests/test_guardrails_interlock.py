"""Fail-closed tests for block occupancy and wind inputs (follow-up to #2).

Every case here feeds the guardrail a signalling input it cannot trust: a missing block status,
a missing or unparseable wind reading, or a passing loop that is not FREE. None of them may be
reinterpreted as "clear". Note that `approved_speed_kmh` is the guardrail's own output, not the
observed speed of a train.
"""

import pytest

from railpulse_agent.guardrails import enforce_railway_physics_limits
from railpulse_agent.tools import calculate_schedule_recovery

CLEAR_BTK = {
    "primary_block_id": "BLK-AGSTAFA-M1",
    "primary_block_status": "FREE",
    "siding_block_id": "BLK-AGSTAFA-SIDING-S1",
    "siding_block_status": "FREE",
    "wind_speed_kmh": 28,
    "telemetry_age_s": 0.0,
}


def guardrails(requested_speed_kmh=140, omit=(), **overrides):
    state = {k: v for k, v in CLEAR_BTK.items() if k not in omit}
    state.update(overrides)
    return enforce_railway_physics_limits(
        train_id="ADY-410",
        requested_speed_kmh=requested_speed_kmh,
        use_passing_siding=False,
        corridor_state=state,
    )


def test_clear_corridor_is_untouched():
    res = guardrails()
    assert res["approved_speed_kmh"] == 140
    assert res["assigned_track_block"] == "BLK-AGSTAFA-M1"
    assert res["guardrail_interlock_passed"] is True


def test_missing_primary_block_status_is_not_free():
    res = guardrails(omit=("primary_block_status",))
    assert res["assigned_track_block"] == "BLK-AGSTAFA-SIDING-S1"


def test_null_primary_block_status_is_not_free():
    res = guardrails(primary_block_status=None)
    assert res["assigned_track_block"] == "BLK-AGSTAFA-SIDING-S1"


def test_occupied_passing_loop_holds_the_train():
    res = guardrails(
        140,
        primary_block_status="OCCUPIED",
        siding_block_status="OCCUPIED",
    )
    assert res["approved_speed_kmh"] == 0
    assert res["guardrail_interlock_passed"] is False


def test_stale_feed_and_occupied_loop_both_apply():
    res = guardrails(
        140,
        telemetry_age_s=60.0,
        primary_block_status="MAINTENANCE",
        siding_block_status="OCCUPIED",
    )
    assert res["approved_speed_kmh"] == 0
    assert res["stale_reason"] == "expired"
    assert res["guardrail_interlock_passed"] is False


@pytest.mark.parametrize(
    "wind",
    [
        pytest.param(None, id="null"),
        pytest.param("72 km/h", id="unparseable"),
        pytest.param(float("nan"), id="nan"),
    ],
)
def test_untrustworthy_wind_is_not_calm(wind):
    res = guardrails(150, wind_speed_kmh=wind)
    assert res["approved_speed_kmh"] == 80
    assert "wind_unknown" in res["guardrail_note"]


def test_missing_wind_key_is_not_calm():
    res = guardrails(150, omit=("wind_speed_kmh",))
    assert res["approved_speed_kmh"] == 80
    assert "wind_unknown" in res["guardrail_note"]


def test_reported_interlock_flag_matches_the_hold():
    # A real reroute onto a verified FREE loop still passes; the flag must not be a constant.
    rerouted = calculate_schedule_recovery(train_id="ADY-702", target_speed_kmh=150)
    assert rerouted["assigned_track_block"] == "BLK-BILAJARI-SIDING-S1"
    assert rerouted["guardrail_interlock_passed"] is True

    held = guardrails(140, primary_block_status="OCCUPIED", siding_block_status="OCCUPIED")
    assert held["guardrail_interlock_passed"] is False
