"""
DESKBOT Robot Bridge
Manages the hardware connection to the physical 3D-printed robot
via Bluetooth Serial / USB Serial / BLE, and exposes real-time
2D/3D Digital Twin telemetry.

Includes a Simulation Mode so you can develop and test without
having the physical hardware plugged in.
"""

import logging
import os
import sys
import time
from typing import Any, Dict, Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.protocol import EyeConfig, Expression, MotorSpeed, RobotCommandPacket, ServoPose
from core.robotics.kinematics import (
    clamp_servo_deg,
    compute_head_gaze_vector,
    compute_oled_eye_state,
    servo_deg_to_radians,
)

logger = logging.getLogger("RobotBridge")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class RobotBridge:
    def __init__(self, port: Optional[str] = None, baudrate: int = 115200, simulate: bool = True):
        self.port = port
        self.baudrate = baudrate
        self.simulate = simulate
        self.serial_conn = None
        self.current_state = "IDLE"
        self.current_expression = "idle"
        self.current_pan = 90
        self.current_tilt = 90
        self.current_speed = MotorSpeed.SMOOTH.value
        self.last_updated_ts = time.time()

    def connect(self) -> bool:
        """Connects to the physical robot via Serial/Bluetooth, or initializes simulation."""
        if self.simulate:
            logger.info("🤖 RobotBridge started in [SIMULATION MODE]. Virtual robot is active.")
            return True

        try:
            import serial

            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            logger.info("✅ Connected to physical robot on %s at %d baud.", self.port, self.baudrate)
            return True
        except Exception as e:
            logger.warning("⚠️ Could not connect to physical port '%s': %s. Falling back to simulation mode.", self.port, e)
            self.simulate = True
            return True

    def send_command(self, packet: RobotCommandPacket) -> bool:
        """Sends a motion & expression packet to the robot and updates telemetry."""
        clamped_pan = clamp_servo_deg(packet.servos.pan)
        clamped_tilt = clamp_servo_deg(packet.servos.tilt)
        packet.servos.pan = clamped_pan
        packet.servos.tilt = clamped_tilt

        self.current_state = packet.state
        self.current_expression = packet.eyes.expression.value
        self.current_pan = clamped_pan
        self.current_tilt = clamped_tilt
        self.current_speed = packet.servos.speed.value
        self.last_updated_ts = time.time()

        payload = packet.to_json() + "\n"

        if self.simulate:
            logger.info(
                "[SIMULATED ROBOT] State: %-10s | Eyes: %-10s | Servos: Pan=%d°, Tilt=%d°",
                packet.state,
                packet.eyes.expression.value,
                clamped_pan,
                clamped_tilt,
            )
            return True

        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(payload.encode("utf-8"))
                return True
            except Exception as e:
                logger.error("Failed to send packet to robot: %s", e)
                return False
        return False

    def get_telemetry(self) -> Dict[str, Any]:
        """Return real-time 2D OLED and 3D WebGL posture telemetry."""
        yaw_rad, pitch_rad = servo_deg_to_radians(self.current_pan, self.current_tilt)
        gx, gy, gz = compute_head_gaze_vector(self.current_pan, self.current_tilt)
        return {
            "state": self.current_state,
            "expression": self.current_expression,
            "pan_deg": self.current_pan,
            "tilt_deg": self.current_tilt,
            "speed": self.current_speed,
            "euler_rad": {"yaw_y": round(yaw_rad, 6), "pitch_x": round(pitch_rad, 6)},
            "gaze_vector": {"x": gx, "y": gy, "z": gz},
            "oled": compute_oled_eye_state(self.current_expression, self.current_pan, self.current_tilt),
            "simulate": self.simulate,
            "timestamp": self.last_updated_ts,
        }

    # Convenience emotion & gesture helpers
    def express(
        self,
        expression: Expression,
        pan: int = 90,
        tilt: int = 90,
        speed: MotorSpeed = MotorSpeed.SMOOTH,
    ) -> bool:
        packet = RobotCommandPacket(
            state=expression.value.upper(),
            eyes=EyeConfig(expression=expression),
            servos=ServoPose(pan=clamp_servo_deg(pan), tilt=clamp_servo_deg(tilt), speed=speed),
        )
        return self.send_command(packet)

    def set_listening(self) -> bool:
        """Curious attentive posture with big eyes."""
        return self.express(Expression.LISTENING, pan=90, tilt=105, speed=MotorSpeed.FAST)

    def set_thinking(self) -> bool:
        """Looking up in thought with slight head tilt."""
        return self.express(Expression.THINKING, pan=105, tilt=115, speed=MotorSpeed.SMOOTH)

    def set_happy(self) -> bool:
        """Squinty joyful eyes with happy nod."""
        return self.express(Expression.HAPPY, pan=90, tilt=95, speed=MotorSpeed.SMOOTH)

    def set_confused(self) -> bool:
        """Quizzical tilt."""
        return self.express(Expression.CONFUSED, pan=75, tilt=80, speed=MotorSpeed.SMOOTH)

    def set_idle(self) -> bool:
        """Natural resting posture."""
        return self.express(Expression.IDLE, pan=90, tilt=90, speed=MotorSpeed.SLOW)
