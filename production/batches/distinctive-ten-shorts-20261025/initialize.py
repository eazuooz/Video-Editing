"""Record only the newly requested finite ten-Short production scope."""
from pathlib import Path
import datetime, json

R = Path(__file__).resolve().parents[3]
B = Path(__file__).parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    ids = ['noita-material-pixels', 'viewfinder-mesh-slicing', 'rain-world-two-chunks',
           'outer-wilds-gravity-falloff', 'obra-dinn-dither-stability',
           'd2r-ultrawide-ai-range', 'd2r-loot-grass-clearance', 'd2-modular-sprite-equipment',
           'd2r-renderer-logic-separation', 'd2r-controller-input-adapter']
    slugs = ['shorts-noita-material-pixels', 'shorts-viewfinder-mesh-slicing',
             'shorts-rain-world-body-chunks', 'shorts-outer-wilds-gravity',
             'shorts-obra-dinn-dithering', 'shorts-d2r-ultrawide-ai-range',
             'shorts-d2r-loot-grass-clearance', 'shorts-d2-modular-sprite-equipment',
             'shorts-d2r-renderer-logic-separation', 'shorts-d2r-controller-input-adapter']
    research = ['shared/publishing/shorts-research/distinctive-ideas-2026-10-25.json',
                'shared/publishing/shorts-research/diablo2-ideas-2026-10-25.json']
    candidates = {c['id']: c for f in research for c in read(R/f)['candidates']}
    auth = dict(id='explicit-ten-distinctive-shorts-20261025', status='active',
                recordedAt=now, userEvidence='10개 제작해줘~', slugs=slugs,
                fullProductionAuthorized=True, intermediateApprovalRequired=False,
                scope='Exactly the five approved general-game topics plus five Diablo II topics through complete local final review. The latest explicit request permits this finite batch; no unrelated resumption.',
                automaticAdvanceWithinThisList=True, advanceOutsideList=False,
                youtubeAuthorized=False, driveAuthorized=False, scheduleAuthorized=False,
                deletionAuthorized=False, humanFinalReviewRequired=True,
                resourcePolicy='Do not occupy GPU while the user game is active. Sequence costly jobs; preserve other applications, jobs and staging.')
    control = read(R/'shared/publishing/video-production-control.json')
    control.setdefault('scopedBatchAuthorizations', {})[auth['id']] = auth
    save(R/'shared/publishing/video-production-control.json', control)
    projects = [dict(order=i+1, slug=s, candidateId=k, title=candidates[k]['title'],
                     status='preproduction', humanReview='pending', platform='not-uploaded')
                for i, (k, s) in enumerate(zip(ids, slugs))]
    save(B/'batch.json', dict(schemaVersion=1, authorization=auth, research=research,
                             revision='distinctive-ten-v1', projects=projects,
                             createdAt=now, finalBoundary='ten complete local review deliveries'))
    work = read(R/'shared/publishing/shorts-worklist.json')
    for row in projects:
        assert not any(x.get('slug') == row['slug'] for x in work['rows']), row['slug']
        work['rows'].append(dict(row, authorization=auth['id'], production='preproduction',
                                 review='pending', youtube='not-uploaded', drive='not-requested',
                                 updatedAt=now))
    work['updatedAt'] = now
    work['latestUserSteering'] = dict(userEvidence='10개 제작해줘~', batch=(B/'batch.json').relative_to(R).as_posix(), recordedAt=now)
    save(R/'shared/publishing/shorts-worklist.json', work)
    save(B/'checkpoint.json', dict(status='preproduction-active', updatedAt=now,
         completedVideos=0, requestedVideos=10, gpu='waiting-for-user-game-to-exit',
         next='Acquire and inspect independent FHD footage; finalize scripts and editable scenes.'))
    print('Registered ten explicitly authorized Shorts; unrelated scopes and platform states preserved.')

if __name__ == '__main__': main()
