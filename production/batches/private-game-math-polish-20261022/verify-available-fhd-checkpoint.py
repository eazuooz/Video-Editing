"""Verify partial restore receipts and prepare an explicit owned-file commit."""
import datetime,subprocess
from polish_common import *
owned=[B/name for name in [
 'restore-gameplay.py','review-restored-sources.py','restore-available-fhd.py',
 'restore-available-guides.py','preflight-available-guides.py','moving-available-guide-preflight.py',
 'sample-m17-available-targets.py','plan-m17-available-guides.py','record-available-fhd-review.py',
 'verify-available-fhd-checkpoint.py','progress.py','available-fhd-job.json','gameplay-restoration-status.json',
 'portal-fhd-format-search.json','fhd-remaining-research.json','checkpoint.json','source-blockers.json','queue.json',
]]
sources={};clips=0
for ident in ['M10','M11','M12','M17']:
 e=Episode(ident);e.authorized();restored=read(e.H/'gameplay-restoration.json')
 for sid,record in restored['scenes'].items():
  slot=next(s for s in e.T['scenes'] if s['id']==sid)
  assert record['frames']==round(slot['seconds']*60)
  assert record['speed']==1 and record['originalCutOrderAndDuration']
  assert sha(R/record['path'])==record['sha256']
  e.verify(R/record['path'],record['frames']);clips+=1
  for part in record['sources']:
   source=part['source']
   if source not in sources:
    v=video(R/source);assert v['height']>=1080 and v['width']>=1920
    sources[source]={'width':v['width'],'height':v['height'],'sha256':sha(R/source)}
   assert sources[source]['sha256']==part['sourceSha256']
 review=read(e.H/'available-guides-review.json')
 assert sha(R/review['preflight'])==review['preflightSha256']
 assert sha(R/review['selectedPlayback'])==review['selectedPlaybackSha256']
 assert review['fullMasterReady'] is False and review['humanReview']=='pending'
 owned.extend(e.H/name for name in ['gameplay-restoration.json','restored-source-review-actual.json',
  'available-annotation-registry.json','restored-available-guides.json','observed-guide-composition.json',
  'observed-guide-preflight.json','moving-available-guide-preflight.json','available-guides-review.json',
  'available-guides-initial-findings.json','lg04-observed-head-repair.json','observed-guides.json',
  'available-guide-targets.json','available-guide-targets-review.json'])
 owned.extend((e.H/'available-tracks').glob('*.json'))
assert clips==16 and len(sources)==3
queue=read(B/'queue.json');assert sum(e['status']=='ready-for-human-review' for e in queue['entries'])==11
cp=read(B/'checkpoint.json');assert not cp['active'] and not cp['currentJobs']
for name in ['shared/publishing/video-worklist.json','docs/VIDEO_WORKLIST.md','docs/GAME_MATH_PRIVATE_POLISH.md']:owned.append(R/name)
report=B/'available-fhd-verification.json'
save(report,{'verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'restoredSlots':clips,
 'sources':sources,'sourceHashAndDimensionsPassed':True,'exactOriginalFrameCountsPassed':True,
 'partialReviewReceiptsPassed':True,'readyFullMasters':11,'remainingFullMasters':5,'humanReview':'pending',
 'newTts':False,'timelineRewrite':False,'platformMutation':False})
owned.append(report)
changed=[]
for path in owned:
 if not path.is_file():continue
 name=rel(path);old=subprocess.run(['git','show','HEAD:'+name],cwd=R,capture_output=True)
 if old.returncode or old.stdout.replace(b'\r\n',b'\n')!=path.read_bytes().replace(b'\r\n',b'\n'):changed.append(name)
out=R/'shared/output/private-game-math-polish-20261022'
save(out/'available-fhd-partial-commit.json',{'paths':sorted(set(changed)),
 'message':'Restore sixteen original FHD math scenes and repair observed guide tracking'})
print('Verified16 FHD slots from3 sources;11 full masters ready;5 incomplete.')
print('Owned changed files:',len(changed))
for path in changed:print(path)
