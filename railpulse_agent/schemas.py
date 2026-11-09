"""Pydantic v2 data contracts and structured JSON output schemas for RailPulse AI."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

StaleReason = Literal["expired", "clock_skew"]


class TrainTelemetry(BaseModel):
    """Live GPS, speed, and block telemetry for an active Azerbaijan Railways (ADY) train."""

    train_id: str = Field(..., description="Unique train identifier, e.g., ADY-702.")
    route_name: str = Field(..., description="Corridor name, e.g., Baku-Ganja High-Speed Express.")
    current_station: str = Field(..., description="Last passed or current station.")
    next_station: str = Field(..., description="Upcoming station stop.")
    latitude: float = Field(..., description="Current GPS latitude.")
    longitude: float = Field(..., description="Current GPS longitude.")
    current_speed_kmh: int = Field(..., ge=0, le=250, description="Current train speed in km/h.")
    delay_minutes: int = Field(..., ge=0, description="Current schedule delay in minutes.")
    current_block_id: str = Field(..., description="Active railway track block ID.")
    scheduled_eta: str = Field(..., description="Original scheduled arrival time (HH:MM).")


class CorridorSignalWeather(BaseModel):
    """Track block occupancy and live Caspian wind telemetry along a rail corridor."""

    corridor_id: str = Field(..., description="Rail corridor identifier.")
    primary_block_id: str = Field(..., description="Primary track block ID ahead.")
    primary_block_status: Literal["FREE", "OCCUPIED", "MAINTENANCE"] = Field(
        ..., description="Signaling status of the primary block."
    )
    siding_block_id: str = Field(..., description="Passing loop / alternate siding block ID.")
    siding_block_status: Literal["FREE", "OCCUPIED"] = Field(
        ..., description="Occupancy status of the passing loop siding."
    )
    wind_speed_kmh: int = Field(..., ge=0, le=200, description="Live Caspian crosswind speed in km/h.")
    weather_alert: str = Field(..., description="Active weather advisory on the corridor.")
    received_at_monotonic: Optional[float] = Field(
        default=None,
        description="Consumer-side time.monotonic() timestamp stamped at telemetry ingest.",
    )
    producer_offset_s: Optional[float] = Field(
        default=None,
        description="Wayside producer wall-clock offset (observed_at - received_at) in seconds.",
    )


class GuardrailDecision(BaseModel):
    """Structured result returned by deterministic railway physics & freshness guardrails."""

    speed_kmh: int = Field(..., ge=0, le=160, description="Approved cruise speed in km/h.")
    approved_speed_kmh: int = Field(..., ge=0, le=160, description="Approved cruise speed in km/h.")
    assigned_track_block: str = Field(..., description="Verified track block ID.")
    guardrail_interlock_passed: bool = Field(
        default=False,
        description="False when the guardrail fails closed: unknown block status or an occupied passing loop.",
    )
    stale_reason: Optional[StaleReason] = Field(
        default=None,
        description="Telemetry halt discriminator: 'expired' (>15.0s) or 'clock_skew' (<-0.5s).",
    )
    age_used: Optional[float] = Field(
        default=None,
        description="Clamped non-negative telemetry age (max(0.0, age_s)) evaluated by the freshness interlock.",
    )
    producer_offset_s: Optional[float] = Field(
        default=None,
        description="Observed wayside producer clock offset in seconds for NTP drift telemetry.",
    )
    guardrail_note: str = Field(..., description="Audit note from the deterministic railway guardrail.")


class ScheduleRecoveryPlan(BaseModel):
    """Deterministic ETA and headway calculation produced by the schedule recovery tool."""

    train_id: str = Field(..., description="Train identifier.")
    approved_speed_kmh: int = Field(..., description="Guardrail-verified target speed in km/h.")
    assigned_track_block: str = Field(..., description="Assigned track block after interlocking check.")
    recovered_minutes: int = Field(..., description="Delay minutes recovered by this dispatch plan.")
    updated_eta: str = Field(..., description="Updated station arrival time (HH:MM).")
    stale_reason: Optional[StaleReason] = Field(
        default=None,
        description="Telemetry halt reason ('expired' or 'clock_skew') when speed is clamped to 0.",
    )
    age_used: Optional[float] = Field(
        default=None,
        description="Clamped non-negative telemetry age (max(0.0, age_s)) evaluated by the freshness interlock.",
    )
    producer_offset_s: Optional[float] = Field(
        default=None,
        description="Wayside producer clock offset in seconds for observability.",
    )
    guardrail_note: str = Field(..., description="Audit note from the deterministic railway guardrail.")


class RailDispatchAdvisory(BaseModel):
    """Strict structured JSON output schema enforced on the Gemma ADK agent (output_schema)."""

    train_id: str = Field(..., description="Target train identifier (e.g., ADY-702).")
    route_name: str = Field(..., description="Rail corridor name.")
    operational_status: Literal[
        "ON_TIME",
        "DELAY_RECOVERY",
        "WIND_SPEED_RESTRICTED",
        "REROUTED_SIDING",
        "TELEMETRY_HALT",
    ] = Field(
        ..., description="High-level dispatch status badge for the Streamlit dashboard."
    )
    approved_speed_kmh: int = Field(
        ..., ge=0, le=160, description="Deterministic guardrail-approved speed in km/h."
    )
    assigned_block_id: str = Field(..., description="Verified track block assigned to the train.")
    updated_eta: str = Field(..., description="Updated arrival time at next station (HH:MM).")
    delay_minutes_remaining: int = Field(..., ge=0, description="Remaining delay in minutes after recovery.")
    tools_invoked: List[str] = Field(
        ..., description="Ordered list of Python tools invoked during dispatch reasoning."
    )
    guardrail_interlock_passed: bool = Field(
        ..., description="True if deterministic block occupancy and wind caps were enforced."
    )
    stale_reason: Optional[StaleReason] = Field(
        default=None,
        description="Observable telemetry halt discriminator ('expired' vs 'clock_skew').",
    )
    age_used: Optional[float] = Field(
        default=None,
        description="Clamped non-negative telemetry age (max(0.0, age_s)) evaluated by the freshness interlock.",
    )
    producer_offset_s: Optional[float] = Field(
        default=None,
        description="Wayside sensor wall-clock offset (seconds) for NTP drift monitoring.",
    )
    guardrail_intervention_summary: str = Field(
        ..., description="Explanation of any speed clamping or block rerouting applied by the guardrail."
    )
    passenger_announcement: str = Field(
        ..., description="Clear passenger-facing station board announcement."
    )
