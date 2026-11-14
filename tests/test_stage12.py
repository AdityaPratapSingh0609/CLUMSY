"""Stage 12 Verification Suite: 3D Printing, OpenSCAD Tolerances & Slicer Profile."""

from __future__ import annotations

import unittest

from core.robotics.cad_verifier import (
    PRINTABLE_PARTS,
    generate_part_ascii_stl,
    parse_scad_modules,
    parse_scad_parameters,
    verify_cad_and_tolerances,
)


class TestStage12CADAnd3DPrinting(unittest.TestCase):
    def test_scad_parameters_and_servo_tolerance_clearance(self) -> None:
        params = parse_scad_parameters("cad/deskbot_model.scad")
        modules = parse_scad_modules("cad/deskbot_model.scad")

        self.assertAlmostEqual(params["TOLERANCE"], 0.3, places=3)
        self.assertAlmostEqual(params["WALL_THICKNESS"], 2.4, places=3)
        for mod in ("robot_head", "neck_pan_tilt", "robot_body", "robot_base", "deskbot_full_assembly"):
            self.assertIn(mod, modules)

    def test_mechanical_fit_and_slicer_profile_verification(self) -> None:
        report = verify_cad_and_tolerances("cad/deskbot_model.scad", "cad/slicer_profile.json")
        self.assertTrue(report["passed"], f"CAD verification failed: {report}")
        self.assertEqual(report["servo_pocket_mm"], (23.3, 12.5))
        self.assertTrue(report["oled_fits_head"])
        self.assertTrue(report["mcu_fits_body"])
        self.assertTrue(report["servo_fits_body"])
        self.assertTrue(report["base_stable"])
        self.assertTrue(report["slicer_valid"])

    def test_watertight_ascii_stl_export_for_all_four_parts(self) -> None:
        for part in PRINTABLE_PARTS:
            stl = generate_part_ascii_stl(part, "cad/deskbot_model.scad")
            self.assertTrue(stl.startswith(f"solid {part}"))
            self.assertTrue(stl.strip().endswith(f"endsolid {part}"))
            self.assertEqual(stl.count("facet normal"), 12)
            self.assertEqual(stl.count("vertex "), 36)


if __name__ == "__main__":
    unittest.main()
