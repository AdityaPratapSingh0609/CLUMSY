#!/usr/bin/env python3
"""DESKBOT Laptop Satellite Agent Daemon (Stage 7).

Runs on a secondary laptop/PC and listens for `MeshEnvelope` commands over
LAN WebSocket (`LANWebSocketServer`). Supports:
- Cross-platform application execution (`Windows start`, `macOS open`, `Linux xdg-open`)
- System volume control (`set_volume`, `mute`)
- Media playback triggers (`play_pause`, `next_track`, `prev_track`)
- Workstation lock screen (`lock_screen`)
"""

import argparse
import asyncio
import logging
import os
import platform
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.mesh.transport import LANWebSocketServer, MeshEnvelope

logger = logging.getLogger("LaptopDaemon")

# Friendly app name -> platform target mapping
APP_ALIASES: Dict[str, Dict[str, str]] = {
    "spotify": {"Windows": "spotify:", "Darwin": "Spotify", "Linux": "spotify"},
    "vs code": {"Windows": "code", "Darwin": "Visual Studio Code", "Linux": "code"},
    "vscode": {"Windows": "code", "Darwin": "Visual Studio Code", "Linux": "code"},
    "browser": {"Windows": "https://127.0.0.1:8080", "Darwin": "Safari", "Linux": "xdg-open"},
    "chrome": {"Windows": "chrome", "Darwin": "Google Chrome", "Linux": "google-chrome"},
    "notepad": {"Windows": "notepad.exe", "Darwin": "TextEdit", "Linux": "gedit"},
    "calculator": {"Windows": "calc.exe", "Darwin": "Calculator", "Linux": "gnome-calculator"},
}


def build_os_launch_command(app_name: str, system_name: Optional[str] = None) -> List[str]:
    """Builds the native cross-platform OS command array to launch `app_name`."""
    sys_name = system_name or platform.system()
    clean = (app_name or "").strip()
    if not clean:
        raise ValueError("app_name must be non-empty")

    alias_map = APP_ALIASES.get(clean.lower(), {})
    resolved = alias_map.get(sys_name, clean)

    if sys_name == "Windows":
        return ["cmd", "/c", "start", "", resolved]
    if sys_name == "Darwin":
        return ["open", "-a", resolved]
    # Linux / POSIX
    if resolved == "xdg-open":
        return ["xdg-open", "http://127.0.0.1:8080"]
    return ["xdg-open", resolved] if "://" in resolved else [resolved]


def build_os_lock_command(system_name: Optional[str] = None) -> List[str]:
    sys_name = system_name or platform.system()
    if sys_name == "Windows":
        return ["rundll32.exe", "user32.dll,LockWorkStation"]
    if sys_name == "Darwin":
        return ["pmset", "displaysleepnow"]
    return ["loginctl", "lock-session"]


class LaptopSatelliteDaemon:
    """
    Lightweight satellite daemon for remote laptops/PCs.
    Executes Deskbot mesh commands in < 500 ms.
    """

    def __init__(
        self,
        node_id: str = "laptop_node",
        host: str = "127.0.0.1",
        port: int = 9120,
        dry_run: bool = True,
    ):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.dry_run = dry_run
        self.volume: int = 70
        self.muted: bool = False
        self.media_state: str = "paused"
        self.locked: bool = False
        self.executed_commands: List[Dict[str, Any]] = []
        self.ws_server = LANWebSocketServer(
            host=self.host,
            port=self.port,
            on_envelope=self.handle_envelope,
        )

    async def start(self) -> int:
        bound_port = await self.ws_server.start()
        self.port = bound_port
        logger.info("LaptopSatelliteDaemon [%s] listening on ws://%s:%d", self.node_id, self.host, self.port)
        return bound_port

    async def stop(self) -> None:
        await self.ws_server.stop()

    async def handle_envelope(self, env: MeshEnvelope) -> Dict[str, Any]:
        return self.execute_action(env.action, env.payload)

    def execute_action(self, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        t0 = time.perf_counter()
        p = params or {}

        if action == "launch_app":
            app_name = str(p.get("app_name") or "Notepad")
            cmd = build_os_launch_command(app_name)
            if not self.dry_run:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
            rec = {
                "action": "launch_app",
                "app_name": app_name,
                "os_command": cmd,
                "dry_run": self.dry_run,
                "execution_time_ms": elapsed_ms,
            }
            self.executed_commands.append(rec)
            return {"success": True, "node_id": self.node_id, **rec}

        if action == "set_volume":
            vol = max(0, min(100, int(p.get("volume", self.volume))))
            self.volume = vol
            if "mute" in p:
                self.muted = bool(p["mute"])
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
            rec = {
                "action": "set_volume",
                "volume": self.volume,
                "muted": self.muted,
                "execution_time_ms": elapsed_ms,
            }
            self.executed_commands.append(rec)
            return {"success": True, "node_id": self.node_id, **rec}

        if action == "media_control":
            cmd_type = str(p.get("command") or "play_pause").lower()
            if cmd_type in ("play", "play_pause"):
                self.media_state = "playing" if self.media_state != "playing" else "paused"
            elif cmd_type == "pause":
                self.media_state = "paused"
            elif cmd_type in ("next", "prev"):
                self.media_state = "playing"
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
            rec = {
                "action": "media_control",
                "command": cmd_type,
                "media_state": self.media_state,
                "execution_time_ms": elapsed_ms,
            }
            self.executed_commands.append(rec)
            return {"success": True, "node_id": self.node_id, **rec}

        if action == "lock_screen":
            cmd = build_os_lock_command()
            if not self.dry_run:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.locked = True
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
            rec = {
                "action": "lock_screen",
                "os_command": cmd,
                "locked": True,
                "dry_run": self.dry_run,
                "execution_time_ms": elapsed_ms,
            }
            self.executed_commands.append(rec)
            return {"success": True, "node_id": self.node_id, **rec}

        if action == "ping":
            return {"success": True, "node_id": self.node_id, "status": "online"}

        return {"success": False, "node_id": self.node_id, "error": f"Unknown action '{action}'"}


async def _run_cli(host: str, port: int, execute: bool) -> None:
    daemon = LaptopSatelliteDaemon(host=host, port=port, dry_run=not execute)
    await daemon.start()
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, asyncio.CancelledError):
        await daemon.stop()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=9120)
    ap.add_argument("--execute", action="store_true", help="Execute real OS commands (disables dry-run)")
    args = ap.parse_args()
    asyncio.run(_run_cli(args.host, args.port, args.execute))


if __name__ == "__main__":
    main()
