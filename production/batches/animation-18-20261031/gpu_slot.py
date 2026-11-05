"""Coordinate offscreen renders and optional GPU audio checks with other local jobs."""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import subprocess
import time
import uuid

LEASE = Path(__file__).resolve().parents[3] / 'shared/output/GPU_HANDOFF.json'


@contextmanager
def idle_slot(owner, *, wait=False):
    token = uuid.uuid4().hex
    owned = False
    try:
        while True:
            if not LEASE.exists():
                query = subprocess.run(
                    ['nvidia-smi', '--query-gpu=memory.free,utilization.gpu', '--format=csv,noheader,nounits'],
                    capture_output=True, text=True, check=True,
                )
                free, utilization = map(int, query.stdout.splitlines()[0].split(','))
                if free >= 8192 and utilization < 15:
                    try:
                        with LEASE.open('x', encoding='utf8') as stream:
                            json.dump({'owner': owner, 'id': token, 'pid': os.getpid(),
                                       'createdAt': datetime.now(timezone.utc).isoformat()}, stream)
                        owned = True
                        break
                    except FileExistsError:
                        pass
            if not wait:
                break
            time.sleep(10)
        yield owned
    finally:
        if owned and LEASE.exists() and json.loads(LEASE.read_text('utf-8-sig')).get('id') == token:
            LEASE.unlink()
