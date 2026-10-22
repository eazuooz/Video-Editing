"""Verify delivered files against existing QA; never infer human approval."""
import datetime
from polish_common import *
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
q=read(B/'queue.json');reports=[]
assert [x['id'] for x in q['entries']]==[f'M{i:02}' for i in range(5,21)]
for entry in q['entries']:
 e=Episode(entry['id']);manifest=read(e.H/'outputs.json');qa=read(e.H/'technical-qa.json');v=read(e.H/'visual-review.json')
 assert sha(e.P/'production/timeline.json')==entry['originalTimelineSha256']==qa['originalTimelineSha256']
 assert len(manifest['outputs'])==4
 checked=[]
 for item in manifest['outputs']:
  p=R/item['path'];assert p.is_file() and p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],str(p)
  checked.append(item)
 movies={x['kind']:x for x in qa['outputs']}
 assert set(movies)=={'clean','captioned'}
 frames=round(entry['seconds']*60)
 for kind,x in movies.items():
  assert x['fullDecode'] and x['resolution']==[1920,1080] and x['fps']=='60/1' and x['frames']==frames
  assert x['timestamps']['contiguous']
  assert x['sha256']==next(y['sha256'] for y in checked if y['path'].endswith(f'.{kind}.mp4'))
 assert movies['clean']['unchangedRecoveredDecodedPcmSha256']==movies['captioned']['unchangedRecoveredDecodedPcmSha256']
 assert qa['wordsAndCueTimesPreserved'] and not qa['newTts'] and not qa['newMusic']
 assert v['status']=='passed' and v['captionedSha256']==movies['captioned']['sha256'] and v['humanReview']=='pending'
 assert (e.D/'index.html').is_file()
 manifest.update(technicalQa='passed',technicalQaEvidence=rel(e.H/'technical-qa.json'),directVisualReview=rel(e.H/'visual-review.json'),humanReview='pending',uploadAuthorized=False)
 save(e.H/'outputs.json',manifest)
 reports.append({'id':e.id,'title':entry['title'],'status':'ready-for-local-human-review','frames':frames,'outputs':checked,'technicalQa':rel(e.H/'technical-qa.json'),'visualReview':rel(e.H/'visual-review.json'),'index':rel(e.D/'index.html'),'humanReview':'pending'})
report={'checkedAt':now,'status':'passed','episodes':reports,'episodeCount':len(reports),'outputCount':sum(len(x['outputs']) for x in reports),'newRender':False,'newTts':False,'platformMutation':False,'humanReview':'pending','scope':'Rehashed all64 delivered files and unchanged timelines. Reused hash-bound full decode, frame/timestamp, preserved recovered audio/caption and actual visual QA evidence. No claim of new whole-film listening or original lossless PCM recovery.','originalResolutionExceptions':rel(B/'portal-original-resolution-exception.json')}
save(B/'final-delivery-audit.json',report)
cp=read(B/'checkpoint.json');cp.update(updatedAt=now,status='all-sixteen-ready-for-local-human-review',active=[],blocked=[],currentJobs=[])
cp['latestStatusReport']={'at':now,'ready':16,'incomplete':0,'sourceBlockers':0,'activeMediaWorkerObserved':False,'workerStatusFile':rel(B/'approved-portal-finish-job.json'),'pendingNewWholeMasters':False}
cp['finalDeliveryAudit']={'path':rel(B/'final-delivery-audit.json'),'sha256':sha(B/'final-delivery-audit.json'),'outputs':64,'humanReview':'pending'}
cp['nextAction']='All16 local outputs are ready for human review. Stop only dedicated automation16, selectively commit/push, then await user review. No next-video or platform action.'
cp['sourceReplacementDecision']['status']='completed-local-review-pending'
save(B/'checkpoint.json',cp)
w=read(R/'shared/publishing/video-worklist.json');w['privateMathPolish'].update(status='all-sixteen-ready-for-local-human-review',finalDeliveryAudit=cp['finalDeliveryAudit']);w['privateMathPolish']['sourceReplacementDecision']['status']='completed-local-review-pending';save(R/'shared/publishing/video-worklist.json',w)
c=read(R/'shared/publishing/video-production-control.json');a=c['scopedBatchAuthorizations']['private-math-overnight-polish-20261022'];a.update(status='completed-local-review-pending',completedAt=now,automaticAdvanceWithinThisList=False,finalDeliveryAudit=cp['finalDeliveryAudit']);a['sourceReplacementDecision']['status']='completed-local-review-pending';c['updatedAt']=now;save(R/'shared/publishing/video-production-control.json',c)
print('PASS:16 episodes,64 actual files,32 current1080p60 masters. Human review pending.')
