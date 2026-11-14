"""Vercel Serverless Function Entrypoint for CLUMSY: your everyday AI."""

from __future__ import annotations

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dashboard.server import DeskbotRequestHandler


class handler(DeskbotRequestHandler):
    """Vercel Python Serverless handler compatible with BaseHTTPRequestHandler."""

    pass
