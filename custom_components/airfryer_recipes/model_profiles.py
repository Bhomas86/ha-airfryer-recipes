"""Owner-reported appliance limits, separate from adapter capabilities.

These values describe the appliance. They never add adapter programs, authorize
sending or replace the pinned upstream service's strict bounds.
"""

from __future__ import annotations

from typing import Any

TURBO_TOWER_MODEL = "CAF-DC111S-AEU"
TURBO_TOWER_TEMPERATURES = {
    "airfry": (120, 230),
    "roast": (175, 230),
    "bake": (80, 205),
    "grill": (160, 230),
    "reheat": (40, 205),
    "dry": (35, 95),
    "proof": (30, 45),
}


def describe_model_profile(model: str | None) -> dict[str, Any] | None:
    """Expose only static profile metadata for the exact model."""
    if model != TURBO_TOWER_MODEL:
        return None
    return {
        "source": "owner_reported",
        "programs": [
            {"id": program, "temperature_c": {"min": low, "max": high},
             "temperature_step_c": 1 if program == "proof" else None}
            for program, (low, high) in TURBO_TOWER_TEMPERATURES.items()
        ],
    }
