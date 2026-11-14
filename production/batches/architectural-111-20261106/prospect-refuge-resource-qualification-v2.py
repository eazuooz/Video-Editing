"""Selected06.02 resource classification for two exact audited idle Edge trees.

Never terminates/suspends an app, opens a browser/CDP endpoint, reads a profile,
or grants ownership/completion. Unknown/new/unreadable/active trees still block.
The unchanged native base guard must also be clear before AND after sampling.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import time
import uuid
import psutil

BASE = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-06-02/resource-observations')
AUDIT = BASE / 'browser-resource-audit-v1.json'
AUDIT_SHA = 'ad3df634b671d7f4f17ff5e50b1ed05ef796ebd25a47501ce8cb57e213e555ee'
SAMPLES = BASE / 'target-process-os-samples.json'
SAMPLES_SHA = '4ac8ffaba25e179992052e34bffc46e4f478c67b52d3e87947e62d9d81c38083'
EDGE_EXE = 'c:/program files (x86)/microsoft/edge/application/msedge.exe'
PROFILES = {24696: 'MRrs9r', 66848: 'CjR4D5'}
CONTROLLERS = {24696: 17188, 66848: 10848}
GPU_PIDS = {24696: 79116, 66848: 82808}
# pid: (parent, creationTime, SHA256 of exact UTF8 JSON argv array).
EXPECTED = {
    8492: (24696, 1793842814.0451424, '4dd5c9414feb12b705fa9cc20585caeaeeb897783938cb3df82e7a9bc86d2791'),
    18612: (24696, 1793842814.3492873, 'ac03700be6c5efad5c8832a64ca626c6d156be7737a82c68610e3949464e0b90'),
    19724: (66848, 1793846022.845116, '603f4ab6f5205d7a8f9570f6ddf973dd64f4c7ef98c0b3786b868d5dd6c8432e'),
    20064: (66848, 1793846023.2841847, 'a0625556def5ab7212e6f6db0cccb004f440821123cb985e4d7a5505150ef565'),
    24696: (17188, 1793842814.0241988, 'e01c59ce7735fb9ba94876f3b6d9d0c1b06478d4c988e2815d01bec73170fa93'),
    25232: (24696, 1793842814.2301333, '171ce69dcd582e63c258ce8679f225ccfac2d7198ee6861ca8b63c032f81ba1a'),
    39388: (66848, 1793846023.4689803, 'b0a8417378f4965ba2387a71d34f1091b7791fe2b2ba49c9bc394c771c84c9e9'),
    47236: (24696, 1793842874.242546, '778897dac9f66a015e39b9117f3406781d434bcc8a2ec550c5db80fa5cee3fd4'),
    57076: (66848, 1793846083.330866, '94d4c48e4bb9ec35eaf69a1987c76ac916628758228aeb050bb5be57bda35767'),
    61220: (66848, 1793846023.4697337, '85c7e98c129a52b6ad2e59209b12fcc0dea30a31c49a6e294eac00b6f7aa1e51'),
    66848: (10848, 1793846022.7800095, 'f84e5c8caee6b440ef6624b1449ae22ee2e0f2a78dcab1c722e6069ecd9be28a'),
    74112: (66848, 1793846023.193128, '7471a0908851ef8e5ee40beb85c2c88ddeade43c2409960927db9de8a3422150'),
    74928: (24696, 1793842814.348981, 'f8435e9be177dbd28476ae2243cbe2814dd45ef3c621d86b0de25ed42e49c914'),
    78496: (24696, 1793842814.174225, '8bd3b2b0d58dd9cc9911d8794aac2d2f14cb9f94e40f2ef4e096b835721acfe1'),
    79116: (24696, 1793842814.17209, '997b7d1f8d76457f7e78bd522f4f79c6a8a39303b36b224b021373a6bee5e8f3'),
    82808: (66848, 1793846023.1802516, 'dccd7ee436faf935cff1c52619e4bd5b6a19f7c1be83d6df6764dc36892d235d'),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def argv_sha(args):
    return hashlib.sha256(json.dumps(args, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()


def expected_tree(root):
    return {root} | {pid for pid, value in EXPECTED.items() if value[0] == root}


def connected_peer(row):
    remote = row.get('remote', [])
    if not isinstance(remote, (list, tuple)):
        return True  # Unreadable/malformed endpoint cannot establish idle.
    if not remote:
        return str(row.get('status', '')).upper() == 'ESTABLISHED'
    if len(remote) < 2:
        return True
    return remote[0] not in ('', '0.0.0.0', '::') or remote[1] != 0


def _single_snapshot(snapshot):
    if snapshot.get('errors'):
        return 'Resource metadata unreadable: ' + '; '.join(snapshot['errors']), set()
    # A Windows PID is not a process identity. A proved different birth time
    # means the audited process exited and that number now belongs to another
    # process. New headless/profile processes still block below and all current
    # processes still pass the unchanged global resource guard.
    rows = {}
    for row in snapshot['rows']:
        pid = int(row['pid'])
        expected = EXPECTED.get(pid)
        created = row.get('created')
        if expected and type(created) in (int, float) and math.isfinite(created) and created > 0:
            if abs(created - expected[1]) > .001:
                continue
        rows[pid] = row
    qualified = set()
    for root in PROFILES:
        members = expected_tree(root)
        existing = members & rows.keys()
        if root not in rows:
            if existing:
                return 'Audited root disappeared but descendant tree remains; preserve and inspect', set()
            continue
        if existing != members:
            return 'Audited eight-process browser tree changed', set()
        controller = snapshot.get('controllers', {}).get(str(CONTROLLERS[root]))
        if controller != 'absent':
            return 'Recorded browser controller is present/reused or unreadable', set()
        descendants = {root}
        while True:
            extra = {int(pid) for pid, ppid in snapshot['processParents'].items() if ppid in descendants}
            if extra <= descendants:
                break
            descendants |= extra
        if descendants != members:
            return 'New/unregistered browser child or reparented tree', set()
        for pid in members:
            row = rows[pid]
            ppid, created, signature = EXPECTED[pid]
            if (row.get('ppid') != ppid or not isinstance(row.get('created'), (int, float))
                    or abs(row['created'] - created) > 0.001 or row.get('cmdSHA256') != signature
                    or row.get('name', '').lower() != 'msedge.exe'
                    or row.get('exe', '').replace('\\', '/').lower() != EDGE_EXE):
                return 'Browser PID/creation/parent/executable/exact-argv signature changed', set()
            if not isinstance(row.get('tcp'), list):
                return 'Browser TCP metadata unreadable', set()
            if any(connected_peer(connection) for connection in row['tcp']):
                return 'Browser has a connected or unknown nonzero TCP peer', set()
            values = [row.get(key) for key in ('cpuSeconds', 'readBytes', 'writeBytes')]
            if any(type(value) not in (int, float) or not math.isfinite(value) or value < 0 for value in values):
                return 'Browser CPU/IO metadata unreadable', set()
        counters = snapshot.get('gpuCounters', {}).get(str(GPU_PIDS[root]))
        if not isinstance(counters, list) or not counters or any(type(v) not in (int, float) or not math.isfinite(v) or v != 0 for v in counters):
            return 'Audited browser GPU counters active, unavailable or unknown', set()
        qualified |= members
    if set(snapshot.get('headlessPids', [])) - qualified:
        return 'Another unknown/new headless browser/render process is running', set()
    if set(snapshot.get('sameProfilePids', [])) - qualified:
        return 'Unregistered process shares an audited temporary profile', set()
    return None, qualified


def evaluate_pair(before, after, base_reason_before=None, base_reason_after=None):
    """Pure classification; fixtures pass snapshots, never touch live processes."""
    if base_reason_before or base_reason_after:
        return dict(qualified=False, reason=base_reason_before or base_reason_after, qualifiedPids=[])
    elapsed = after['monotonic'] - before['monotonic']
    # Keep the requested sleep2..3s. Windows counter-query warmup can add
    # several seconds to the observed interval; longer zero-activity evidence
    # remains useful, with an explicit30s cap rather than an unbounded wait.
    if not 2.0 <= elapsed <= 30.0:
        return dict(qualified=False, reason='CPU/IO qualification interval outside bounded2..30s', qualifiedPids=[])
    reason, first = _single_snapshot(before)
    if reason:
        return dict(qualified=False, reason=reason, qualifiedPids=[])
    reason, second = _single_snapshot(after)
    if reason:
        return dict(qualified=False, reason=reason, qualifiedPids=[])
    if first != second:
        return dict(qualified=False, reason='Audited browser identities changed during qualification', qualifiedPids=[])
    a, b = ({row['pid']: row for row in snap['rows']} for snap in (before, after))
    for pid in first:
        if any(a[pid][key] != b[pid][key] for key in ('cpuSeconds', 'readBytes', 'writeBytes')):
            return dict(qualified=False, reason='Audited browser CPU or diskIO became active', qualifiedPids=[])
    return dict(qualified=True, reason=None, qualifiedPids=sorted(first), sampleIntervalSeconds=elapsed,
                classification='Exact audited idle-orphan infrastructure; ownership/completion not established',
                ownershipVerified=False, processTerminationAuthorized=False)


def gpu_counters():
    # This command only queries OS counters; no browser or GPU workload starts.
    command = ("$ErrorActionPreference='Stop'; @(Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine | "
               "Where-Object { $_.Name -match 'pid_(79116|82808)_' } | "
               "ForEach-Object { [pscustomobject]@{name=$_.Name;utilization=$_.UtilizationPercentage} }) | ConvertTo-Json -Compress")
    result = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', command],
                            capture_output=True, text=True, encoding='utf-8', timeout=12,
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if result.returncode:
        raise RuntimeError('OS targetGPU counters unavailable')
    rows = json.loads(result.stdout or '[]')
    if isinstance(rows, dict):
        rows = [rows]
    if not isinstance(rows, list):
        raise RuntimeError('OS targetGPU counters missing')
    output = {}
    for row in rows:
        match = re.search(r'^pid_(79116|82808)_', row['name'])
        if not match:
            raise RuntimeError('Unexpected GPU-counter identity')
        output.setdefault(match[1], []).append(row['utilization'])
    return output


def snapshot():
    out = dict(monotonic=time.monotonic(), observedAtUtc=datetime.now(timezone.utc).isoformat(),
               rows=[], processParents={}, controllers={}, headlessPids=[], sameProfilePids=[], errors=[], gpuCounters={})
    browsers = ('chrome.exe', 'msedge.exe', 'chromium.exe')
    for process in psutil.process_iter(['pid', 'ppid', 'name']):
        try:
            info = process.info
            out['processParents'][str(process.pid)] = info['ppid']
            if (info.get('name') or '').lower() in browsers:
                if info.get('ppid') is None:
                    out['errors'].append('Unreadable browser parent PID' + str(process.pid))
                try:
                    args = process.cmdline()
                    if any(arg.startswith('--headless') for arg in args):
                        out['headlessPids'].append(process.pid)
                    if any('puppeteer_dev_chrome_profile-' + suffix in arg for suffix in PROFILES.values() for arg in args):
                        out['sameProfilePids'].append(process.pid)
                except psutil.NoSuchProcess:
                    continue
                except psutil.AccessDenied:
                    out['errors'].append('Unreadable browser argv PID' + str(process.pid))
        except psutil.NoSuchProcess:
            continue
        except psutil.AccessDenied:
            out['errors'].append('Unreadable process tree PID' + str(process.pid))
    for pid in EXPECTED:
        try:
            process = psutil.Process(pid)
            args = process.cmdline()
            cpu = process.cpu_times()
            io = process.io_counters()
            tcp = [dict(status=c.status, local=list(c.laddr), remote=list(c.raddr) if c.raddr else [])
                   for c in process.net_connections(kind='tcp')]
            out['rows'].append(dict(pid=pid, ppid=process.ppid(), name=process.name(), created=process.create_time(),
                                    exe=process.exe(), cmdSHA256=argv_sha(args), cpuSeconds=cpu.user + cpu.system,
                                    readBytes=io.read_bytes, writeBytes=io.write_bytes, tcp=tcp))
        except psutil.NoSuchProcess:
            continue
        except (psutil.AccessDenied, OSError) as error:
            out['errors'].append('Unreadable targetPID' + str(pid) + ':' + type(error).__name__)
    for pid in CONTROLLERS.values():
        try:
            psutil.Process(pid).create_time()
            out['controllers'][str(pid)] = 'present-or-reused'
        except psutil.NoSuchProcess:
            out['controllers'][str(pid)] = 'absent'
        except (psutil.AccessDenied, OSError):
            out['controllers'][str(pid)] = 'unknown'
    try:
        out['gpuCounters'] = gpu_counters()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        out['errors'].append('GPU counters unknown:' + type(error).__name__)
    return out


def qualify(base_guard, sample_seconds=2.0):
    """Read-only bounded CPU revalidation, with a fresh immutable check receipt."""
    report = dict(schemaVersion='architectural111-resource-qualification-v2', topicId='06.02',
                  policy='Root-recommended resource classification under user no-other-active-work rule; not ownership/completion/termination permission',
                  createdAtUtc=datetime.now(timezone.utc).isoformat(), qualified=False, qualifiedPids=[], snapshots=[],
                  moduleSHA256=sha(__file__), processMutationPerformed=False, browserAccessPerformed=False,
                  audit=dict(path=str(AUDIT), sha256=AUDIT_SHA), osSamples=dict(path=str(SAMPLES), sha256=SAMPLES_SHA))
    try:
        if sha(AUDIT) != AUDIT_SHA or sha(SAMPLES) != SAMPLES_SHA:
            raise RuntimeError('Pinned browser resource evidence changed')
        if not callable(base_guard) or not 2.0 <= sample_seconds <= 3.0:
            raise RuntimeError('Unchanged global GPU guard and bounded sampling required')
        before_reason = base_guard()
        report['baseGuardBefore'] = before_reason
        if before_reason:
            report['reason'] = before_reason
        else:
            before = snapshot()
            time.sleep(sample_seconds)
            after = snapshot()
            report['snapshots'] = [before, after]
            after_reason = base_guard()
            report['baseGuardAfter'] = after_reason
            report.update(evaluate_pair(before, after, before_reason, after_reason))
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, psutil.Error) as error:
        report.update(qualified=False, qualifiedPids=[], reason='Resource qualification unknown: ' + str(error))
    folder = BASE / 'qualifications'
    path = folder / (time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:12] + '.json')
    try:
        folder.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(tmp, path)
    except OSError:
        return dict(qualified=False, qualifiedPids=[], reason='Cannot preserve resource qualification evidence')
    return dict(qualified=report['qualified'], qualifiedPids=report['qualifiedPids'], reason=report.get('reason'),
                evidence=dict(path=str(path), sha256=sha(path)))


if __name__ == '__main__':
    print(json.dumps(dict(topicId='06.02', sourcePrepared=True, actualQualificationPerformed=False,
                         runtime='Called only through selected native busy_reason with unchanged global guard')))
