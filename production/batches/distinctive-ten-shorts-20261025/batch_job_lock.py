"""Cooperative, process-owned lock for this finite batch's expensive jobs.

Voice queue integration (before invoking render-voice.py):
    SERIAL_JOB_LOCK_PROTOCOL = 'distinctive-ten-serial-v1'
    with SerialJobLock(slug=slug, stage='tts', wait_seconds=0):
        subprocess.run(...)
Catch JobBusy and recheck authorization/resources later. Do not kill another job.
The lock is never stolen on an elapsed timeout or an apparently stale PID.
"""
from pathlib import Path
import argparse
import datetime
import json
import os
import subprocess
import time
import uuid

LOCK_PROTOCOL = 'distinctive-ten-serial-v1'
MEDIA_ROOT = Path('C:/Users/1/Videos/YamyamProduction/distinctive-ten-shorts-20261025')
LOCK_PATH = MEDIA_ROOT / 'locks/serial-job.lock'


class JobBusy(RuntimeError):
    pass


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def inspect_lock(path=LOCK_PATH):
    path = Path(path)
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding='utf8'))
    except (OSError, ValueError):
        return {'state': 'unreadable-or-being-created', 'path': str(path)}
    try:
        import psutil
        process = psutil.Process(int(value['pid']))
        value['ownerLive'] = abs(process.create_time() - float(value['processCreateTime'])) < .05
    except Exception:
        value['ownerLive'] = False
    value['path'] = str(path)
    value['stalePolicy'] = 'Never automatically delete; inspect owner/process tree and exact token.'
    return value


class SerialJobLock:
    def __init__(self, slug, stage, wait_seconds=0, path=LOCK_PATH):
        self.path = Path(path)
        self.slug, self.stage = slug, stage
        self.wait_seconds = max(0, float(wait_seconds))
        self.token = uuid.uuid4().hex
        self.record = None

    def __enter__(self):
        import psutil
        deadline = time.monotonic() + self.wait_seconds
        self.path.parent.mkdir(parents=True, exist_ok=True)
        while True:
            record = dict(protocol=LOCK_PROTOCOL, token=self.token, pid=os.getpid(),
                          processCreateTime=psutil.Process().create_time(), slug=self.slug,
                          stage=self.stage, acquiredAt=now(), updatedAt=now())
            try:
                descriptor = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise JobBusy('Serial batch job is occupied: ' + json.dumps(inspect_lock(self.path), ensure_ascii=False))
                time.sleep(min(1, max(0, deadline - time.monotonic())))
                continue
            try:
                with os.fdopen(descriptor, 'w', encoding='utf8') as stream:
                    json.dump(record, stream, ensure_ascii=False, indent=2)
                    stream.write('\n')
                    stream.flush()
                    os.fsync(stream.fileno())
                self.record = record
                return self
            except BaseException:
                # A partial acquisition is deliberately retained for inspection.
                raise

    def _owned(self):
        current = json.loads(self.path.read_text(encoding='utf8'))
        if current.get('token') != self.token or current.get('pid') != os.getpid():
            raise RuntimeError('Lock ownership changed; never release another process lock.')
        return current

    def set_stage(self, stage):
        self._owned()
        self.record.update(stage=stage, updatedAt=now())
        temp = self.path.with_name(self.path.name + '.' + self.token + '.tmp')
        with temp.open('x', encoding='utf8') as stream:
            json.dump(self.record, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        self._owned()
        os.replace(temp, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.record is not None:
            self._owned()
            self.path.unlink()  # Exact owned lock only; media and other jobs are untouched.
            self.record = None
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspect', action='store_true')
    parser.add_argument('--stage', default='wrapped-job')
    parser.add_argument('--slug', default='finite-batch')
    parser.add_argument('--wait-seconds', type=float, default=0)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.inspect:
        print(json.dumps(inspect_lock(), ensure_ascii=False, indent=2))
        return
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('Supply --inspect or an explicit command after --.')
    try:
        with SerialJobLock(args.slug, args.stage, args.wait_seconds):
            raise SystemExit(subprocess.call(command))
    except JobBusy as error:
        print(str(error))
        raise SystemExit(75)


if __name__ == '__main__':
    main()
