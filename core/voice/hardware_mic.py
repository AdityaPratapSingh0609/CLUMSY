"""Native Windows Offline Hardware Microphone Listener (`MS-1033-80-DESK`).

Uses Windows built-in `System.Speech.Recognition.SpeechRecognitionEngine` attached directly
to the default hardware microphone (`SetInputToDefaultAudioDevice()`) so that even when the
user opens CLUMSY inside an Electron WebView, Brave, or 100% offline browser where
`webkitSpeechRecognition` fails with `network` error, live spoken commands ("Hey Clumsy",
"Thank you", "Explain quantum mechanics", "Write Python code", etc.) are captured directly
from the hardware mic and streamed to both `/` and `/mobile`.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("HardwareMic")

POWERSHELL_MIC_SCRIPT = r"""
$ErrorActionPreference = 'SilentlyContinue'
Add-Type -AssemblyName System.Speech
$rec = New-Object System.Speech.Recognition.SpeechRecognitionEngine

# Boost accuracy for common CLUMSY commands + full open-ended dictation
$choices = New-Object System.Speech.Recognition.Choices
$choices.Add(@(
  "hey clumsy",
  "hi clumsy",
  "wake up",
  "go to sleep",
  "thank you",
  "thanks clumsy",
  "i love you",
  "tell me a joke",
  "how are you",
  "who are you",
  "what time is it",
  "explain quantum mechanics",
  "explain black holes",
  "explain machine learning",
  "explain artificial intelligence",
  "explain neural networks",
  "write a python code",
  "write a java code",
  "write python code for binary search",
  "write java code to print hello",
  "check my phone battery",
  "play music",
  "pause music",
  "next track"
))
$gb = New-Object System.Speech.Recognition.GrammarBuilder($choices)
$cmdGrammar = New-Object System.Speech.Recognition.Grammar($gb)
$cmdGrammar.Priority = 127
$rec.LoadGrammar($cmdGrammar)

$dictGrammar = New-Object System.Speech.Recognition.DictationGrammar
$rec.LoadGrammar($dictGrammar)

$rec.SetInputToDefaultAudioDevice()
Write-Output "MIC_READY"
[Console]::Out.Flush()

while ($true) {
  $res = $rec.Recognize([TimeSpan]::FromSeconds(4))
  if ($null -ne $res -and $res.Confidence -ge 0.25 -and $res.Text.Trim().Length -gt 0) {
    $txt = $res.Text.Trim()
    Write-Output "TRANSCRIPT:$txt"
    [Console]::Out.Flush()
  }
}
"""


class HardwareMicrophoneDaemon:
    """Background daemon that captures live speech from the Windows default microphone offline."""

    def __init__(self) -> None:
        self.enabled = sys.platform.startswith("win")
        self.is_ready = False
        self._proc: Optional[subprocess.Popen[str]] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._queue: List[Dict[str, Any]] = []
        self._seq = 0

    def start(self) -> None:
        if not self.enabled or self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self) -> None:
        while self.enabled:
            try:
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                self._proc = subprocess.Popen(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command", POWERSHELL_MIC_SCRIPT],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    bufsize=1,
                    creationflags=creationflags,
                )
                assert self._proc.stdout is not None
                for raw_line in self._proc.stdout:
                    line = raw_line.strip()
                    if not line:
                        continue
                    if line == "MIC_READY":
                        self.is_ready = True
                        logger.info("🎙️ Native Windows Offline Hardware Microphone (MS-1033-80-DESK) active.")
                    elif line.startswith("TRANSCRIPT:"):
                        transcript = line[len("TRANSCRIPT:") :].strip()
                        if transcript:
                            with self._lock:
                                self._seq += 1
                                self._queue.append(
                                    {
                                        "id": self._seq,
                                        "transcript": transcript,
                                        "timestamp": time.time(),
                                    }
                                )
                                if len(self._queue) > 30:
                                    self._queue = self._queue[-30:]
                            logger.info("🎙️ Hardware Mic Recognized: '%s'", transcript)
            except Exception as exc:
                logger.debug("Hardware mic loop exception: %s", exc)
            time.sleep(2.0)

    def poll_since(self, last_id: int = -1) -> Dict[str, Any]:
        """Return any new transcripts captured since `last_id`."""
        with self._lock:
            if last_id < 0:
                # Return current latest sequence ID without replaying old history on initial connect
                return {
                    "ready": self.is_ready,
                    "latest_id": self._seq,
                    "items": [],
                }
            items = [item for item in self._queue if item["id"] > last_id]
            return {
                "ready": self.is_ready,
                "latest_id": self._seq,
                "items": items,
            }


hardware_mic_daemon = HardwareMicrophoneDaemon()
