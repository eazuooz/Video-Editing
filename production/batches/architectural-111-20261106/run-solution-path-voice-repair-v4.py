"""Run the selected 11.05 repair with 46 exact copies and four new clauses.

Default preparation is read-only. Only the exact guarded execute entry can
take the worker singleton, stage immutable inputs or invoke Qwen.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

PREPARER = HERE / 'prepare-solution-path-voice-repair-v4.py'
PREPARER_SHA = '9a70bbe5d3886e08b3afb4a3dbc16e3751dbd039a561f5003850736d26b5dfd3'
LIFECYCLE = HERE / 'run-selected-voice-repair-v4.py'
LIFECYCLE_SHA = 'c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366'


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


SELF_SHA = sha(__file__)


def check_sources():
    if (sha(__file__) != SELF_SHA or sha(PREPARER) != PREPARER_SHA
            or sha(LIFECYCLE) != LIFECYCLE_SHA):
        raise RuntimeError('Frozen selected V4 repair source changed')
    if 'prep' in globals():
        prep.check_sources()


check_sources()
spec = importlib.util.spec_from_file_location('solution_voice_repair_v4_preparation', PREPARER)
prep = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = prep
spec.loader.exec_module(prep)
life = prep.module('solution_voice_repair_v4_private_lifecycle', LIFECYCLE)
base = life.base
life.REPAIR_PROTOCOL = prep.PROTOCOL
life.__file__ = str(Path(__file__).resolve())
base.prep = prep.prep
base.zen.busy_reason = prep.voice_entry.audited_native_busy
resource = prep.voice_entry.resource
original_process_reason = resource.process_reason
original_save = base.save
CURRENT = None
CURRENT_ARGS = None


def execute_tail_matches(args):
    return (isinstance(args, list) and len(args) == 8 and all(isinstance(a, str) for a in args)
            and args[1:4] == ['-u', '-X', 'utf8'] and args[5:] == ['--execute', '--wait-hours', '6']
            and Path(args[4]).resolve() == Path(__file__).resolve())


def execute_parent_matches(info, own, parent):
    """Accept only the exact current Dvenv launcher for the exact Cbase child."""
    try:
        fields = ('pid', 'ppid', 'create_time', 'name', 'exe', 'cmdline')
        if any(any(row.get(key) is None for key in fields) for row in (info, own, parent)):
            return False
        if any(type(row[key]) is not int or row[key] <= 0
               for row in (info, own, parent) for key in ('pid', 'ppid')):
            return False
        if any(type(row['create_time']) not in (int, float) or not math.isfinite(row['create_time'])
               or row['create_time'] <= 0 for row in (info, own, parent)):
            return False
        if (own['pid'] == parent['pid'] or own['ppid'] != parent['pid']
                or info['pid'] != parent['pid'] or info['ppid'] != parent['ppid']):
            return False
        args, parent_args = own['cmdline'], parent['cmdline']
        if (not execute_tail_matches(args) or not execute_tail_matches(parent_args)
                or args[1:] != parent_args[1:] or info['cmdline'] != parent_args):
            return False
        launcher = Path(prep.RUNTIME_PINS[0]['path']).resolve()
        body = Path(prep.RUNTIME_PINS[2]['path']).resolve()
        return (Path(parent_args[0]).resolve() == Path(parent['exe']).resolve() == Path(info['exe']).resolve() == launcher
                and Path(args[0]).resolve() == Path(own['exe']).resolve() == body
                and own['name'].lower() == parent['name'].lower() == info['name'].lower() == 'python.exe'
                and abs(info['create_time'] - parent['create_time']) < .001
                and 0 <= own['create_time'] - parent['create_time'] < 30)
    except (AttributeError, KeyError, TypeError, ValueError, OSError):
        return False


def own_wrapper_marker(record, own):
    try:
        return (isinstance(record, dict) and record.get('protocol') == base.PROTOCOL
                and record.get('owner') == 'architectural-111-11-05-voice' and record.get('topicId') == '11.05'
                and record.get('stage') == 'voice' and isinstance(record.get('token'), str) and bool(record['token'])
                and record.get('pid') == own['pid'] and type(record.get('createTime')) in (int, float)
                and math.isfinite(record['createTime']) and abs(record['createTime'] - own['create_time']) < .001
                and record.get('argv') == own['cmdline']
                and record.get('commandSHA256') == base.digest(own['cmdline']) and record.get('child') is None)
    except (KeyError, TypeError, ValueError):
        return False


def launcher_processes():
    fields = ['pid', 'ppid', 'create_time', 'name', 'exe', 'cmdline']
    own = resource.psutil.Process(os.getpid()).as_dict(fields)
    parent = resource.psutil.Process(own['ppid']).as_dict(fields)
    return own, parent


def approved_execute_launcher():
    if os.name != 'nt':
        return False
    try:
        own, parent = launcher_processes()
        return own['pid'] == os.getpid() and parent['pid'] == os.getppid() and execute_parent_matches(parent, own, parent)
    except (resource.psutil.NoSuchProcess, resource.psutil.AccessDenied, OSError, ValueError, KeyError, TypeError):
        return False


def scoped_process_reason(info, own_pid, qualified=frozenset()):
    if os.name == 'nt' and own_pid == os.getpid() and info.get('pid') == os.getppid():
        try:
            own, parent = launcher_processes()
            marker = Path(base.MEDIA) / '11-05-voice-worker.json'
            record = base.read(marker)
            if (own_wrapper_marker(record, own) and execute_parent_matches(info, own, parent)
                    and base.read(marker) == record):
                return None
        except (resource.psutil.NoSuchProcess, resource.psutil.AccessDenied, OSError, ValueError, KeyError, TypeError):
            pass
    return original_process_reason(info, own_pid, qualified)


resource.process_reason = scoped_process_reason


def prepared(args):
    check_sources()
    if args.topic != '11.05':
        raise prep.Pending('Only selected 11.05 repair is supported')
    return prep.prepare(args.repair_plan, args.native_evidence, args.native_qa, args.narration)


def active_prepared(args):
    global CURRENT, CURRENT_ARGS
    CURRENT_ARGS = args
    CURRENT = prepared(args)
    life.CURRENT = CURRENT
    return CURRENT


def fresh_stage(full):
    """Recheck the exact full preparation before staging any subset or copy."""
    check_sources()
    if CURRENT_ARGS is None:
        raise RuntimeError('No current V4 repair invocation')
    fresh = prepared(CURRENT_ARGS)['_basePrepared']
    if full != fresh:
        raise prep.Pending('V4 preparation inputs changed before staging')
    return prep.prep.core.immutable_stage(fresh)


def retry_owner_token(path, value):
    """Allow a bounded sharing retry on only the same owned metadata."""
    try:
        media = Path(base.MEDIA).resolve()
        record = base.read(media / '11-05-voice-worker.json')
        me = base.identity()
        owner = 'architectural-111-11-05-voice'
        if not execute_tail_matches(me['argv']):
            return False
        if (record.get('protocol') != base.PROTOCOL or record.get('owner') != owner
                or record.get('pid') != me['pid'] or abs(record.get('createTime', 0) - me['createTime']) >= .01
                or record.get('argv') != me['argv'] or record.get('commandSHA256') != base.digest(me['argv'])
                or not record.get('token')):
            return False
        token = record['token']
        path = Path(path).resolve()
        if path == media / '11-05-voice-progress.json':
            return (token if value.get('protocol') == base.PROTOCOL and value.get('owner') == owner
                    and value.get('pid') == me['pid'] and value.get('token') == token else False)
        if CURRENT is None or CURRENT['repair']['identity']['protocol'] != prep.PROTOCOL:
            return False
        if value.get('protocol') != base.PROTOCOL or value.get('fingerprint') != CURRENT['fingerprint']:
            return False
        if path == base.output_of(CURRENT) / 'scene-progress.json':
            return token
        return token if path == media / '11-05-voice-evidence.json' and value.get('topicId') == '11.05' else False
    except (OSError, ValueError, TypeError, KeyError):
        return False


def metadata_save(path, value):
    token = retry_owner_token(path, value)
    if not token:
        return original_save(path, value)
    error = None
    for attempt in range(10):
        if attempt and retry_owner_token(path, value) != token:
            raise error
        try:
            return original_save(path, value)
        except PermissionError as caught:
            error = caught
            if getattr(caught, 'winerror', None) != 5 or attempt == 9 or retry_owner_token(path, value) != token:
                raise
            time.sleep(min(.05 * (attempt + 1), .25))


def install_hooks():
    life.prepared = prepared
    life.active_prepared = active_prepared
    life.original_stage = fresh_stage
    life.install_hooks()
    base.prepared = active_prepared
    base.save = metadata_save


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--topic', default='11.05')
    parser.add_argument('--repair-plan', default=str(prep.PLAN))
    parser.add_argument('--native-evidence')
    parser.add_argument('--native-qa')
    parser.add_argument('--narration', default=str(prep.NARRATION))
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--wait-hours', type=float, default=6)
    args = parser.parse_args(argv)
    args.semantic_components = None
    if args.topic != '11.05' or not math.isfinite(args.wait_hours) or not 0 < args.wait_hours <= 6:
        parser.error('Only a finite 11.05 repair up to six hours is supported')
    if args.execute and (argv is not None or not approved_execute_launcher()):
        parser.error('Use the exact eight-argument V4 execute entry through the approved Windows venv launcher')
    return args


def main(argv=None):
    args = arguments(argv)
    install_hooks()
    status = dict(staged=False, reuseCopied=False, modelStarted=False, gpuLeaseMutated=False)
    try:
        prov = active_prepared(args)
        if args.execute:
            return base.execute(args)
        out = base.output_of(prov)
        complete = life.verify_complete(prov, out) if (out / 'voice-complete-proof.json').is_file() else None
        result = dict(ready=True, topicId='11.05', fullVoiceFingerprint=prov['fingerprint'],
                      repairFingerprint=prov['repair']['fingerprint'], logicalSentenceCount=48,
                      fullSceneCount=len(prov['script']['scenes']), reuseCount=len(prov['repair']['rows']),
                      missingOnlyCount=len(prov['repair']['missing']),
                      engineSceneIds=[row['id'] for row in prov['repair']['missing']], existingComplete=bool(complete))
    except (prep.Pending, base.prep.Pending, FileNotFoundError) as error:
        result = dict(ready=False, reason=str(error))
    print(json.dumps(dict(result, **status), ensure_ascii=False))
    if args.execute and not result['ready']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
