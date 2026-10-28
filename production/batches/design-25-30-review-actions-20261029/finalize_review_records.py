"""Close this finite batch at local review and outstanding platform declarations."""
from pathlib import Path
import datetime, json, subprocess, sys
from scoped_json import load, patch

ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).resolve().parent
KEY = BATCH.name
REVISIONS = {'D25':'limited-color-world','D29':'kind-to-beginners'}
UPLOADS = {'D26':'computer-controlled-players','D27':'in-game-cutscenes','D28':'start-with-climax','D30':'respect-player-time'}

def main():
    revisions = {ep:load((ROOT/f'projects/{slug}/production/clarity-v3/review-status.json').read_bytes()) for ep,slug in REVISIONS.items()}
    assert all(r['status']=='local-review-ready' and r['fourOutputsVerified'] is True for r in revisions.values())
    uploads = {ep:load((ROOT/f'projects/{slug}/production/upload-20261029/youtube-progress.json').read_bytes()) for ep,slug in UPLOADS.items()}
    assert all(p['uploadComplete'] and p['status']=='available-settings-complete-private-upload-draft' for p in uploads.values())
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    control = ROOT/'shared/publishing/video-production-control.json'
    before = control.read_bytes()
    entry = load(before)['finiteBatchAuthorizations'][KEY]
    assert entry['gpuAuthorized'] and not entry['schedulingAuthorized'] and not entry['deleteAuthorized'] and not entry['driveAuthorized']
    entry.update(status='local-reviews-ready-private-drafts-user-fields-pending',updatedAt=now,
        completedLocalRevisions=list(REVISIONS),humanReviewPendingEpisodeIds=list(REVISIONS),
        privateDraftUploads=list(UPLOADS),platformFinalSavedEpisodeIds=[ep for ep,p in uploads.items() if p.get('finalWorkflowSaved')],
        localReviewIndex='output/game-design-25-29-clarity-v3-20261029/index.html',
        remainingPlatformItems={ep:p['remaining'] for ep,p in uploads.items()})
    after=patch(before,['finiteBatchAuthorizations',KEY],entry)
    assert control.read_bytes()==before,'Concurrent control edit; preserve and retry'
    control.write_bytes(after)
    checkpoint=BATCH/'checkpoint.json'; state=load(checkpoint.read_bytes())
    state.update(status=entry['status'],updatedAt=now,resourceSlot=None,
        revisions={ep:f"local-review-ready-four-outputs-{r['durationSeconds']}s-1920x1080-60fps-human-review-pending" for ep,r in revisions.items()},
        next='User reviews D25/D29 corrected local masters. Four private drafts await user ad self-assessment and AI-field confirmation before final save. No new production, public publication, scheduling, deletion, Drive or automatic continuation.')
    checkpoint.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for script in ['update_scoped_worklist.py','build_review_hub.py']:
        subprocess.run([sys.executable,'-X','utf8',str(BATCH/script)],cwd=ROOT,check=True)
    print(json.dumps({'status':entry['status'],'revisions':{ep:r['captionedSha256'] for ep,r in revisions.items()},'platformMutation':False,'gitMutation':False}))

if __name__=='__main__':main()
