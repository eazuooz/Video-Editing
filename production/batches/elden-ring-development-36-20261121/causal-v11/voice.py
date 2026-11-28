"""Render only evidence-locked causal episodes with the established Shorts speaker."""
import argparse
from pathlib import Path
import sys
import shutil

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import make_approved_voice_v2 as approved

WORK = Path('D:/YamyamProduction/elden-ring-development-36-causal-v11/voice')

def run(episode, execute, lock_path=None):
    path = lock_path or HERE / 'locked' / f'{episode}.json'
    lock = approved.read(path)
    assert lock['id'] == episode and lock['scriptLockedForVoice']
    assert len(lock['narrationKo']) == 4
    for source in lock['inputs']:
        assert approved.sha(Path(source['path'])) == source['sha256'], source['path']
    fingerprint = approved.sha(path)
    output = WORK / episode / fingerprint[:12]
    approved.PLAN_SHA = fingerprint
    approved.pinned_plan = lambda: [lock]
    approved.PROJECT = 'elden-ring-causal-v11-voice-' + episode
    sys.path.insert(0, str(approved.QWEN))
    from resources import install_voice_profile
    install_voice_profile(approved)
    reason = approved.busy(approved.resource_guard(), approved.MIN_FREE)
    print({'episode': episode, 'lockSha256': fingerprint, 'guard': reason, 'output': str(output)}, flush=True)
    if not execute or reason:
        return
    output.mkdir(parents=True, exist_ok=True)
    for reuse in lock.get('reuseUnchangedVoice', []):
        prior_lock = Path(reuse['lock'])
        assert approved.sha(prior_lock) == reuse['lockSha256']
        prior = approved.read(prior_lock)
        index = reuse['take']
        assert prior['narrationKo'][index] == lock['narrationKo'][index]
        source = Path(reuse['wav'])
        assert approved.sha(source) == reuse['sha256']
        prior_output = source.parent.parent
        identity = approved.read(prior_output / 'voice-identity-v2.json')
        assert identity['planSha256'] == reuse['lockSha256']
        reference = approved.read(approved.APPROVED)['inputs']
        assert identity['referenceSha256'] == reference['reference']
        assert identity['referenceTextSha256'] == reference['referenceText']
        dest = output / 'approved-voice' / source.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists(): assert approved.sha(dest) == reuse['sha256']
        else: shutil.copyfile(source, dest)
        old_review = prior_output / 'voice-qa-source' / f'{episode}-{index}.json'
        if old_review.exists():
            review = approved.read(old_review)
            assert review['sha256'] == reuse['sha256'] and review['expected'] == lock['narrationKo'][index]
            new_review = output / 'voice-qa-source' / old_review.name
            new_review.parent.mkdir(parents=True, exist_ok=True)
            if not new_review.exists(): shutil.copyfile(old_review, new_review)
    if lock.get('reuseUnchangedVoice'):
        approved.save(output / 'reuse-proof.json', dict(lockSha256=fingerprint,
                      takes=lock['reuseUnchangedVoice'], byteExact=True))
    approved.render(output, 0, set())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode', required=True, choices=[f'{i:02}' for i in range(1,37)])
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--lock', type=Path)
    args = parser.parse_args()
    run(args.episode, args.execute, args.lock)
