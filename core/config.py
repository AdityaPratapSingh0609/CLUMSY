"""DESKBOT configuration loader (stdlib only, supports both config.yaml and config.json).

Reads config/config.yaml (or config/config.json), deep-merges it over built-in
defaults, and lets environment variables override single values:
DESKBOT__SECTION__KEY=value (parsed as JSON when possible).
"""

import copy
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_YAML_PATH = PROJECT_ROOT / "config" / "config.yaml"
DEFAULT_JSON_PATH = PROJECT_ROOT / "config" / "config.json"

DEFAULTS: Dict[str, Any] = {
    "project": {"name": "DESKBOT", "version": "0.1.0"},
    "llm": {
        "model_path": "models/qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "context_length": 4096,
        "max_tokens": 512,
        "temperature": 0.3,
        "n_gpu_layers": 0,
    },
    "stt": {"model_size": "tiny.en", "compute_type": "int8", "language": "en", "sample_rate": 16000},
    "tts": {
        "voice_model": "en_US-lessac-medium",
        "sample_rate": 22050,
        "elevenlabs_voice_id": "ZF6FPAbjXT4488VcRRnw",
        "elevenlabs_voice_name": "Amelia",
        "voice_description": "Young and enthusiastic British female voice",
    },
    "wake_word": {"phrase": "hey deskbot", "threshold": 0.7},
    "robot": {
        "serial_port": None,
        "baudrate": 115200,
        "simulate": True,
        "servo_min_angle": 15,
        "servo_max_angle": 165,
    },
    "mesh": {"bluetooth_enabled": True, "lan_enabled": True, "websocket_port": 9120},
    "dashboard": {"host": "127.0.0.1", "port": 8080},
    "plugins": {"directory": "plugins", "hot_reload": True},
}


class ConfigError(Exception):
    pass


def _parse_scalar(raw: str) -> Any:
    val = raw.strip()
    # Strip inline comment outside quotes
    if not (val.startswith('"') or val.startswith("'")):
        if " #" in val:
            val = val.split(" #", 1)[0].strip()
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    low = val.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low in ("null", "none", "~", ""):
        return None
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val


def _load_yaml_stdlib(text: str, source: Path) -> Dict[str, Any]:
    """Minimal stdlib YAML loader for 1- and 2-level mappings (falls back if PyYAML absent)."""
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        if loaded is None:
            return {}
        if not isinstance(loaded, dict):
            raise ConfigError(f"{source} must contain a mapping at top level")
        return loaded
    except ImportError:
        pass

    data: Dict[str, Any] = {}
    current_section: Optional[str] = None
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            raise ConfigError(f"Invalid YAML syntax in {source}:{lineno}: {line!r}")
        indent = len(line) - len(line.lstrip(" "))
        key, _, rest = stripped.partition(":")
        key = key.strip()
        rest = rest.strip()
        if indent == 0:
            if rest == "" or rest.startswith("#"):
                current_section = key
                data.setdefault(current_section, {})
            else:
                current_section = None
                data[key] = _parse_scalar(rest)
        else:
            if current_section is None or not isinstance(data.get(current_section), dict):
                raise ConfigError(f"Unexpected indentation in {source}:{lineno}")
            data[current_section][key] = _parse_scalar(rest)
    return data


def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


class Config:
    """Section/key accessor. Missing file -> defaults; malformed file -> ConfigError."""

    def __init__(self, path: Optional[os.PathLike] = None, env: Optional[Dict[str, str]] = None):
        if path is not None:
            self.path = Path(path)
        elif DEFAULT_YAML_PATH.exists():
            self.path = DEFAULT_YAML_PATH
        else:
            self.path = DEFAULT_JSON_PATH

        data: Dict[str, Any] = {}
        if self.path.exists():
            raw_text = self.path.read_text(encoding="utf-8")
            suffix = self.path.suffix.lower()
            if suffix in (".yaml", ".yml"):
                if raw_text.lstrip().startswith("{"):
                    try:
                        data = json.loads(raw_text)
                    except json.JSONDecodeError as e:
                        raise ConfigError(f"Invalid YAML/JSON in {self.path}: {e}") from e
                else:
                    data = _load_yaml_stdlib(raw_text, self.path)
            else:
                try:
                    data = json.loads(raw_text)
                except json.JSONDecodeError as e:
                    raise ConfigError(f"Invalid JSON in {self.path}: {e}") from e
            if not isinstance(data, dict):
                raise ConfigError(f"{self.path} must contain a top-level mapping/object")
        self._data = _deep_merge(DEFAULTS, data)
        self._apply_env(os.environ if env is None else env)

    def _apply_env(self, env: Dict[str, str]) -> None:
        for name, raw in env.items():
            if not name.startswith("DESKBOT__"):
                continue
            parts = name[len("DESKBOT__") :].lower().split("__")
            if len(parts) != 2:
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError:
                value = raw
            self._data.setdefault(parts[0], {})[parts[1]] = value

    def section(self, name: str) -> Dict[str, Any]:
        return self._data.get(name, {})

    def get(self, section: str, key: str, default: Any = None) -> Any:
        return self.section(section).get(key, default)

    def resolve_path(self, section: str, key: str) -> Path:
        """Resolve a configured relative path against the project root."""
        p = Path(self.get(section, key, ""))
        return p if p.is_absolute() else PROJECT_ROOT / p

    def as_dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self._data)

    def __repr__(self) -> str:
        return f"Config(path={self.path}, sections={sorted(self._data)})"
