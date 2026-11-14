"""DESKBOT Offline Speech-to-Text (STT) Engine (Stage 3).

Supports:
1. `faster-whisper` (`tiny.en` / `base.en`, `int8` quantized) on 16 kHz mono
   PCM bytes or WAV files.
2. Injectable `backend` callable `(wav_bytes: bytes) -> str` for deterministic
   unit testing and latency verification.
3. Stdlib `wave` helper `pcm16_to_wav_bytes` / `wav_bytes_to_pcm16`.
"""

import io
import logging
import time
import wave
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Union

logger = logging.getLogger("STT")


def pcm16_to_wav_bytes(pcm_bytes: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
    """Packs raw 16-bit signed little-endian PCM bytes into an in-memory RIFF WAV container."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()


def wav_bytes_to_pcm16(wav_bytes: bytes) -> Tuple[bytes, int]:
    """Unpacks RIFF WAV bytes into `(pcm16_bytes, sample_rate)`."""
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        return wf.readframes(wf.getnframes()), wf.getframerate()


class SpeechToTextEngine:
    def __init__(
        self,
        model_size: str = "tiny.en",
        compute_type: str = "int8",
        language: str = "en",
        sample_rate: int = 16000,
        backend: Optional[Callable[[bytes], str]] = None,
    ):
        self.model_size = model_size
        self.compute_type = compute_type
        self.language = language
        self.sample_rate = sample_rate
        self._custom_backend = backend
        self.whisper_model = None
        self.engine_type = "custom_backend" if backend is not None else "offline_pcm_stt"
        if backend is None:
            self._init_faster_whisper()

    def _init_faster_whisper(self) -> None:
        try:
            from faster_whisper import WhisperModel  # type: ignore

            self.whisper_model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type=self.compute_type,
            )
            self.engine_type = "faster_whisper"
            logger.info("Loaded faster-whisper (%s, %s)", self.model_size, self.compute_type)
        except Exception:
            self.whisper_model = None

    def transcribe_pcm(self, pcm16_bytes: bytes) -> Dict[str, Any]:
        """Transcribes raw 16 kHz 16-bit mono PCM audio and returns timing metrics."""
        t0 = time.perf_counter()
        wav_bytes = pcm16_to_wav_bytes(pcm16_bytes, sample_rate=self.sample_rate)

        if self._custom_backend is not None:
            text = self._custom_backend(wav_bytes).strip()
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            return {
                "text": text,
                "language": self.language,
                "engine": "custom_backend",
                "latency_ms": latency_ms,
                "audio_bytes": len(pcm16_bytes),
            }

        if self.whisper_model is not None:
            segments, info = self.whisper_model.transcribe(
                io.BytesIO(wav_bytes),
                beam_size=1,
                language=self.language,
            )
            text = " ".join(seg.text.strip() for seg in segments).strip()
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            return {
                "text": text,
                "language": getattr(info, "language", self.language),
                "engine": "faster_whisper",
                "latency_ms": latency_ms,
                "audio_bytes": len(pcm16_bytes),
            }

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "text": "",
            "language": self.language,
            "engine": self.engine_type,
            "latency_ms": latency_ms,
            "audio_bytes": len(pcm16_bytes),
        }

    def transcribe(self, audio_or_text: Union[bytes, str, Path]) -> Dict[str, Any]:
        """Convenience wrapper accepting raw PCM16 bytes, WAV file path, or pre-decoded text."""
        if isinstance(audio_or_text, bytes):
            if audio_or_text[:4] == b"RIFF":
                pcm, _ = wav_bytes_to_pcm16(audio_or_text)
                return self.transcribe_pcm(pcm)
            return self.transcribe_pcm(audio_or_text)
        if isinstance(audio_or_text, Path) or (isinstance(audio_or_text, str) and Path(audio_or_text).exists()):
            raw = Path(audio_or_text).read_bytes()
            return self.transcribe(raw)
        t0 = time.perf_counter()
        text = str(audio_or_text).strip()
        return {
            "text": text,
            "language": self.language,
            "engine": self.engine_type,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
            "audio_bytes": 0,
        }
