"""Preserve v31 evidence, repair one UI cut; no original PCM/model regeneration."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, psutil
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
proof=lambda p:{'path':rel(p),'sha256':sha(p)}
def write(p,j):
 assert not p.exists(),p
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
sessions=[]
for folder,ep,sid in [('episode04-dlss-chapter-v31',P/'dlss-chapter-review-execution-v31.json',75247),('episode04-dlss-encoded-v31',R/'production/research/game-lighting-history/local/episode04-dlss-encoded-v31/execution.json',41725),('episode04-postprocess-native-v32',R/'production/research/game-lighting-history/local/episode04-postprocess-native-v32/execution.json',26771)]:
 s=read(ep);w=s['worker'];assert s['active'] is None and all(c['exitCode']==0 for c in s['commands'])
 try:assert abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01,'Original worker still alive'
 except psutil.NoSuchProcess:pass
 dest=R/'production/research/game-lighting-history/local'/folder/'session.json'
 write(dest,{'sessionId':sid,'worker':w,'terminalCompletionObserved':True,'exitCode':0,'completedAt':s['endedAt'],'verifiedAt':now(),'execution':proof(ep),'originalWorkerAlive':False})
 sessions.append(proof(dest))
exPath=R/'production/research/game-lighting-history/local/episode04-dlss-encoded-v31/execution.json';ex=read(exPath)
assert(len(ex['items']),len(ex['boards']))==(239,61)
boards=[]
for board in ex['boards']:
 assert sha(R/board['path'])==board['sha256']
 boards.append({**board,'directlyViewed':True,'reviewedAt':now(),'reviewContinuity':'clean001-017 and captioned001-024 in preceding context; captioned025-044 completed in current context'})
review={'reviewedAt':now(),'scope':'All239 planned encoded samples on61 boards directly read, sampled sequences only; final moving/audio approval remains pending.','build':proof(P/'dlss-chapter-review-build-v31.json'),'extraction':proof(exPath),'sessions':sessions,'sampleCount':239,'boards':boards,'allPlannedSamplesDirectlyViewed':True,'sampledCaptionClearanceApproved':False,'rejected':True,'findings':['Captioned boards015-020: fixed cues261/262 cover original DLSS4/DLSS4.5 feature labels in lower band; repair native source framing, preserve caption position.','Artist control source8-20.98s shows MODEL AUTOMASK face region and Base Character slider; strength/tone controls remain above captions. Bottom model-template buttons are partly covered and are not used as evidence for the narrated control claim.','NBA2K27 vendor input/output description is labelled separately from this character technology demo. Red face mask becomes unmasked; the later kitchen character is a different source shot, not one controlled same-scene experiment.','One rendered plus3/5 generated display frames is not multiplied simulation/ray work or an input-latency measurement. Numerical diagrams and fixed captions are readable in sampled frames.'],'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'qaApproved':False,'uploaded':False,'newTts':0,'newGitImages':0}
rp=P/'dlss-encoded-direct-review-v31.json';write(rp,review)
plan=read(P/'dlss-chapter-review-plan-v31.json');old=read(P/'dlss-chapter-review-build-v31.json');execution=read(P/'dlss-chapter-review-execution-v31.json')
assert len(execution['results'])==len(plan['cuts'])==9
changed=[]
for c,ref in zip(plan['cuts'],execution['results']):
 assert c['id']==ref['id'] and c['frames']==ref['frames'] and sha(R/ref['path'])==ref['sha256']
 if c['id']=='19-guide-generated-ui-actual-ui-comparison':
  c['shiftUpPixels']=180
  c['framingReason']='Remove top180 rows and pad bottom180 black; retain both DLSS4/4.5 feature labels above fixed boxed captions and preserve comparison reticles. No scaling/time/PCM change.'
  changed.append(c['id'])
 else:c['reuseEncodedCut']={**ref,'reusedByteIdentical':True}
assert len(changed)==1
plan.update({'preparedAt':now(),'scope':'One native UI framing repair; preserve8 encoded clean cuts,6970 frames, full original chapter PCM/AAC and24 caption cues. Sampled final/moving approvals remain pending.','supersededPlan':proof(P/'dlss-chapter-review-plan-v31.json'),'priorBuild':proof(P/'dlss-chapter-review-build-v31.json'),'rejectedReview':proof(rp),'changes':{'cuts':changed,'cueIds':[261,262],'timingChanged':False,'pcmChanged':False,'aacReencoded':False}})
write(P/'dlss-chapter-review-plan-v33.json',plan)
src=R/'production/research/game-lighting-history/build-episode04-hair-chapter-v30.py'
s=src.read_text('utf-8').replace('hair','dlss').replace('Hair','Dlss').replace('v30','v33').replace('V30','V33')
s=s.replace("N==8577 and len(plan['cuts'])==12 and len(plan['entries'])==10 and len(plan['cues'])==34","N==6970 and len(plan['cuts'])==9 and len(plan['entries'])==7 and len(plan['cues'])==24")
s=s.replace(",'cleanCaptionBoundaryAudit'",'').replace("'total':12","'total':9").replace("'captionCues':34,'reusedEncodedCuts':11","'captionCues':24,'reusedEncodedCuts':8")
s=s.replace("if c.get('shiftUpPixels'):vf+=['crop=1920:1020:0:60','pad=1920:1080:0:0:black']","if c.get('shiftUpPixels'):\n   shift=c['shiftUpPixels'];vf+=[f'crop=1920:{1080-shift}:0:{shift}','pad=1920:1080:0:0:black']")
s=s.replace('episode04-dlss-chapter-v29/game-lighting-history-04-dlss-chapter.clean.mp4','episode04-dlss-chapter-v31/game-lighting-history-04-dlss-chapter.clean.mp4')
s=s.replace('142.96s','116.16s').replace('transparency/dlss chapter','postprocess chapter')
dest=src.with_name('build-episode04-dlss-chapter-v33.py');assert not dest.exists();compile(s,str(dest),'exec');dest.write_text(s,'utf-8')
src=R/'production/research/game-lighting-history/extract-episode04-dlss-encoded-v31.py'
s=src.read_text('utf-8').replace('v31','v33').replace('V31','V33')
s=s.replace('for c in metrics:',"for c in [m for m in metrics if m['id'] in [261,262]]:")
s=s.replace("for c in plan['cuts']:\n  for frame,name", "for c in [cut for cut in plan['cuts'] if cut['id']=='19-guide-generated-ui-actual-ui-comparison']:\n  for frame,name")
s=s.replace("[c for c in plan['cuts'] if c['kind']=='actual']","[c for c in plan['cuts'] if c['id']=='19-guide-generated-ui-actual-ui-comparison']")
dest=src.with_name('extract-episode04-dlss-scoped-v33.py');assert not dest.exists();compile(s,str(dest),'exec');dest.write_text(s,'utf-8')
cp=R/'production/research/game-lighting-history/checkpoint.json';j=read(cp)
j['episode04DlssEncodedDirectReviewV31']={**proof(rp),'sampleCount':239,'boards':61,'rejected':True,'allFinalPixelsReviewed':False}
j['ownedActiveWork']={'status':'no-active-owned-media-worker','next':'Run one CPU2 DLSS native-framing repair, then scoped encoded QA; postprocess native direct review continues.'}
j['updatedAt']=now();tmp=cp.with_suffix('.dlss-repair-v33.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cp)
print(json.dumps({'review':proof(rp),'changedCuts':changed,'reusedCuts':8,'newTts':0,'newGitImages':0}))
