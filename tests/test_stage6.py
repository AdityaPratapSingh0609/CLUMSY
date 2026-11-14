import json
import unittest

from core.mesh.transport import (
    BluetoothMeshTransport,
    DualTransportRouter,
    LANServiceBeacon,
    LANWebSocketServer,
    MeshEnvelope,
    PacketIntegrityError,
)


class Stage6EnvelopeAndBeaconTests(unittest.TestCase):
    def test_envelope_crc32_and_tamper_detection(self):
        env = MeshEnvelope(
            source_device="desktop_host",
            target_device="laptop_node",
            action="launch_app",
            payload={"app_name": "Spotify"},
        )
        wire = env.to_json()
        restored = MeshEnvelope.from_json(wire)
        self.assertEqual(restored.message_id, env.message_id)
        self.assertEqual(restored.payload, {"app_name": "Spotify"})

        # Tamper with payload without updating crc32
        tampered = json.loads(wire)
        tampered["payload"]["app_name"] = "MaliciousApp"
        with self.assertRaises(PacketIntegrityError):
            MeshEnvelope.from_json(json.dumps(tampered))

    def test_mdns_service_beacon_roundtrip(self):
        raw = LANServiceBeacon.encode_announcement(
            node_id="laptop_node",
            host="192.168.1.42",
            port=9120,
            capabilities=["app_launch", "media_play"],
        )
        decoded = LANServiceBeacon.decode_announcement(raw)
        self.assertEqual(decoded["node_id"], "laptop_node")
        self.assertEqual(decoded["port"], 9120)


class Stage6AsyncTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_lan_websocket_sub_10ms_and_ble_sub_30ms(self):
        """Stage 6 success criteria: < 10 ms over LAN WebSocket and < 30 ms over Bluetooth."""
        async def _lan_handler(env: MeshEnvelope):
            return {"status": "launched", "app": env.payload.get("app_name")}

        server = LANWebSocketServer(host="127.0.0.1", port=0, on_envelope=_lan_handler)
        port = await server.start()

        router = DualTransportRouter()
        router.register_lan_endpoint("laptop_node", "127.0.0.1", port)

        async def _ble_handler(env: MeshEnvelope):
            return {"battery": 88, "unread": 1}

        router.ble.register_gatt_peer("phone_node", _ble_handler)

        try:
            # Warmup LAN connection handshake, then measure packet delivery latency
            warmup_env = MeshEnvelope(
                source_device="desktop_host",
                target_device="laptop_node",
                action="ping",
                transport="lan_websocket",
            )
            await router.send(warmup_env)

            lan_env = MeshEnvelope(
                source_device="desktop_host",
                target_device="laptop_node",
                action="launch_app",
                payload={"app_name": "VS Code"},
                transport="lan_websocket",
            )
            lan_reply, lan_ms = await router.send(lan_env)
            self.assertEqual(lan_reply.payload["app"], "VS Code")
            self.assertLess(lan_ms, 10.0, f"LAN latency {lan_ms} ms >= 10 ms")

            ble_env = MeshEnvelope(
                source_device="desktop_host",
                target_device="phone_node",
                action="get_details",
                transport="bluetooth",
            )
            ble_reply, ble_ms = await router.send(ble_env)
            self.assertEqual(ble_reply.payload["battery"], 88)
            self.assertLess(ble_ms, 30.0, f"BLE latency {ble_ms} ms >= 30 ms")
        finally:
            await router.close_all()
            await server.stop()

    async def test_automatic_retry_on_transient_failure(self):
        attempts = 0

        async def _flaky_ble_peer(env: MeshEnvelope):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise ConnectionError("Simulated transient BLE radio drop")
            return {"recovered": True, "attempts": attempts}

        router = DualTransportRouter(max_retries=3, retry_delay_sec=0.002)
        router.ble.register_gatt_peer("robot_avatar", _flaky_ble_peer)

        env = MeshEnvelope(
            source_device="desktop_host",
            target_device="robot_avatar",
            action="set_pose",
            payload={"pan": 90, "tilt": 95},
            transport="bluetooth",
        )
        reply, _ms = await router.send(env)
        self.assertTrue(reply.payload["recovered"])
        self.assertEqual(attempts, 2)


if __name__ == "__main__":
    unittest.main()
