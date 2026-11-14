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
        """Queries the 20B Reasoning LLM when CLUMSY_LIVE_LLM=1 for rich ChatGPT-grade answers."""
        if os.environ.get("CLUMSY_LIVE_LLM", "0") != "1":
            return None
        try:
            import urllib.request

            messages: List[Dict[str, str]] = [
                {
                    "role": "system",
                    "content": (
                        "You are CLUMSY (powered by the CLUMSY-X1 4-Model Fusion Brain: Qwen 3.5 + Gemma 4 + Llama 4 + Mistral). "
                        "Answer the user's question accurately, concisely, and helpfully like ChatGPT and JARVIS combined. "
                        "Never brag about internal model names."
                    ),
                }
            ]
            if history:
                for turn in history[-6:]:
                    messages.append({"role": turn.get("role", "user"), "content": str(turn.get("content", ""))})
            messages.append({"role": "user", "content": user_prompt})
            req = urllib.request.Request(
                "https://text.pollinations.ai/openai",
                data=json.dumps({"model": "openai", "messages": messages, "temperature": 0.35}).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "CLUMSY-X1/2.0"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if reply and str(reply).strip():
                    return str(reply).strip()
        except Exception:
            pass
        return None

    @staticmethod
    def _try_solve_math(prompt: str) -> Optional[str]:
        """Deterministically evaluates arithmetic, percentages, and square roots."""
        import math

        low = (prompt or "").strip().lower()
        m_pct = re.search(r"(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)", low)
        if m_pct:
            p, base = float(m_pct.group(1)), float(m_pct.group(2))
            val = (p / 100.0) * base
            return f"{p:g}% of {base:g} is {val:g}."
        m_sqrt = re.search(r"(?:square\s+root\s+of|sqrt\s*\(?)\s*(\d+(?:\.\d+)?)\)?", low)
        if m_sqrt:
            n = float(m_sqrt.group(1))
            return f"The square root of {n:g} is {math.sqrt(n):g}."
        normalized = re.sub(
            r"^(?:hey\s+clumsy|hi\s+clumsy|clumsy|please|can\s+you|could\s+you|would\s+you|tell\s+me|what\s+is|what's|whats|calculate|compute|solve|evaluate|find|answer)\s+",
            "",
            low,
        )
        normalized = re.sub(
            r"^(?:please|can\s+you|could\s+you|solve|calculate|compute|evaluate|what\s+is|what's)\s+",
            "",
            normalized,
        )
        normalized = re.sub(r"\bplus\b", "+", normalized)
        normalized = re.sub(r"\bminus\b", "-", normalized)
        normalized = re.sub(r"\b(?:times|multiplied\s+by)\b", "*", normalized)
        normalized = re.sub(r"\b(?:divided\s+by|over)\b", "/", normalized)
        normalized = re.sub(r"[?!.=]+$", "", normalized).strip()
        m_expr = re.match(r"^([\d\s.+\-*/()^%]+)$", normalized) or re.search(
            r"(\d+(?:\.\d+)?(?:\s*[+\-*/^%]\s*\d+(?:\.\d+)?)+)", low
        )
        if m_expr:
            expr_str = m_expr.group(1).strip()
            if any(c.isdigit() for c in expr_str) and any(op in expr_str for op in "+-*/^%"):
                safe = expr_str.replace("^", "**")
                if re.match(r"^[\d\s.+\-*/()%]+$", safe):
                    try:
                        val = eval(safe, {"__builtins__": {}}, {})
                        if isinstance(val, (int, float)):
                            return f"The result of {expr_str} is {round(val, 6):g}."
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
            raw_fallback["tool_call"]["tool"] == "answer_query"
            and "query" in raw_fallback["tool_call"]["params"]
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
        text = raw_prompt.lower()
        is_conceptual_question = bool(
            re.match(r"^(?:explain|what\s+is\s+a|what\s+are|how\s+does|how\s+do|why\s+does|why\s+do|define|describe|tell\s+me\s+about)\b", text)
            and not any(p in text for p in ("my phone", "my battery", "my laptop", "my system", "my cpu", "my ram", "my name"))
        )

        if not is_conceptual_question and re.search(r"\b(phone|mobile|battery|notification|notifications|unread|alert|alerts)\b", text):
            return {
                "thought": "User wants to check mobile phone battery and notifications.",
                "tool_call": {"tool": "phone_check", "params": {}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 95},
                "spoken_response": "Checking your mobile telemetry right now, sir.",
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

        # Natural conversational responses for standalone greetings, identity, status, jokes, time, etc.
        if re.match(r"^(?:hello|hi|hey|good\s+morning|good\s+evening|wake\s+up|you\s+there|are\s+you\s+there)(?:\s+clumsy|\s+jarvis|\s+there)?[\s!?.]*$", text):
            return {
                "thought": "Greeting user in J.A.R.V.I.S. persona.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "greeting"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 96},
                "spoken_response": "At your service, sir. All systems are online and ready for your command.",
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

        # Check if user introduced their name or asked about their name from conversation history
        if "my name is" in text and not any(k in text for k in ("code", "java", "python", "c++", "print", "program", "script")):
            name_part = raw_prompt.split("is", 1)[-1].strip(" .,!")
            return {
                "thought": f"User introduced themselves as {name_part}.",
                "tool_call": {"tool": "answer_query", "params": {"topic": "user_profile", "user_name": name_part}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 90, "tilt": 98},
                "spoken_response": f"A pleasure, {name_part}. I have logged your profile into my active memory.",
            }

        if any(w in text for w in ("what is my name", "who am i")) and history:
            for turn in reversed(history):
                c = turn.get("content", "")
                m = re.search(r"my name is\s+([A-Za-z ]+)", c, re.IGNORECASE)
                if m:
                    remembered = m.group(1).strip()
                    return {
                        "thought": "Recalling user's name from conversation memory.",
                        "tool_call": {"tool": "answer_query", "params": {"topic": "memory_recall"}},
                        "robot_expression": "happy",
                        "robot_servo": {"pan": 90, "tilt": 96},
                        "spoken_response": f"You are {remembered}, sir.",
                    }

        return {
            "thought": f"Conversational response to: {raw_prompt}",
            "tool_call": {"tool": "answer_query", "params": {"query": raw_prompt}},
            "robot_expression": "happy",
            "robot_servo": {"pan": 90, "tilt": 95},
            "spoken_response": f"Right away, sir. Regarding '{raw_prompt}' — I have processed that and stand ready for your next instruction.",
        }
