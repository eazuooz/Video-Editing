"""Record one selected review after inspecting the exact encoded sample grid."""

import argparse
from datetime import datetime
from pathlib import Path

from assemble_planned import HERE, common
from build_review_index import main as build_review_index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('episode')
    parser.add_argument('--visual-check', required=True)
    parser.add_argument('--point', action='append', nargs=2, metavar=('SECONDS', 'LABEL'), required=True)
    parser.add_argument('--audition-note', action='append', default=[])
    args = parser.parse_args()
    episode = args.episode
    selection = common.load(common.ROOT / 'shared/publishing/video-production-control.json')[
        'designSpecifics18Selected20261111']
    assert episode in selection['episodes'] and not selection['youtubeAuthorized']
    folder = common.OUTPUT.parent / episode
    result = common.load(folder / 'delivery.json')
    assert result['episode'] == episode and result['stage'] == 'encoded-sample-review-pending'
    assert result['technicalQa'] and not result['humanReviewed'] and not result['platformChanged']
    assert all(common.sha(entry['path']) == entry['sha256'] for entry in result['files'])
    master = next(file for file in result['files'] if file['path'].endswith('.captioned.mp4'))
    proof = common.load(common.MEDIA / f'{episode}-assembly' / 'qa' / 'sample-proof.json')
    assert proof['masterSha256'] == master['sha256']
    assert Path(proof['finalFrameGrid']).is_file() and proof['sampleTimes']
    assert min(proof['asrCharacterCoverage'].values()) >= .93
    proof.pop('stage')
    proof.update(visualCheck=args.visual_check, auditionNotes=args.audition_note)
    points = [{'seconds': float(seconds), 'label': label} for seconds, label in args.point]
    assert all(0 <= point['seconds'] < proof['durationSeconds'] for point in points)

    plan = common.load(HERE / 'local' / episode / 'render-plan.json')
    review_path = HERE / episode / 'delivery-review.json'
    ready = 'local-final-review-ready'
    result.update(stage=ready, masterSha256=master['sha256'], durationSeconds=proof['durationSeconds'],
                  reviewPoints=points, qa=proof, reviewIndex=str(folder / 'index.html'), renderPlan=plan)
    common.save(folder / 'delivery.json', result)
    common.save(review_path, result)

    batch_path = HERE / 'batch.json'
    batch = common.load(batch_path)
    item = next(row for row in batch['episodes'] if row['id'] == episode)
    item.update(stage=ready, status=ready, masterSha256=result['masterSha256'],
                next='Local review by user.', deliveryManifest=review_path.relative_to(common.ROOT).as_posix(),
                reviewPage=f'http://127.0.0.1:9298/{episode}/')
    batch['qaCounts']['completeMasters'] = sum(row['stage'] == ready for row in batch['episodes'])
    batch['updatedAt'] = datetime.now().astimezone().isoformat()
    next_episode = next((row['id'] for row in batch['episodes'] if row['stage'] != ready), None)
    batch['status'] = (f'DS01-{episode}-local-review-ready-{next_episode}-production-active' if next_episode
                       else 'all-18-local-final-review-ready')
    common.save(batch_path, batch)
    build_review_index()


if __name__ == '__main__':
    main()
