from pathlib import Path
import tempfile
import unittest

from core.tool_router import (
    PluginLoader,
    SchemaValidationError,
    ShortcutIntentMatcher,
    ToolRegistry,
    validate_against_schema,
)


class Stage5ToolRouterTests(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        self.loader = PluginLoader(self.registry)
        self.loaded = self.loader.load_all()

    def test_builtin_plugins_loaded(self):
        self.assertIn("media_player", self.loaded)
        self.assertIn("app_launcher", self.loaded)
        self.assertIn("system_monitor", self.loaded)

    def test_media_player_schema_and_execution(self):
        res_play = self.registry.execute("media_player", {"action": "play"})
        self.assertEqual(res_play["status"], "playing")

        res_next = self.registry.execute("media_player", {"action": "next"})
        self.assertEqual(res_next["status"], "playing")

        res_vol = self.registry.execute("media_player", {"action": "volume", "volume": 40})
        self.assertEqual(res_vol["volume"], 40)

        # Invalid enum and out-of-range volume must be rejected with 100% accuracy
        with self.assertRaises(SchemaValidationError):
            self.registry.execute("media_player", {"action": "explode"})
        with self.assertRaises(SchemaValidationError):
            self.registry.execute("media_player", {"action": "volume", "volume": 150})
        with self.assertRaises(SchemaValidationError):
            self.registry.execute("media_player", {"action": "play", "extra_field": 1})

    def test_app_launcher_schema_and_defaults(self):
        res = self.registry.execute("app_launcher", {"app_name": "Spotify"})
        self.assertEqual(res["target"], "desktop_host")
        self.assertEqual(res["app_name"], "Spotify")
        self.assertEqual(res["args"], [])

        with self.assertRaises(SchemaValidationError):
            self.registry.execute("app_launcher", {})
        with self.assertRaises(SchemaValidationError):
            self.registry.execute("app_launcher", {"app_name": ""})

    def test_system_monitor_returns_real_os_metrics(self):
        res = self.registry.execute("system_monitor", {})
        self.assertGreaterEqual(res["cpu_cores"], 1)
        self.assertGreater(res["disk_free_gb"], 0.0)
        self.assertGreater(res["ram"]["total_mb"], 0.0)

    def test_plugin_hot_reload(self):
        with tempfile.TemporaryDirectory() as d:
            pdir = Path(d)
            plugin_file = pdir / "custom_echo.py"
            plugin_file.write_text(
                "from core.tool_router import ToolSpec\n"
                "def register_tools(reg):\n"
                "    reg.register(ToolSpec(\n"
                "        name='custom_echo',\n"
                "        description='Echo test',\n"
                "        parameters_schema={'type': 'object', 'properties': {'msg': {'type': 'string'}}, 'required': ['msg']},\n"
                "        handler=lambda a: {'echo': a['msg']}\n"
                "    ))\n",
                encoding="utf-8",
            )
            reg = ToolRegistry()
            loader = PluginLoader(reg, plugins_dir=pdir)
            self.assertEqual(loader.load_all(), ["custom_echo"])
            self.assertEqual(reg.execute("custom_echo", {"msg": "hi"}), {"echo": "hi"})
            self.assertEqual(loader.reload_modified(), [])

    def test_shortcut_intent_matcher(self):
        matcher = ShortcutIntentMatcher()
        m1 = matcher.match("please open Spotify on my laptop")
        self.assertEqual(m1, ("app_launcher", {"app_name": "Spotify", "target": "laptop_node"}))

        m2 = matcher.match("pause the music right now")
        self.assertEqual(m2, ("media_player", {"action": "pause"}))

        m3 = matcher.match("check system status and cpu")
        self.assertEqual(m3, ("system_monitor", {"include_processes": False}))


if __name__ == "__main__":
    unittest.main()
