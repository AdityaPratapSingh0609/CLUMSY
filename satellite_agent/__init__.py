"""DESKBOT Satellite Agents Package (Stages 7 & 8)."""

from satellite_agent.pc_client import LaptopSatelliteDaemon, build_os_launch_command
from satellite_agent.mobile.phone_bridge import PhoneCompanionBridge, PhoneNotification

__all__ = [
    "LaptopSatelliteDaemon",
    "build_os_launch_command",
    "PhoneCompanionBridge",
    "PhoneNotification",
]
