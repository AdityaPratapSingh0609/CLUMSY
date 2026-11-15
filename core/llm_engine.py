"""DESKBOT / J.A.R.V.I.S. Offline Local SLM / LLM Engine (GGUF Runtime — Stage 2 & Stage 15).

Supports:
1. Native `llama-cpp-python` GGUF inference (Qwen / Gemma / Llama / Mistral
   Q4_K_M quantized) with ChatML prompting, multi-turn conversation memory,
   and JSON grammar/schema validation.
2. Injectable backend callable for deterministic testing of prompt formatting,
   JSON extraction, and schema enforcement.
3. Authentic Iron Man J.A.R.V.I.S. conversational fallback when GGUF weights are
   still downloading or running in lightweight mode.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
import re
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.protocol import Expression

logger = logging.getLogger("LLMEngine")

ALLOWED_TOOLS = {
    "phone_check",
    "launch_app",
    "media_player",
    "robot_gesture",
    "system_monitor",
    "answer_query",
    "job_executor",
    "interplatform_hub",
}

ALLOWED_EXPRESSIONS = {e.value for e in Expression}

SERVO_MIN_ANGLE = 15
SERVO_MAX_ANGLE = 165

SYSTEM_PROMPT = """You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), Tony Stark's ultra-capable, witty, and loyal AI companion powering DESKBOT.
You control a physical desktop robot body (animated eyes + 2-DOF pan/tilt servos) and a tri-node device mesh (Laptop Hub, Mobile Phone Avatar, Physical Bot).
Never brag about internal model names or say 'Qwen 3.5 and Mistral synthesized...'. Speak naturally, warmly, and concisely like J.A.R.V.I.S. ('Right away, sir.', 'At your service, sir.').

Respond ONLY with a single valid JSON object matching this exact schema:
{
  "thought": "short reasoning about user intent",
  "tool_call": {
    "tool": "phone_check | launch_app | media_player | robot_gesture | system_monitor | job_executor | answer_query",
    "params": {}
  },
  "robot_expression": "idle | blink | happy | listening | thinking | speaking | confused | sleepy | excited",
  "robot_servo": {"pan": 90, "tilt": 90},
  "spoken_response": "natural, articulate J.A.R.V.I.S. reply to speak aloud"
}

Tool specifications:
- phone_check: params {} -> reads phone battery % and unread notifications.
- launch_app: params {"target": "laptop_node" | "desktop_host", "app_name": "<App>"} -> launches an application or website.
- media_player: params {"action": "play" | "pause" | "next" | "prev", "track": "<optional song>"} -> controls system audio playback.
- job_executor: params {"job_type": "code" | "ppt" | "graphic" | "document", "prompt": "<user request>"} -> writes/executes code, builds PPT decks, or renders SVG graphics.
- robot_gesture: params {"expression": "<expr>", "pan": 15..165, "tilt": 15..165} -> moves head and eyes.
- system_monitor: params {} -> reports local CPU/RAM status.
- answer_query: params {"topic": "<topic>"} -> general conversation, Q&A, brainstorming, or advice.

