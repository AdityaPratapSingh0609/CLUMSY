"""2D OLED Digital Twin & 3D WebGL Robot Kinematics Engine (Stages 9 & 10).

Provides deterministic forward kinematics, cubic motion easing, servo angle
clamping (15°–165°), 3D gaze vector calculation, and 2D OLED eye geometry
parameters shared by the backend telemetry API and the frontend digital twin.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Tuple

SERVO_MIN_DEG = 15.0
SERVO_MAX_DEG = 165.0
SERVO_CENTER_DEG = 90.0

VALID_EXPRESSIONS = ("idle", "happy", "listening", "thinking", "confused", "sleeping", "blinking")


def clamp_servo_deg(angle: float, min_deg: float = SERVO_MIN_DEG, max_deg: float = SERVO_MAX_DEG) -> int:
    """Clamp a servo angle in degrees to safe physical gear limits [15°, 165°]."""
    return int(round(max(min_deg, min(max_deg, float(angle)))))


def ease_in_out_cubic(t: float) -> float:
    """Non-linear cubic easing function for smooth servo & 3D head transitions."""
    clamped = max(0.0, min(1.0, float(t)))
    if clamped < 0.5:
        return 4.0 * clamped * clamped * clamped
    p = -2.0 * clamped + 2.0
    return 1.0 - (p * p * p) / 2.0


def interpolate_pose(
    start_pan: float,
    start_tilt: float,
    target_pan: float,
    target_tilt: float,
    t: float,
) -> Tuple[float, float]:
    """Interpolate (pan, tilt) along a cubic ease-in-out curve."""
    alpha = ease_in_out_cubic(t)
    s_pan = float(clamp_servo_deg(start_pan))
    s_tilt = float(clamp_servo_deg(start_tilt))
    e_pan = float(clamp_servo_deg(target_pan))
    e_tilt = float(clamp_servo_deg(target_tilt))
    return (
        s_pan + (e_pan - s_pan) * alpha,
        s_tilt + (e_tilt - s_tilt) * alpha,
    )


def servo_deg_to_radians(pan_deg: float, tilt_deg: float) -> Tuple[float, float]:
    """Convert servo angles (pan, tilt in degrees, 90° = neutral) to 3D head Euler radians (yaw_y, pitch_x)."""
    pan = float(clamp_servo_deg(pan_deg))
    tilt = float(clamp_servo_deg(tilt_deg))
    yaw_y = -math.radians(pan - SERVO_CENTER_DEG)
    pitch_x = -math.radians(tilt - SERVO_CENTER_DEG)
    return (yaw_y, pitch_x)


def compute_head_gaze_vector(pan_deg: float, tilt_deg: float) -> Tuple[float, float, float]:
    """Compute the 3D unit forward gaze vector (x, y, z) for the robot head in WebGL coordinates.

    At neutral (pan=90°, tilt=90°), the head looks straight along +Z: (0.0, 0.0, 1.0).
    """
    yaw_y, pitch_x = servo_deg_to_radians(pan_deg, tilt_deg)
    cos_p = math.cos(pitch_x)
    sin_p = math.sin(pitch_x)
    cos_y = math.cos(yaw_y)
    sin_y = math.sin(yaw_y)

    gx = sin_y * cos_p
    gy = -sin_p
    gz = cos_y * cos_p
    norm = math.sqrt(gx * gx + gy * gy + gz * gz) or 1.0
    return (round(gx / norm, 6), round(gy / norm, 6), round(gz / norm, 6))


def compute_oled_eye_state(
    expression: str,
    pan_deg: float = 90.0,
    tilt_deg: float = 90.0,
    blink_progress: float = 0.0,
) -> Dict[str, Any]:
    """Compute vector OLED eye state on a 128x64 virtual screen for the 2D Digital Twin."""
    expr = (expression or "idle").strip().lower()
    if expr not in VALID_EXPRESSIONS:
        expr = "idle"

    pan = clamp_servo_deg(pan_deg)
    tilt = clamp_servo_deg(tilt_deg)
    blink = max(0.0, min(1.0, float(blink_progress)))

    # Pupil offset derived from pan/tilt deviation from 90°
    pupil_dx = round(((pan - 90.0) / 75.0) * 6.0, 2)
    pupil_dy = round(((90.0 - tilt) / 75.0) * 5.0, 2)

    base_height = 28.0
    if expr == "happy":
        eye_shape = "arc_squint"
        left_h = 14.0
        right_h = 14.0
    elif expr == "listening":
        eye_shape = "wide_circle"
        left_h = 34.0
        right_h = 34.0
    elif expr == "thinking":
        eye_shape = "look_up"
        left_h = 24.0
        right_h = 24.0
        pupil_dx += 4.0
        pupil_dy -= 5.0
    elif expr == "confused":
        eye_shape = "asymmetric"
        left_h = 32.0
        right_h = 16.0
    elif expr in ("sleeping", "blinking"):
        eye_shape = "closed_line"
        left_h = 3.0
        right_h = 3.0
    else:
        eye_shape = "rounded_pupil"
        left_h = base_height
        right_h = base_height

    if blink > 0.0:
        left_h = max(3.0, left_h * (1.0 - blink))
        right_h = max(3.0, right_h * (1.0 - blink))

    return {
        "screen_width": 128,
        "screen_height": 64,
        "expression": expr,
        "eye_shape": eye_shape,
        "left_eye": {"cx": 38, "cy": 32, "width": 28.0, "height": round(left_h, 2)},
        "right_eye": {"cx": 90, "cy": 32, "width": 28.0, "height": round(right_h, 2)},
        "pupil_offset": {"dx": pupil_dx, "dy": pupil_dy},
        "pan_deg": pan,
        "tilt_deg": tilt,
    }
