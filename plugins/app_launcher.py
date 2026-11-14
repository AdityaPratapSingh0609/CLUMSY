"""Universal Cross-Device Application & Website Launcher Plugin (Stage 5 & Stage 21)."""

from __future__ import annotations

import subprocess
import sys
from typing import Any, Dict, List
import webbrowser

from core.tool_router import ToolRegistry, ToolSpec

LAUNCH_HISTORY: List[Dict[str, Any]] = []

APP_COMMAND_MAP: Dict[str, Dict[str, str]] = {
    "spotify": {"type": "uri", "cmd": "spotify:"},
    "vs code": {"type": "cmd", "cmd": "code"},
    "vscode": {"type": "cmd", "cmd": "code"},
    "notepad": {"type": "cmd", "cmd": "notepad.exe"},
    "calculator": {"type": "cmd", "cmd": "calc.exe"},
    "calc": {"type": "cmd", "cmd": "calc.exe"},
    "terminal": {"type": "cmd", "cmd": "wt.exe"},
    "cmd": {"type": "cmd", "cmd": "cmd.exe"},
    "file explorer": {"type": "cmd", "cmd": "explorer.exe"},
    "explorer": {"type": "cmd", "cmd": "explorer.exe"},
    "settings": {"type": "uri", "cmd": "ms-settings:"},
    "browser": {"type": "url", "cmd": "https://www.google.com"},
    "chrome": {"type": "url", "cmd": "https://www.google.com"},
    "youtube": {"type": "url", "cmd": "https://www.youtube.com"},
    "github": {"type": "url", "cmd": "https://github.com"},
    "whatsapp": {"type": "url", "cmd": "https://web.whatsapp.com"},
    "discord": {"type": "url", "cmd": "https://discord.com/app"},
}

APP_LAUNCHER_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "target": {
            "type": "string",
            "enum": ["laptop_node", "desktop_host"],
            "default": "desktop_host",
        },
        "app_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 64,
        },
        "args": {
            "type": "array",
            "items": {"type": "string"},
            "default": [],
        },
        "execute_os": {
            "type": "boolean",
            "default": False,
        },
    },
    "required": ["app_name"],
    "additionalProperties": False,
}


def resolve_app_command(app_name: str) -> Dict[str, str]:
    key = (app_name or "").strip().lower()
    if key in APP_COMMAND_MAP:
        return APP_COMMAND_MAP[key]
    for k, spec in APP_COMMAND_MAP.items():
        if k in key:
            return spec
    if key.startswith(("http://", "https://", "www.")):
        url = key if key.startswith("http") else f"https://{key}"
        return {"type": "url", "cmd": url}
    return {"type": "cmd", "cmd": app_name}


def handle_app_launcher(params: Dict[str, Any]) -> Dict[str, Any]:
    target = params.get("target", "desktop_host")
    app_name = params["app_name"]
    args = params.get("args", [])
    spec = resolve_app_command(app_name)

    if params.get("execute_os", False):
        try:
            if spec["type"] in ("url", "uri"):
                webbrowser.open(spec["cmd"])
            elif sys.platform.startswith("win"):
                subprocess.Popen([spec["cmd"], *args], shell=False)
        except Exception:
            pass

    entry = {
        "target": target,
        "app_name": app_name,
        "args": args,
        "resolved_command": spec["cmd"],
        "command_type": spec["type"],
    }
    LAUNCH_HISTORY.append(entry)
    return {
        "success": True,
        "tool": "app_launcher",
        "target": entry["target"],
        "app_name": entry["app_name"],
        "args": entry["args"],
        "resolved_command": entry["resolved_command"],
        "command_type": entry["command_type"],
        "message": f"Launched {entry['app_name']} ({spec['cmd']}) on {entry['target']}",
    }


def register_tools(registry: ToolRegistry) -> None:
    registry.register(
        ToolSpec(
            name="app_launcher",
            description="Launch an application or website on the desktop host or remote laptop node.",
            parameters_schema=APP_LAUNCHER_SCHEMA,
            handler=handle_app_launcher,
            plugin_source="plugins.app_launcher",
        )
    )
