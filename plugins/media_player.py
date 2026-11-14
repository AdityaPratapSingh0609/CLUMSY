"""Universal System Audio & Offline Media Player Plugin (Stage 5 & Stage 21)."""

from __future__ import annotations

from typing import Any, Dict, List

from core.tool_router import ToolRegistry, ToolSpec

PLAYLIST: List[str] = [
    "Chill Synth Beats (Local)",
    "Midnight Lo-Fi Study Session",
    "Cyberpunk Ambient Horizon",
    "Acoustic Morning Breeze",
    "J.A.R.V.I.S. Arc Reactor Synthwave",
]

_STATE: Dict[str, Any] = {
    "status": "paused",
    "track_index": 0,
    "volume": 75,
}

MEDIA_PLAYER_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": ["play", "pause", "next", "prev", "volume"],
            "default": "play",
        },
        "track": {
            "type": "string",
            "default": "",
        },
        "volume": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "default": 75,
        },
    },
    "required": ["action"],
    "additionalProperties": False,
}


def handle_media_player(params: Dict[str, Any]) -> Dict[str, Any]:
    action = params.get("action", "play")
    requested_track = str(params.get("track") or "").strip()

    if requested_track and action == "play":
        if requested_track not in PLAYLIST:
            PLAYLIST.append(requested_track)
        _STATE["track_index"] = PLAYLIST.index(requested_track)
        _STATE["status"] = "playing"
    elif action == "play":
        _STATE["status"] = "playing"
    elif action == "pause":
        _STATE["status"] = "paused"
    elif action == "next":
        _STATE["track_index"] = (_STATE["track_index"] + 1) % len(PLAYLIST)
        _STATE["status"] = "playing"
    elif action == "prev":
        _STATE["track_index"] = (_STATE["track_index"] - 1) % len(PLAYLIST)
        _STATE["status"] = "playing"
    elif action == "volume":
        _STATE["volume"] = int(params.get("volume", _STATE["volume"]))

    return {
        "success": True,
        "tool": "media_player",
        "action": action,
        "status": _STATE["status"],
        "track": PLAYLIST[_STATE["track_index"]],
        "volume": _STATE["volume"],
    }


def register_tools(registry: ToolRegistry) -> None:
    registry.register(
        ToolSpec(
            name="media_player",
            description="Control local offline music playback (play, pause, next, prev, volume, custom track).",
            parameters_schema=MEDIA_PLAYER_SCHEMA,
            handler=handle_media_player,
            plugin_source="plugins.media_player",
        )
    )
