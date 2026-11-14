import io
import tempfile
import unittest
import wave
from pathlib import Path

from core.event_bus import EventBus, EventType
from core.orchestrator import Orchestrator
from core.voice.stt import wav_bytes_to_pcm16
from core.voice.tts import AudioPlaybackQueue, TextToSpeechEngine, synthesize_chime_wav
from core.voice.vad import pcm16_rms


class Stage4TTSTests(unittest.TestCase):
    def test_chime_presets_generate_valid_wav(self):
        for preset in ("chime_wake", "chime_think", "chime_happy", "chime_error"):
            wav_bytes = synthesize_chime_wav(preset, sample_rate=22050)
            self.assertEqual(wav_bytes[:4], b"RIFF")
            pcm, sr = wav_bytes_to_pcm16(wav_bytes)
            self.assertEqual(sr, 22050)
            self.assertGreater(pcm16_rms(pcm), 500.0)

    def test_tts_synthesis_rtf_below_0_15(self):
        """Stage 4 success criterion: Real-Time Factor (RTF) < 0.15 (< 150 ms per 1s audio)."""
        tts = TextToSpeechEngine(sample_rate=22050)
        with tempfile.TemporaryDirectory() as d:
            out_wav = Path(d) / "reply.wav"
            res = tts.synthesize(
                "Hello! I checked your phone battery and launched Spotify on your laptop.",
                output_wav_path=out_wav,
            )
            self.assertTrue(out_wav.exists())
            with wave.open(io.BytesIO(res["wav_bytes"]), "rb") as wf:
                self.assertEqual(wf.getnchannels(), 1)
                self.assertEqual(wf.getsampwidth(), 2)
                self.assertEqual(wf.getframerate(), 22050)
            self.assertGreater(res["duration_sec"], 0.5)
            self.assertLess(res["rtf"], 0.15, f"RTF {res['rtf']} >= 0.15")


class Stage4PlaybackAsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_playback_queue_emits_tts_events(self):
        bus = EventBus()
        tts = TextToSpeechEngine()
        q = AudioPlaybackQueue(tts_engine=tts, event_bus=bus)
        events = []

        async def _listener(evt):
            events.append((evt.topic, evt.data.get("kind")))

        bus.subscribe(EventType.TTS_PLAY, _listener)
        bus.subscribe(EventType.TTS_DONE, _listener)

        await q.start()
        await q.enqueue_chime("chime_wake")
        await q.enqueue_speech("Deskbot is ready.")
        await q.wait_until_drained()
        await q.stop()

        self.assertEqual(
            events,
            [
                ("tts.play", "chime"),
                ("tts.done", "chime"),
                ("tts.play", "speech"),
                ("tts.done", "speech"),
            ],
        )

    async def test_orchestrator_voice_wake_stt_brain_tts_flow(self):
        orch = Orchestrator()
        await orch.start()
        await orch.bus.emit(
            EventType.STT_RESULT,
            {"text": "Hey Deskbot, check my phone battery"},
            source="test_mic",
        )
        await orch.audio_queue.wait_until_drained()
        kinds = [item["kind"] for item in orch.audio_queue.played_items]
        self.assertIn("chime", kinds)
        self.assertIn("speech", kinds)
        await orch.stop()


if __name__ == "__main__":
    unittest.main()
