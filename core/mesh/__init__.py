"""DESKBOT Mesh Package (Stages 6–8)."""

from core.mesh.device_manager import DeviceMeshManager, DeviceNode
from core.mesh.transport import (
    BluetoothMeshTransport,
    DualTransportRouter,
    LANServiceBeacon,
    LANWebSocketClient,
    LANWebSocketServer,
    MeshEnvelope,
    PacketIntegrityError,
    TransportDeliveryError,
)

__all__ = [
    "DeviceMeshManager",
    "DeviceNode",
    "MeshEnvelope",
    "PacketIntegrityError",
    "TransportDeliveryError",
    "LANWebSocketServer",
    "LANWebSocketClient",
    "LANServiceBeacon",
    "BluetoothMeshTransport",
    "DualTransportRouter",
]
