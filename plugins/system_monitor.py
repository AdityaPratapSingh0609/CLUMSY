"""Local system hardware & memory monitor plugin (Stage 5)."""

import ctypes
import os
import platform
from pathlib import Path
import shutil
from typing import Any, Dict

from core.tool_router import ToolRegistry, ToolSpec

SYSTEM_MONITOR_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "include_processes": {
            "type": "boolean",
            "default": False,
        }
    },
    "additionalProperties": False,
}


def _get_ram_info_mb() -> Dict[str, float]:
    if os.name == "nt":
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):  # type: ignore[attr-defined]
            total_mb = round(stat.ullTotalPhys / (1024 * 1024), 1)
            avail_mb = round(stat.ullAvailPhys / (1024 * 1024), 1)
            return {
                "total_mb": total_mb,
                "available_mb": avail_mb,
                "used_pct": float(stat.dwMemoryLoad),
            }
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        kv = {}
        for line in meminfo.read_text(encoding="utf-8").splitlines():
            parts = line.split(":")
            if len(parts) == 2:
                kv[parts[0].strip()] = int(parts[1].strip().split()[0])
        total_kb = kv.get("MemTotal", 0)
        avail_kb = kv.get("MemAvailable", kv.get("MemFree", 0))
        if total_kb > 0:
            used_pct = round(100.0 * (total_kb - avail_kb) / total_kb, 1)
            return {
                "total_mb": round(total_kb / 1024, 1),
                "available_mb": round(avail_kb / 1024, 1),
                "used_pct": used_pct,
            }
    return {"total_mb": 0.0, "available_mb": 0.0, "used_pct": 0.0}


def handle_system_monitor(params: Dict[str, Any]) -> Dict[str, Any]:
    disk = shutil.disk_usage(Path.cwd())
    ram = _get_ram_info_mb()
    return {
        "success": True,
        "tool": "system_monitor",
        "os": platform.system(),
        "cpu_cores": os.cpu_count() or 1,
        "ram": ram,
        "disk_free_gb": round(disk.free / (1024 ** 3), 2),
        "include_processes": bool(params.get("include_processes", False)),
    }


def register_tools(registry: ToolRegistry) -> None:
    registry.register(
        ToolSpec(
            name="system_monitor",
            description="Report real-time CPU core count, RAM utilization, and free disk space.",
            parameters_schema=SYSTEM_MONITOR_SCHEMA,
            handler=handle_system_monitor,
            plugin_source="plugins.system_monitor",
        )
    )
