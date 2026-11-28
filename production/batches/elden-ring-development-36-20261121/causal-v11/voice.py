"""Render only evidence-locked causal episodes with the established Shorts speaker."""
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import make_approved_voice_v2 as approved

WORK = Path('D:/YamyamProduction/elden-ring-development-36-causal-v11/voice')

def run(episode, execute):
    path = HERE / 'locked' / f'{episode}.json'
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
    reason = approved.busy(approved.resource_guard(), approved.MIN_FREE)
    print({'episode': episode, 'lockSha256': fingerprint, 'guard': reason, 'output': str(output)}, flush=True)
    if not execute or reason:
        return
    output.mkdir(parents=True, exist_ok=True)
    approved.render(output, 0, set())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode', required=True, choices=[f'{i:02}' for i in range(1,37)])
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    run(args.episode, args.execute)
