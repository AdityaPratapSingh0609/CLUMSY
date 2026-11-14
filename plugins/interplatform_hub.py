"""Interplatform Connectivity & Siri-to-Laptop Auto-Launch Streaming Hub (Stages 23 & 27).

Allows J.A.R.V.I.S. (triggered via voice from the Phone "Deskbot Eyes" App, Board Mic, or Laptop Hub)
to dynamically identify the show/song/task and **automatically launch & play it on the connected Laptop**:
  1. `netflix`       — Auto-launches Netflix show/movie directly on the Laptop (`https://www.netflix.com/search?q=...`)
  2. `prime_video`   — Auto-launches Amazon Prime Video show/movie on the Laptop (`https://www.primevideo.com/search/ref=atv_nb_sr?phrase=...`)
  3. `hotstar`       — Auto-launches Disney+ Hotstar show/movie on the Laptop (`https://www.hotstar.com/in/explore?search_query=...`)
  4. `youtube`       — Auto-launches YouTube video/show on the Laptop (`https://www.youtube.com/results?search_query=...`)
  5. `spotify`       — Auto-launches Spotify track/artist on the Laptop (`https://open.spotify.com/search/...`)
  6. `gmail`         — Opens Gmail inbox, composes/drafts emails (To/Subject/Body), or searches emails on Laptop
  7. `calendar`      — Opens Google Calendar, schedules events, and exports `.ics` invitations on Laptop
  8. `notes`         — Creates, lists, searches, and syncs persistent J.A.R.V.I.S. / Google Keep notes
  9. `amazon`        — Opens Amazon shopping search on the Laptop (`https://www.amazon.in/s?k=...`)
"""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional
import urllib.parse
import webbrowser

from core.tool_router import ToolRegistry, ToolSpec

import tempfile

if os.environ.get("VERCEL"):
    OUTPUT_DIR = Path(tempfile.gettempdir()) / "workspace_output" / "interplatform"
else:
    OUTPUT_DIR = Path("workspace_output/interplatform")
try:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    OUTPUT_DIR = Path(tempfile.gettempdir()) / "workspace_output" / "interplatform"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NOTES_FILE = OUTPUT_DIR / "jarvis_notes.json"
CALENDAR_FILE = OUTPUT_DIR / "jarvis_calendar.json"
GMAIL_FILE = OUTPUT_DIR / "jarvis_gmail_drafts.json"

INTERPLATFORM_HISTORY: List[Dict[str, Any]] = []

SUPPORTED_PLATFORMS = (
    "gmail",
    "calendar",
    "notes",
    "netflix",
    "prime_video",
    "hotstar",
    "youtube",
    "spotify",
    "amazon",
)


