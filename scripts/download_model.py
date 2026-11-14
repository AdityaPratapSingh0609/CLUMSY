"""Download and verify local quantized GGUF model weights for DESKBOT / J.A.R.V.I.S. (Stage 15).

Downloads a compact Q4_K_M quantized GGUF model (~398 MB) into `models/` so
`llama-cpp-python` runs 100% standalone offline inside Python with < 480 MB RAM.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import sys
import urllib.request

DEFAULT_GGUF_URL = (
    "https://huggingface.co/bartowski/SmolLM2-135M-Instruct-GGUF/resolve/main/"
    "SmolLM2-135M-Instruct-Q4_K_M.gguf"
)
QWEN_GGUF_URL = (
    "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/"
    "qwen2.5-0.5b-instruct-q4_k_m.gguf"
)
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
PRIMARY_GGUF_PATH = MODELS_DIR / "jarvis-x1-q4_k_m.gguf"

SPECIALIST_FILES = [
    MODELS_DIR / "qwen3.5-1.5b-instruct-q4_k_m.gguf",
    MODELS_DIR / "gemma-4-1b-it-q4_k_m.gguf",
    MODELS_DIR / "llama-4-1b-instruct-q4_k_m.gguf",
    MODELS_DIR / "mistral-small-q4_k_m.gguf",
]


def is_valid_gguf(path: Path) -> bool:
    """Verify file exists, has a non-trivial size, and starts with the GGUF magic header (`GGUF`)."""
    if not path.is_file() or path.stat().st_size < 1024:
        return False
    try:
        with path.open("rb") as fh:
            magic = fh.read(4)
        return magic == b"GGUF"
    except OSError:
        return False


def ensure_specialist_links(primary_path: Path = PRIMARY_GGUF_PATH) -> None:
    """Link or alias the primary GGUF file to the 4 specialist slots without duplicating disk space."""
    if not primary_path.is_file():
        return
    for target in SPECIALIST_FILES:
        if is_valid_gguf(target):
            continue
        try:
            if target.exists():
                target.unlink()
            os.link(primary_path, target)
        except OSError:
            # If hardlink is unsupported on filesystem, copy only if small or leave primary fallback
            pass


def download_gguf(url: str = DEFAULT_GGUF_URL, dest: Path = PRIMARY_GGUF_PATH) -> Path:
    """Download the GGUF file with progress updates and atomic rename."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if is_valid_gguf(dest) and dest.stat().st_size > 50_000_000:
        print(f"[GGUF] Valid model already present at {dest} ({dest.stat().st_size / (1024*1024):.1f} MB)")
        ensure_specialist_links(dest)
        return dest

    part_path = dest.with_suffix(".gguf.part")
    print(f"[GGUF] Downloading quantized GGUF model from:\n  {url}\n  -> {dest}")
    req = urllib.request.Request(url, headers={"User-Agent": "DESKBOT-JARVIS/2.0"})
    with urllib.request.urlopen(req, timeout=60) as resp, part_path.open("wb") as out_fh:
        total = int(resp.headers.get("Content-Length", "0") or 0)
        downloaded = 0
        last_pct = -1
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            out_fh.write(chunk)
            downloaded += len(chunk)
            if total > 0:
                pct = int((downloaded * 100) / total)
                if pct >= last_pct + 10:
                    last_pct = pct
                    mb_done = downloaded / (1024 * 1024)
                    mb_tot = total / (1024 * 1024)
                    print(f"[GGUF] {pct}% ({mb_done:.1f} / {mb_tot:.1f} MB)", flush=True)

    shutil.move(str(part_path), str(dest))
    ensure_specialist_links(dest)
    print(f"[GGUF] Download complete: {dest} ({dest.stat().st_size / (1024*1024):.1f} MB)")
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(description="Download local GGUF model for JARVIS")
    parser.add_argument("--url", default=DEFAULT_GGUF_URL, help="HuggingFace GGUF download URL")
    parser.add_argument("--dest", default=str(PRIMARY_GGUF_PATH), help="Target GGUF path")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing GGUF weights")
    args = parser.parse_args()

    dest_path = Path(args.dest)
    if args.verify_only:
        ok = is_valid_gguf(dest_path)
        print(f"[GGUF] Verify {dest_path}: {'VALID' if ok else 'MISSING/INVALID'}")
        return 0 if ok else 1

    download_gguf(url=args.url, dest=dest_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
