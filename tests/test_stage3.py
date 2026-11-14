from array import array
import math
import unittest

from core.voice.stt import SpeechToTextEngine, pcm16_to_wav_bytes, wav_bytes_to_pcm16
from core.voice.vad import AudioRingBuffer, VoiceActivityDetector, pcm16_rms, pcm16_zcr
from core.voice.wake_word import WakeWordDetector


def _make_sine_pcm16(freq_hz: float = 440.0, duration_ms: int = 20, sample_rate: int = 16000, amp: int = 8000) -> bytes:
    n = int(sample_rate * (duration_ms / 1000.0))
    two_pi = 2.0 * math.pi
    samples = array("h", [int(amp * math.sin(two_pi * freq_hz * i / sample_rate)) for i in range(n)])
    return samples.tobytes()


def _make_silence_pcm16(duration_ms: int = 20, sample_rate: int = 16000) -> bytes:
    n = int(sample_rate * (duration_ms / 1000.0))
    return b"\x00\x00" * n


class Stage3VoiceSTTTests(unittest.TestCase):
    def test_ring_buffer_capacity_and_latest_slice(self):
        ring = AudioRingBuffer(max_duration_sec=1.0, sample_rate=1000)  # 2000 bytes capacity
        ring.write(b"\x01\x00" * 800)   # 1600 bytes
        ring.write(b"\x02\x00" * 600)   # +1200 bytes -> total 2800 -> capped at 2000
        self.assertEqual(len(ring.read_all()), 2000)
        latest_half = ring.read_latest(0.5)
        self.assertEqual(len(latest_half), 1000)
        self.assertEqual(latest_half, b"\x02\x00" * 500)

    def test_pcm16_rms_and_zcr(self):
        silence = _make_silence_pcm16(20)
        tone = _make_sine_pcm16(440.0, 20, amp=10000)
        self.assertEqual(pcm16_rms(silence), 0.0)
        self.assertEqual(pcm16_zcr(silence), 0.0)
        self.assertAlmostEqual(pcm16_rms(tone), 10000 / math.sqrt(2), delta=300)
        self.assertGreater(pcm16_zcr(tone), 0.02)

    def test_vad_segments_voiced_utterance_with_preroll(self):
        vad = VoiceActivityDetector(
            sample_rate=16000,
            frame_duration_ms=20,
            energy_threshold=500.0,
            onset_frames=3,
            silence_frames=4,
            preroll_frames=2,
        )
        silent_frame = _make_silence_pcm16(20)
        voiced_frame = _make_sine_pcm16(300.0, 20, amp=6000)

        for _ in range(3):
            self.assertIsNone(vad.process_frame(silent_frame))
        for _ in range(6):
            self.assertIsNone(vad.process_frame(voiced_frame))
        self.assertTrue(vad.in_speech)

        out = None
        for _ in range(4):
            out = vad.process_frame(silent_frame)
        self.assertIsNotNone(out)
        self.assertFalse(vad.in_speech)
        # 2 preroll + 4 remaining voiced + 4 silence tail = 10 frames of 640 bytes
        self.assertGreaterEqual(len(out), 8 * len(voiced_frame))

    def test_wake_word_frame_scorer_and_transcript_extractor(self):
        triggered = []
        ww = WakeWordDetector(
            wake_phrase="hey deskbot",
            threshold=0.7,
            frame_scorer=lambda frame: 0.85 if pcm16_rms(frame) > 1000 else 0.1,
            on_wake_detected=lambda score: triggered.append(score),
        )
        self.assertLess(ww.score_audio_frame(_make_silence_pcm16(20)), 0.7)
        self.assertEqual(len(triggered), 0)
        self.assertGreaterEqual(ww.score_audio_frame(_make_sine_pcm16(440.0, 20, amp=5000)), 0.7)
        self.assertEqual(len(triggered), 1)

        detected, cmd = ww.extract_command("Hey Deskbot, open Spotify on my laptop")
        self.assertTrue(detected)
        self.assertEqual(cmd, "open Spotify on my laptop")

    def test_stt_wav_roundtrip_and_sub_300ms_latency(self):
        pcm = _make_sine_pcm16(440.0, 200, amp=4000)
        wav = pcm16_to_wav_bytes(pcm, sample_rate=16000)
        unpacked, sr = wav_bytes_to_pcm16(wav)
        self.assertEqual(sr, 16000)
        self.assertEqual(unpacked, pcm)

        stt = SpeechToTextEngine(backend=lambda wav_b: "open spotify on my laptop")
        res = stt.transcribe_pcm(pcm)
        self.assertEqual(res["text"], "open spotify on my laptop")
        self.assertLess(res["latency_ms"], 300.0, f"STT latency {res['latency_ms']} ms >= 300 ms")


if __name__ == "__main__":
    unittest.main()
