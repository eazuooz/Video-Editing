"""Prepare a selective source and ledger commit after complete local QA."""
from datetime import datetime
from zoneinfo import ZoneInfo

from finish_review import sha
from plan_observations import BATCH, HERE, ROOT, load, relative, save


def main():
    manifest = load(HERE / 'review-manifest.json')
    control_path = ROOT / 'shared/publishing/video-production-control.json'
    control = load(control_path)['animationContrastRevision20261108']
    assert manifest['scope'] == control['episodes'] and not manifest['humanReviewed']
    stamp = datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
    checkpoint = load(HERE / 'checkpoint.json')
    checkpoint.update(status='local-final-review-ready', updatedAt=stamp,
                      deliveryManifest=relative(HERE / 'review-manifest.json'), reviewUrl=manifest['url'],
                      outputFolder=manifest['outputFolder'], technicalQaEpisodes=len(manifest['records']),
                      observationCueCount=sum(len(row['cues']) for row in manifest['records']))
    save(HERE / 'checkpoint.json', checkpoint)
    control['reviewFeedback20261110'] = {
        'status': 'local-final-review-ready', 'updatedAt': stamp,
        'checkpoint': relative(HERE / 'checkpoint.json'), 'manifest': relative(HERE / 'review-manifest.json'),
        'url': manifest['url'], 'episodes': manifest['scope'], 'humanReviewed': False, 'platformChanged': False,
    }
    work = {row['id']: row for row in load(ROOT / 'shared/publishing/video-worklist.json')['rows']}
    spec = load(BATCH / 'integration-progress-commit-spec.json')
    spec['control'] = control
    spec['worklist'] = []
    for d in manifest['records']:
        master = next(f for f in d['files'] if f['kind'] == 'captioned.mp4')
        assert sha(master['path']) == master['sha256']
        revision = work[d['id']]['contrastRevision']
        revision['reviewFeedback20261110'] = {
            'status': 'local-final-review-ready', 'reviewUrl': manifest['url'] + d['id'] + '/',
            'captionedMasterSha256': master['sha256'], 'humanReviewed': False,
            'observationCueCount': len(d['cues']),
        }
        spec['worklist'].append({'id': d['id'], 'set': {'updatedAt': stamp, 'contrastRevision': revision}})
    spec['markdownStatus'] = '피드백 반영본 완료 · 통합 페이지에서 사용자 검수 대기'
    spec['ownedPaths'] = sorted(relative(path) for path in HERE.iterdir()
                                if path.is_file() and path.suffix in {'.json', '.py', '.md'})
    spec['ownedPaths'].append(relative(BATCH / 'serve_review.cjs'))
    save(BATCH / 'local/review-notes-20261110/scoped-commit-spec.json', spec)


if __name__ == '__main__':
    main()