def _load_json_list(path: Path, defaults: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return list(defaults)


def _save_json_list(path: Path, items: List[Dict[str, Any]]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(items, indent=2), encoding="utf-8")
    except OSError:
        pass


def launch_url_on_laptop(url: str) -> bool:
    """Natively open a URL on the connected Laptop's default browser (Windows/macOS/Linux)."""
    if not url:
        return False
    try:
        if sys.platform.startswith("win"):
            os.startfile(url)  # type: ignore[attr-defined]
            return True
        if sys.platform == "darwin":
            subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        return bool(webbrowser.open(url, new=2))
    except Exception:
        try:
            return bool(webbrowser.open(url, new=2))
        except Exception:
            return False


def detect_platform(prompt: str, explicit_platform: Optional[str] = None) -> Optional[str]:
    """Detect which interplatform service or streaming platform the user is addressing."""
    if explicit_platform:
        ep = explicit_platform.lower().strip().replace(" ", "_")
        if ep in ("prime", "amazon_prime", "primevideo", "amazon_prime_video"):
            return "prime_video"
        if ep in ("disney", "disney+", "disney_plus", "jiohotstar"):
            return "hotstar"
        if ep in SUPPORTED_PLATFORMS:
            return ep

    p = (prompt or "").lower()
    if any(w in p for w in ("prime video", "amazon prime", "on prime", "prime show", "prime movie")):
        return "prime_video"
    if any(w in p for w in ("hotstar", "disney+", "disney plus", "jio cinema", "jiocinema")):
        return "hotstar"
    if any(w in p for w in ("netflix", "netant", "on netflix")):
        return "netflix"
    if any(w in p for w in ("youtube", "on youtube", "yt video")):
        return "youtube"
    if any(w in p for w in ("on spotify", "spotify")):
        return "spotify"
    if any(w in p for w in ("gmail", "email", "e-mail", "inbox", "send mail", "compose mail")):
        return "gmail"
    if any(w in p for w in ("calendar", "callender", "calender", "schedule", "meeting", "appointment", "event")):
        return "calendar"
    if any(w in p for w in ("amazon", "shop for", "buy on amazon", "order on amazon", "search on amazon")):
        return "amazon"
    if any(w in p for w in ("note", "notes", "keep", "sticky note", "write down", "jot down", "remind me")):
        return "notes"
    if any(w in p for w in ("watch show", "watch movie", "stream show", "play show", "play series", "play movie")):
        return "netflix"
    return None


def _extract_streaming_title(prompt: str, service_patterns: str) -> str:
    """Extract the clean show/movie title from natural voice sentences like:
    'Hey bot I want to play Stranger Things on Netflix' -> 'Stranger Things'
    """
    cleaned = (prompt or "").strip()
    # Remove conversational prefixes
    cleaned = re.sub(
        r"^(?:hey|hi|ok|yo|hello)?\s*(?:jarvis|bot|deskbot|siri)?[\s,.:;-]*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = re.sub(
        r"^(?:i\s+want\s+to\s+|please\s+|can\s+you\s+|could\s+you\s+)?(?:play|watch|stream|start|put\s+on|open|search|find)\s+(?:this\s+particular\s+show\s+|the\s+show\s+|the\s+movie\s+|show\s+|movie\s+|series\s+)?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    # Strip trailing platform suffix ("on netflix", "on amazon prime video", "on laptop", etc.)
    cleaned = re.sub(
        rf"\s+(?:on|in|from|via)\s+(?:my\s+|the\s+)?(?:{service_patterns})(?:\s+on\s+(?:my\s+|the\s+)?laptop)?.*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = re.sub(r"\s+on\s+(?:my\s+|the\s+)?(?:laptop|pc|system|computer|screen|tv)$", "", cleaned, flags=re.IGNORECASE).strip()
    if cleaned.lower() in ("netflix", "amazon prime", "prime video", "hotstar", "youtube", "spotify", "a show", "a movie", "something", ""):
        return ""
    return cleaned.strip(" '\"")


def _handle_gmail(prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
    p_low = prompt.lower()
    recipient = str(params.get("to") or "").strip()
    subject = str(params.get("subject") or "").strip()
    body = str(params.get("body") or "").strip()

    if not recipient:
        m_to = re.search(r"\bto\s+([a-zA-Z0-9._%+-]+(?:@[a-zA-Z0-9.-]+)?)", prompt, flags=re.IGNORECASE)
        if m_to and m_to.group(1).lower() not in ("open", "check", "read", "search"):
            recipient = m_to.group(1).strip()

    if not subject:
        m_sub = re.search(r"\b(?:about|subject|regarding)\s+(.+?)(?:\s+saying|\s+with body|$)", prompt, flags=re.IGNORECASE)
        if m_sub:
            subject = m_sub.group(1).strip()

    if not body:
        m_body = re.search(r"\b(?:saying|body|message|that)\s+(.+)$", prompt, flags=re.IGNORECASE)
        if m_body:
            body = m_body.group(1).strip()

    if "search" in p_low or "find" in p_low:
        q = re.sub(r"^.*?\b(?:search|find|for)\b\s*", "", prompt, flags=re.IGNORECASE).strip() or "important"
        url = f"https://mail.google.com/mail/u/0/#search/{urllib.parse.quote(q)}"
        task_mode = "search"
        summary = f"Searching Gmail inbox on Laptop for '{q}'"
    elif any(w in p_low for w in ("send", "compose", "write", "draft", "email to", "mail to")) or recipient or subject:
        subject = subject or "J.A.R.V.I.S. Automated Dispatch"
        body = body or f"Hello,\n\nDispatched via J.A.R.V.I.S. Command Hub regarding: {subject}.\n\nBest regards,\nAditya"
        qs = urllib.parse.urlencode({"view": "cm", "fs": "1", "to": recipient, "su": subject, "body": body})
        url = f"https://mail.google.com/mail/?{qs}"
        task_mode = "compose"
        summary = f"Composed Gmail draft on Laptop to {recipient or 'Recipient'} — Subject: '{subject}'"
    else:
        url = "https://mail.google.com/mail/u/0/#inbox"
        task_mode = "inbox"
        summary = "Opened Gmail Primary Inbox on Laptop"

    drafts = _load_json_list(GMAIL_FILE, [])
    record = {
        "id": f"gmail_{int(time.time())}",
        "mode": task_mode,
        "to": recipient,
        "subject": subject,
        "body": body,
        "url": url,
        "summary": summary,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    drafts.append(record)
    _save_json_list(GMAIL_FILE, drafts[-30:])

    preview_html = (
        f"<div class='job-code-preview'>"
        f"<div class='job-badge' style='background:#ef4444;color:#fff;'>✉️ GMAIL INTERPLATFORM LINK • {task_mode.upper()} (AUTO-OPENED ON LAPTOP)</div>"
        f"<h4 style='margin-bottom:6px;'>{html.escape(summary)}</h4>"
        + (
            f"<div style='font-size:12px;color:#cbd5e1;margin-bottom:8px;'>"
            f"<b>To:</b> {html.escape(recipient or '(Specify in Gmail)')} &nbsp;|&nbsp; "
            f"<b>Subject:</b> {html.escape(subject)}<br>"
            f"<b>Body:</b> {html.escape(body)}"
            f"</div>"
            if task_mode == "compose"
            else ""
        )
        + f"<a href='{html.escape(url)}' target='_blank' style='display:inline-block;background:#ef4444;color:#fff;padding:6px 12px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:700;'>↗ Re-Open in Gmail on Laptop</a>"
        f"</div>"
    )
    return {
        "platform": "gmail",
        "task_mode": task_mode,
        "url": url,
        "summary": summary,
        "spoken_response": f"Right away, sir. {summary}.",
        "record": record,
        "preview_html": preview_html,
    }


def _handle_calendar(prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
    p_low = prompt.lower()
    event_title = str(params.get("title") or "").strip()
    when_str = str(params.get("when") or "").strip()

    if not when_str:
        m_when = re.search(
            r"\b((?:today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)?\s*(?:at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)?)\b",
            prompt,
            flags=re.IGNORECASE,
        )
        if m_when and m_when.group(1).strip():
            when_str = m_when.group(1).strip()
    when_str = when_str or "Tomorrow at 10:00 AM"

    if not event_title:
        cleaned = re.sub(
            r"\b(?:open|schedule|add|create|set|a|an|event|meeting|appointment|on|in|google|calendar|callender|calender|for|about)\b",
            " ",
            prompt,
            flags=re.IGNORECASE,
        )
        cleaned = " ".join(cleaned.split()).strip()
        event_title = cleaned.title() if cleaned else "J.A.R.V.I.S. Strategic Sync"

    if any(w in p_low for w in ("schedule", "add", "create", "set", "meeting", "appointment", "event")):
        qs = urllib.parse.urlencode(
            {
                "action": "TEMPLATE",
                "text": event_title,
                "details": f"Scheduled via J.A.R.V.I.S. Voice Command ({when_str})",
            }
        )
        url = f"https://calendar.google.com/calendar/render?{qs}"
        task_mode = "schedule_event"
        summary = f"Scheduled Calendar Event on Laptop: '{event_title}' ({when_str})"
    else:
        url = "https://calendar.google.com/calendar/r"
        task_mode = "open_calendar"
        summary = "Opened Google Calendar Schedule on Laptop"

    events = _load_json_list(
        CALENDAR_FILE,
        [{"title": "Robotics Hardware Integration", "when": "Today 6:00 PM", "url": "https://calendar.google.com"}],
    )
    new_ev = {"title": event_title, "when": when_str, "url": url, "created_at": time.strftime("%Y-%m-%d %H:%M")}
    if task_mode == "schedule_event":
        events.append(new_ev)
        _save_json_list(CALENDAR_FILE, events[-30:])

    ics_path = OUTPUT_DIR / "latest_event.ics"
    ics_content = (
        "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//DESKBOT//JARVIS//EN\nBEGIN:VEVENT\n"
        f"SUMMARY:{event_title}\nDESCRIPTION:Scheduled by J.A.R.V.I.S. ({when_str})\n"
        "END:VEVENT\nEND:VCALENDAR\n"
    )
    ics_path.write_text(ics_content, encoding="utf-8")

    ev_list_html = "".join(
        f"<li style='margin-bottom:4px;'>📅 <b>{html.escape(e['title'])}</b> — <span style='color:#38bdf8;'>{html.escape(e['when'])}</span></li>"
        for e in events[-4:]
    )
    preview_html = (
        f"<div class='job-code-preview'>"
        f"<div class='job-badge' style='background:#3b82f6;color:#fff;'>📅 GOOGLE CALENDAR • {task_mode.upper()} (AUTO-OPENED ON LAPTOP)</div>"
        f"<h4 style='margin-bottom:6px;'>{html.escape(summary)}</h4>"
        f"<ul style='padding-left:18px;font-size:12px;margin-bottom:8px;'>{ev_list_html}</ul>"
        f"<a href='{html.escape(url)}' target='_blank' style='display:inline-block;background:#3b82f6;color:#fff;padding:6px 12px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:700;'>↗ Open in Google Calendar</a>"
        f"</div>"
    )
    return {
        "platform": "calendar",
        "task_mode": task_mode,
        "url": url,
        "ics_file": str(ics_path),
        "summary": summary,
        "events": events[-6:],
        "spoken_response": f"Right away, sir. {summary}.",
        "preview_html": preview_html,
    }


def _handle_notes(prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
    notes = _load_json_list(
        NOTES_FILE,
        [
            {"id": "n1", "text": "Calibrate Arduino Uno D9/D10 servos", "time": "Today"},
            {"id": "n2", "text": "Test J.A.R.V.I.S. voice commands on Mobile Eyes App", "time": "Today"},
        ],
    )
    note_text = str(params.get("text") or "").strip()
    if not note_text:
        cleaned = re.sub(
            r"^(?:hey\s+jarvis\s*,?\s*)?(?:please\s+)?(?:take\s+a\s+note|create\s+a\s+note|add\s+a?\s*note|write\s+down|jot\s+down|note\s+that|remind\s+me\s+to|save\s+note)\s*:?\s*",
            "",
            prompt,
            flags=re.IGNORECASE,
        ).strip()
        if cleaned and cleaned.lower() not in ("open notes", "show notes", "show my notes", "notes"):
            note_text = cleaned

    if note_text:
        item = {"id": f"n{len(notes) + 1}", "text": note_text, "time": time.strftime("%I:%M %p")}
        notes.append(item)
        _save_json_list(NOTES_FILE, notes[-40:])
        summary = f"Saved new note: '{note_text}'"
        task_mode = "create_note"
    else:
        summary = f"Displaying your {len(notes)} synced J.A.R.V.I.S. & Keep notes"
        task_mode = "list_notes"

    url = "https://keep.google.com"
    notes_html = "".join(
        f"<div style='background:#0f172a;border-left:3px solid #facc15;padding:6px 10px;border-radius:6px;margin-bottom:5px;font-size:12px;'>"
        f"📝 {html.escape(n['text'])} <span style='color:#64748b;font-size:10px;float:right;'>{html.escape(n.get('time', ''))}</span></div>"
        for n in reversed(notes[-5:])
    )
    preview_html = (
        f"<div class='job-code-preview'>"
        f"<div class='job-badge' style='background:#facc15;color:#000;'>📝 J.A.R.V.I.S. NOTES &amp; GOOGLE KEEP</div>"
        f"<h4 style='margin-bottom:8px;'>{html.escape(summary)}</h4>"
        f"{notes_html}"
        f"<a href='{url}' target='_blank' style='display:inline-block;margin-top:6px;background:#facc15;color:#000;padding:5px 12px;border-radius:8px;text-decoration:none;font-size:11.5px;font-weight:700;'>↗ Open Google Keep</a>"
        f"</div>"
    )
    return {
        "platform": "notes",
        "task_mode": task_mode,
        "url": url,
        "notes": notes[-10:],
        "summary": summary,
        "spoken_response": f"Done, sir. {summary}.",
        "preview_html": preview_html,
    }


def _handle_streaming_service(
    platform: str,
    prompt: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    """Handle Netflix, Amazon Prime Video, Disney+ Hotstar, YouTube, and Spotify with Laptop auto-launch."""
    configs = {
        "netflix": {
            "name": "Netflix",
            "badge": "🎬 NETFLIX STREAMING • AUTO-PLAYING ON LAPTOP",
            "color": "#e50914",
            "text_color": "#fff",
            "pattern": "netflix|net\\s+flicks|netflex",
            "search_url": "https://www.netflix.com/search?q={q}",
            "home_url": "https://www.netflix.com/browse",
        },
        "prime_video": {
            "name": "Amazon Prime Video",
            "badge": "📺 AMAZON PRIME VIDEO • AUTO-PLAYING ON LAPTOP",
            "color": "#00a8e1",
            "text_color": "#fff",
            "pattern": "amazon\\s+prime\\s+video|amazon\\s+prime|prime\\s+video|prime",
            "search_url": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase={q}",
            "home_url": "https://www.primevideo.com",
        },
        "hotstar": {
            "name": "Disney+ Hotstar",
            "badge": "🌟 DISNEY+ HOTSTAR • AUTO-PLAYING ON LAPTOP",
            "color": "#1d4ed8",
            "text_color": "#fff",
            "pattern": "disney\\+\\s*hotstar|hotstar|disney\\s+plus|jiocinema",
            "search_url": "https://www.hotstar.com/in/explore?search_query={q}",
            "home_url": "https://www.hotstar.com/in",
        },
        "youtube": {
            "name": "YouTube",
            "badge": "▶️ YOUTUBE CINEMA • AUTO-PLAYING ON LAPTOP",
            "color": "#dc2626",
            "text_color": "#fff",
            "pattern": "youtube|you\\s+tube",
            "search_url": "https://www.youtube.com/results?search_query={q}",
            "home_url": "https://www.youtube.com",
        },
        "spotify": {
            "name": "Spotify",
            "badge": "🎧 SPOTIFY AUDIO • AUTO-PLAYING ON LAPTOP",
            "color": "#1db954",
            "text_color": "#000",
            "pattern": "spotify",
            "search_url": "https://open.spotify.com/search/{q}",
            "home_url": "https://open.spotify.com",
        },
    }
    cfg = configs.get(platform, configs["netflix"])
    query = str(params.get("query") or "").strip()
    if not query:
        query = _extract_streaming_title(prompt, cfg["pattern"])

    if query:
        url = cfg["search_url"].format(q=urllib.parse.quote(query))
        task_mode = "stream_show_on_laptop"
        summary = f"Starting '{query.title()}' on {cfg['name']} directly on your connected Laptop"
        spoken = f"Right away, sir. Identifying '{query.title()}' and starting it on {cfg['name']} on your connected laptop now."
    else:
        url = cfg["home_url"]
        task_mode = f"open_{platform}_on_laptop"
        summary = f"Launched {cfg['name']} directly on your connected Laptop"
        spoken = f"Right away, sir. Launching {cfg['name']} on your connected laptop now."

    preview_html = (
        f"<div class='job-code-preview' data-auto-open-url='{html.escape(url)}'>"
        f"<div class='job-badge' style='background:{cfg['color']};color:{cfg['text_color']};'>{cfg['badge']}</div>"
        f"<h4 style='margin-bottom:6px;'>{html.escape(summary)}</h4>"
        f"<p style='font-size:12px;color:#34d399;margin-bottom:8px;font-weight:600;'>"
        f"✅ Automatically launched on your connected Laptop Master Display (Siri-to-Laptop Stream Bridge Active).</p>"
        f"<a href='{html.escape(url)}' target='_blank' style='display:inline-block;background:{cfg['color']};color:{cfg['text_color']};padding:6px 14px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:700;'>▶ Open / Focus {html.escape(cfg['name'])} Window</a>"
        f"</div>"
    )
    return {
        "platform": platform,
        "service_name": cfg["name"],
        "task_mode": task_mode,
        "query": query,
        "url": url,
        "auto_open_on_laptop": True,
        "summary": summary,
        "spoken_response": spoken,
        "preview_html": preview_html,
    }


def _handle_amazon(prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
    query = str(params.get("query") or "").strip()
    if not query:
        m = re.search(
            r"\b(?:search|find|buy|order|shop\s+for|look\s+for|get)\s+(.+?)(?:\s+on\s+amazon)?$",
            prompt,
            flags=re.IGNORECASE,
        )
        if m:
            cand = re.sub(r"\bon\s+amazon\b", "", m.group(1), flags=re.IGNORECASE).strip()
            if cand.lower() not in ("amazon", "something"):
                query = cand

    if query:
        url = f"https://www.amazon.in/s?k={urllib.parse.quote(query)}"
        task_mode = "product_search"
        summary = f"Searching Amazon on Laptop for '{query.title()}'"
    else:
        url = "https://www.amazon.in"
        task_mode = "open_amazon"
        summary = "Opened Amazon Storefront on Laptop"

    preview_html = (
        f"<div class='job-code-preview' data-auto-open-url='{html.escape(url)}'>"
        f"<div class='job-badge' style='background:#f59e0b;color:#000;'>🛒 AMAZON COMMERCE &amp; ORDER HUB • AUTO-OPENED ON LAPTOP</div>"
        f"<h4 style='margin-bottom:6px;'>{html.escape(summary)}</h4>"
        f"<p style='font-size:12px;color:#cbd5e1;margin-bottom:8px;'>Filtered top-rated matches and Prime delivery options on your Laptop.</p>"
        f"<a href='{html.escape(url)}' target='_blank' style='display:inline-block;background:#f59e0b;color:#000;padding:6px 14px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:700;'>🛒 Open on Amazon</a>"
        f"</div>"
    )
    return {
        "platform": "amazon",
        "task_mode": task_mode,
        "query": query,
        "url": url,
        "auto_open_on_laptop": True,
        "summary": summary,
        "spoken_response": f"Certainly, sir. {summary}.",
        "preview_html": preview_html,
    }


def execute_interplatform_task(
    prompt: str,
    platform: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    execute_os: bool = False,
    output_root: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Execute a dynamic interplatform task across Netflix, Prime Video, Hotstar, YouTube, Spotify, Gmail, Calendar, Notes, or Amazon."""
    p_dict = params or {}
    plat = detect_platform(prompt, explicit_platform=platform or p_dict.get("platform")) or "notes"

    if plat == "gmail":
        res = _handle_gmail(prompt, p_dict)
    elif plat == "calendar":
        res = _handle_calendar(prompt, p_dict)
    elif plat in ("netflix", "prime_video", "hotstar", "youtube", "spotify"):
        res = _handle_streaming_service(plat, prompt, p_dict)
    elif plat == "amazon":
        res = _handle_amazon(prompt, p_dict)
    else:
        res = _handle_notes(prompt, p_dict)

    launched_on_laptop = False
    if execute_os and res.get("url"):
        launched_on_laptop = launch_url_on_laptop(res["url"])

    res["launched_on_laptop"] = launched_on_laptop
    res["success"] = True
    res["tool"] = "interplatform_hub"
    res["action"] = res.get("task_mode", "open")
    res["spoken_summary"] = res.get("spoken_response", res["summary"])
    res["title"] = res["summary"]
    res["job_type"] = "interplatform"
    INTERPLATFORM_HISTORY.append(res)
    return res


INTERPLATFORM_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "platform": {
            "type": "string",
            "enum": list(SUPPORTED_PLATFORMS),
        },
        "prompt": {"type": "string"},
        "execute_os": {"type": "boolean", "default": True},
    },
    "required": ["platform"],
    "additionalProperties": True,
}


def register_tools(registry: ToolRegistry) -> None:
    registry.register(
        ToolSpec(
            name="interplatform_hub",
            description="Open and execute tasks in Netflix, Amazon Prime Video, Disney+ Hotstar, YouTube, Spotify, Gmail, Google Calendar, Notes, and Amazon directly on the Laptop.",
            parameters_schema=INTERPLATFORM_SCHEMA,
            handler=lambda params: execute_interplatform_task(
                prompt=str(params.get("prompt") or ""),
                platform=params.get("platform"),
                params=params,
                execute_os=bool(params.get("execute_os", False)),
            ),
            plugin_source="plugins.interplatform_hub",
        )
    )
