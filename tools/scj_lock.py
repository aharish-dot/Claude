#!/usr/bin/env python3
"""Process-wide directory lock (mkdir is atomic on Windows and POSIX).

Used so two loops / a loop plus chat-`next` cannot claim the same SCJ id
or rewrite state/index.json at the same time.
"""
from __future__ import annotations

import os
import time


def pid_alive(pid: int) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    except Exception:
        return False
    return True


class DirLock:
    """Exclusive lock via os.mkdir. Not reentrant."""

    def __init__(self, path: str, timeout: float = 600, stale_s: float = 7200):
        self.path = path
        self.timeout = timeout
        self.stale_s = stale_s
        self.held = False
        self._pid_file = os.path.join(path, "pid")

    def _maybe_break_stale(self) -> None:
        if not os.path.isdir(self.path):
            return
        pid = 0
        try:
            with open(self._pid_file, encoding="utf-8") as f:
                pid = int((f.read() or "0").strip() or "0")
        except (OSError, ValueError):
            pid = 0
        try:
            age = time.time() - os.path.getmtime(self.path)
        except OSError:
            age = 0
        if pid_alive(pid):
            return
        if pid or age >= self.stale_s:
            try:
                if os.path.exists(self._pid_file):
                    os.remove(self._pid_file)
                os.rmdir(self.path)
            except OSError:
                pass

    def acquire(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        deadline = time.time() + self.timeout
        while True:
            try:
                os.mkdir(self.path)
                with open(self._pid_file, "w", encoding="utf-8") as f:
                    f.write(str(os.getpid()))
                self.held = True
                return
            except FileExistsError:
                self._maybe_break_stale()
                if time.time() > deadline:
                    raise TimeoutError(
                        f"timed out waiting for lock {self.path} ({self.timeout:.0f}s)"
                    )
                time.sleep(0.15)

    def release(self) -> None:
        if not self.held:
            return
        try:
            if os.path.exists(self._pid_file):
                os.remove(self._pid_file)
            os.rmdir(self.path)
        except OSError:
            pass
        self.held = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
        return False
