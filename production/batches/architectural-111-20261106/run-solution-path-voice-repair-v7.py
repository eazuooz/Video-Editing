"""Run one guarded two-sentence prosody repair for the held 11.05 voice."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PREPARER = HERE / 'prepare-solution-path-voice-repair-v7.py'
PREPARER_SHA = '4852da3df87f45a64b6c92d93bb03caa01fe133132caf0ecf65037a0e199198b'
GUARDED_ENTRY = HERE / 'run-solution-path-voice-repair-v4.py'
GUARDED_ENTRY_SHA = '2eb51314d0210daf04d0fd97af83eb1c674fc4088557b1e4b7ded89f93282854'
LIFECYCLE = HERE / 'run-selected-voice-repair-v4.py'
LIFECYCLE_SHA = 'c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366'


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


SELF_SHA = sha(__file__)


def check_entry_sources():
    if (sha(__file__) != SELF_SHA or sha(GUARDED_ENTRY) != GUARDED_ENTRY_SHA
            or sha(LIFECYCLE) != LIFECYCLE_SHA or (PREPARER_SHA and sha(PREPARER) != PREPARER_SHA)):
        raise RuntimeError('Frozen selected V7 repair source changed')


check_entry_sources()
spec = importlib.util.spec_from_file_location('solution_voice_repair_v7_private_guarded_entry', GUARDED_ENTRY)
guarded = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = guarded
spec.loader.exec_module(guarded)
prep = guarded.prep.module('solution_voice_repair_v7_preparation', PREPARER)
life, base = guarded.life, guarded.base


def check_sources():
    check_entry_sources()
    if not PREPARER_SHA:
        raise prep.Pending('Awaiting frozen V7 preparer and held recording, unchanged canonical input and previous QA pins')
    prep.check_sources()


# Bind only this private guard instance to V7. The exact direct-venv process
# classifier, ownership retry, worker singleton and GPU guard are unchanged.
guarded.__file__ = str(Path(__file__).resolve())
guarded.check_sources = check_sources
guarded.prep = prep
life.__file__ = guarded.__file__
life.REPAIR_PROTOCOL = prep.PROTOCOL


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
    if args.execute and (argv is not None or not guarded.approved_execute_launcher()):
        parser.error('Use the exact eight-argument V7 execute entry through the approved Windows venv launcher')
    return args


def main(argv=None):
    args = arguments(argv)
    status = dict(staged=False, reuseCopied=False, modelStarted=False, gpuLeaseMutated=False)
    try:
        check_sources()
        guarded.install_hooks()
        prov = guarded.active_prepared(args)
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
