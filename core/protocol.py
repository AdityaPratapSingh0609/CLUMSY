"""
DESKBOT Robot Communication Protocol
Defines standardized packet formats for controlling the physical robot's
eyes (OLED/LCD), servo motors, and emotion states over Bluetooth/Serial/Wi-Fi.
"""

from dataclasses import dataclass, asdict
from enum import Enum
import json
from typing import Optional


class Expression(str, Enum):
    IDLE = "idle"
    BLINK = "blink"
    HAPPY = "happy"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    CONFUSED = "confused"
    SLEEPY = "sleepy"
    EXCITED = "excited"
    LOVE = "love"
    CODING = "coding"
    WINK = "wink"
    SURPRISED = "surprised"
    FOCUSED = "focused"


class MotorSpeed(str, Enum):
    SLOW = "slow"
    SMOOTH = "smooth"
    FAST = "fast"


@dataclass
class ServoPose:
    pan: int = 90    # 0 to 180 degrees (90 is center)
    tilt: int = 90   # 0 to 180 degrees (90 is horizontal eye-level)
    speed: MotorSpeed = MotorSpeed.SMOOTH


@dataclass
class EyeConfig:
    expression: Expression = Expression.IDLE
    brightness: int = 255  # 0 to 255
    auto_blink: bool = True


@dataclass
class RobotCommandPacket:
    state: str
    eyes: EyeConfig
    servos: ServoPose
    sound_fx: Optional[str] = None

    def to_json(self) -> str:
        data = asdict(self)
        # Convert enums to string values
        data["eyes"]["expression"] = self.eyes.expression.value
        data["servos"]["speed"] = self.servos.speed.value
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> "RobotCommandPacket":
        raw = json.loads(json_str)
        eyes = EyeConfig(
            expression=Expression(raw["eyes"]["expression"]),
            brightness=raw["eyes"].get("brightness", 255),
            auto_blink=raw["eyes"].get("auto_blink", True)
        )
        servos = ServoPose(
            pan=raw["servos"].get("pan", 90),
            tilt=raw["servos"].get("tilt", 90),
            speed=MotorSpeed(raw["servos"].get("speed", "smooth"))
        )
        return cls(
            state=raw["state"],
            eyes=eyes,
            servos=servos,
            sound_fx=raw.get("sound_fx")
        )
