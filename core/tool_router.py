"""DESKBOT Semantic Tool-Calling & Dynamic Plugin Router (Stage 5).

Provides:
- `validate_against_schema`: strict JSON Schema validator (type, required,
  properties, additionalProperties, enum, minimum, maximum, minLength, default).
- `ToolSpec` & `ToolRegistry`: schema-validated tool registration and execution.
- `PluginLoader`: dynamic discovery and hot-reload of modules in `plugins/`.
- `ShortcutIntentMatcher`: zero-latency regex shortcut matcher for common commands.
"""

import copy
from dataclasses import dataclass, field
import importlib.util
import logging
from pathlib import Path
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("ToolRouter")


class SchemaValidationError(ValueError):
    """Raised when tool call arguments fail JSON Schema validation."""


_TYPE_MAP = {
    "object": dict,
    "string": str,
    "boolean": bool,
    "array": list,
}


def _check_type(val: Any, expected: str, path: str) -> None:
    if expected == "integer":
        if isinstance(val, bool) or not isinstance(val, int):
            raise SchemaValidationError(f"{path}: expected integer, got {type(val).__name__}")
        return
    if expected == "number":
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            raise SchemaValidationError(f"{path}: expected number, got {type(val).__name__}")
        return
    py_type = _TYPE_MAP.get(expected)
    if py_type is not None:
        if expected == "object" and not isinstance(val, dict):
            raise SchemaValidationError(f"{path}: expected object, got {type(val).__name__}")
        if not isinstance(val, py_type):
            raise SchemaValidationError(f"{path}: expected {expected}, got {type(val).__name__}")


