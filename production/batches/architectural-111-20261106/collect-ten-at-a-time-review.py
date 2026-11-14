"""Verify the original ordered series and deliver one authorized ten-video group."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COLLECTOR = HERE/'collect-single-batch-review.py'
COLLECTOR_SHA = '9b1b3c72e2f15e3b5ef8e508f1832511bca10c31dc940937ec1cc47627efda0c'

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--group', type=int, default=1)
    p.add_argument('--deliver', action='store_true')
    args = p.parse_args()
    if not 1 <= args.group <= 12:
        p.error('Group must be 1 to 12')
    if hashlib.sha256(COLLECTOR.read_bytes()).hexdigest() != COLLECTOR_SHA:
        raise ValueError('Original exact-series file validator changed')
    spec = importlib.util.spec_from_file_location('frozen_series_review_validator', COLLECTOR)
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    policy = base.read(HERE/'worklist.json')['deliveryPolicy']
    request = base.read(HERE/'ten-at-a-time-production-request-20261114.json')
    if (policy['mode'] != 'groups-of-10-local-review' or policy['groupSize'] != 10 or
            policy['platformActionsAuthorized'] is not False or request['platformActionsAuthorized'] is not False):
        raise ValueError('Ten-at-a-time local review authority changed')
    complete, pending, invalid = base.verify_series()
    queue = base.read(HERE/'single-production-queue-v1.json')['episodes']
    lo, hi = (args.group-1)*10+1, min(args.group*10, 111)
    selected = [r for r in complete if lo <= r['order'] <= hi]
    waiting = [r for r in pending if lo <= r['order'] <= hi]
    broken = [r for r in invalid if lo <= r['order'] <= hi]
    if args.group == 1 and [r['topicId'] for r in queue[:10]] != policy['firstGroupTopicIds']:
        raise ValueError('First group differs from the authorized original order')
    ready = len(selected) == hi-lo+1 and not waiting and not broken
    status = dict(group=args.group, expected=hi-lo+1, verifiedLocalReviews=len(selected),
                  pending=waiting, invalid=broken, readyToDeliver=ready, delivered=False)
    if args.deliver:
        if not ready:
            print(json.dumps(status, ensure_ascii=False))
            return 2
        manifest = dict(protocol='architectural111-ten-at-a-time-review-v1', group=args.group,
                        range=[lo, hi], episodes=selected, actualHumanReview=False,
                        platformActionsAuthorized=False)
        data = (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
        folder = base.MEDIA/'delivery'/'groups-of-ten'/f'{args.group:02d}'/hashlib.sha256(data).hexdigest()[:24]
        folder.mkdir(parents=True, exist_ok=True)
        page = base.render(selected).replace('레벨디자인 111편 로컬 검수', f'레벨디자인 {args.group}차 {len(selected)}편 로컬 검수')
        base.immutable(folder/'manifest.json', data)
        base.immutable(folder/'index.html', page.encode('utf-8'))
        status.update(index=(folder/'index.html').as_posix(), manifest=(folder/'manifest.json').as_posix(),
                      deliveryFilesPrepared=True)
        # Actual conversation delivery must be recorded only after sending the links.
    print(json.dumps(status, ensure_ascii=False))
    return 2 if broken else 0

if __name__ == '__main__':
    raise SystemExit(main())
