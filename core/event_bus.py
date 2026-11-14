"""DESKBOT async event bus (stdlib asyncio only).

Topic-based pub/sub. Handlers are coroutine functions; a failing handler is
logged and never prevents other handlers from running.
"""

import asyncio
import itertools
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Deque, Dict, List, Optional, Union

logger = logging.getLogger("EventBus")


class EventType(str, Enum):
    WAKE_WORD_DETECTED = "wake_word.detected"
    STT_RESULT = "stt.result"
    TTS_PLAY = "tts.play"
    TTS_DONE = "tts.done"
    BRAIN_THINKING = "brain.thinking"
    BRAIN_RESPONSE = "brain.response"
    BRAIN_ERROR = "brain.error"
    ROBOT_EXPRESSION = "robot.expression"
    ROBOT_CONNECTED = "robot.connected"
    ROBOT_DISCONNECTED = "robot.disconnected"
    MESH_DEVICE_JOINED = "mesh.device_joined"
    MESH_DEVICE_LEFT = "mesh.device_left"
    MESH_COMMAND = "mesh.command"
    MESH_COMMAND_RESULT = "mesh.command_result"
    USER_INPUT = "user.input"
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"


Topic = Union[EventType, str]


def _key(topic: Topic) -> str:
    return topic.value if isinstance(topic, EventType) else str(topic)


@dataclass
class Event:
    topic: str
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = "system"
    timestamp: float = field(default_factory=time.time)
    event_id: int = 0


Handler = Callable[[Event], Awaitable[None]]


class EventBus:
    def __init__(self, history_size: int = 200):
        self._subs: Dict[str, List[Handler]] = defaultdict(list)
        self._wildcard: List[Handler] = []
        self._history: Deque[Event] = deque(maxlen=history_size)
        self._ids = itertools.count(1)
        self.error_count = 0

    def subscribe(self, topic: Topic, handler: Handler) -> None:
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError("event handlers must be 'async def' coroutine functions")
        self._subs[_key(topic)].append(handler)

    def subscribe_all(self, handler: Handler) -> None:
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError("event handlers must be 'async def' coroutine functions")
        self._wildcard.append(handler)

    def unsubscribe(self, topic: Topic, handler: Handler) -> bool:
        handlers = self._subs.get(_key(topic), [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False

    async def publish(self, event: Event) -> int:
        """Deliver to all handlers concurrently; returns number of handlers invoked."""
        event.event_id = next(self._ids)
        self._history.append(event)
        topic_handlers = self._subs.get(event.topic)
        if not topic_handlers and not self._wildcard:
            return 0
        if not self._wildcard and topic_handlers and len(topic_handlers) == 1:
            h = topic_handlers[0]
            try:
                await h(event)
            except asyncio.CancelledError:
                raise
            except BaseException as r:
                self.error_count += 1
                logger.error("handler %s failed on %s: %r", getattr(h, "__name__", h), event.topic, r)
            return 1
        handlers = [*(topic_handlers or ()), *self._wildcard]
        results = await asyncio.gather(*(h(event) for h in handlers), return_exceptions=True)
        for h, r in zip(handlers, results):
            if isinstance(r, asyncio.CancelledError):
                raise r
            if isinstance(r, BaseException):
                self.error_count += 1
                logger.error("handler %s failed on %s: %r", getattr(h, "__name__", h), event.topic, r)
        return len(handlers)

    async def emit(self, topic: Topic, data: Optional[Dict[str, Any]] = None,
                   source: str = "system") -> int:
        return await self.publish(Event(topic=_key(topic), data=data or {}, source=source))

    def recent(self, n: int = 10) -> List[Event]:
        return list(self._history)[-n:]

    @property
    def stats(self) -> Dict[str, int]:
        return {
            "topics": len([t for t, h in self._subs.items() if h]),
            "handlers": sum(len(h) for h in self._subs.values()) + len(self._wildcard),
            "published": self._history[-1].event_id if self._history else 0,
            "handler_errors": self.error_count,
        }
