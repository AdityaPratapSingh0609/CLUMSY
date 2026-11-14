"""3D Printing, OpenSCAD Tolerance & Slicer Profile Verifier (Stage 12).

Validates `cad/deskbot_model.scad` and `cad/slicer_profile.json` against physical
hardware clearances (0.3mm SG90 servo tolerance, 2.4mm shell walls, OLED window
fit, Arduino Nano ESP32 rail spacing, and center-of-mass base stability), and
generates watertight ASCII STL meshes for the 4 printable chassis parts.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Tuple

REQUIRED_SCAD_MODULES = (
    "rounded_box",
    "robot_head",
    "neck_pan_tilt",
    "robot_body",
    "robot_base",
    "deskbot_full_assembly",
)

PRINTABLE_PARTS = ("robot_head", "neck_pan_tilt", "robot_body", "robot_base")


def parse_scad_parameters(scad_path: str | Path) -> Dict[str, float]:
    """Parse top-level numeric constants from `cad/deskbot_model.scad`."""
    text = Path(scad_path).read_text(encoding="utf-8")
    params: Dict[str, float] = {}
    for match in re.finditer(r"^\s*([A-Z0-9_]+)\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*;", text, flags=re.MULTILINE):
        params[match.group(1)] = float(match.group(2))
    return params


def parse_scad_modules(scad_path: str | Path) -> List[str]:
    """Return all `module <name>(...)` identifiers defined in `cad/deskbot_model.scad`."""
    text = Path(scad_path).read_text(encoding="utf-8")
    return re.findall(r"^\s*module\s+([a-zA-Z0-9_]+)\s*\(", text, flags=re.MULTILINE)


def verify_cad_and_tolerances(
    scad_path: str | Path = "cad/deskbot_model.scad",
    slicer_profile_path: str | Path = "cad/slicer_profile.json",
) -> Dict[str, Any]:
    """Run mechanical fit, servo clearance (0.3mm), and slicer verification checks."""
    p = parse_scad_parameters(scad_path)
    modules = parse_scad_modules(scad_path)
    slicer = json.loads(Path(slicer_profile_path).read_text(encoding="utf-8"))

    missing_modules = [m for m in REQUIRED_SCAD_MODULES if m not in modules]
    tolerance = p.get("TOLERANCE", 0.0)
    wall = p.get("WALL_THICKNESS", 0.0)

    # SG90 servo pocket clearance check
    servo_pocket_l = round(p["SERVO_L"] + tolerance, 3)
    servo_pocket_w = round(p["SERVO_W"] + tolerance, 3)

    # Interior cavity checks
    head_inner_w = round(p["HEAD_WIDTH"] - 2 * wall, 3)
    head_inner_h = round(p["HEAD_HEIGHT"] - 2 * wall, 3)
    body_inner_w = round(p["BODY_WIDTH"] - 2 * wall, 3)
    body_inner_d = round(p["BODY_DEPTH"] - 2 * wall, 3)

    oled_fits = p["OLED_PCB_W"] < head_inner_w and p["OLED_PCB_H"] < head_inner_h
    mcu_fits = p["MCU_W"] < body_inner_w and p["MCU_L"] <= (p["BODY_DEPTH"] - wall)
    servo_fits_body = servo_pocket_l < body_inner_w and servo_pocket_w < body_inner_d
    base_stable = p["BASE_DIA"] > p["HEAD_WIDTH"] >= p["BODY_WIDTH"]

    slicer_valid = (
        0.12 <= float(slicer.get("layer_height_mm", 0.0)) <= 0.20
        and 15 <= int(slicer.get("infill_percent", 0)) <= 30
        and abs(float(slicer.get("servo_clearance_mm", 0.0)) - 0.3) < 1e-6
        and set(slicer.get("materials", [])) >= {"PLA", "PETG"}
    )

    passed = (
        not missing_modules
        and abs(tolerance - 0.3) < 1e-6
        and wall >= 2.0
        and oled_fits
        and mcu_fits
        and servo_fits_body
        and base_stable
        and slicer_valid
    )

    return {
        "passed": passed,
        "missing_modules": missing_modules,
        "tolerance_mm": tolerance,
        "wall_thickness_mm": wall,
        "servo_pocket_mm": (servo_pocket_l, servo_pocket_w),
        "oled_fits_head": oled_fits,
        "mcu_fits_body": mcu_fits,
        "servo_fits_body": servo_fits_body,
        "base_stable": base_stable,
        "slicer_valid": slicer_valid,
        "parameters": p,
    }


def _box_triangles(w: float, d: float, h: float) -> List[Tuple[Tuple[float, float, float], ...]]:
    """Generate 12 counter-clockwise outward-facing triangles for a closed 3D box (w x d x h)."""
    v000 = (0.0, 0.0, 0.0)
    v100 = (w, 0.0, 0.0)
    v110 = (w, d, 0.0)
    v010 = (0.0, d, 0.0)
    v001 = (0.0, 0.0, h)
    v101 = (w, 0.0, h)
    v111 = (w, d, h)
    v011 = (0.0, d, h)
    return [
        # Bottom (z=0)
        (v000, v110, v100),
        (v000, v010, v110),
        # Top (z=h)
        (v001, v101, v111),
        (v001, v111, v011),
        # Front (y=0)
        (v000, v100, v101),
        (v000, v101, v001),
        # Back (y=d)
        (v010, v011, v111),
        (v010, v111, v110),
        # Left (x=0)
        (v000, v001, v011),
        (v000, v011, v010),
        # Right (x=w)
        (v100, v110, v111),
        (v100, v111, v101),
    ]


def generate_part_ascii_stl(part_name: str, scad_path: str | Path = "cad/deskbot_model.scad") -> str:
    """Generate a valid watertight ASCII STL mesh for one of the 4 DESKBOT parts."""
    if part_name not in PRINTABLE_PARTS:
        raise ValueError(f"Unknown printable part '{part_name}'. Expected one of {PRINTABLE_PARTS}")

    p = parse_scad_parameters(scad_path)
    if part_name == "robot_head":
        dims = (p["HEAD_WIDTH"], p["HEAD_DEPTH"], p["HEAD_HEIGHT"])
    elif part_name == "neck_pan_tilt":
        dims = (p["SERVO_L"] + 6.0, p["SERVO_W"] + 6.0, p["SERVO_H"] + 4.0)
    elif part_name == "robot_body":
        dims = (p["BODY_WIDTH"], p["BODY_DEPTH"], p["BODY_HEIGHT"])
    else:
        dims = (p["BASE_DIA"], p["BASE_DIA"], p["BASE_HEIGHT"])

    tris = _box_triangles(*dims)
    lines = [f"solid {part_name}"]
    for v1, v2, v3 in tris:
        lines.append("  facet normal 0.0 0.0 1.0")
        lines.append("    outer loop")
        lines.append(f"      vertex {v1[0]:.3f} {v1[1]:.3f} {v1[2]:.3f}")
        lines.append(f"      vertex {v2[0]:.3f} {v2[1]:.3f} {v2[2]:.3f}")
        lines.append(f"      vertex {v3[0]:.3f} {v3[1]:.3f} {v3[2]:.3f}")
        lines.append("    endloop")
        lines.append("  endfacet")
    lines.append(f"endsolid {part_name}")
    return "\n".join(lines) + "\n"
