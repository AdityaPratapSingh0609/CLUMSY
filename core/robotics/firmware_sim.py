"""Virtual Arduino Uno & ESP32 Firmware Simulator (Stage 14).

Emulates `firmware/deskbot_avatar.ino` in pure Python so DESKBOT runs 100%
virtually when the physical Arduino Uno is not connected yet, while verifying
serial/Bluetooth packet parsing (`<P90,T95,Ehappy>` and JSON), non-linear
cubic easing (`easeInOutCubic`), hardware servo clamps (`15°–165°`), and the
10-second Bluetooth watchdog timer.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Tuple

from core.robotics.kinematics import clamp_servo_deg, ease_in_out_cubic, interpolate_pose

WATCHDOG_TIMEOUT_SEC = 10.0


class VirtualArduinoBotSimulator:
    """Cycle-accurate behavioral simulator for `firmware/deskbot_avatar.ino`."""

    def __init__(self, board_mode: str = "arduino_uno") -> None:
        self.board_mode = board_mode
        self.start_pan = 90.0
        self.start_tilt = 90.0
        self.current_pan = 90.0
        self.current_tilt = 90.0
        self.target_pan = 90.0
        self.target_tilt = 90.0
        self.expression = "idle"
        self.move_duration_sec = 0.26
        self.move_start_ts = time.perf_counter()
        self.last_packet_ts = self.move_start_ts
        self.packets_processed = 0

    @staticmethod
    def encode_uno_compact_frame(pan: int, tilt: int, expression: str = "idle") -> str:
        """Encode a low-SRAM Arduino Uno frame `<P90,T95,Ehappy>`."""
        c_pan = clamp_servo_deg(pan)
        c_tilt = clamp_servo_deg(tilt)
        return f"<P{c_pan},T{c_tilt},E{expression.strip().lower()}>"

    def process_packet(self, raw_line: str, now_ts: float | None = None) -> Dict[str, Any]:
        """Parse either a compact `<P90,T95,Ehappy>` frame or a JSON command line."""
        t0 = time.perf_counter()
        now = now_ts if now_ts is not None else t0
        line = (raw_line or "").strip()
        if not line:
            return {"ack": False, "error": "empty_packet"}

        pan = int(self.target_pan)
        tilt = int(self.target_tilt)
        expr = self.expression

        if line.startswith("<") and line.endswith(">"):
            body = line[1:-1]
            for token in body.split(","):
                if token.startswith("P"):
                    pan = int(token[1:])
                elif token.startswith("T"):
                    tilt = int(token[1:])
                elif token.startswith("E"):
                    expr = token[1:].strip().lower()
        else:
            obj = json.loads(line)
            if "eyes" in obj and isinstance(obj["eyes"], dict):
                expr = str(obj["eyes"].get("expression", expr)).lower()
            elif "expression" in obj:
                expr = str(obj["expression"]).lower()

            if "servos" in obj and isinstance(obj["servos"], dict):
                pan = int(obj["servos"].get("pan", pan))
                tilt = int(obj["servos"].get("tilt", tilt))
            else:
                pan = int(obj.get("pan", pan))
                tilt = int(obj.get("tilt", tilt))

        self.start_pan = self.current_pan
        self.start_tilt = self.current_tilt
        self.target_pan = float(clamp_servo_deg(pan))
        self.target_tilt = float(clamp_servo_deg(tilt))
        self.expression = expr
        self.move_start_ts = now
        self.last_packet_ts = now
        self.packets_processed += 1

        latency_ms = round((time.perf_counter() - t0) * 1000.0, 3)
        return {
            "ack": True,
            "board": self.board_mode,
            "target_pan": int(self.target_pan),
            "target_tilt": int(self.target_tilt),
            "expression": self.expression,
            "latency_ms": latency_ms,
        }

    def step(self, now_ts: float | None = None) -> Dict[str, Any]:
        """Advance servo cubic easing and check 10s Bluetooth watchdog."""
        now = now_ts if now_ts is not None else time.perf_counter()

        if self.expression != "idle" and (now - self.last_packet_ts) > WATCHDOG_TIMEOUT_SEC:
            self.start_pan = self.current_pan
            self.start_tilt = self.current_tilt
            self.target_pan = 90.0
            self.target_tilt = 90.0
            self.expression = "idle"
            self.move_start_ts = now

        progress = (now - self.move_start_ts) / max(0.001, self.move_duration_sec)
        p, t = interpolate_pose(
            self.start_pan,
            self.start_tilt,
            self.target_pan,
            self.target_tilt,
            progress,
        )
        self.current_pan = round(p, 2)
        self.current_tilt = round(t, 2)
        return {
            "pan_deg": self.current_pan,
            "tilt_deg": self.current_tilt,
            "target_pan": int(self.target_pan),
            "target_tilt": int(self.target_tilt),
            "expression": self.expression,
            "eased_alpha": round(ease_in_out_cubic(progress), 4),
        }

    def sample_trajectory(self, steps: int = 5) -> List[Tuple[float, float]]:
        """Sample the cubic easing trajectory from start pose to target pose."""
        pts: List[Tuple[float, float]] = []
        for i in range(steps + 1):
            t = i / max(1, steps)
            pts.append(
                interpolate_pose(
                    self.start_pan,
                    self.start_tilt,
                    self.target_pan,
                    self.target_tilt,
                    t,
                )
            )
        return pts


def verify_ino_firmware_source(ino_path: str | Path = "firmware/deskbot_avatar.ino") -> Dict[str, Any]:
    """Verify `firmware/deskbot_avatar.ino` has Arduino Uno + ESP32 support, cubic easing, and clamps."""
    src = Path(ino_path).read_text(encoding="utf-8")
    checks = {
        "has_arduino_uno_support": "SoftwareSerial" in src and "PIN_PAN_SERVO  = 9" in src,
        "has_esp32_support": "#if defined(ESP32)" in src and "BluetoothSerial" in src,
        "has_cubic_easing": "easeInOutCubic" in src,
        "has_angle_clamps": "SERVO_MIN_DEG 15" in src and "SERVO_MAX_DEG 165" in src,
        "has_watchdog": "WATCHDOG_TIMEOUT_MS" in src,
        "has_compact_uno_protocol": 'line.startsWith("<")' in src,
    }
    return {"passed": all(checks.values()), **checks}
