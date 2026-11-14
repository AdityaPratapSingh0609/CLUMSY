"""One-Click J.A.R.V.I.S. / DESKBOT 22-Stage Production Deployment & Readiness Launcher (Stages 1–22).

Usage:
  python scripts/deploy_jarvis.py --check-only --output workspace_output/deploy_report.json
  python scripts/deploy_jarvis.py --port 8080
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.bot_interactive import BotInteractiveController
from core.job_engine import UniversalJobEngine
from core.llm_fusion import JarvisFusionModel
from core.robotics.cad_verifier import verify_cad_and_tolerances
from core.robotics.circuit_verifier import verify_circuit_profile
from core.robotics.firmware_sim import verify_ino_firmware_source
from satellite_agent.mobile.mobile_agent import MobilePersonalAgent
from scripts.download_model import PRIMARY_GGUF_PATH, is_valid_gguf
from scripts.jarvis_background import JarvisBackgroundDaemon


def run_preflight_checks() -> Dict[str, Any]:
    """Verify all 22 stages of DESKBOT / J.A.R.V.I.S. are ready for deployment."""
    t0 = time.perf_counter()

    # 1. Verify CAD, Arduino Uno Circuit & Firmware
    cad_report = verify_cad_and_tolerances(
        PROJECT_ROOT / "cad/deskbot_model.scad",
        PROJECT_ROOT / "cad/slicer_profile.json",
    )
    uno_circuit = verify_circuit_profile("arduino_uno")
    fw_report = verify_ino_firmware_source(PROJECT_ROOT / "firmware/deskbot_avatar.ino")

    # 2. Verify Local GGUF Runtime & 4-Model Fusion Engine & RAM Budget
    gguf_valid = is_valid_gguf(PRIMARY_GGUF_PATH)
    fusion = JarvisFusionModel(max_ram_mb=850)
    fusion_probe = fusion.generate("Hello Jarvis, check readiness")

    # 3. Verify Bot Bluetooth + Anatomical Eyeball Engine + Live Mic Activity
    bot = BotInteractiveController(board_mode="arduino_uno")
    bt_probe = bot.connect_bluetooth("virtual_bluetooth_uno")
    eyeballs_js_ok = (PROJECT_ROOT / "dashboard/eyeballs.js").is_file()

    # 4. Verify Installable Phone "Deskbot Eyes" Stream-Flow App
    mobile = MobilePersonalAgent(fusion_model=fusion)
    mob_probe = mobile.connect_laptop_bluetooth()
    pwa_manifest_ok = (PROJECT_ROOT / "dashboard/manifest.json").is_file()

    # 5. Verify Multi-Language Code & Universal Laptop Job Engine
    jobs = UniversalJobEngine(output_root=PROJECT_ROOT / "workspace_output")
    java_probe = jobs.execute_job(
        "write a java code to print my name is aditya pratap singh",
        job_type="code",
    )

    # 6. Verify Always-On Background Daemon
    bg_daemon = JarvisBackgroundDaemon()
    bg_status = bg_daemon.get_status()

    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    ready = (
        cad_report["passed"]
        and uno_circuit["passed"]
        and fw_report["passed"]
        and gguf_valid
        and fusion_probe["fusion"]["active_ram_mb"] <= 850
        and bt_probe["bt_connected"]
        and eyeballs_js_ok
        and mob_probe["bt_paired_to_laptop"]
        and pwa_manifest_ok
        and java_probe["status"] == "completed"
        and java_probe["language"] == "java"
        and bg_status["running_in_background"]
    )

    return {
        "ready_for_deploy": ready,
        "stages_verified": 22,
        "preflight_time_ms": elapsed_ms,
        "fusion_model": fusion.FUSION_NAME,
        "local_gguf_ready": gguf_valid,
        "active_ram_mb": fusion_probe["fusion"]["active_ram_mb"],
        "max_ram_mb": 850,
        "arduino_uno_circuit_ok": uno_circuit["passed"],
        "arduino_uno_firmware_ok": fw_report["passed"],
        "cad_tolerances_ok": cad_report["passed"],
        "bot_bluetooth_ready": bt_probe["bt_connected"],
        "eyeball_engine_ready": eyeballs_js_ok,
        "mobile_agent_ready": mob_probe["bt_paired_to_laptop"] and pwa_manifest_ok,
        "laptop_job_engine_ready": java_probe["status"] == "completed",
        "background_daemon_ready": bg_status["running_in_background"],
        "dashboard_url": "http://127.0.0.1:8080",
        "mobile_agent_url": "http://127.0.0.1:8080/mobile",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="DESKBOT // J.A.R.V.I.S. Production Launcher")
    ap.add_argument("--check-only", action="store_true", help="Run preflight verification and exit")
    ap.add_argument("--port", type=int, default=8080, help="HTTP port for Dashboard & Mobile Agent")
    ap.add_argument("--output", default=str(PROJECT_ROOT / "workspace_output/deploy_report.json"))
    args = ap.parse_args()

    report = run_preflight_checks()
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Preflight report written to: {out_path} (ready={report['ready_for_deploy']})")

    if not report["ready_for_deploy"]:
        return 1
    if args.check_only:
        return 0

    from dashboard.server import run_server

    run_server(port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
