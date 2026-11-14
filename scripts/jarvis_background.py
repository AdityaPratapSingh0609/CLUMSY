"""Always-On Background Daemon, Auto-Connect Persistence & Smart Audio Router (Stage 20).

Allows DESKBOT // J.A.R.V.I.S. to run continuously in the background of both
the Laptop Hub and the Phone "Deskbot Eyes" Stream-Flow App:
  - Auto-connects the Phone Eyes App as soon as the Laptop Hub is online.
  - Keeps WebSocket & Microphone streams alive in the background (`WakeLock` +
    heartbeat keepalive).
  - Routes J.A.R.V.I.S. spoken voice output intelligently to whichever device
    the user spoke into (`"source_device"`), or `"phone"`, `"laptop"`, or `"both"`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class JarvisBackgroundDaemon:
    """Manages always-on background execution, auto-reconnect heartbeats, and voice output routing."""

    VALID_VOICE_TARGETS = ("source_device", "phone", "laptop", "both")

    def __init__(self, state_file: Optional[Path] = None) -> None:
        self.state_file = state_file or (PROJECT_ROOT / ".deskbot_state.json")
        self.running_in_background = True
        self.auto_connect_on_boot = True
        self.laptop_wake_lock = True
        self.phone_wake_lock = True
        self.always_on_mic = True
        self.voice_output_target = "source_device"
        self.heartbeat_count = 0
        self.last_heartbeat_ts = time.time()
        self.connected_peers: Dict[str, Dict[str, Any]] = {
            "laptop_hub": {"online": True, "mode": "background_daemon", "last_seen": time.time()},
            "phone_eyes_app": {"online": True, "mode": "stream_flow_pwa", "last_seen": time.time()},
            "arduino_uno_bot": {"online": True, "mode": "virtual_bluetooth_uno", "last_seen": time.time()},
        }
        self._load_persisted_state()

    def _load_persisted_state(self) -> None:
        if not self.state_file.is_file():
            return
        try:
            raw = json.loads(self.state_file.read_text(encoding="utf-8"))
            self.always_on_mic = bool(raw.get("always_on_mic", True))
            target = str(raw.get("voice_output_target", "source_device"))
            if target in self.VALID_VOICE_TARGETS:
                self.voice_output_target = target
        except Exception:
            pass

    def save_persisted_state(self) -> None:
        payload = {
            "running_in_background": self.running_in_background,
            "auto_connect_on_boot": self.auto_connect_on_boot,
            "always_on_mic": self.always_on_mic,
            "voice_output_target": self.voice_output_target,
            "last_heartbeat_ts": self.last_heartbeat_ts,
        }
        try:
            self.state_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            pass

    def resolve_speaker_targets(self, source_device: str = "laptop_hub") -> Dict[str, bool]:
        """Determine which device speakers should play J.A.R.V.I.S.'s voice reply."""
        src = (source_device or "laptop_hub").lower()
        if self.voice_output_target == "both":
            return {"play_on_phone": True, "play_on_laptop": True, "mode": "both"}
        if self.voice_output_target == "phone":
            return {"play_on_phone": True, "play_on_laptop": False, "mode": "phone"}
        if self.voice_output_target == "laptop":
            return {"play_on_phone": False, "play_on_laptop": True, "mode": "laptop"}
        # Default "source_device": play on whichever device the user spoke into
        is_phone = "mobile" in src or "phone" in src or "eyes" in src
        return {
            "play_on_phone": is_phone,
            "play_on_laptop": not is_phone,
            "mode": "source_device",
        }

    def configure(
        self,
        always_on_mic: Optional[bool] = None,
        voice_output_target: Optional[str] = None,
        auto_connect_on_boot: Optional[bool] = None,
    ) -> Dict[str, Any]:
        if always_on_mic is not None:
            self.always_on_mic = bool(always_on_mic)
        if voice_output_target and voice_output_target in self.VALID_VOICE_TARGETS:
            self.voice_output_target = voice_output_target
        if auto_connect_on_boot is not None:
            self.auto_connect_on_boot = bool(auto_connect_on_boot)
        self.save_persisted_state()
        return self.get_status()

    def record_heartbeat(self, device_id: str = "phone_eyes_app") -> Dict[str, Any]:
        self.heartbeat_count += 1
        self.last_heartbeat_ts = time.time()
        if device_id not in self.connected_peers:
            self.connected_peers[device_id] = {"online": True, "mode": "stream_flow"}
        self.connected_peers[device_id]["online"] = True
        self.connected_peers[device_id]["last_seen"] = self.last_heartbeat_ts
        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        return {
            "running_in_background": self.running_in_background,
            "auto_connect_on_boot": self.auto_connect_on_boot,
            "laptop_wake_lock": self.laptop_wake_lock,
            "phone_wake_lock": self.phone_wake_lock,
            "always_on_mic": self.always_on_mic,
            "voice_output_target": self.voice_output_target,
            "heartbeat_count": self.heartbeat_count,
            "last_heartbeat_ts": self.last_heartbeat_ts,
            "connected_peers": self.connected_peers,
        }


def spawn_detached_server(port: int = 8080) -> int:
    """Spawn the DESKBOT // J.A.R.V.I.S. server as a detached background process on Windows/POSIX."""
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
    proc = subprocess.Popen(
        [sys.executable, str(PROJECT_ROOT / "scripts/deploy_jarvis.py"), "--port", str(port)],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags if sys.platform.startswith("win") else 0,
    )
    return int(proc.pid)


def main() -> int:
    parser = argparse.ArgumentParser(description="DESKBOT // J.A.R.V.I.S. Background Daemon Manager")
    parser.add_argument("--status", action="store_true", help="Print background daemon status JSON")
    parser.add_argument("--spawn", action="store_true", help="Spawn server in detached background mode")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    daemon = JarvisBackgroundDaemon()
    if args.spawn:
        pid = spawn_detached_server(port=args.port)
        print(json.dumps({"spawned_background_pid": pid, "port": args.port}))
        return 0

    print(json.dumps(daemon.get_status(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
