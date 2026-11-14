"""DESKBOT offline voice pipeline package (Stages 3 & 4)."""

from core.voice.vad import AudioRingBuffer, VoiceActivityDetector, pcm16_rms
from core.voice.wake_word import WakeWordDetector
from core.voice.stt import SpeechToTextEngine, pcm16_to_wav_bytes
from core.voice.tts import AudioPlaybackQueue, TextToSpeechEngine, synthesize_chime_wav

__all__ = [
    "AudioRingBuffer",
    "VoiceActivityDetector",
    "pcm16_rms",
    "WakeWordDetector",
    "SpeechToTextEngine",
    "pcm16_to_wav_bytes",
    "TextToSpeechEngine",
    "AudioPlaybackQueue",
    "synthesize_chime_wav",
]
