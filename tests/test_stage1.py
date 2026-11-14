import asyncio
import json
import tempfile
import time
import unittest
from pathlib import Path

from core.config import Config, ConfigError
from core.event_bus import Event, EventBus, EventType


class ConfigTests(unittest.TestCase):
    def test_defaults_when_file_missing(self):
        c = Config(path="does/not/exist.json", env={})
        self.assertTrue(c.get("robot", "simulate"))
        self.assertEqual(c.get("dashboard", "port"), 8080)

    def test_file_overrides_and_deep_merge(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.json"
            p.write_text(json.dumps({"dashboard": {"port": 9000}}))
            c = Config(path=p, env={})
            self.assertEqual(c.get("dashboard", "port"), 9000)
            self.assertEqual(c.get("dashboard", "host"), "127.0.0.1")  # default kept

    def test_env_override_parses_json(self):
        c = Config(path="x.json", env={"DESKBOT__ROBOT__SIMULATE": "false",
                                       "DESKBOT__DASHBOARD__PORT": "1234"})
        self.assertIs(c.get("robot", "simulate"), False)
        self.assertEqual(c.get("dashboard", "port"), 1234)

    def test_malformed_json_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text("{not json")
            with self.assertRaises(ConfigError):
                Config(path=p, env={})

    def test_shipped_config_loads(self):
        c = Config(env={})
        self.assertEqual(c.get("project", "name"), "DESKBOT")
        self.assertEqual(c.get("llm", "context_length"), 4096)

    def test_yaml_file_loads_and_overrides(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "config.yaml"
            p.write_text("dashboard:\n  port: 7777\nrobot:\n  simulate: false\n", encoding="utf-8")
            c = Config(path=p, env={})
            self.assertEqual(c.get("dashboard", "port"), 7777)
            self.assertIs(c.get("robot", "simulate"), False)
            self.assertEqual(c.get("dashboard", "host"), "127.0.0.1")


class EventBusTests(unittest.IsolatedAsyncioTestCase):
    async def test_subscribe_and_publish(self):
        bus, got = EventBus(), []

        async def h(e: Event):
            got.append(e.data["x"])

        bus.subscribe(EventType.USER_INPUT, h)
        n = await bus.emit(EventType.USER_INPUT, {"x": 1})
        self.assertEqual((n, got), (1, [1]))

    async def test_wildcard_and_no_subscribers(self):
        bus, seen = EventBus(), []

        async def w(e: Event):
            seen.append(e.topic)

        bus.subscribe_all(w)
        await bus.emit("custom.topic")
        self.assertEqual(seen, ["custom.topic"])
        self.assertEqual(await EventBus().emit("nobody"), 0)

    async def test_failing_handler_isolated(self):
        bus, ok = EventBus(), []

        async def bad(e):
            raise RuntimeError("boom")

        async def good(e):
            ok.append(1)

        bus.subscribe("t", bad)
        bus.subscribe("t", good)
        with self.assertLogs("EventBus", level="ERROR"):
            await bus.emit("t")
        self.assertEqual(ok, [1])
        self.assertEqual(bus.error_count, 1)

    async def test_unsubscribe(self):
        bus, got = EventBus(), []

        async def h(e):
            got.append(1)

        bus.subscribe("t", h)
        self.assertTrue(bus.unsubscribe("t", h))
        self.assertFalse(bus.unsubscribe("t", h))
        await bus.emit("t")
        self.assertEqual(got, [])

    async def test_sync_handler_rejected(self):
        with self.assertRaises(TypeError):
            EventBus().subscribe("t", lambda e: None)

    async def test_history_ring_buffer(self):
        bus = EventBus(history_size=5)
        for i in range(12):
            await bus.emit("t", {"i": i})
        self.assertEqual([e.data["i"] for e in bus.recent(10)], [7, 8, 9, 10, 11])

    async def test_throughput_10k_events_per_sec(self):
        """Stage 1 success criterion: >= 10,000 events/sec without blocking."""
        bus, count = EventBus(), 0

        async def h(e):
            nonlocal count
            count += 1

        bus.subscribe("t", h)
        start = time.perf_counter()
        for _ in range(10_000):
            await bus.emit("t")
        elapsed = time.perf_counter() - start
        self.assertEqual(count, 10_000)
        self.assertLess(elapsed, 1.0, f"10k events took {elapsed:.2f}s")

    async def test_event_loop_not_blocked(self):
        """A concurrent ticker keeps running while events flow."""
        bus, ticks = EventBus(), 0

        async def slow(e):
            await asyncio.sleep(0.001)

        async def ticker():
            nonlocal ticks
            while True:
                ticks += 1
                await asyncio.sleep(0.005)

        bus.subscribe("t", slow)
        t = asyncio.create_task(ticker())
        for _ in range(100):
            await bus.emit("t")
        t.cancel()
        self.assertGreater(ticks, 5)


if __name__ == "__main__":
    unittest.main()
