"""Single-writer OS lock. A crashed process releases it; the lock file is retained."""
from __future__ import annotations

import json
import os
from pathlib import Path


class BuildLock:
    def __init__(self, output: Path):
        self.path = output / ".build.lock"
        self.handle = None

    def __enter__(self):
        descriptor = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        self.handle = os.fdopen(descriptor, "r+b", buffering=0)
        try:
            self.handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.handle.close()
            raise RuntimeError("A build is running; output is locked") from exc
        content = self.handle.read()
        try:
            if content and not content.startswith(b"B\n"):
                raise ValueError("Unrecognized lock format")
            self.previous = json.loads(content[2:]) if len(content) > 2 else None
        except (ValueError, UnicodeError) as exc:
            self.__exit__(None, None, None)
            raise RuntimeError("A build is running, or a legacy lock requires inspection before removal") from exc
        return self

    def record(self, value: dict):
        self.handle.seek(0)
        self.handle.write(b"B\n" + json.dumps(value).encode("utf-8"))
        self.handle.truncate()
        os.fsync(self.handle.fileno())

    def __exit__(self, *args):
        if self.handle is None or self.handle.closed:
            return
        self.handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        self.handle.close()
