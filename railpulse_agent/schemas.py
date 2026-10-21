"""Pydantic v2 data contracts and structured JSON output schemas for RailPulse AI."""

from typing import List, Literal
from pydantic import BaseModel, Field


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


class ScheduleRecoveryPlan(BaseModel):
    """Deterministic ETA and headway calculation produced by the schedule recovery tool."""

    train_id: str = Field(..., description="Train identifier.")
    approved_speed_kmh: int = Field(..., description="Guardrail-verified target speed in km/h.")
    assigned_track_block: str = Field(..., description="Assigned track block after interlocking check.")
    recovered_minutes: int = Field(..., description="Delay minutes recovered by this dispatch plan.")
    updated_eta: str = Field(..., description="Updated station arrival time (HH:MM).")
    guardrail_note: str = Field(..., description="Audit note from the deterministic railway guardrail.")


class RailDispatchAdvisory(BaseModel):
    """Strict structured JSON output schema enforced on the Gemma ADK agent (output_schema)."""

    train_id: str = Field(..., description="Target train identifier (e.g., ADY-702).")
    route_name: str = Field(..., description="Rail corridor name.")
    operational_status: Literal["ON_TIME", "DELAY_RECOVERY", "WIND_SPEED_RESTRICTED", "REROUTED_SIDING"] = Field(
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
    guardrail_intervention_summary: str = Field(
        ..., description="Explanation of any speed clamping or block rerouting applied by the guardrail."
    )
    passenger_announcement: str = Field(
        ..., description="Clear passenger-facing station board announcement."
    )
