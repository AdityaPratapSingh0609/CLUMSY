import unittest

from core.mesh.transport import DualTransportRouter, MeshEnvelope
from satellite_agent.pc_client import (
    LaptopSatelliteDaemon,
    build_os_launch_command,
    build_os_lock_command,
)


class Stage7LaptopDaemonTests(unittest.TestCase):
    def test_cross_platform_launch_commands(self):
        win_cmd = build_os_launch_command("Spotify", system_name="Windows")
        self.assertEqual(win_cmd, ["cmd", "/c", "start", "", "spotify:"])

        mac_cmd = build_os_launch_command("VS Code", system_name="Darwin")
        self.assertEqual(mac_cmd, ["open", "-a", "Visual Studio Code"])

        lin_cmd = build_os_launch_command("Spotify", system_name="Linux")
        self.assertEqual(lin_cmd, ["spotify"])

    def test_cross_platform_lock_commands(self):
        self.assertIn("LockWorkStation", " ".join(build_os_lock_command("Windows")))
        self.assertEqual(build_os_lock_command("Darwin"), ["pmset", "displaysleepnow"])
        self.assertEqual(build_os_lock_command("Linux"), ["loginctl", "lock-session"])

    def test_volume_media_and_lock_actions(self):
        daemon = LaptopSatelliteDaemon(dry_run=True)

        vol_res = daemon.execute_action("set_volume", {"volume": 45, "mute": True})
        self.assertEqual(vol_res["volume"], 45)
        self.assertTrue(vol_res["muted"])

        media_res = daemon.execute_action("media_control", {"command": "play"})
        self.assertEqual(media_res["media_state"], "playing")

        lock_res = daemon.execute_action("lock_screen", {})
        self.assertTrue(lock_res["locked"])


class Stage7AsyncWebSocketDaemonTests(unittest.IsolatedAsyncioTestCase):
    async def test_remote_app_launch_under_500ms(self):
        """Stage 7 success criterion: Laptop launches requested app within 500 ms of Deskbot command."""
        daemon = LaptopSatelliteDaemon(host="127.0.0.1", port=0, dry_run=True)
        port = await daemon.start()
        router = DualTransportRouter()
        router.register_lan_endpoint("laptop_node", "127.0.0.1", port)

        try:
            env = MeshEnvelope(
                source_device="desktop_host",
                target_device="laptop_node",
                action="launch_app",
                payload={"app_name": "Spotify"},
                transport="lan_websocket",
            )
            reply, rtt_ms = await router.send(env)
            self.assertTrue(reply.payload["success"])
            self.assertEqual(reply.payload["app_name"], "Spotify")
            self.assertLess(rtt_ms, 500.0, f"App launch RTT {rtt_ms} ms >= 500 ms")
        finally:
            await router.close_all()
            await daemon.stop()


if __name__ == "__main__":
    unittest.main()
