"""DESKBOT Audio Ring Buffer & Voice Activity Detection (Stage 3).

Provides:
- `AudioRingBuffer`: fixed-capacity circular buffer for 16 kHz 16-bit mono PCM.
- `pcm16_rms` / `pcm16_zcr`: fast stdlib (`array('h')`) signal energy and
  zero-crossing-rate computation.
- `VoiceActivityDetector`: stateful speech onset + silence-hangover segmenter
  (uses `webrtcvad` when installed, or deterministic RMS+ZCR detector).
"""

from array import array
from collections import deque
import math
import sys
from typing import Deque, List, Optional


def _samples_from_pcm16(pcm_bytes: bytes) -> array:
    if len(pcm_bytes) % 2 != 0:
        pcm_bytes = pcm_bytes[:-1]
    samples = array("h")
    samples.frombytes(pcm_bytes)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples


def pcm16_rms(pcm_bytes: bytes) -> float:
    """Computes Root-Mean-Square (RMS) amplitude of 16-bit signed little-endian PCM."""
    samples = _samples_from_pcm16(pcm_bytes)
    n = len(samples)
    if n == 0:
        return 0.0
    total = 0.0
    for s in samples:
        total += float(s) * float(s)
    return math.sqrt(total / n)


def pcm16_zcr(pcm_bytes: bytes) -> float:
    """Computes zero-crossing rate in [0.0, 1.0] for 16-bit signed PCM."""
    samples = _samples_from_pcm16(pcm_bytes)
    n = len(samples)
    if n < 2:
        return 0.0
    crossings = 0
    prev = samples[0]
    for s in samples[1:]:
        if (prev >= 0 and s < 0) or (prev < 0 and s >= 0):
            crossings += 1
        prev = s
    return crossings / (n - 1)


class AudioRingBuffer:
    """Circular byte buffer for 16-bit mono PCM audio at a given sample rate."""

    def __init__(self, max_duration_sec: float = 10.0, sample_rate: int = 16000):
        if max_duration_sec <= 0 or sample_rate <= 0:
            raise ValueError("max_duration_sec and sample_rate must be positive")
        self.sample_rate = sample_rate
        self.bytes_per_sample = 2
        self.capacity_bytes = int(max_duration_sec * sample_rate) * self.bytes_per_sample
        self._buf = bytearray()

    def write(self, pcm_bytes: bytes) -> None:
        if not pcm_bytes:
            return
        self._buf.extend(pcm_bytes)
        overflow = len(self._buf) - self.capacity_bytes
        if overflow > 0:
            del self._buf[:overflow]

    def read_latest(self, duration_sec: float) -> bytes:
        n_bytes = int(duration_sec * self.sample_rate) * self.bytes_per_sample
        if n_bytes <= 0:
            return b""
        return bytes(self._buf[-n_bytes:])

    def read_all(self) -> bytes:
        return bytes(self._buf)

    def clear(self) -> None:
        self._buf.clear()

    @property
    def duration_sec(self) -> float:
        return len(self._buf) / (self.sample_rate * self.bytes_per_sample)


class VoiceActivityDetector:
    """
    Segments a continuous stream of 16 kHz PCM frames into complete speech utterances.

    Includes a pre-roll ring of frames so initial consonants before speech onset
    confirmation are preserved.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        frame_duration_ms: int = 20,
        energy_threshold: float = 500.0,
        onset_frames: int = 3,
        silence_frames: int = 10,
        preroll_frames: int = 4,
    ):
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_bytes = int(sample_rate * (frame_duration_ms / 1000.0)) * 2
        self.energy_threshold = energy_threshold
        self.onset_frames = onset_frames
        self.silence_frames = silence_frames
        self._preroll: Deque[bytes] = deque(maxlen=max(preroll_frames, 1))
        self._active_frames: List[bytes] = []
        self._voiced_streak = 0
        self._silence_streak = 0
        self.in_speech = False
        self._webrtc_vad = None
        try:
            import webrtcvad  # type: ignore

            if frame_duration_ms in (10, 20, 30) and sample_rate in (8000, 16000, 32000, 48000):
                self._webrtc_vad = webrtcvad.Vad(2)
        except ImportError:
            pass

    def is_frame_voiced(self, frame: bytes) -> bool:
        """Returns True if a single PCM16 frame contains voice activity."""
        if not frame:
            return False
        rms = pcm16_rms(frame)
        if rms < self.energy_threshold:
            return False
        if self._webrtc_vad is not None and len(frame) == self.frame_bytes:
            try:
                return bool(self._webrtc_vad.is_speech(frame, self.sample_rate))
            except Exception:
                pass
        return True

    def process_frame(self, frame: bytes) -> Optional[bytes]:
        """
        Feeds one PCM16 frame into the segmenter.
        Returns complete utterance bytes when an utterance finishes, else None.
        """
        voiced = self.is_frame_voiced(frame)
        if not self.in_speech:
            self._preroll.append(frame)
            if voiced:
                self._voiced_streak += 1
                if self._voiced_streak >= self.onset_frames:
                    self.in_speech = True
                    self._silence_streak = 0
                    self._active_frames = list(self._preroll)
                    self._preroll.clear()
            else:
                self._voiced_streak = 0
            return None

        # Currently inside a speech segment
        self._active_frames.append(frame)
        if voiced:
            self._silence_streak = 0
        else:
            self._silence_streak += 1
            if self._silence_streak >= self.silence_frames:
                utterance = b"".join(self._active_frames)
                self.reset()
                return utterance
        return None

    def flush(self) -> Optional[bytes]:
        """Forces end-of-utterance if currently in speech."""
        if self.in_speech and self._active_frames:
            utterance = b"".join(self._active_frames)
            self.reset()
            return utterance
        self.reset()
        return None

    def reset(self) -> None:
        self._preroll.clear()
        self._active_frames.clear()
        self._voiced_streak = 0
        self._silence_streak = 0
        self.in_speech = False