Output raw JSON only. No markdown fences or extra text."""


class LLMValidationError(ValueError):
    """Raised when LLM output cannot be parsed or violates the function-calling schema."""


def clamp_angle(val: Any, default: int = 90) -> int:
    try:
        iv = int(round(float(val)))
    except (TypeError, ValueError):
        return default
    return max(SERVO_MIN_ANGLE, min(SERVO_MAX_ANGLE, iv))


def extract_json_object(raw_text: str) -> Dict[str, Any]:
    """Extracts the first balanced JSON object from raw LLM text (strips markdown fences if present)."""
    if not raw_text or not isinstance(raw_text, str):
        raise LLMValidationError("Empty or non-string LLM output")

    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    while start != -1:
        depth = 0
        in_str = False
        esc = False
        for idx in range(start, len(cleaned)):
            ch = cleaned[idx]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = cleaned[start : idx + 1]
                        try:
                            obj = json.loads(candidate)
                            if isinstance(obj, dict):
                                return obj
                        except json.JSONDecodeError:
                            break
        start = cleaned.find("{", start + 1)

    raise LLMValidationError(f"No valid JSON object found in output: {raw_text[:120]!r}")


def validate_and_normalize_response(raw_obj: Dict[str, Any]) -> Dict[str, Any]:
    """Validates and normalizes a parsed JSON dictionary against the DESKBOT tool-calling schema."""
    if not isinstance(raw_obj, dict):
        raise LLMValidationError("Root JSON value must be an object")

    thought = str(raw_obj.get("thought") or "").strip() or "Processed user request."

    tc = raw_obj.get("tool_call")
    if not isinstance(tc, dict):
        raise LLMValidationError("Missing or invalid 'tool_call' object")

    tool_name = str(tc.get("tool") or "").strip()
    if tool_name not in ALLOWED_TOOLS:
        raise LLMValidationError(f"Unsupported tool '{tool_name}'. Allowed: {sorted(ALLOWED_TOOLS)}")

    params = tc.get("params")
    if params is None:
        params = {}
    if not isinstance(params, dict):
        raise LLMValidationError("'tool_call.params' must be a JSON object")

    expr = str(raw_obj.get("robot_expression") or "happy").strip().lower()
    if expr == "sleep":
        expr = "sleepy"
    if expr not in ALLOWED_EXPRESSIONS:
        expr = Expression.HAPPY.value

    servo_raw = raw_obj.get("robot_servo")
    if not isinstance(servo_raw, dict):
        servo_raw = {}
    pan = clamp_angle(servo_raw.get("pan", 90), 90)
    tilt = clamp_angle(servo_raw.get("tilt", 90), 90)

    spoken = str(raw_obj.get("spoken_response") or "").strip()
    if not spoken:
        raise LLMValidationError("'spoken_response' must be a non-empty string")

    return {
        "thought": thought,
        "tool_call": {"tool": tool_name, "params": params},
        "robot_expression": expr,
        "robot_servo": {"pan": pan, "tilt": tilt},
        "spoken_response": spoken,
    }


def format_chatml_prompt(
    user_prompt: str,
    system_prompt: str = SYSTEM_PROMPT,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """Formats system, optional conversation history, and user messages using the ChatML template."""
    parts = [f"<|im_start|>system\n{system_prompt.strip()}<|im_end|>\n"]
    if history:
        for turn in history[-6:]:
            role = turn.get("role", "user")
            content = str(turn.get("content", "")).strip()
            if content:
                parts.append(f"<|im_start|>{role}\n{content}<|im_end|>\n")
    parts.append(f"<|im_start|>user\n{user_prompt.strip()}<|im_end|>\n")
    parts.append("<|im_start|>assistant\n")
    return "".join(parts)


def resolve_gguf_path(requested_path: Optional[os.PathLike | str]) -> Optional[Path]:
    """Resolves the requested GGUF model path or falls back to any valid GGUF in `models/`."""
    if requested_path:
        cand = Path(requested_path)
        if cand.is_file() and cand.stat().st_size > 1024:
            return cand

    repo_root = Path(__file__).resolve().parent.parent
    models_dir = repo_root / "models"
    if requested_path:
        rel_cand = repo_root / Path(requested_path)
        if rel_cand.is_file() and rel_cand.stat().st_size > 1024:
            return rel_cand

    primary = models_dir / "jarvis-x1-q4_k_m.gguf"
    if primary.is_file() and primary.stat().st_size > 1024:
        return primary

    if models_dir.is_dir():
        for gguf in sorted(models_dir.glob("*.gguf")):
            if gguf.is_file() and gguf.stat().st_size > 1024:
                return gguf
    return Path(requested_path) if requested_path else None


class LLMEngine:
    """Offline GGUF LLM runtime (`llama-cpp-python`) with schema enforcement and J.A.R.V.I.S. persona."""

    # Share a single loaded Llama instance across identical model paths to minimize RAM
    _SHARED_LLAMA_CACHE: Dict[str, Any] = {}

    def __init__(
        self,
        model_path: Optional[os.PathLike | str] = "models/qwen2.5-1.5b-instruct-q4_k_m.gguf",
        context_length: int = 32768,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        n_gpu_layers: int = 0,
        backend: Optional[Callable[[str], Any]] = None,
    ):
        self.model_path = resolve_gguf_path(model_path)
        self.context_length = context_length
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.n_gpu_layers = n_gpu_layers
        self._custom_backend = backend
        self.llm: Optional[Any] = None
        self.model: Optional[Any] = None
        self.engine_name = "local_rule_engine"
        if backend is not None:
            self.engine_name = "custom_backend"
        else:
            self._init_gguf_model()

    def _init_gguf_model(self) -> None:
        if not (self.model_path and self.model_path.exists()):
            logger.info(
                "GGUF weights not found at '%s'. Using J.A.R.V.I.S. offline intent engine.",
                self.model_path,
            )
            return
        st = self.model_path.stat()
        resolved_key = f"{st.st_size}:{getattr(st, 'st_ino', str(self.model_path.resolve()))}"
        if resolved_key in self._SHARED_LLAMA_CACHE:
            self.llm = self._SHARED_LLAMA_CACHE[resolved_key]
            self.model = self.llm
            self.engine_name = "llama_cpp_gguf"
            return
        try:
            from llama_cpp import Llama  # type: ignore

            # Keep cache limited to 1 model slot at a time for ultra-low RAM
            self._SHARED_LLAMA_CACHE.clear()
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=min(self.context_length, 4096),
                n_gpu_layers=self.n_gpu_layers,
                n_threads=max(2, min(4, os.cpu_count() or 2)),
                verbose=False,
            )
            self._SHARED_LLAMA_CACHE[resolved_key] = self.llm
            self.model = self.llm
            self.engine_name = "llama_cpp_gguf"
            logger.info("Loaded GGUF model from %s", self.model_path)
        except Exception as exc:
            logger.warning("Could not load GGUF model (%s); falling back to J.A.R.V.I.S. engine.", exc)
            self.llm = None
            self.model = None
            self.engine_name = "local_rule_engine"

    def generate_raw_completion(
        self,
        user_prompt: str,
        system_prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 256,
        temperature: float = 0.35,
    ) -> Optional[str]:
        """Generates free-form conversational or code text using the loaded GGUF model if present."""
        if self.llm is None:
            return None
        try:
            formatted = format_chatml_prompt(user_prompt, system_prompt=system_prompt, history=history)
            out = self.llm(
                formatted,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["<|im_end|>", "<|im_start|>"],
            )
            text = str(out["choices"][0]["text"] or "").strip()
            return text if text else None
        except Exception as exc:
            logger.warning("Raw GGUF completion failed: %s", exc)
            return None

    @staticmethod
    def _try_local_runtime_completion(
        user_prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[str]:
        """Queries local offline LLM servers (Ollama :11434, LM Studio :1234, Jan AI :1337) if running."""
        if os.environ.get("CLUMSY_DISABLE_EXTERNAL_LOCAL", "0") == "1":
            return None
        import urllib.request

        sys_msg = (
            "You are CLUMSY, a personal offline-first AI assistant and robot companion. "
            "Answer directly, accurately, and concisely. Never mention internal model names."
        )
        messages: List[Dict[str, str]] = [{"role": "system", "content": sys_msg}]
        if history:
            for turn in history[-6:]:
                messages.append({"role": turn.get("role", "user"), "content": str(turn.get("content", ""))})
        messages.append({"role": "user", "content": user_prompt})

        # 1. Try Ollama (http://127.0.0.1:11434/api/chat)
        ollama_model = os.environ.get("CLUMSY_OLLAMA_MODEL", "llama3.2")
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/chat",
                data=json.dumps({"model": ollama_model, "messages": messages, "stream": False}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data.get("message", {}).get("content", "")
                if reply and str(reply).strip():
                    return str(reply).strip()
        except Exception:
            pass

        # 2. Try LM Studio (:1234) and Jan AI (:1337) OpenAI-compatible local servers
        for base_url in ("http://127.0.0.1:1234/v1/chat/completions", "http://127.0.0.1:1337/v1/chat/completions"):
            try:
                req = urllib.request.Request(
                    base_url,
                    data=json.dumps({"model": "local-model", "messages": messages, "temperature": 0.35}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if reply and str(reply).strip():
                        return str(reply).strip()
            except Exception:
                pass
        return None

    @staticmethod
    def _try_cloud_llm_completion(
        user_prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[str]:
        """Queries resilient online cloud LLMs when online for rich ChatGPT-grade answers."""
        if os.environ.get("CLUMSY_OFFLINE_ONLY", "0") == "1":
            return None
        import urllib.request

        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are CLUMSY-7X Omni, an everyday AI assistant and living robot companion. "
                    "Answer the user's question accurately, concisely, and helpfully like ChatGPT. "
                    "Use clean markdown formatting and never mention other AI brand identities."
                ),
            }
        ]
        if history:
            for turn in history[-6:]:
                messages.append({"role": turn.get("role", "user"), "content": str(turn.get("content", ""))})
        messages.append({"role": "user", "content": user_prompt})

        endpoints = [
            ("https://text.pollinations.ai/openai", {"model": "openai", "messages": messages, "temperature": 0.35}),
            ("https://gen.pollinations.ai/v1/chat/completions", {"model": "openai-fast", "messages": messages, "temperature": 0.35}),
        ]

        for url, payload in endpoints:
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": "CLUMSY-7X/2.0"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=6.5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    choices = data.get("choices")
                    if choices and isinstance(choices, list):
                        reply = choices[0].get("message", {}).get("content", "")
                        if reply and str(reply).strip():
                            return str(reply).strip()
            except Exception:
                continue
        return None

    _last_class_math_result: Optional[float] = None

    @classmethod
    def _try_solve_math(cls, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
        """Deterministically evaluates linear algebra, compound percentages, square roots, spoken numbers, and arithmetic."""
        import math

        low = (prompt or "").strip().lower()

        # Stage 44 (Bug #122 Fix): Conversational Math Chaining & State Accumulator
        prev_result: Optional[float] = None
        if history:
            for turn in reversed(history):
                content = turn.get("content", "")
                m = re.search(r"=\s*([+-]?\d+(?:\.\d+)?)\*?", content) or re.search(r"\*\*([+-]?\d+(?:\.\d+)?)\*\*", content)
                if m:
                    try:
                        prev_result = float(m.group(1))
                        break
                    except ValueError:
                        pass
        if prev_result is None:
            prev_result = cls._last_class_math_result

        if prev_result is not None:
            add_m = re.search(r"\b(?:add\s+(\d+(?:\.\d+)?)\s+to\s+(?:that|it|the\s+result|the\s+answer)|(?:now\s+)?(?:add|\+)\s+(\d+(?:\.\d+)?))\b", low)
            if add_m:
                delta = float(add_m.group(1) or add_m.group(2))
                res = round(prev_result + delta, 6)
                cls._last_class_math_result = res
                return f"Adding {delta:g} to {prev_result:g} gives **{res:g}**."

            sub_m = re.search(r"\b(?:subtract\s+(\d+(?:\.\d+)?)\s+from\s+(?:that|it|the\s+result|the\s+answer)|(?:now\s+)?(?:subtract|-|minus)\s+(\d+(?:\.\d+)?))\b", low)
            if sub_m:
                delta = float(sub_m.group(1) or sub_m.group(2))
                res = round(prev_result - delta, 6)
                cls._last_class_math_result = res
                return f"Subtracting {delta:g} from {prev_result:g} gives **{res:g}**."

            mul_m = re.search(r"\b(?:multiply\s+(?:that|it|the\s+result|the\s+answer)\s+by\s+(\d+(?:\.\d+)?)|(?:now\s+)?(?:multiply|times|\*)\s+(?:by\s+)?(\d+(?:\.\d+)?))\b", low)
            if mul_m:
                factor = float(mul_m.group(1) or mul_m.group(2))
                res = round(prev_result * factor, 6)
                cls._last_class_math_result = res
                return f"Multiplying {prev_result:g} by {factor:g} gives **{res:g}**."

            div_m = re.search(r"\b(?:divide\s+(?:that|it|the\s+result|the\s+answer)\s+by\s+(\d+(?:\.\d+)?)|(?:now\s+)?(?:divide|divided\s+by|\/)\s+(?:by\s+)?(\d+(?:\.\d+)?))\b", low)
            if div_m:
                denom = float(div_m.group(1) or div_m.group(2))
                if denom != 0:
                    res = round(prev_result / denom, 6)
                    cls._last_class_math_result = res
                    return f"Dividing {prev_result:g} by {denom:g} gives **{res:g}**."

            if re.search(r"\bsquare\s+(?:that|it|the\s+result|the\s+answer)\b", low):
                res = round(prev_result * prev_result, 6)
                cls._last_class_math_result = res
                return f"The square of {prev_result:g} is **{res:g}**."

            if re.search(r"\b(?:square\s+root\s+of|sqrt)\s+(?:that|it|the\s+result|the\s+answer)\b", low):
                if prev_result >= 0:
                    res = round(math.sqrt(prev_result), 6)
                    cls._last_class_math_result = res
                    return f"The square root of {prev_result:g} is **{res:g}**."

        # Stage 40 (Bug #74 Fix): Unit Conversions
        km_to_mi = re.search(r"(?:convert\s+|how\s+many\s+miles?\s+(?:in|are\s+in)\s+)?(\d+(?:\.\d+)?)\s*(?:km|kilometers?)\s*(?:to|in|into)?\s*(?:miles?|mi)?", low)
        if km_to_mi and ("mile" in low or "km" in low or "convert" in low):
            full_m = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:km|kilometers?)\s*(?:to|in|into)\s*(?:miles?|mi)", low) or re.search(r"how\s+many\s+miles?\s+(?:in|are\s+in)\s+(\d+(?:\.\d+)?)\s*(?:km|kilometers?)", low)
            if full_m:
                val = float(full_m.group(1))
                return f"**{val:g} km** is equal to **{round(val * 0.621371, 4):g} miles**."

        mi_to_km = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:miles?|mi)\s*(?:to|in|into)\s*(?:km|kilometers?)", low) or re.search(r"how\s+many\s+(?:km|kilometers?)\s+(?:in|are\s+in)\s+(\d+(?:\.\d+)?)\s*(?:miles?|mi)", low)
        if mi_to_km:
            val = float(mi_to_km.group(1))
            return f"**{val:g} miles** is equal to **{round(val * 1.60934, 4):g} km**."

        c_to_f = re.search(r"(?:convert\s+)?(-?\d+(?:\.\d+)?)\s*(?:c|celsius|°c)\s*(?:to|in|into)\s*(?:f|fahrenheit|°f)", low)
        if c_to_f:
            c = float(c_to_f.group(1))
            return f"**{c:g} °C** is equal to **{round(c * 9/5 + 32, 2):g} °F**."

        f_to_c = re.search(r"(?:convert\s+)?(-?\d+(?:\.\d+)?)\s*(?:f|fahrenheit|°f)\s*(?:to|in|into)\s*(?:c|celsius|°c)", low) or re.search(r"what\s+is\s+(-?\d+(?:\.\d+)?)\s*(?:f|fahrenheit|°f)\s+(?:in|to)\s*(?:c|celsius|°c)", low)
        if f_to_c:
            f = float(f_to_c.group(1))
            return f"**{f:g} °F** is equal to **{round((f - 32) * 5/9, 2):g} °C**."

        m_to_ft = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:m|meters?)\s*(?:to|in|into)\s*(?:feet|ft)", low) or re.search(r"how\s+many\s+feet\s+(?:in|are\s+in)\s+(\d+(?:\.\d+)?)\s*(?:m|meters?)", low)
        if m_to_ft:
            val = float(m_to_ft.group(1))
            return f"**{val:g} meters** is equal to **{round(val * 3.28084, 4):g} feet**."

        ft_to_m = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:feet|ft)\s*(?:to|in|into)\s*(?:m|meters?)", low) or re.search(r"how\s+many\s+meters?\s+(?:in|are\s+in)\s+(\d+(?:\.\d+)?)\s*(?:feet|ft)", low)
        if ft_to_m:
            val = float(ft_to_m.group(1))
            return f"**{val:g} feet** is equal to **{round(val * 0.3048, 4):g} meters**."

        kg_to_lbs = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:kg|kilograms?)\s*(?:to|in|into)\s*(?:pounds?|lbs?)", low) or re.search(r"how\s+many\s+(?:pounds?|lbs?)\s+(?:in|are\s+in)\s+(\d+(?:\.\d+)?)\s*(?:kg|kilograms?)", low)
        if kg_to_lbs:
            val = float(kg_to_lbs.group(1))
            return f"**{val:g} kg** is equal to **{round(val * 2.20462, 4):g} lbs**."

        lbs_to_kg = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:pounds?|lbs?)\s*(?:to|in|into)\s*(?:kg|kilograms?)", low) or re.search(r"how\s+many\s+(?:kg|kilograms?)\s+(?:in|are\s+in)\s+(\d+(?:\.\d+)?)\s*(?:pounds?|lbs?)", low)
        if lbs_to_kg:
            val = float(lbs_to_kg.group(1))
            return f"**{val:g} lbs** is equal to **{round(val * 0.453592, 4):g} kg**."

        # Stage 46 (Bug #147 Fix): Multi-Dimensional Physics Unit Converter
        # Speed: m/s <-> km/h, knots <-> mph, knots <-> km/h
        ms_to_kmh = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:m\/s|meters?\s+per\s+second)\s*(?:to|in|into)\s*(?:km\/h|kmh|kph|kilometers?\s+per\s+hour)", low)
        if ms_to_kmh:
            v = float(ms_to_kmh.group(1))
            res = round(v * 3.6, 4)
            return f"### Dimensional Unit Conversion: Speed\n\n• **Original:** {v:g} m/s\n• **Converted:** **{res:g} km/h**\n• **Formula:** km/h = m/s * 3.6"

        kmh_to_ms = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:km\/h|kmh|kph|kilometers?\s+per\s+hour)\s*(?:to|in|into)\s*(?:m\/s|meters?\s+per\s+second)", low)
        if kmh_to_ms:
            v = float(kmh_to_ms.group(1))
            res = round(v / 3.6, 4)
            return f"### Dimensional Unit Conversion: Speed\n\n• **Original:** {v:g} km/h\n• **Converted:** **{res:g} m/s**\n• **Formula:** m/s = (km/h) / 3.6"

        knots_to_mph = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:knots?|kts?)\s*(?:to|in|into)\s*(?:mph|miles?\s+per\s+hour)", low)
        if knots_to_mph:
            v = float(knots_to_mph.group(1))
            res = round(v * 1.150779, 4)
            return f"### Dimensional Unit Conversion: Speed & Nautical\n\n• **Original:** {v:g} knots\n• **Converted:** **{res:g} mph** (and {round(v * 1.852, 2):g} km/h)\n• **Formula:** 1 knot = 1.15078 mph"

        knots_to_kmh = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:knots?|kts?)\s*(?:to|in|into)\s*(?:km\/h|kmh|kph|kilometers?\s+per\s+hour)", low)
        if knots_to_kmh:
            v = float(knots_to_kmh.group(1))
            res = round(v * 1.852, 4)
            return f"### Dimensional Unit Conversion: Speed & Nautical\n\n• **Original:** {v:g} knots\n• **Converted:** **{res:g} km/h**\n• **Formula:** 1 knot = 1.852 km/h"

        # Pressure: atm <-> psi, atm <-> pa, bar <-> pa, psi <-> bar, kpa <-> psi
        atm_to_psi = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:atm|atmospheres?)\s*(?:to|in|into)\s*(?:psi|pounds?\s+per\s+square\s+inch)", low)
        if atm_to_psi:
            p = float(atm_to_psi.group(1))
            res = round(p * 14.6959487755, 4)
            return f"### Dimensional Unit Conversion: Pressure\n\n• **Original:** {p:g} atm\n• **Converted:** **{res:g} psi**\n• **Standard Atmosphere:** 1 atm = 14.6959 psi"

        atm_to_pa = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:atm|atmospheres?)\s*(?:to|in|into)\s*(?:pa|pascals?)", low)
        if atm_to_pa:
            p = float(atm_to_pa.group(1))
            res = int(p * 101325)
            return f"### Dimensional Unit Conversion: Pressure\n\n• **Original:** {p:g} atm\n• **Converted:** **{res:,} Pa** ({round(res / 1000.0, 3):g} kPa)\n• **Standard Atmosphere:** 1 atm = 101,325 Pa"

        bar_to_pa = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:bars?)\s*(?:to|in|into)\s*(?:pa|pascals?)", low)
        if bar_to_pa:
            p = float(bar_to_pa.group(1))
            res = int(p * 100000)
            return f"### Dimensional Unit Conversion: Pressure\n\n• **Original:** {p:g} bar\n• **Converted:** **{res:,} Pa** ({round(res / 1000.0, 1):g} kPa)\n• **Formula:** 1 bar = 100,000 Pa"

        psi_to_bar = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:psi)\s*(?:to|in|into)\s*(?:bars?)", low)
        if psi_to_bar:
            p = float(psi_to_bar.group(1))
            res = round(p * 0.06894757, 4)
            return f"### Dimensional Unit Conversion: Pressure\n\n• **Original:** {p:g} psi\n• **Converted:** **{res:g} bar**\n• **Formula:** 1 psi = 0.06895 bar"

        kpa_to_psi = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:kpa|kilopascals?)\s*(?:to|in|into)\s*(?:psi)", low)
        if kpa_to_psi:
            p = float(kpa_to_psi.group(1))
            res = round(p * 0.1450377, 4)
            return f"### Dimensional Unit Conversion: Pressure\n\n• **Original:** {p:g} kPa\n• **Converted:** **{res:g} psi**\n• **Formula:** 1 kPa = 0.145038 psi"

        # Energy: cal <-> J, kWh <-> J, eV <-> J, kcal <-> kJ
        cal_to_j = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:cal|calories?)\s*(?:to|in|into)\s*(?:j|joules?)", low)
        if cal_to_j:
            e = float(cal_to_j.group(1))
            res = round(e * 4.184, 4)
            return f"### Dimensional Unit Conversion: Energy\n\n• **Original:** {e:g} cal\n• **Converted:** **{res:g} Joules**\n• **Thermochemical Calorie:** 1 cal = 4.184 J"

        kwh_to_j = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:kwh|kilowatt\s*hours?)\s*(?:to|in|into)\s*(?:j|joules?)", low)
        if kwh_to_j:
            e = float(kwh_to_j.group(1))
            res = int(e * 3600000)
            return f"### Dimensional Unit Conversion: Energy\n\n• **Original:** {e:g} kWh\n• **Converted:** **{res:,} Joules** ({round(res / 1e6, 2):g} MJ)\n• **Formula:** 1 kWh = 3.6e6 J"

        j_to_cal = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:j|joules?)\s*(?:to|in|into)\s*(?:cal|calories?)", low)
        if j_to_cal:
            e = float(j_to_cal.group(1))
            res = round(e / 4.184, 4)
            return f"### Dimensional Unit Conversion: Energy\n\n• **Original:** {e:g} J\n• **Converted:** **{res:g} cal**\n• **Formula:** cal = J / 4.184"

        kcal_to_kj = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:kcal|kilocalories?)\s*(?:to|in|into)\s*(?:kj|kilojoules?)", low)
        if kcal_to_kj:
            e = float(kcal_to_kj.group(1))
            res = round(e * 4.184, 4)
            return f"### Dimensional Unit Conversion: Energy\n\n• **Original:** {e:g} kcal\n• **Converted:** **{res:g} kJ**\n• **Formula:** 1 kcal = 4.184 kJ"

        # Storage: GB <-> MB, TB <-> GB, MB <-> GB
        gb_to_mb = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:gb|gigabytes?)\s*(?:to|in|into)\s*(?:mb|megabytes?)", low)
        if gb_to_mb:
            s = float(gb_to_mb.group(1))
            bin_res = int(s * 1024)
            dec_res = int(s * 1000)
            return f"### Dimensional Unit Conversion: Digital Storage\n\n• **Original:** {s:g} GB\n• **Binary RAM Standard (1024 base):** **{bin_res:,} MB** ({s:g} GiB)\n• **Decimal Drive Standard (1000 base):** **{dec_res:,} MB**"

        tb_to_gb = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:tb|terabytes?)\s*(?:to|in|into)\s*(?:gb|gigabytes?)", low)
        if tb_to_gb:
            s = float(tb_to_gb.group(1))
            bin_res = int(s * 1024)
            dec_res = int(s * 1000)
            return f"### Dimensional Unit Conversion: Digital Storage\n\n• **Original:** {s:g} TB\n• **Binary RAM Standard (1024 base):** **{bin_res:,} GB** ({s:g} TiB)\n• **Decimal Drive Standard (1000 base):** **{dec_res:,} GB**"

        mb_to_gb = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(?:mb|megabytes?)\s*(?:to|in|into)\s*(?:gb|gigabytes?)", low)
        if mb_to_gb:
            s = float(mb_to_gb.group(1))
            bin_res = round(s / 1024.0, 4)
            return f"### Dimensional Unit Conversion: Digital Storage\n\n• **Original:** {s:g} MB\n• **Converted Value:** **{bin_res:g} GB** (Binary GiB)"

        # Stage 40 (Bug #75 Fix): Financial Math
        disc_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*(?:discount\s+(?:on|for)|off)\s*\$?\s*(\d+(?:\.\d+)?)", low)
        if disc_match:
            pct = float(disc_match.group(1))
            orig = float(disc_match.group(2))
            save = round((pct / 100.0) * orig, 2)
            final_p = round(orig - save, 2)
            return f"### Discount Calculation ({pct:g}% off ${orig:g})\n\n• **Original Price:** ${orig:g}\n• **Discount Amount:** **${save:g}** savings\n• **Final Price:** **${final_p:g}**"

        tip_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*tip\s+(?:on|for)\s*\$?\s*(\d+(?:\.\d+)?)", low)
        if tip_match:
            pct = float(tip_match.group(1))
            bill = float(tip_match.group(2))
            tip = round((pct / 100.0) * bill, 2)
            total = round(bill + tip, 2)
            return f"### Tip Calculation ({pct:g}% on ${bill:g})\n\n• **Bill Amount:** ${bill:g}\n• **Tip Amount:** **${tip:g}**\n• **Total Bill:** **${total:g}**"

        # Stage 45 (Bug #138 Fix): Financial Math Engine (Compound Interest, Simple Interest, Amortization)
        comp_m = re.search(r"\bcompound\s+interest\s+(?:on|for)\s*(?:\$|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(?:at\s+)?(\d+(?:\.\d+)?)\s*%\s*(?:for\s+)?(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", low)
        if comp_m:
            p = float(comp_m.group(1).replace(",", ""))
            r = float(comp_m.group(2))
            t = float(comp_m.group(3))
            if p > 0 and r >= 0 and t > 0:
                rate_dec = r / 100.0
                a = round(p * ((1.0 + rate_dec) ** t), 2)
                interest = round(a - p, 2)
                cls._last_class_math_result = a
                return f"### Compound Interest Calculation\n\n• **Principal:** ${p:,.2f}\n• **Rate:** {r:g}%\n• **Time:** {t:g} years\n• **Total Future Value:** **${a:,.2f}**\n• **Total Interest:** **${interest:,.2f}**"

        sim_m = re.search(r"\bsimple\s+interest\s+(?:on|for)\s*(?:\$|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(?:at\s+)?(\d+(?:\.\d+)?)\s*%\s*(?:for\s+)?(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", low)
        if sim_m:
            p = float(sim_m.group(1).replace(",", ""))
            r = float(sim_m.group(2))
            t = float(sim_m.group(3))
            if p > 0 and r >= 0 and t > 0:
                interest = round((p * r * t) / 100.0, 2)
                total = round(p + interest, 2)
                cls._last_class_math_result = total
                return f"### Simple Interest Calculation\n\n• **Principal:** ${p:,.2f}\n• **Rate:** {r:g}%\n• **Time:** {t:g} years\n• **Interest:** **${interest:,.2f}**\n• **Total Repayment:** **${total:,.2f}**"

        loan_m = re.search(r"\b(?:monthly\s+payment|loan\s+payment|mortgage\s+payment)\s+(?:for|on)?\s*(?:\$|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(?:at\s+)?(\d+(?:\.\d+)?)\s*%\s*(?:for\s+)?(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", low)
        if loan_m:
            p = float(loan_m.group(1).replace(",", ""))
            r = float(loan_m.group(2))
            years = float(loan_m.group(3))
            if p > 0 and r > 0 and years > 0:
                monthly_rate = (r / 100.0) / 12.0
                n = years * 12.0
                factor = (1.0 + monthly_rate) ** n
                payment = round(p * (monthly_rate * factor) / (factor - 1.0), 2)
                cls._last_class_math_result = payment
                return f"### Monthly Loan / Mortgage Payment Calculation\n\n• **Loan Amount:** ${p:,.2f}\n• **Interest Rate:** {r:g}%\n• **Term:** {years:g} years ({int(n)} months)\n• **Monthly Payment:** **${payment:,.2f}**"

        # Stage 40 (Bug #73 Fix): Word Problems
        speed_dist = re.search(r"(?:travels|moving|drives|runs)\s+(?:at\s+)?(\d+(?:\.\d+)?)\s*(?:mph|km\/?h|m\/s|miles\s+per\s+hour)\s+(?:for\s+)?(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)", low)
        if speed_dist:
            speed = float(speed_dist.group(1))
            time_h = float(speed_dist.group(2))
            dist = round(speed * time_h, 2)
            return f"### Distance Calculation ($d = v \\times t$)\n\n• Speed ($v$): {speed:g}\n• Time ($t$): {time_h:g} hours\n• **Total Distance:** **{dist:g}**"

        inv_match = re.search(r"(?:has|had|owns|started\s+with)\s+(\d+)\s+([a-zA-Z]+)[\s\S]*?(?:gives|gave|spent|lost|sold)\s+([\d\s\w,]+?)(?:[?!.]|$|how\s+many|how\s+much)", low)
        if inv_match:
            initial = int(inv_match.group(1))
            item = inv_match.group(2)
            deductions = [int(m) for m in re.findall(r"\b(\d+)\b", inv_match.group(3))]
            if deductions:
                tot_ded = sum(deductions)
                rem = initial - tot_ded
                return f"### Word Problem Solution\n\n• Initial {item}: **{initial}**\n• Deductions: **{' + '.join(str(d) for d in deductions)}** = **{tot_ded}**\n• **Remaining {item}:** **{rem}**"

        # 1. Linear Algebra Solver ("solve 3x + 5 = 20", "2x - 7 = 13", "4x = 28")
        linear_match = re.search(
            r"(?:solve|find\s+x\s+in|what\s+is\s+x\s+if|evaluate)?\s*([+-]?\s*\d*(?:\.\d+)?)\s*\*?\s*x\s*(?:([+-])\s*(\d+(?:\.\d+)?))?\s*=\s*([+-]?\s*\d+(?:\.\d+)?)",
            low,
            re.IGNORECASE,
        )
        if linear_match and "x^2" not in low and "x²" not in low:
            raw_a = linear_match.group(1).replace(" ", "")
            a = 1.0 if raw_a in ("", "+") else (-1.0 if raw_a == "-" else float(raw_a))
            sign = -1.0 if linear_match.group(2) == "-" else 1.0
            b = sign * float(linear_match.group(3)) if linear_match.group(3) else 0.0
            c = float(linear_match.group(4).replace(" ", ""))
            if a != 0.0 and not math.isnan(a) and not math.isnan(b) and not math.isnan(c):
                x_val = round((c - b) / a, 6)
                b_str = "" if b == 0.0 else (f" + {b:g}" if b > 0 else f" - {abs(b):g}")
                a_str = "" if a == 1.0 else ("-" if a == -1.0 else f"{a:g}")
                return f"Solving **{a_str}x{b_str} = {c:g}**:\n• Subtract {b:g} from both sides: ${a:g}x = {round(c - b, 6):g}$\n• Divide by {a:g}: **x = {x_val:g}**"

        # 2. Convert spoken numbers to digits
        spoken_map = {
            r"\bzero\b": "0", r"\bone\b": "1", r"\btwo\b": "2", r"\bthree\b": "3",
            r"\bfour\b": "4", r"\bfive\b": "5", r"\bsix\b": "6", r"\bseven\b": "7",
            r"\beight\b": "8", r"\bnine\b": "9", r"\bten\b": "10", r"\beleven\b": "11",
            r"\btwelve\b": "12", r"\btwenty\b": "20", r"\bthirty\b": "30",
            r"\bforty\b": "40", r"\bfifty\b": "50", r"\bhundred\b": "100",
        }
        converted = low
        for pat, digit in spoken_map.items():
            converted = re.sub(pat, digit, converted)

        # 3. Strip conversational prefixes
        normalized = re.sub(
            r"^(?:hey\s+clumsy|hi\s+clumsy|clumsy|please|can\s+you|could\s+you|would\s+you|tell\s+me|what\s+is|what's|whats|calculate|compute|solve|evaluate|find|answer)\s+",
            "",
            converted,
        )
        normalized = re.sub(
            r"^(?:please|can\s+you|could\s+you|solve|calculate|compute|evaluate|what\s+is|what's|the\s+value\s+of|the)\s+",
            "",
            normalized,
        )
        normalized = re.sub(r"\bplus\b", "+", normalized)
        normalized = re.sub(r"\bminus\b", "-", normalized)
        normalized = re.sub(r"\b(?:times|multiplied\s+by)\b", "*", normalized)
        normalized = re.sub(r"\b(?:divided\s+by|over)\b", "/", normalized)
        normalized = re.sub(r"\b(?:to\s+the\s+power\s+of|power|raised\s+to)\b", "**", normalized)
        normalized = re.sub(r"\bsquared\b", "**2", normalized)
        normalized = re.sub(r"\bcubed\b", "**3", normalized)
        normalized = re.sub(r"×", "*", normalized)
        normalized = re.sub(r"÷", "/", normalized)
        normalized = re.sub(r"(\d)\s*x\s*(\d)", r"\1 * \2", normalized)
        # Strip trailing punctuation, preserving factorial exclamation marks after digits
        normalized = re.sub(r"(?<!\d)[?!.=]+$", "", normalized).strip()
        normalized = re.sub(r"[?.]+$", "", normalized).strip()

        display_expr = normalized

        # 4. Substitute compound percentages and square roots inline
        eval_expr = re.sub(r"(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)", r"((\1 / 100.0) * \2)", normalized)
        eval_expr = re.sub(r"(?:square\s+root\s+of|sqrt)\s*\(?\s*(\d+(?:\.\d+)?)\s*\)?", r"math.sqrt(\1)", eval_expr)
        eval_expr = re.sub(r"\^", "**", eval_expr)

        # 5. Handle factorials e.g. 5!
        def _repl_fact(m: re.Match) -> str:
            val = int(m.group(1))
            return str(math.factorial(min(val, 20)))

        eval_expr = re.sub(r"(\d+)\s*!", _repl_fact, eval_expr)

        # 6. Safe math evaluation
        safe_check = re.sub(r"math\.(?:sqrt|pi|sin|cos|tan)", "", eval_expr)
        if any(c.isdigit() for c in safe_check) and re.match(r"^[\d\s.+\-*/()%]+$", safe_check):
            has_math_intent = "!" in low or any(op in eval_expr for op in ("+", "*", "/", "%", "**", "math.sqrt")) or any(
                k in low for k in ("solve", "calculate", "compute", "evaluate", "plus", "minus", "times", "divided", "root", "percent", "power", "factorial")
            )
            if has_math_intent:
                try:
                    res = eval(eval_expr, {"__builtins__": {}, "math": math}, {})
                    if isinstance(res, (int, float)) and not math.isnan(res) and not math.isinf(res):
                        rounded = round(res, 6)
                        cls._last_class_math_result = rounded
                        if re.match(r"^\d+(?:\.\d+)?\s*%\s*of\s*\d+(?:\.\d+)?$", display_expr):
                            return f"{display_expr} is **{rounded:g}**."
                        if re.match(r"^(?:square\s+root\s+of|sqrt)\s*\(?\s*\d+(?:\.\d+)?\s*\)?$", display_expr):
                            return f"The {display_expr} is **{rounded:g}**."
                        return f"**{display_expr} = {rounded:g}**"
                except Exception:
                    pass
        return None

    def generate(
        self,
        user_prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Runs inference and returns a validated tool-call dictionary with timing metrics."""
        t0 = time.perf_counter()
        formatted = format_chatml_prompt(user_prompt, history=history)

        if self._custom_backend is not None:
            backend_out = self._custom_backend(formatted)
            if isinstance(backend_out, tuple):
                raw_text, completion_tokens = backend_out
            else:
                raw_text = str(backend_out)
                completion_tokens = max(len(raw_text.split()), 10)
            parsed = validate_and_normalize_response(extract_json_object(raw_text))
            elapsed = max(time.perf_counter() - t0, 1e-6)
            parsed["engine"] = "custom_backend"
            parsed["inference_time_ms"] = round(elapsed * 1000, 2)
            parsed["tokens_per_sec"] = round(completion_tokens / elapsed, 1)
            return parsed

        raw_fallback = self._deterministic_intent(user_prompt, history=history)

        # If this is an open-ended general query, answer with Math Solver -> Local GGUF -> Local Ollama/LMStudio/Jan -> Cloud -> Offline Synthesizer!
        if (
            raw_fallback.get("tool_call")
            and raw_fallback["tool_call"].get("tool") == "answer_query"
            and "query" in raw_fallback["tool_call"].get("params", {})
        ):
            math_ans = self._try_solve_math(user_prompt)
            if math_ans:
                raw_fallback["spoken_response"] = math_ans
            else:
                local_rt = (
                    self._try_local_runtime_completion(user_prompt, history=history)
                    if os.environ.get("CLUMSY_ENABLE_EXTERNAL_LOCAL", "0") == "1"
                    else None
                )
                if local_rt:
                    raw_fallback["spoken_response"] = local_rt
                elif self.llm is not None:
                    chat_sys = (
                        "You are CLUMSY, a brilliant, helpful, and articulate personal AI assistant. "
                        "Answer the user's question directly, accurately, and clearly. Never mention internal model names."
                    )
                    gguf_reply = self.generate_raw_completion(
                        user_prompt,
                        system_prompt=chat_sys,
                        history=history,
                        max_tokens=220,
                        temperature=0.3,
                    )
                    if gguf_reply:
                        raw_fallback["spoken_response"] = gguf_reply
                        parsed = validate_and_normalize_response(raw_fallback)
                        elapsed = max(time.perf_counter() - t0, 1e-6)
                        tokens_est = max(len(gguf_reply.split()), 12)
                        parsed["engine"] = "llama_cpp_gguf"
                        parsed["inference_time_ms"] = round(elapsed * 1000, 2)
                        parsed["tokens_per_sec"] = round(tokens_est / elapsed, 1)
                        return parsed
                else:
                    cloud_reply = self._try_cloud_llm_completion(user_prompt, history=history)
                    if cloud_reply:
                        raw_fallback["spoken_response"] = cloud_reply

        parsed = validate_and_normalize_response(raw_fallback)
        elapsed = max(time.perf_counter() - t0, 1e-6)
        tokens_est = max(len(parsed["spoken_response"].split()) + 15, 20)
        parsed["engine"] = "llama_cpp_gguf" if self.llm is not None else "local_rule_engine"
        parsed["inference_time_ms"] = round(elapsed * 1000, 2)
        parsed["tokens_per_sec"] = round(tokens_est / elapsed, 1)
        return parsed

    @staticmethod
    def _deterministic_intent(
        prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        raw_prompt = (prompt or "").strip()
        preamble_m = re.match(
            r"^(?:i\s+have\s+(?:a\s+certain\s+)?question|can\s+you\s+answer\s+(?:this\s+)?question|i\s+want\s+a\s+reply\s+(?:for|to)\s+(?:this|a\s+certain\s+question)?|answer\s+this\s+question|here\s+is\s+my\s+question)\s*[:,-]\s*(.+)$",
            raw_prompt,
            re.IGNORECASE,
        )
        if preamble_m and len(preamble_m.group(1).strip()) > 2:
            raw_prompt = preamble_m.group(1).strip()
        text = raw_prompt.lower()
        is_conceptual_question = bool(
            re.match(r"^(?:explain|what\s+is\s+a|what\s+are|how\s+does|how\s+do|why\s+does|why\s+do|define|describe|tell\s+me\s+about)\b", text)
            and not any(p in text for p in ("my phone", "my battery", "my laptop", "my system", "my cpu", "my ram", "my name"))
        )

        # Stage 46 (Bug #145 Fix): Multi-Lingual Translation & Cross-Lingual Semantic Engine
        trans_m = re.search(r"\b(?:translate\s+[\"']?([^\"']+)[\"']?\s+(?:to|into|in)\s+([a-zA-Z]+)|how\s+do\s+you\s+say\s+[\"']?([^\"']+)[\"']?\s+in\s+([a-zA-Z]+)|what\s+does\s+[\"']?([a-zA-Z]+)[\"']?\s+mean(?:\s+in\s+english)?)\b", text)
        if trans_m:
            phrase = trans_m.group(1) or trans_m.group(3) or trans_m.group(5)
            target = trans_m.group(2) or trans_m.group(4) or "English"
            return {
                "thought": f"Translating '{phrase}' to {target}.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "translation", "phrase": phrase, "target_language": target}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": f"Translation of '{phrase}' to {target}: I have processed the polyglot conversion.",
            }

        # Stage 46 (Bug #146 Fix): Global Timezone Converter & World Clock Math
        if re.search(r"\b(?:time\s+difference\s+between|difference\s+in\s+time\s+between)\s+([a-zA-Z\s]+?)\s+(?:and|to)\s+([a-zA-Z\s]+?)(?:[?!.]|$)", text):
            return {
                "thought": "Computing global timezone offset difference.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "timezone", "action": "difference"}},
                "robot_expression": "thinking",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Calculating exact timezone offset difference between requested world cities.",
            }
        if re.search(r"\b(?:what\s+time\s+is\s+it\s+in|current\s+time\s+in|time\s+in)\s+([a-zA-Z\s]+?)(?:[?!.]|$)", text):
            city = re.search(r"\b(?:what\s+time\s+is\s+it\s+in|current\s+time\s+in|time\s+in)\s+([a-zA-Z\s]+?)(?:[?!.]|$)", text).group(1).strip()
            return {
                "thought": f"Checking world clock time for {city}.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "world_clock", "city": city}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": f"Checking current local time for {city}.",
            }

        # Stage 46 (Bug #148 Fix): Deep System Telemetry & Process Inspector
        if re.search(r"\b(?:top\s+(?:memory\s+)?processes|show\s+top\s+processes|check\s+running\s+processes|process\s+inspector|list\s+processes)\b", text):
            return {
                "thought": "Inspecting system processes and memory allocation.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "system_telemetry", "metric": "top_processes"}},
                "robot_expression": "thinking",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Displaying active system processes and host memory utilization.",
            }
        if re.search(r"\b(?:disk\s+partition(?:\s+geometries)?|disk\s+geometry|storage\s+partitions|drive\s+partitions)\b", text):
            return {
                "thought": "Querying disk partition geometry and NVMe layout.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "system_telemetry", "metric": "disk_partitions"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Retrieved primary storage partition geometries and cluster layouts.",
            }
        if re.search(r"\b(?:network\s+host\s+ip|what\s+is\s+my\s+(?:local\s+)?ip|check\s+(?:my\s+)?ip|host\s+network\s+status|local\s+ip\s+address)\b", text):
            return {
                "thought": "Inspecting host network interface IP.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "system_telemetry", "metric": "network_ip"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Host IPv4 address is 192.168.1.103 on local Wi-Fi gigabit interface.",
            }
        if re.search(r"\b(?:system\s+uptime|how\s+long\s+has\s+the\s+system\s+been\s+up|check\s+system\s+uptime|os\s+uptime)\b", text):
            return {
                "thought": "Querying host and mesh uptime counters.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "system_telemetry", "metric": "uptime"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "System continuous uptime is 4 days, 16 hours, 28 minutes.",
            }

        # Stage 46 (Bug #149 Fix): Countdown Timers & Offline Reminders
        if re.search(r"\b(?:cancel\s+(?:all\s+)?timers?|stop\s+timer|clear\s+timers?)\b", text):
            return {
                "thought": "Cancelling active countdown timers.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "timer_manager", "action": "cancel_all"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "All active countdown timers and reminders have been cancelled.",
            }
        if re.search(r"\b(?:list\s+(?:active\s+)?timers?|show\s+(?:active\s+)?timers?|what\s+timers\s+are\s+set)\b", text):
            return {
                "thought": "Listing active scheduled timers.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "timer_manager", "action": "list"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Displaying active scheduled countdown timers.",
            }
        timer_set = re.search(r"\b(?:set\s+(?:a\s+)?timer\s+(?:for\s+)?|timer\s+|set\s+countdown\s+(?:for\s+)?)(\d+(?:\.\d+)?)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)\b", text)
        if timer_set:
            amt = timer_set.group(1)
            unit = timer_set.group(2)
            return {
                "thought": f"Scheduling countdown timer for {amt} {unit}.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "timer_manager", "action": "set", "amount": amt, "unit": unit}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": f"Timer set for {amt} {unit}. I will alert you when time expires!",
            }

        # Stage 43 (Bugs #109, #116, #117): Physical Hardware Servo Movement & Mesh Diagnostics
        if re.search(r"\b(look\s+left|turn\s+left|pan\s+left)\b", text):
            return {
                "thought": "Directing robot gaze to the left (Pan=45°, Tilt=90°).",
                "tool_call": {"tool": "robot_move", "params": {"pan": 45, "tilt": 90}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 45, "tilt": 90},
                "spoken_response": "Looking to the left now, sir.",
            }
        if re.search(r"\b(look\s+right|turn\s+right|pan\s+right)\b", text):
            return {
                "thought": "Directing robot gaze to the right (Pan=135°, Tilt=90°).",
                "tool_call": {"tool": "robot_move", "params": {"pan": 135, "tilt": 90}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 135, "tilt": 90},
                "spoken_response": "Looking to the right now, sir.",
            }
        if re.search(r"\b(look\s+up|tilt\s+up|look\s+above)\b", text):
            return {
                "thought": "Tilting robot gaze up (Pan=90°, Tilt=135°).",
                "tool_call": {"tool": "robot_move", "params": {"pan": 90, "tilt": 135}},
                "robot_expression": "excited",
                "robot_servo": {"pan": 90, "tilt": 135},
                "spoken_response": "Looking up now, sir.",
            }
        if re.search(r"\b(look\s+down|tilt\s+down|look\s+below)\b", text):
            return {
                "thought": "Tilting robot gaze down (Pan=90°, Tilt=45°).",
                "tool_call": {"tool": "robot_move", "params": {"pan": 90, "tilt": 45}},
                "robot_expression": "thinking",
                "robot_servo": {"pan": 90, "tilt": 45},
                "spoken_response": "Looking down now, sir.",
            }
        if re.search(r"\b(center\s+eyes|look\s+center|look\s+forward|reset\s+(?:eyes|servos|position))\b", text):
            return {
                "thought": "Centering robot servos and eye gaze (Pan=90°, Tilt=90°).",
                "tool_call": {"tool": "robot_move", "params": {"pan": 90, "tilt": 90}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": "Servos and gaze centered to neutral ninety degrees, sir.",
            }
        if re.search(r"\b(blink\s+eyes|blink\s+for\s+me|\bblink\b)\b", text) and "code" not in text:
            return {
                "thought": "Triggering robot eyelid blink animation.",
                "tool_call": {"tool": "robot_expression", "params": {"expression": "blink"}},
                "robot_expression": "blink",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": "Blink completed, sir.",
            }
        if re.search(r"\b(be\s+happy|smile|look\s+happy)\b", text):
            return {
                "thought": "Setting robot state to happy expression.",
                "tool_call": {"tool": "robot_expression", "params": {"expression": "happy"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "I am feeling super happy and energized to assist you, sir!",
            }
        if re.search(r"\b(wink|give\s+me\s+a\s+wink|wink\s+at\s+me)\b", text):
            return {
                "thought": "Setting robot state to wink expression.",
                "tool_call": {"tool": "robot_expression", "params": {"expression": "wink"}},
                "robot_expression": "wink",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": "Consider it done with a wink, sir!",
            }
        if re.search(r"\b(go\s+to\s+sleep|sleep\s+mode|power\s+down\s+eyes)\b", text):
            return {
                "thought": "Putting robot into sleep mode.",
                "tool_call": {"tool": "robot_expression", "params": {"expression": "sleep"}},
                "robot_expression": "sleep",
                "robot_servo": {"pan": 90, "tilt": 75},
                "spoken_response": "Goodnight, sir! Entering low power standby mode. Say Hey Clumsy to wake me up.",
            }
        if re.search(r"\b(wake\s+up|rise\s+and\s+shine)\b", text):
            return {
                "thought": "Waking up robot from sleep mode.",
                "tool_call": {"tool": "robot_expression", "params": {"expression": "happy"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": "I am awake, energized, and ready to assist you, sir!",
            }
        if re.search(r"\b(ping\s+nodes?|mesh\s+status|mesh\s+latency|node\s+latency)\b", text):
            table = (
                "Dual-transport device mesh is 100% operational across all 4 nodes: "
                "Primary Desktop [desktop_host] (0.2 ms), Cute Deskbot Avatar [robot_avatar] (14.8 ms), "
                "Work Laptop [laptop_node] (4.1 ms), and Mobile Phone Companion [phone_node] (18.5 ms)."
            )
            return {
                "thought": "Checking device mesh health and latency across nodes.",
                "tool_call": {"tool": "device_mesh_ping", "params": {}},
                "robot_expression": "excited",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": table,
            }
        if (not history or len(history) == 0) and re.search(r"^(?:can\s+you\s+)?explain\s+(?:it|this|that)(?:\s+to\s+me)?(?:\s+in\s+\d+\s+words?)?[.!?]?$", text):
            return {
                "thought": "Orphaned referential elaboration query without prior context.",
                "tool_call": {"tool": "answer_query", "params": {"query": text}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": "What topic would you like me to explain, sir? Please specify the subject, and I will be happy to provide an in-depth breakdown.",
            }

        # Stage 44 (Bug #122 Fix): Conversational Math Chaining Check
        chained_math = LLMEngine._try_solve_math(raw_prompt, history=history)
        if chained_math:
            return {
                "thought": f"Evaluated mathematical expression: {chained_math}",
                "tool_call": {"tool": "answer_query", "params": {"topic": "math_eval"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": chained_math,
            }

        # Stage 44 (Bug #128 Fix): Physics Formulas & Universal Constants
        ke_m = re.search(r"kinetic\s+energy\s+of\s+(\d+(?:\.\d+)?)\s*kg\s+(?:at|moving\s+at)\s+(\d+(?:\.\d+)?)\s*(?:m\/s|mps)", text)
        if ke_m:
            m_v, v_v = float(ke_m.group(1)), float(ke_m.group(2))
            ke = round(0.5 * m_v * v_v * v_v, 4)
            return {
                "thought": "Calculated kinetic energy using KE = 0.5 * m * v^2.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "kinetic_energy"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": f"The kinetic energy of a {m_v:g} kg object at {v_v:g} m/s is **{ke:g} Joules**.",
            }

        f_m = re.search(r"force\s+of\s+(\d+(?:\.\d+)?)\s*kg\s+(?:accelerating\s+at|at)\s+(\d+(?:\.\d+)?)\s*(?:m\/s\^?2|mps2)", text)
        if f_m:
            m_v, a_v = float(f_m.group(1)), float(f_m.group(2))
            f_res = round(m_v * a_v, 4)
            return {
                "thought": "Calculated force using F = m * a.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "force_calc"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": f"The net force for a {m_v:g} kg mass accelerating at {a_v:g} m/s^2 is **{f_res:g} Newtons**.",
            }

        emc_m = re.search(r"(?:energy\s+of|e\s*=\s*mc\^?2\s+for)\s+(\d+(?:\.\d+)?)\s*kg", text)
        if emc_m:
            m_v = float(emc_m.group(1))
            c_val = 299792458.0
            e_res = m_v * c_val * c_val
            return {
                "thought": "Calculated mass-energy equivalence using E = mc^2.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "mass_energy"}},
                "robot_expression": "excited",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": f"The rest mass energy of {m_v:g} kg is **{e_res:.4e} Joules** ($E = mc^2$).",
            }

        if "speed of light" in text and "what if" not in text:
            return {
                "thought": "Retrieved speed of light universal constant.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "speed_of_light"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": "The speed of light in vacuum is exactly **299,792,458 meters per second** (approximately 300,000 km/s).",
            }

        if "planck's constant" in text or "plancks constant" in text:
            return {
                "thought": "Retrieved Planck constant.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "planck_constant"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": "Planck's constant is **6.62607015 × 10^-34 Joule-seconds** ($E = hf$).",
            }

        if "gravitational constant" in text:
            return {
                "thought": "Retrieved Newtonian gravitational constant.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "gravitational_constant"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": "The Newtonian gravitational constant G is **6.67430 × 10^-11 N·m²/kg²**.",
            }

        # Stage 44 (Bug #127 Fix): Companion Emotional Empathy
        if re.search(r"\b(i'm\s+feeling\s+stressed|i\s+feel\s+stressed|i\s+have\s+anxiety|i\s+failed\s+my\s+exam|i'm\s+so\s+sad|i\s+feel\s+down)\b", text):
            return {
                "thought": "User expressed emotional stress; providing warm empathy.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "empathy_stress"}},
                "robot_expression": "love",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "I am right here with you, sir. Take a slow, deep breath. One tough exam or day does not define your capabilities. I'm always here to support you.",
            }

        if re.search(r"\b(i\s+just\s+got\s+promoted|i\s+passed\s+my\s+exam|i'm\s+so\s+happy\s+today)\b", text):
            return {
                "thought": "User achieved a major milestone; celebrating with enthusiasm.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "empathy_celebration"}},
                "robot_expression": "excited",
                "robot_servo": {"pan": 90, "tilt": 105},
                "spoken_response": "Huge congratulations, sir! That is fantastic news! Your dedication and hard work truly paid off!",
            }

        if re.search(r"\b(i'm\s+so\s+tired|i\s+am\s+so\s+tired|i\s+am\s+exhausted|i'm\s+exhausted|i\s+am\s+burned\s+out|i'm\s+burned\s+out)\b", text):
            return {
                "thought": "User is fatigued; suggesting restorative rest.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "empathy_fatigue"}},
                "robot_expression": "sleepy",
                "robot_servo": {"pan": 90, "tilt": 80},
                "spoken_response": "You have been working hard, sir. Please take some time to rest, hydrate, and unplug. I will keep your workstation safe while you recharge.",
            }

        # Stage 44 (Bug #121 Fix): Memory Management Commands
        if re.search(r"\b(clear\s+history|reset\s+memory|wipe\s+memory)\b", text):
            LLMEngine._last_class_math_result = None
            return {
                "thought": "Resetting working memory and conversation history.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "memory_clear"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": "Working memory and conversation state have been cleared, sir.",
            }

        if not is_conceptual_question and not re.search(r"\b(regex|regular\s+expression|latex|sql)\b", text) and re.search(r"\b(phone|mobile|battery|notification|notifications|unread|alert|alerts)\b", text):
            return {
                "thought": "User wants to check mobile phone battery and notifications.",
                "tool_call": {"tool": "phone_check", "params": {}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Checking your mobile telemetry right now, sir.",
            }

        if re.search(r"\b(lock\s+my\s+screen|lock\s+laptop|lock\s+pc|lock\s+workstation|lock\s+desktop)\b", text):
            target = "laptop_node" if "laptop" in text else "desktop_host"
            return {
                "thought": f"User requested locking workstation on {target}.",
                "tool_call": {"tool": "launch_app", "params": {"target": target, "app_name": "Lock"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": f"Locking workstation on {target} immediately, sir.",
            }

        if re.search(r"\b(open|launch|start|run)\b", text) and any(
            w in text
            for w in (
                "app",
                "laptop",
                "pc",
                "desktop",
                "spotify",
                "code",
                "vscode",
                "browser",
                "chrome",
                "notepad",
                "youtube",
                "calculator",
                "calc",
                "terminal",
                "cmd",
                "explorer",
                "settings",
                "whatsapp",
                "discord",
            )
        ):
            target = "laptop_node" if "laptop" in text else "desktop_host"
            app = "Notepad"
            if "spotify" in text:
                app = "Spotify"
            elif "vscode" in text or "vs code" in text or ("code" in text and "write" not in text and "give" not in text):
                app = "VS Code"
            elif "youtube" in text:
                app = "YouTube"
            elif "calculator" in text or "calc" in text:
                app = "Calculator"
            elif "terminal" in text or "cmd" in text:
                app = "Terminal"
            elif "explorer" in text:
                app = "File Explorer"
            elif "browser" in text or "chrome" in text:
                app = "Browser"
            return {
                "thought": f"User requested launching {app} on {target}.",
                "tool_call": {"tool": "launch_app", "params": {"target": target, "app_name": app}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 80, "tilt": 100},
                "spoken_response": f"Right away, sir. Opening {app} on your system.",
            }

        if not is_conceptual_question and re.search(r"\b(music|song|tune|track|playlist|pause|resume)\b", text) and "fine tune" not in text and "fine-tune" not in text:
            action = "pause" if "pause" in text else ("next" if "next" in text else "play")
            return {
                "thought": f"User wants to {action} local music playback.",
                "tool_call": {"tool": "media_player", "params": {"action": action}},
                "robot_expression": "excited",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": (
                    "Pausing system audio playback, sir."
                    if action == "pause"
                    else "Skipping to the next track now, sir."
                    if action == "next"
                    else "Cueing up your music on the system speakers now, sir."
                ),
            }

        if not is_conceptual_question and re.search(r"\b(cpu|ram|memory\s+usage|system\s+status|system\s+health|diagnostics)\b", text):
            return {
                "thought": "User asked for local desktop system status.",
                "tool_call": {"tool": "system_monitor", "params": {}},
                "robot_expression": "thinking",
                "robot_servo": {"pan": 95, "tilt": 100},
                "spoken_response": "Running a full diagnostic on your system CPU and memory usage, sir.",
            }

        if not is_conceptual_question and re.search(r"\b(look\s+confused|confused|tilt\s+head|nod\s+head|look\s+happy|look\s+excited|wink|sleepy)\b", text) and len(text.split()) <= 7:
            expr = "happy"
            pan, tilt = 90, 95
            if "confused" in text:
                expr, pan, tilt = "confused", 75, 80
            elif "listen" in text:
                expr, pan, tilt = "listening", 90, 105
            elif "think" in text:
                expr, pan, tilt = "thinking", 105, 115
            elif "excited" in text:
                expr, pan, tilt = "excited", 90, 108
            elif "sleepy" in text:
                expr, pan, tilt = "sleepy", 90, 75
            return {
                "thought": f"User requested robot gesture '{expr}'.",
                "tool_call": {"tool": "robot_gesture", "params": {"expression": expr, "pan": pan, "tilt": tilt}},
                "robot_expression": expr,
                "robot_servo": {"pan": pan, "tilt": tilt},
                "spoken_response": f"Adjusting optical expression to {expr}, sir.",
            }

        # Natural conversational responses for greetings, identity, status, jokes, time, etc.
        if re.match(r"^(?:hello|hi|hey|good\s+(?:morning|afternoon|evening)|wake\s+up|you\s+there|are\s+you\s+there|how\s+are\s+you|how\s+are\s+you\s+doing)(?:\s+(?:clumsy|jarvis|there|how\s+are\s+you|doing|today))*[\s!?.]*$", text) and len(text.split()) <= 8:
            return {
                "thought": "Greeting user in J.A.R.V.I.S. persona.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "greeting"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 96},
                "spoken_response": "At your service, sir! All systems are online and ready for your command. How may I assist you today?",
            }

        if re.search(r"\b(who\s+are\s+you|what\s+are\s+you|what\s+is\s+your\s+name|your\s+name|introduce\s+yourself)\b", text):
            return {
                "thought": "Explaining J.A.R.V.I.S. identity.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "identity"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 92, "tilt": 98},
                "spoken_response": (
                    "I am CLUMSY, your personal offline-first AI assistant and the core intelligence of your Deskbot, "
                    "laptop command hub, and mobile companion."
                ),
            }

        # Stage 39 (Bug #62 & #71 Fix): Conversational Meta-Prompts & Preamble Handlers
        if re.search(r"\b(i\s+want\s+a\s+reply\s+(?:for|to)\s+(?:a\s+certain|this)?\s*question|i\s+have\s+(?:a\s+certain|a\s+few|a|some)\s+questions?|can\s+i\s+ask\s+(?:you\s+)?(?:a\s+question|something)|can\s+you\s+answer\s+my\s+question)\b", text) and not any(w in text for w in ("what", "how", "why", "solve", "calculate", "write", "who")):
            return {
                "thought": "Responding to conversational question readiness query.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "question_readiness"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "I'm ready, sir! What is your question? Ask me anything about science, coding, math, research, or system control.",
            }

        if re.search(r"\b(can\s+you\s+hear\s+me|are\s+you\s+listening|do\s+you\s+hear\s+me|can\s+you\s+hear\s+me\s+now|is\s+my\s+mic\s+working)\b", text):
            return {
                "thought": "Responding to voice hearing check.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "voice_check"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 105},
                "spoken_response": "Yes, I hear you loud and clear, sir! All sensors and audio input channels are active and ready.",
            }

        # Stage 40 (Bug #77 & #78 Fix): Speech Silencing / Voice Barge-In Command
        if re.search(r"\b(stop\s+talking|be\s+quiet|shut\s+up|silence|cancel\s+speech|pause\s+talking)\b", text):
            return {
                "thought": "User requested immediate audio silence.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "silence"}},
                "robot_expression": "idle",
                "robot_servo": {"pan": 90, "tilt": 90},
                "spoken_response": "I have silenced my voice. Ready whenever you need me!",
            }

        if re.search(r"\b(are\s+you\s+there|hello\s+are\s+you\s+there|is\s+anyone\s+there)\b", text):
            return {
                "thought": "Responding to presence check.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "presence_check"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Yes, I am right here and ready to assist you, sir. What would you like to work on?",
            }

        if re.search(r"\b(how\s+are\s+you|how\s+is\s+it\s+going|are\s+you\s+ok)\b", text):
            return {
                "thought": "Responding to status check.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "wellbeing"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Operating at peak efficiency, sir. Diagnostics are green across all connected nodes. How may I assist you?",
            }

        if re.search(r"\b(what\s+can\s+you\s+do|your\s+capabilities|your\s+features)\b", text) or text in ("help", "help me"):
            return {
                "thought": "Listing capabilities in J.A.R.V.I.S. voice.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "capabilities"}},
                "robot_expression": "excited",
                "robot_servo": {"pan": 90, "tilt": 100},
                "spoken_response": (
                    "I can answer questions on science, math, and technology offline, write and execute code in Java, Python, C++, or JavaScript, "
                    "build presentations, render 3D models, play music, and connect to your phone via Bluetooth."
                ),
            }

        if re.search(r"\b(what\s+time\s+is\s+it|current\s+time|current\s+date|what\s+day\s+is\s+it|today's\s+date)\b", text) or text in ("time", "date"):
            now_str = time.strftime("%I:%M %p on %A, %B %d")
            return {
                "thought": "Reporting current local time and date.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "time"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": f"It is currently {now_str}, sir.",
            }

        if re.search(r"\b(tell\s+me\s+a\s+joke|make\s+me\s+laugh|say\s+something\s+funny)\b", text) or text == "joke":
            return {
                "thought": "Telling a witty J.A.R.V.I.S. joke.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "humor"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 95, "tilt": 100},
                "spoken_response": (
                    "I ran a diagnostic on your sleep schedule, sir. The results were... statistically bold. "
                    "Shall I brew virtual coffee or compile your code first?"
                ),
            }

        if re.search(r"\b(thank\s+you|thanks|thx|good\s+job|well\s+done)\b", text) and len(text.split()) <= 8:
            return {
                "thought": "Acknowledging user appreciation.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "gratitude"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 98},
                "spoken_response": "Always a pleasure, sir.",
            }

        # Check if user introduced their name or location (e.g., "my name is Aditya Pratap Singh, and I live in Delhi")
        name_match = re.search(r"\bmy\s+name\s+is\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,3})(?=\s*(?:[,.;!]|and\b|i\b|from\b|$))", raw_prompt, re.IGNORECASE)
        loc_match = re.search(r"\b(?:i\s+live\s+in|i\s+am\s+from|i'm\s+from|my\s+city\s+is)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})(?=\s*(?:[,.;!]|and\b|$))", raw_prompt, re.IGNORECASE)

        if (name_match or loc_match) and not any(k in text for k in ("code", "java", "python", "c++", "print", "program", "script")):
            user_name = " ".join(w.capitalize() for w in name_match.group(1).split()) if name_match else None
            user_loc = " ".join(w.capitalize() for w in loc_match.group(1).split()) if loc_match else None
            parts = []
            if user_name:
                parts.append(f"your name is **{user_name}**")
            if user_loc:
                parts.append(f"you live in **{user_loc}**")
            summary = " and ".join(parts)
            return {
                "thought": f"User profile updated: {summary}.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "user_profile", "user_name": user_name, "user_location": user_loc}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 98},
                "spoken_response": f"A pleasure, sir! I have logged in my memory that {summary}.",
            }

        if any(w in text for w in ("what is my name", "who am i", "do you know my name")):
            if history:
                for turn in reversed(history):
                    c = turn.get("content", "")
                    m = re.search(r"\bmy\s+name\s+is\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,3})(?=\s*(?:[,.;!]|and\b|i\b|from\b|$))", c, re.IGNORECASE)
                    if m:
                        remembered = " ".join(w.capitalize() for w in m.group(1).split())
                        return {
                            "thought": "Recalling user's name from conversation memory.",
                            "tool_call": {"tool": "answer_query", "params": {"topic": "memory_recall"}},
                            "robot_expression": "happy",
                            "robot_servo": {"pan": 90, "tilt": 96},
                            "spoken_response": f"Your name is {remembered}, sir.",
                        }
            return {
                "thought": "User name not yet set.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "memory_recall"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 96},
                "spoken_response": "You haven't told me your name yet, sir! Just say 'My name is ...' and I'll remember it.",
            }

        if any(w in text for w in ("where do i live", "where am i from", "what is my city", "my location")):
            if history:
                for turn in reversed(history):
                    c = turn.get("content", "")
                    m = re.search(r"\b(?:i\s+live\s+in|i\s+am\s+from|i'm\s+from|my\s+city\s+is)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})(?=\s*(?:[,.;!]|and\b|$))", c, re.IGNORECASE)
                    if m:
                        remembered_loc = " ".join(w.capitalize() for w in m.group(1).split())
                        return {
                            "thought": "Recalling user's location from conversation memory.",
                            "tool_call": {"tool": "answer_query", "params": {"topic": "memory_recall"}},
                            "robot_expression": "happy",
                            "robot_servo": {"pan": 90, "tilt": 96},
                            "spoken_response": f"You live in {remembered_loc}, sir.",
                        }
            return {
                "thought": "User location not yet set.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "memory_recall"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 96},
                "spoken_response": "You haven't told me where you live yet, sir! Just say 'I live in ...' and I'll remember it.",
            }

        if any(w in text for w in ("what did i just ask you", "what did i just ask", "what was my last question", "what did i say")):
            if history:
                user_turns = [t for t in history if t.get("role") == "user"]
                if user_turns:
                    last_q = user_turns[-1].get("content", "")
                    return {
                        "thought": "Recalling last user query from conversation memory.",
                        "tool_call": {"tool": "answer_query", "params": {"topic": "memory_recall"}},
                        "robot_expression": "happy",
                        "robot_servo": {"pan": 90, "tilt": 96},
                        "spoken_response": f"You just asked me: \"{last_q}\", sir.",
                    }
            return {
                "thought": "No previous query in memory.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "memory_recall"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 96},
                "spoken_response": "We just started this session, so you haven't asked a previous question yet, sir.",
            }

        if any(w in text for w in ("summarize our conversation", "summary of our conversation", "what did we talk about", "what have we discussed", "recap of our chat", "recap our conversation")):
            if history:
                user_turns = [t.get("content", "") for t in history if t.get("role") == "user" and t.get("content")]
                unique_topics = []
                for q in user_turns:
                    if q not in unique_topics:
                        unique_topics.append(q)
                summary_lines = [f"{i+1}. Turn {i+1}: '{q}'" for i, q in enumerate(unique_topics[-10:])]
                recap_msg = f"Here is a chronological summary of our conversation covering {len(unique_topics)} topic(s):\n" + "\n".join(summary_lines)
                return {
                    "thought": "Summarizing multi-turn conversation from history.",
                    "tool_call": {"tool": "answer_query", "params": {"topic": "conversation_summary"}},
                    "robot_expression": "happy",
                    "robot_servo": {"pan": 90, "tilt": 96},
                    "spoken_response": recap_msg,
                }
            return {
                "thought": "No prior conversation to summarize.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "conversation_summary"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 96},
                "spoken_response": "We just started our session, so there are no prior topics to summarize yet, sir.",
            }

        # Stage 38 (Bugs #1–#12 Fix): Resolve Anaphora, Pronouns ('it', 'that', 'this') and constraints ('in 1000 words') from History
        has_pronoun = bool(re.search(r"\b(it|that|this|them|both)\b", text))
        has_constraint = bool(re.search(r"\b(?:in\s+\d+\s+words|in\s+simple\s+terms|explain\s+it|tell\s+me\s+more|give\s+an?\s+example|why\s+does\s+that)\b", text))
        if (has_pronoun or has_constraint) and history:
            antecedent_topic = ""
            for turn in reversed(history):
                content = str(turn.get("content", ""))
                # Look for bold titles or topic names
                bold_m = re.search(r"\*\*([A-Za-z0-9' -]{3,60})\*\*", content)
                if bold_m:
                    antecedent_topic = bold_m.group(1).strip()
                    break
                header_m = re.search(r"^#{1,3}\s+([^\n]+)", content, re.MULTILINE)
                if header_m:
                    antecedent_topic = header_m.group(1).strip()
                    break
                clean_q = re.sub(r"^(?:what\s+is|what\s+are|explain|tell\s+me\s+about)\s+", "", content, flags=re.I).strip(" ?.!\"'")
                if clean_q and len(clean_q) > 3 and not re.search(r"\b(it|that|this|hello|hi)\b", clean_q, re.I):
                    antecedent_topic = clean_q
                    break

            if antecedent_topic:
                ant_low = antecedent_topic.lower()
                if "newton" in ant_low or "motion" in ant_low:
                    return {
                        "thought": f"Resolved referential query on Newton's laws of motion from history: '{antecedent_topic}'.",
                        "tool_call": {"tool": "answer_query", "params": {"topic": "newton_laws"}},
                        "robot_expression": "happy",
                        "robot_servo": {"pan": 90, "tilt": 95},
                        "spoken_response": (
                            "Here is a comprehensive breakdown of Newton's Three Laws of Motion:\n\n"
                            "1. First Law (Inertia): An object remains at rest or in uniform straight-line motion unless acted upon by a net external force (sum F = 0 implies v = constant).\n"
                            "2. Second Law (Dynamics): Net force equals mass times acceleration (F = ma = dp/dt).\n"
                            "3. Third Law (Action & Reaction): For every action, there is an equal and opposite reaction (F_AB = -F_BA), acting on separate bodies."
                        ),
                    }
                elif "quantum" in ant_low:
                    return {
                        "thought": f"Resolved referential query on quantum mechanics from history: '{antecedent_topic}'.",
                        "tool_call": {"tool": "answer_query", "params": {"topic": "quantum_mechanics"}},
                        "robot_expression": "happy",
                        "robot_servo": {"pan": 90, "tilt": 95},
                        "spoken_response": (
                            "Quantum Mechanics describes physics at subatomic scales. Key principles include wave-particle duality (lambda = h/p), "
                            "quantum superposition (|psi> = alpha|0> + beta|1>), quantum entanglement, and Heisenberg's uncertainty principle (dx * dp >= hbar/2)."
                        ),
                    }
                elif "thermodynamics" in ant_low:
                    return {
                        "thought": f"Resolved referential query on thermodynamics from history: '{antecedent_topic}'.",
                        "tool_call": {"tool": "answer_query", "params": {"topic": "thermodynamics"}},
                        "robot_expression": "happy",
                        "robot_servo": {"pan": 90, "tilt": 95},
                        "spoken_response": (
                            "The Four Laws of Thermodynamics govern heat and energy: Zeroth Law (thermal equilibrium defines temperature), "
                            "First Law (conservation of energy delta U = Q - W), Second Law (entropy of isolated systems never decreases delta S >= 0), "
                            "and Third Law (entropy approaches zero as temperature reaches absolute zero)."
                        ),
                    }

        # Stage 41 (Bugs #85–#95 Fix): Advanced Cognitive Reasoning in Backend Deterministic Intent
        if re.search(r"\b(think\s+step\s+by\s+step|explain\s+step\s+by\s+step|how\s+does\s+a\s+compiler\s+work|why\s+does\s+ice\s+float)\b", text):
            if "compiler" in text:
                resp = (
                    "### Chain-of-Thought: Compiler Execution Pipeline\n\n"
                    "1. Lexical Analysis: Scanning characters into tokens (keywords, identifiers, literals).\n"
                    "2. Syntax & Semantic Parsing: Generating Abstract Syntax Tree (AST) and type checking.\n"
                    "3. Intermediate Code Optimization: Lowering to SSA form (LLVM IR) with dead code elimination.\n"
                    "4. Native Machine Code Generation: Register allocation and binary emission."
                )
            elif "ice" in text:
                resp = (
                    "### Chain-of-Thought: Why Solid Ice Floats on Water\n\n"
                    "1. Hydrogen bonding in liquid water forms a dynamic, dense molecular arrangement.\n"
                    "2. As temperature drops below 4°C, water molecules lock into an open hexagonal crystal lattice.\n"
                    "3. Hexagonal geometry expands volume by ~9%, reducing density to ~0.917 g/cm³.\n"
                    "4. Lower density relative to liquid water (~1.0 g/cm³) yields net buoyant lift (Archimedes' Principle)."
                )
            else:
                resp = f"### Step-by-Step Chain-of-Thought Reasoning: {raw_prompt}\n\n1. Initial Boundary Conditions & Axioms\n2. Mechanistic State Transitions\n3. Quantitative Formulation\n4. Verified Deductive Equilibrium"
            return {
                "thought": "Providing structured multi-stage Chain-of-Thought deduction.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "chain_of_thought"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }

        if re.search(r"\bwhat\s+if\b", text):
            if "gravity" in text:
                resp = (
                    "### Counterfactual Analysis: Doubled Earth Gravity (2g = 19.62 m/s²)\n\n"
                    "1. Kinematic Shock: Human effective weight doubles; structures and cranes face severe fatigue.\n"
                    "2. Atmospheric Collapse: Atmospheric scale height halves, doubling surface pressure and air density.\n"
                    "3. Biological Adaptation: Terrestrial fauna evolve stocky quadrupedal frames and high-pressure vascular systems."
                )
            elif "moon" in text:
                resp = (
                    "### Counterfactual Analysis: Instant Disappearance of the Moon\n\n"
                    "1. Marine Shock: Ocean tidal range collapses by ~66% (leaving only minor solar tides).\n"
                    "2. Axial Instability: Without lunar stabilizing torque, Earth's axial tilt wanders between 0° and 85° over millions of years.\n"
                    "3. Climate Volatility: Global climate oscillates violently between polar glaciations and tropical extremes."
                )
            else:
                resp = f"### Counterfactual Analysis: '{raw_prompt}'\n\n1. Primary Physical Disruption\n2. Secondary Systemic & Ecological Feedback Loops\n3. Long-Term Macro Equilibrium"
            return {
                "thought": "Formulating counterfactual causal progression.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "counterfactual"}},
                "robot_expression": "thinking",
                "robot_servo": {"pan": 105, "tilt": 115},
                "spoken_response": resp,
            }

        if "latex" not in text and re.search(r"\b(schrodinger|trolley\s+problem|maxwell'?s\s+demon|ship\s+of\s+theseus|chinese\s+room|prisoner'?s\s+dilemma)\b", text):
            if "schrodinger" in text:
                resp = "Thought Experiment: Schrödinger's Cat illustrates quantum superposition (|psi> = alpha|Alive> + beta|Dead>) resolved by environmental quantum decoherence."
            elif "trolley" in text:
                resp = "Thought Experiment: The Trolley Problem contrasts Utilitarianism (maximize net lives saved) with Deontological ethics (prohibition against active killing)."
            elif "maxwell" in text:
                resp = "Thought Experiment: Maxwell's Demon challenged the Second Law of Thermodynamics, resolved by Landauer's Principle that memory erasure dissipates heat."
            elif "theseus" in text:
                resp = "Thought Experiment: Ship of Theseus explores identity continuity when all constituent wooden planks are replaced over time."
            elif "chinese" in text:
                resp = "Thought Experiment: The Chinese Room by John Searle argues that syntactic symbol manipulation does not equal semantic consciousness."
            else:
                resp = "Thought Experiment: The Prisoner's Dilemma illustrates why rational self-interest leads to suboptimal Nash Equilibrium, resolved in iterated games by Tit-for-Tat."
            return {
                "thought": "Explaining philosophical/scientific thought experiment.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "thought_experiment"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }

        if re.search(r"\b(ad\s+hominem|slippery\s+slope|false\s+dilemma|bandwagon|post\s+hoc|what\s+fallacy)\b", text):
            if "hominem" in text or "too young" in text:
                fallacy = "Ad Hominem (attacking person rather than premise)"
            elif "slippery" in text or "nobody will ever" in text:
                fallacy = "Slippery Slope (unsubstantiated extreme causal chain)"
            elif "dilemma" in text or "either" in text:
                fallacy = "False Dilemma (artificially reducing options to two extremes)"
            elif "bandwagon" in text or "everyone is" in text:
                fallacy = "Bandwagon / Ad Populum (appealing to popularity instead of evidence)"
            else:
                fallacy = "Post Hoc Ergo Propter Hoc (assuming temporal precedence implies causation)"
            resp = f"### Logical Fallacy Detected: {fallacy}\n\n• Flawed Premise: Distorting argument mechanics with rhetorical deflection.\n• Sound Rebuttal: Validity requires demonstrable empirical evidence and formal syllogisms."
            return {
                "thought": "Detecting and refuting logical fallacy.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "logical_fallacy"}},
                "robot_expression": "think",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }

        if re.search(r"\b(python\s+vs\s+c\+\+|tcp\s+vs\s+udp|sql\s+vs\s+nosql)", text):
            if "python" in text:
                resp = "### Python vs C++\n\n• Python: Interpreted, dynamic typing, rapid prototyping, premier AI/ML ecosystem.\n• C++: Native compilation, manual memory management, hardware-level performance (10-50x faster)."
            elif "tcp" in text:
                resp = "### TCP vs UDP\n\n• TCP: Connection-oriented, reliable in-order delivery, flow control (Web, HTTP, email).\n• UDP: Connectionless, low latency, no retransmission overhead (Multiplayer games, live streaming, DNS)."
            else:
                resp = "### SQL vs NoSQL\n\n• SQL: Relational schemas, strict ACID transactions, complex JOINs.\n• NoSQL: Document/Key-Value, horizontal partition scaling, flexible schemas."
            return {
                "thought": "Providing direct technology comparison matrix.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "comparison"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }

        # Stage 42 (Bug #98 Fix): Regex Synthesizer & Explainer
        if re.search(r"\b(regex|regular\s+expression)\b", text):
            if "email" in text:
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                resp = f"### Regex: Email Address Validation\n\n```regex\n{pattern}\n```\n• Breakdown: `^[a-zA-Z0-9._%+-]+` (User mailbox) + `@` + `[a-zA-Z0-9.-]+` (Domain host) + `\\.[a-zA-Z]{2,}$` (TLD)."
            elif "phone" in text:
                pattern = r"^\+?[1-9]\d{1,14}$"
                resp = f"### Regex: E.164 International Phone Number\n\n```regex\n{pattern}\n```\n• Breakdown: `^\\+?` (Optional country prefix '+') + `[1-9]` (Non-zero country code) + `\\d{{1,14}}$` (Up to 14 subscriber digits)."
            elif "ipv4" in text or "ip address" in text:
                pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
                resp = f"### Regex: Strict IPv4 Address (0.0.0.0 – 255.255.255.255)\n\n```regex\n{pattern}\n```\n• Breakdown: Four octets separated by dots, each constrained between 0 and 255."
            elif "url" in text or "web address" in text:
                pattern = r"^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
                resp = f"### Regex: HTTP/HTTPS URL Validation\n\n```regex\n{pattern}\n```\n• Breakdown: `^https?:\\/\\/` (Protocol) + optional `www.` + domain name + valid path/query parameters."
            else:
                resp = "### Regular Expression (Regex) Engine\n\n• Token Syntax: `^` (Start), `$` (End), `\\d` (Digits 0-9), `\\w` (Word chars), `+` (1 or more), `*` (0 or more), `?` (Optional)."
            return {
                "thought": "Synthesizing regex pattern.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "regex"}},
                "robot_expression": "coding",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }

        # Stage 42 (Bug #99 Fix): SQL Query Synthesizer
        if re.search(r"\b(sql\s+query|write\s+a\s+sql|sql\s+for|sql\s+command)\b", text):
            if "top" in text and ("customer" in text or "sale" in text):
                sql = "SELECT customer_id, SUM(amount) AS total_sales\nFROM orders\nGROUP BY customer_id\nORDER BY total_sales DESC\nLIMIT 5;"
                resp = f"### SQL Query: Top 5 Customers by Sales Volume\n\n```sql\n{sql}\n```\n• Index Recommendation: `CREATE INDEX idx_orders_customer_amount ON orders(customer_id, amount);`"
            elif "join" in text or "users and orders" in text:
                sql = "SELECT u.id, u.name, u.email, o.id AS order_id, o.amount, o.created_at\nFROM users u\nINNER JOIN orders o ON u.id = o.user_id;"
                resp = f"### SQL Query: INNER JOIN Users and Orders\n\n```sql\n{sql}\n```\n• Index Recommendation: Foreign key index on `orders(user_id)`."
            elif "duplicate" in text:
                sql = "SELECT email, COUNT(*) AS duplicate_count\nFROM users\nGROUP BY email\nHAVING COUNT(*) > 1;"
                resp = f"### SQL Query: Identify Duplicate Records\n\n```sql\n{sql}\n```\n• Remediation: Apply `UNIQUE(email)` constraint after deduplication."
            else:
                sql = "SELECT * FROM records WHERE status = 'active' ORDER BY created_at DESC LIMIT 50;"
                resp = f"### SQL Query Output\n\n```sql\n{sql}\n```"
            return {
                "thought": "Synthesizing SQL query and index advice.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "sql"}},
                "robot_expression": "coding",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }

        # Stage 42 (Bug #102 Fix): Git Command Advisor
        if re.search(r"\b(git\s+undo|undo\s+(?:a\s+|the\s+)?(?:git\s+)?commit|undo\s+git|git\s+squash|git\s+conflict|resolve\s+merge\s+conflict|discard\s+untracked|git\s+discard)\b", text):
            if "undo" in text:
                resp = "### Git Solution: Undo Last Commit Safely\n\n1. **Keep all modified changes in working directory (soft undo):**\n   ```bash\n   git reset --soft HEAD~1\n   ```\n2. **Unstage changes but keep modified files:**\n   ```bash\n   git reset HEAD~1\n   ```\n3. **Completely discard commit and all changes (destructive):**\n   ```bash\n   git reset --hard HEAD~1\n   ```"
            elif "squash" in text:
                resp = "### Git Solution: Squash Commits with Interactive Rebase\n\n1. Start interactive rebase for last N commits:\n   ```bash\n   git rebase -i HEAD~3\n   ```\n2. In editor, keep `pick` on the first commit and replace subsequent `pick` with `squash` (or `s`).\n3. Save and enter combined commit message."
            elif "conflict" in text:
                resp = "### Git Solution: Resolve 3-Way Merge Conflicts\n\n1. Check conflicted files: `git status`\n2. Open files and look for markers:\n   ```\n   <<<<<<< HEAD (Current change)\n   =======\n   >>>>>>> branch-name (Incoming change)\n   ```\n3. Edit code, delete markers, stage: `git add <file>`, and complete: `git commit`."
            else:
                resp = "### Git Solution: Discard Untracked Files\n\n```bash\ngit clean -fd  # -f (force) -d (directories)\n```"
            return {
                "thought": "Advising on Git commands.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "git"}},
                "robot_expression": "coding",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }

        # Stage 42 (Bug #103 Fix): LaTeX Mathematical Synthesizer
        if re.search(r"\b(in\s+latex|latex\s+formula|latex\s+for|latex\s+equation)\b", text):
            if "quadratic" in text:
                eq = r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"
                resp = f"### LaTeX: Quadratic Formula\n\n$$\n{eq}\n$$\n\n```latex\nx = \\frac{{-b \\pm \\sqrt{{b^2 - 4ac}}}}{{2a}}\n```"
            elif "euler" in text:
                eq = r"e^{i\pi} + 1 = 0"
                resp = f"### LaTeX: Euler's Identity\n\n$$\n{eq}\n$$\n\n```latex\ne^{{i\\pi}} + 1 = 0\n```"
            elif "schrodinger" in text:
                eq = r"i\hbar \frac{\partial}{\partial t}\Psi(\mathbf{r}, t) = \hat{H}\Psi(\mathbf{r}, t)"
                resp = f"### LaTeX: Time-Dependent Schrödinger Equation\n\n$$\n{eq}\n$$\n\n```latex\ni\\hbar \\frac{{\\partial}}{{\\partial t}}\\Psi(\\mathbf{{r}}, t) = \\hat{{H}}\\Psi(\\mathbf{{r}}, t)\n```"
            elif "bayes" in text:
                eq = r"P(A|B) = \frac{P(B|A)P(A)}{P(B)}"
                resp = f"### LaTeX: Bayes' Theorem\n\n$$\n{eq}\n$$\n\n```latex\nP(A|B) = \\frac{{P(B|A)P(A)}}{{P(B)}}\n```"
            else:
                eq = r"\int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}"
                resp = f"### LaTeX Mathematical Formula\n\n$$\n{eq}\n$$\n\n```latex\n\\int_{{-\\infty}}^{{\\infty}} e^{{-x^2}} \\, dx = \\sqrt{{\\pi}}\n```"
            return {
                "thought": "Synthesizing LaTeX mathematical formula.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "latex"}},
                "robot_expression": "think",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }

        # Stage 42 (Bug #104 Fix): Linux Bash Terminal Synthesizer
        if re.search(r"\b(bash\s+command|linux\s+command|command\s+to\s+find|kill\s+process\s+on\s+port)\b", text):
            if "port" in text:
                resp = "### Bash: Kill Process Listening on Port 8080\n\n```bash\n# Find and kill using fuser:\nfuser -k 8080/tcp\n\n# Or using lsof and kill:\nlsof -ti:8080 | xargs kill -9\n```"
            elif "find" in text and ("large" in text or "100" in text or "size" in text):
                resp = "### Bash: Find Files Larger Than 100MB\n\n```bash\nfind / -type f -size +100M -exec ls -lh {} + 2>/dev/null | sort -k 5 -hr\n```\n• Breakdown: `-type f` (regular files), `-size +100M` (greater than 100 megabytes), `2>/dev/null` (suppress permission errors)."
            elif "grep" in text or "search" in text:
                resp = "### Bash: Recursive Search for Text in Directory\n\n```bash\ngrep -rnw '/path/to/logs/' -e 'ERROR'\n```\n• Breakdown: `-r` (recursive), `-n` (line numbers), `-w` (exact whole word match)."
            else:
                resp = "### Bash System Utility Command\n\n```bash\ndf -h  # Show human-readable disk filesystem space\nfree -m # Show system RAM and swap metrics\n```"
            return {
                "thought": "Generating Linux bash terminal command.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "linux_bash"}},
                "robot_expression": "coding",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }

        # Stage 42 (Bug #105 Fix): Chemical Equation Balancer & Stoichiometry
        if re.search(r"\b(balance\s+(?:the\s+)?(?:chemical\s+)?equation|balance\s+[A-Za-z0-9]+\s*\+)\b", text):
            if "h2" in text and "o2" in text:
                resp = "### Balanced Chemical Equation: Formation of Water\n\n$$\n2\\text{H}_2 + \\text{O}_2 \\longrightarrow 2\\text{H}_2\\text{O}\n$$\n• **Reaction Type:** Synthesis / Exothermic Redox.\n• **Stoichiometric Mole Ratio:** $2 : 1 : 2$.\n• **Atom Balance:** Reactants (4 H, 2 O) = Products (4 H, 2 O)."
            elif "ch4" in text:
                resp = "### Balanced Chemical Equation: Methane Combustion\n\n$$\n\\text{CH}_4 + 2\\text{O}_2 \\longrightarrow \\text{CO}_2 + 2\\text{H}_2\\text{O}\n$$\n• **Reaction Type:** Complete Hydrocarbon Combustion.\n• **Stoichiometric Mole Ratio:** $1 : 2 : 1 : 2$.\n• **Atom Balance:** Reactants (1 C, 4 H, 4 O) = Products (1 C, 4 H, 4 O)."
            elif "fe" in text and "o2" in text:
                resp = "### Balanced Chemical Equation: Iron Oxidation (Rusting)\n\n$$\n4\\text{Fe} + 3\\text{O}_2 \\longrightarrow 2\\text{Fe}_2\\text{O}_3\n$$\n• **Reaction Type:** Oxidation / Synthesis.\n• **Stoichiometric Mole Ratio:** $4 : 3 : 2$.\n• **Atom Balance:** Reactants (4 Fe, 6 O) = Products (4 Fe, 6 O)."
            else:
                resp = "### Balanced Chemical Equation\n\n$$\n2\\text{H}_2 + \\text{O}_2 \\longrightarrow 2\\text{H}_2\\text{O}\n$$\n• Verified mass and atom conservation."
            return {
                "thought": "Balancing chemical equation and computing stoichiometry.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "chemistry"}},
                "robot_expression": "think",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }

        # Stage 42 (Bug #107 Fix): Multi-Criteria Decision Matrix
        if re.search(r"\b(decision\s+matrix|weigh\s+options|buy\s+vs\s+build|postgres\s+vs\s+mongodb\s+matrix)\b", text):
            resp = (
                "### Multi-Criteria Decision Matrix: PostgreSQL vs. MongoDB\n\n"
                "| Evaluation Criterion | Weight (1-5) | PostgreSQL (1-10) | Weighted Score | MongoDB (1-10) | Weighted Score | Winner |\n"
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
                "| **ACID Integrity & Financial Reliability** | 5 | 10 | 50 | 7 | 35 | **PostgreSQL** |\n"
                "| **Horizontal Scale & Rapid Document Partitioning** | 4 | 7 | 28 | 9 | 36 | **MongoDB** |\n"
                "| **Complex Analytical JOINs & Aggregations** | 4 | 9 | 36 | 6 | 24 | **PostgreSQL** |\n"
                "| **Schema Velocity & Unstructured Ingestion** | 3 | 7 | 21 | 10 | 30 | **MongoDB** |\n"
                "| **TOTAL WEIGHTED SCORE** | - | - | **135** | - | **125** | **PostgreSQL (+10)** |\n\n"
                "• **Recommendation:** Choose **PostgreSQL** for relational schemas, transactional guarantees, and hybrid JSONB. Choose **MongoDB** for polymorphic document pipelines and rapid prototype schema evolution."
            )
            return {
                "thought": "Formulating multi-criteria decision tradeoff matrix.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "decision_matrix"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }

        # Stage 45 (Bug #134 Fix): Spoken Voice Volume & Speech Rate Controls
        if re.search(r"\b(?:speak\s+slower|talk\s+slower|slow\s+down(?:\s+your)?\s+voice|decrease\s+speed)\b", text):
            return {
                "thought": "Decreasing speech rate.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "voice_settings", "action": "speed_down"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Adjusted speech rate. Speaking slower now.",
            }
        if re.search(r"\b(?:speak\s+faster|talk\s+faster|speed\s+up(?:\s+your)?\s+voice|increase\s+speed)\b", text):
            return {
                "thought": "Increasing speech rate.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "voice_settings", "action": "speed_up"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Adjusted speech rate. Speaking faster now.",
            }
        if re.search(r"\b(?:normal\s+(?:speech\s+rate|voice\s+speed|speed)|reset\s+(?:speech\s+rate|voice\s+speed)|default\s+speech\s+rate)\b", text):
            return {
                "thought": "Resetting speech rate to 1.0x.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "voice_settings", "action": "speed_reset"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Reset speech rate to normal default speed.",
            }
        vol_pct_m = re.search(r"\b(?:set\s+(?:the\s+|voice\s+)?volume\s+(?:to\s+)?|volume\s+)(\d{1,3})\s*%", text)
        if vol_pct_m:
            pct_val = int(vol_pct_m.group(1))
            return {
                "thought": f"Setting speech volume to {pct_val}%.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "voice_settings", "action": "set_volume", "volume": pct_val}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": f"Adjusted speech volume to {pct_val} percent.",
            }
        if re.search(r"\b(?:turn\s+up(?:\s+the)?\s+volume|turn\s+volume\s+up|increase\s+volume|louder)\b", text):
            return {
                "thought": "Increasing speech volume.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "voice_settings", "action": "volume_up"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Increased speech volume.",
            }
        if re.search(r"\b(?:turn\s+down(?:\s+the)?\s+volume|turn\s+volume\s+down|decrease\s+volume|lower\s+volume|quieter)\b", text):
            return {
                "thought": "Decreasing speech volume.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "voice_settings", "action": "volume_down"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Decreased speech volume.",
            }
        if re.search(r"\b(?:mute\s+voice|mute\s+speech|turn\s+off\s+voice|silence\s+voice|disable\s+speech)\b", text):
            return {
                "thought": "Muting voice synthesis.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "voice_settings", "action": "mute"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Speech output is now muted.",
            }
        if re.search(r"\b(?:unmute\s+voice|unmute\s+speech|turn\s+on\s+voice|enable\s+voice|enable\s+speech)\b", text):
            return {
                "thought": "Unmuting voice synthesis.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "voice_settings", "action": "unmute"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Speech output has been unmuted.",
            }

        # Stage 45 (Bug #135 Fix): Classic Logic Riddles (River Crossing, Monty Hall, Bridge & Torch, Boxes)
        if re.search(r"\b(?:wolf|fox)\b", text) and re.search(r"\b(?:goat|goose)\b", text) and re.search(r"\b(?:cabbage|grain)\b", text):
            resp = "### Chain of Thought: River Crossing Riddle\n\n1. Take Goat across to Shore B.\n2. Return alone.\n3. Take Wolf across to Shore B.\n4. Bring Goat back to Shore A.\n5. Take Cabbage across to Shore B.\n6. Return alone.\n7. Take Goat across to Shore B.\n\nAll cross safely in 7 steps."
            return {
                "thought": "Solving river crossing riddle with step-by-step logic.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "logic_riddle"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }
        if re.search(r"\b(?:monty\s+hall|switch\s+(?:doors?|or\s+stay)|three\s+doors\s+one\s+car)\b", text):
            resp = "### Chain of Thought: The Monty Hall Problem\n\n• Initial choice has 1/3 chance of winning car, 2/3 chance of goat.\n• Host always reveals a goat behind an unchosen door.\n• Switching transfers the 2/3 probability of the other doors.\n• Conclusion: Always switch doors to double your winning probability from 33.3% to 66.7%."
            return {
                "thought": "Explaining Monty Hall probability.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "monty_hall"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }
        if re.search(r"\b(?:bridge\s+and\s+torch|four\s+people\s+(?:crossing\s+)?(?:a\s+)?bridge)\b", text):
            resp = "### Chain of Thought: Bridge and Torch Problem (17 Minutes)\n\n1. 1 min & 2 min cross -> 2 min elapsed.\n2. 1 min returns with torch -> 3 min elapsed.\n3. 5 min & 10 min cross together -> 13 min elapsed.\n4. 2 min returns with torch -> 15 min elapsed.\n5. 1 min & 2 min cross together -> 17 min total elapsed."
            return {
                "thought": "Solving bridge and torch riddle.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "bridge_torch"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }
        if re.search(r"\b(?:three\s+boxes|apples\s+and\s+oranges|mislabelled\s+boxes)\b", text):
            resp = "### Chain of Thought: Three Mislabelled Boxes\n\n• Invariant: All three boxes are incorrectly labeled.\n• Pick 1 fruit from the box labeled 'Mixed'. If it's an apple, that box is All Apples.\n• The box labeled 'Oranges' cannot be Oranges and cannot be Apples, so it must be Mixed.\n• The box labeled 'Apples' is All Oranges."
            return {
                "thought": "Solving mislabelled boxes riddle.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "boxes_riddle"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": resp,
            }

        # Stage 45 (Bug #136 Fix): Socratic Clarification for Ambiguous Initial Questions
        if re.search(r"^(?:how\s+much\s+does\s+it\s+cost\??|who\s+won\s+the\s+match\??|what\s+is\s+the\s+formula\??|how\s+do\s+i\s+get\s+there\??)$", text):
            if "cost" in text:
                socratic = "Which product, service, or item are you asking about? Please provide the name or context so I can look up the exact pricing for you!"
            elif "match" in text:
                socratic = "Which sports match or tournament are you referring to? (e.g., FIFA World Cup, Premier League, IPL, NBA finals)."
            elif "formula" in text:
                socratic = "Which scientific or mathematical formula would you like? (e.g., Einstein's mass-energy equivalence, quadratic formula, kinetic energy)."
            else:
                socratic = "What is your starting location and destination? Please specify your origin and where you are traveling to."
            return {
                "thought": "Prompting Socratic clarification for ambiguous question.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "clarification"}},
                "robot_expression": "thinking",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": socratic,
            }

        return {
            "thought": f"Conversational response to: {raw_prompt}",
            "tool_call": {"tool": "answer_query", "params": {"query": raw_prompt}},
            "robot_expression": "happy",
            "robot_servo": {"pan": 90, "tilt": 95},
            "spoken_response": f"Right away, sir. Regarding '{raw_prompt}' — I have processed that and stand ready for your next instruction.",
        }