def validate_against_schema(instance: Any, schema: Dict[str, Any], path: str = "$") -> Any:
    """
    Validates `instance` against `schema` (JSON Schema subset) and returns a
    normalized copy with default values populated.
    """
    data = copy.deepcopy(instance)
    expected_type = schema.get("type")
    if expected_type:
        _check_type(data, expected_type, path)

    if "enum" in schema and data not in schema["enum"]:
        raise SchemaValidationError(f"{path}: value {data!r} not in allowed enum {schema['enum']}")

    if isinstance(data, (int, float)) and not isinstance(data, bool):
        if "minimum" in schema and data < schema["minimum"]:
            raise SchemaValidationError(f"{path}: {data} < minimum {schema['minimum']}")
        if "maximum" in schema and data > schema["maximum"]:
            raise SchemaValidationError(f"{path}: {data} > maximum {schema['maximum']}")

    if isinstance(data, str):
        if "minLength" in schema and len(data) < schema["minLength"]:
            raise SchemaValidationError(f"{path}: string shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            raise SchemaValidationError(f"{path}: string longer than maxLength {schema['maxLength']}")

    if isinstance(data, list) and "items" in schema:
        item_schema = schema["items"]
        data = [validate_against_schema(v, item_schema, f"{path}[{i}]") for i, v in enumerate(data)]

    if isinstance(data, dict):
        props = schema.get("properties", {})
        # Apply defaults before required check
        for prop_name, prop_schema in props.items():
            if prop_name not in data and "default" in prop_schema:
                data[prop_name] = copy.deepcopy(prop_schema["default"])

        for req in schema.get("required", ()):
            if req not in data:
                raise SchemaValidationError(f"{path}: missing required property '{req}'")

        if schema.get("additionalProperties") is False:
            extra = set(data) - set(props)
            if extra:
                raise SchemaValidationError(f"{path}: unexpected properties {sorted(extra)}")

        for k, v in list(data.items()):
            if k in props:
                data[k] = validate_against_schema(v, props[k], f"{path}.{k}")

    return data


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    plugin_source: str = "builtin"


class ToolRegistry:
    """Central registry for schema-validated DESKBOT tools."""

    def __init__(self):
        self._tools: Dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if not spec.name or not isinstance(spec.parameters_schema, dict):
            raise ValueError("Invalid ToolSpec")
        self._tools[spec.name] = spec
        logger.debug("Registered tool '%s' from %s", spec.name, spec.plugin_source)

    def unregister(self, name: str) -> bool:
        return self._tools.pop(name, None) is not None

    def get(self, name: str) -> Optional[ToolSpec]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters_schema,
                "source": t.plugin_source,
            }
            for t in self._tools.values()
        ]

    def execute(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validates `arguments` against the tool's JSON Schema and invokes its handler."""
        spec = self._tools.get(name)
        if spec is None:
            raise KeyError(f"Tool '{name}' is not registered")
        raw_args = {} if arguments is None else arguments
        validated_args = validate_against_schema(raw_args, spec.parameters_schema)
        return spec.handler(validated_args)


class PluginLoader:
    """Dynamically loads and hot-reloads tool plugins from a directory."""

    def __init__(self, registry: ToolRegistry, plugins_dir: Optional[Path] = None):
        self.registry = registry
        project_root = Path(__file__).resolve().parent.parent
        self.plugins_dir = Path(plugins_dir) if plugins_dir else (project_root / "plugins")
        self._mtimes: Dict[Path, float] = {}

    def load_all(self) -> List[str]:
        loaded: List[str] = []
        if not self.plugins_dir.is_dir():
            return loaded
        for py_file in sorted(self.plugins_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            self._load_file(py_file)
            loaded.append(py_file.stem)
        return loaded

    def reload_modified(self) -> List[str]:
        reloaded: List[str] = []
        if not self.plugins_dir.is_dir():
            return reloaded
        for py_file in sorted(self.plugins_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            mtime = py_file.stat().st_mtime
            if self._mtimes.get(py_file) != mtime:
                self._load_file(py_file)
                reloaded.append(py_file.stem)
        return reloaded

    def _load_file(self, py_file: Path) -> None:
        mod_name = f"deskbot_plugin_{py_file.stem}"
        spec = importlib.util.spec_from_file_location(mod_name, py_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load plugin spec from {py_file}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "register_tools"):
            module.register_tools(self.registry)
        self._mtimes[py_file] = py_file.stat().st_mtime


class ShortcutIntentMatcher:
    """Instant regex shortcut matcher for zero-latency voice/text commands."""

    _PATTERNS: List[Tuple[re.Pattern, Callable[[re.Match], Tuple[str, Dict[str, Any]]]]] = [
        (
            re.compile(
                r"\b(?P<verb>open|launch|start)\s+(?P<app>spotify|vs\s*code|vscode|browser|chrome|notepad)"
                r"(?:\s+on\s+(?:my\s+)?(?P<dev>laptop|pc|desktop))?\b",
                re.IGNORECASE,
            ),
            lambda m: (
                "app_launcher",
                {
                    "app_name": {
                        "spotify": "Spotify",
                        "vscode": "VS Code",
                        "vs code": "VS Code",
                        "browser": "Browser",
                        "chrome": "Browser",
                        "notepad": "Notepad",
                    }[re.sub(r"\s+", " ", m.group("app").lower())],
                    "target": "laptop_node"
                    if (m.group("dev") or "").lower() == "laptop"
                    else "desktop_host",
                },
            ),
        ),
        (
            re.compile(
                r"\b(?P<act>play|pause|resume|next|previous|prev)\b.*\b(?:music|song|track|tunes|playlist)\b"
                r"|\b(?:music|song|track|tunes|playlist)\b.*\b(?P<act2>play|pause|resume|next|previous|prev)\b",
                re.IGNORECASE,
            ),
            lambda m: (
                "media_player",
                {
                    "action": {
                        "play": "play",
                        "resume": "play",
                        "pause": "pause",
                        "next": "next",
                        "previous": "prev",
                        "prev": "prev",
                    }[(m.group("act") or m.group("act2")).lower()]
                },
            ),
        ),
        (
            re.compile(r"\b(?:system\s+status|cpu|ram|memory\s+usage|system\s+health)\b", re.IGNORECASE),
            lambda _m: ("system_monitor", {"include_processes": False}),
        ),
    ]

    def match(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        if not text:
            return None
        for pattern, builder in self._PATTERNS:
            m = pattern.search(text)
            if m:
                return builder(m)
        return None
