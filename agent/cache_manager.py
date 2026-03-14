"""
File-based cache manager for live internet data.

Stores API responses locally with a configurable TTL (default 24 hours).
The cache directory is ``.cache/`` at the project root (gitignored).
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Optional


_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")


def _ensure_dir() -> None:
    os.makedirs(_CACHE_DIR, exist_ok=True)


def _key_path(key: str) -> str:
    # Sanitise key for use as a filename
    safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in key)
    return os.path.join(_CACHE_DIR, f"{safe}.json")


class CacheManager:
    """Simple file-based cache with per-entry TTL."""

    def __init__(self, cache_dir: Optional[str] = None) -> None:
        self._dir = cache_dir or _CACHE_DIR
        os.makedirs(self._dir, exist_ok=True)

    def _path(self, key: str) -> str:
        safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in key)
        return os.path.join(self._dir, f"{safe}.json")

    def get_cached(self, key: str) -> Optional[Any]:
        """Return cached data if it exists and has not expired; otherwise ``None``."""
        path = self._path(key)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as fh:
                entry = json.load(fh)
            if time.time() < entry.get("expires_at", 0):
                return entry.get("data")
        except (OSError, json.JSONDecodeError, KeyError):
            pass
        return None

    def set_cache(self, key: str, data: Any, ttl_hours: float = 24) -> None:
        """Store *data* under *key* with an expiry of *ttl_hours* hours."""
        path = self._path(key)
        entry = {
            "data": data,
            "cached_at": time.time(),
            "expires_at": time.time() + ttl_hours * 3600,
        }
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(entry, fh)
        except OSError:
            pass  # Non-fatal — app continues without caching

    def clear_old_cache(self) -> int:
        """Delete all expired cache files. Returns number of files removed."""
        removed = 0
        try:
            for filename in os.listdir(self._dir):
                if not filename.endswith(".json"):
                    continue
                path = os.path.join(self._dir, filename)
                try:
                    with open(path, "r", encoding="utf-8") as fh:
                        entry = json.load(fh)
                    if time.time() >= entry.get("expires_at", 0):
                        os.remove(path)
                        removed += 1
                except (OSError, json.JSONDecodeError, KeyError):
                    # If we can't read it, remove the corrupt file
                    try:
                        os.remove(path)
                        removed += 1
                    except OSError:
                        pass
        except OSError:
            pass
        return removed
