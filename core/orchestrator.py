"""DESKBOT central async orchestrator (Stages 1 – 8 integrated)."""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.brain import AssistantBrain
from core.config import Config
from core.event_bus import Event, EventBus, EventType
from core.llm_engine import LLMEngine
from core.mesh import DeviceMeshManager, DualTransportRouter
from core.robot_bridge import RobotBridge
from core.tool_router import PluginLoader, ToolRegistry
from core.voice import (
    AudioPlaybackQueue,
    AudioRingBuffer,
    SpeechToTextEngine,
    TextToSpeechEngine,
    VoiceActivityDetector,
    WakeWordDetector,
)
from satellite_agent.mobile.phone_bridge import PhoneCompanionBridge
from satellite_agent.pc_client import LaptopSatelliteDaemon

logger = logging.getLogger("Orchestrator")


class Orchestrator:
    """Wires Config, EventBus, RobotBridge, DeviceMeshManager, Satellites, ToolRegistry, TransportRouter, and Voice."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = Config(config_path)
        self.bus = EventBus()
        self.robot = RobotBridge(
            port=self.config.get("robot", "serial_port"),
            baudrate=self.config.get("robot", "baudrate", 115200),
            simulate=self.config.get("robot", "simulate", True),
        )
        self.mesh = DeviceMeshManager()
        self.transport_router = DualTransportRouter()
        self.laptop_daemon = LaptopSatelliteDaemon(node_id="laptop_node", dry_run=True)
        self.phone_bridge = PhoneCompanionBridge(
            device_id="phone_node",
            mesh_manager=self.mesh,
            event_bus=self.bus,
            ble_transport=self.transport_router.ble,
        )
        self.mesh.attach_handler("laptop_node", self.laptop_daemon.execute_action)
        self.mesh.attach_handler("phone_node", self._handle_phone_sync_command)
        self.urgent_alerts: List[Dict[str, Any]] = []

        self.tool_registry = ToolRegistry()
        self.plugin_loader = PluginLoader(
            self.tool_registry,
            plugins_dir=self.config.resolve_path("plugins", "directory"),
        )
        self.plugin_loader.load_all()
        self.llm = LLMEngine(
            model_path=self.config.resolve_path("llm", "model_path"),
            context_length=self.config.get("llm", "context_length", 4096),
            max_tokens=self.config.get("llm", "max_tokens", 512),
            temperature=self.config.get("llm", "temperature", 0.3),
            n_gpu_layers=self.config.get("llm", "n_gpu_layers", 0),
        )
        self.brain = AssistantBrain(
            robot_bridge=self.robot,
            mesh_manager=self.mesh,
            llm_engine=self.llm,
            tool_registry=self.tool_registry,
        )
        sample_rate = self.config.get("stt", "sample_rate", 16000)
        self.audio_ring = AudioRingBuffer(max_duration_sec=10.0, sample_rate=sample_rate)
        self.vad = VoiceActivityDetector(sample_rate=sample_rate)
        self.wake_word = WakeWordDetector(
            wake_phrase=self.config.get("wake_word", "phrase", "hey deskbot"),
            threshold=self.config.get("wake_word", "threshold", 0.7),
            sample_rate=sample_rate,
        )
        self.stt = SpeechToTextEngine(
            model_size=self.config.get("stt", "model_size", "tiny.en"),
            compute_type=self.config.get("stt", "compute_type", "int8"),
            language=self.config.get("stt", "language", "en"),
            sample_rate=sample_rate,
        )
        self.tts = TextToSpeechEngine(
            voice_model=self.config.get("tts", "voice_model", "en_US-lessac-medium"),
            sample_rate=self.config.get("tts", "sample_rate", 22050),
        )
        self.audio_queue = AudioPlaybackQueue(tts_engine=self.tts, event_bus=self.bus)
        self._running = False
        self._wire_events()

    def _handle_phone_sync_command(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action == "get_battery":
            return self.phone_bridge.get_battery_info()
        if action == "get_notifications":
            return self.phone_bridge.get_notifications_info(unread_only=bool(params.get("unread_only", True)))
        if action == "get_details":
            return self.phone_bridge.get_details()
        if action == "mark_read":
            return {"success": True, "cleared": self.phone_bridge.mark_all_read()}
        return {"success": False, "error": f"Unknown phone action '{action}'"}

    def _wire_events(self) -> None:
        self.bus.subscribe(EventType.WAKE_WORD_DETECTED, self._on_wake_word)
        self.bus.subscribe(EventType.STT_RESULT, self._on_stt_result)
        self.bus.subscribe(EventType.USER_INPUT, self._on_user_input)
        self.bus.subscribe(EventType.MESH_COMMAND_RESULT, self._on_mesh_event)

    async def _on_mesh_event(self, event: Event) -> None:
        if event.data.get("event") == "urgent_notification":
            notif = event.data.get("notification", {})
            self.urgent_alerts.append(notif)
            self.robot.set_listening()
            await self.audio_queue.enqueue_chime("chime_wake")

    async def _on_wake_word(self, event: Event) -> None:
        self.robot.set_listening()
        await self.audio_queue.enqueue_chime("chime_wake")

    async def _on_stt_result(self, event: Event) -> None:
        text = str(event.data.get("text") or "").strip()
        if not text:
            return
        detected, command_text = self.wake_word.extract_command(text)
        if detected:
            await self.bus.emit(
                EventType.WAKE_WORD_DETECTED,
                {"phrase": self.wake_word.wake_phrase, "command": command_text},
                source="wake_word",
            )
        await self.bus.emit(EventType.USER_INPUT, {"text": command_text}, source="stt")

    async def _on_user_input(self, event: Event) -> None:
        text = str(event.data.get("text") or "").strip()
        if not text:
            return
        await self.bus.emit(EventType.BRAIN_THINKING, {"query": text}, source="orchestrator")
        result = self.brain.process_query(text)
        await self.audio_queue.enqueue_speech(result["response"])
        await self.bus.emit(EventType.BRAIN_RESPONSE, result, source="brain")

    async def start(self) -> None:
        self._running = True
        self.robot.connect()
        await self.audio_queue.start()
        await self.bus.emit(
            EventType.SYSTEM_STARTUP,
            {"version": self.config.get("project", "version", "0.1.0")},
            source="orchestrator",
        )

    async def stop(self) -> None:
        self._running = False
        await self.audio_queue.wait_until_drained()
        await self.audio_queue.stop()
        await self.transport_router.close_all()
        self.robot.set_idle()
        await self.bus.emit(EventType.SYSTEM_SHUTDOWN, {}, source="orchestrator")

    async def submit_query(self, text: str) -> Dict[str, Any]:
        """Submits a user query via the EventBus and returns the latest BRAIN_RESPONSE."""
        captured: Dict[str, Any] = {}

        async def _capture(evt: Event) -> None:
            captured.update(evt.data)

        self.bus.subscribe(EventType.BRAIN_RESPONSE, _capture)
        try:
            await self.bus.emit(EventType.USER_INPUT, {"text": text}, source="user")
            await self.audio_queue.wait_until_drained()
        finally:
            self.bus.unsubscribe(EventType.BRAIN_RESPONSE, _capture)
        return captured
