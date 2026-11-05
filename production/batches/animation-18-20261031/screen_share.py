"""Run the finite animation batch's voice work only between Discord screen shares."""
import _thread
import json
import os
from pathlib import Path
import re
import runpy
import sys
import threading
import time

import psutil

HOLD = 73
START = "[startStreamWithSource] Starting stream for source id"
STREAM = re.compile(r"\[RTCConnection\(([^,]+), stream\)\] (.+)")


class ShareState:
    def __init__(self):
        self.log = Path(os.environ["APPDATA"]) / "discord/logs/renderer_js.log"
        policy = json.loads(Path(__file__).with_name("batch.json").read_text("utf-8-sig"))["screenShareVoicePolicy"]
        self.confirmed_end = policy.get("confirmedEndAtLocal")
        self.file_id = None
        self.offset = 0
        self.sessions = set()
        self.awaiting_connection = False
        self.seen_end = False
        self.quiet_since = None

    def scan(self, path, offset=0):
        with path.open("rb") as stream:
            stream.seek(offset)
            for raw in stream:
                if not raw.endswith(b"\n"):
                    return stream.tell() - len(raw)
                line = raw.decode("utf-8", errors="replace")
                if self.confirmed_end and line[1:24] <= self.confirmed_end:
                    continue
                if START in line:
                    self.awaiting_connection = True
                    self.seen_end = False
                match = STREAM.search(line)
                if not match:
                    continue
                session, event = match.groups()
                if event.startswith(("Connecting to RTC server", "RTC connected to media server")):
                    # Incoming video alone is not a new local screen share.
                    if self.confirmed_end and not self.awaiting_connection and session not in self.sessions:
                        continue
                    self.sessions.add(session)
                    self.awaiting_connection = False
                elif event.startswith("Destroy RTCConnection"):
                    if session in self.sessions:
                        self.seen_end = True
                    self.sessions.discard(session)
            return stream.tell()

    def clear(self):
        running = any((p.info["name"] or "").lower() == "discord.exe"
                      for p in psutil.process_iter(["name"], ad_value=None))
        if not running:
            self.quiet_since = None
            return True
        try:
            info = self.log.stat()
            if info.st_ino != self.file_id or info.st_size < self.offset:
                self.sessions.clear()
                self.awaiting_connection = False
                self.seen_end = bool(self.confirmed_end)
                self.quiet_since = None
                previous = self.log.with_name("renderer_js.old.log")
                if previous.exists():
                    self.scan(previous)
                self.offset = 0
                self.file_id = info.st_ino
            self.offset = self.scan(self.log, self.offset)
        except OSError:
            self.quiet_since = None
            return False
        if self.sessions or self.awaiting_connection or not self.seen_end:
            self.quiet_since = None
            return False
        if self.quiet_since is None:
            self.quiet_since = time.monotonic()
        return time.monotonic() - self.quiet_since >= 30


def run_when_clear(script, args):
    state = ShareState()
    if not state.clear():
        print("Waiting for Discord screen sharing to finish.", flush=True)
        while not state.clear():
            time.sleep(5)
    finished = threading.Event()
    interrupted = threading.Event()

    def watch():
        while not finished.wait(2):
            if not state.clear():
                interrupted.set()
                _thread.interrupt_main()
                return

    watcher = threading.Thread(target=watch, daemon=True)
    watcher.start()
    sys.argv = [str(script), *args]
    sys.path.insert(0, str(script.parent))
    try:
        runpy.run_path(str(script), run_name="__main__")
    except KeyboardInterrupt:
        if not interrupted.is_set():
            raise
        print("Yielding the animation voice job to Discord; saved chunks are reusable.", flush=True)
        raise SystemExit(HOLD)
    finally:
        finished.set()


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    script = (root / sys.argv[1]).resolve()
    if script not in [root / "qwen3-tts" / x for x in ("render_narration.py", "review_project_narration.py")]:
        raise ValueError("Unexpected animation voice entry point")
    run_when_clear(script, sys.argv[2:])
