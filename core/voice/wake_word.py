"""DESKBOT Offline Wake Word Detector (Stage 3).

Supports:
1. `openwakeword` ONNX inference on 16 kHz PCM frames when installed.
2. Injectable `frame_scorer` callable for deterministic unit testing.
3. Text/transcript wake-phrase matcher and command stripper (e.g.
   "Hey Deskbot, open Spotify" -> detected=True, remainder="open Spotify").
"""

import logging
import re
from typing import Callable, Optional, Tuple

logger = logging.getLogger("WakeWord")


class WakeWordDetector:
    def __init__(
        self,
        wake_phrase: str = "hey deskbot",
        threshold: float = 0.7,
        sample_rate: int = 16000,
        frame_scorer: Optional[Callable[[bytes], float]] = None,
        on_wake_detected: Optional[Callable[[float], None]] = None,
    ):
        self.wake_phrase = wake_phrase.strip().lower()
        self.threshold = float(threshold)
        self.sample_rate = sample_rate
        self._frame_scorer = frame_scorer
        self.on_wake_detected = on_wake_detected
        self.model = None
        self.engine_type = "transcript_and_scorer"
        self.detections = 0
        if frame_scorer is None:
            self._init_openwakeword()

    def _init_openwakeword(self) -> None:
        try:
            from openwakeword.model import Model  # type: ignore

            self.model = Model(inference_framework="onnx")
            self.engine_type = "openwakeword"
            logger.info("Loaded openWakeWord ONNX model.")
        except Exception:
            self.model = None

    def score_audio_frame(self, pcm16_frame: bytes) -> float:
        """Scores a 16 kHz PCM16 frame in [0.0, 1.0] and triggers callback if >= threshold."""
        score = 0.0
        if self._frame_scorer is not None:
            score = float(self._frame_scorer(pcm16_frame))
        elif self.model is not None:
            import numpy as np  # type: ignore

            arr = np.frombuffer(pcm16_frame, dtype=np.int16)
            preds = self.model.predict(arr)
            score = float(max(preds.values())) if preds else 0.0

        if score >= self.threshold:
            self.detections += 1
            if self.on_wake_detected is not None:
                self.on_wake_detected(score)
        return score

    def extract_command(self, transcript: str) -> Tuple[bool, str]:
        """
        Checks if `transcript` starts with or contains the wake phrase.
        Returns (detected, cleaned_command_text).
        """
        if not transcript:
            return False, ""
        pattern = re.compile(
            r"^\s*(?:hey\s+|hi\s+|okay\s+|ok\s+)?"
            + re.escape(self.wake_phrase.replace("hey ", ""))
            + r"[\s,.:;!\-]*",
            flags=re.IGNORECASE,
        )
        m = pattern.match(transcript)
        if m:
            self.detections += 1
            if self.on_wake_detected is not None:
                self.on_wake_detected(1.0)
            remainder = transcript[m.end() :].strip()
            return True, remainder or transcript.strip()
        return False, transcript.strip()
