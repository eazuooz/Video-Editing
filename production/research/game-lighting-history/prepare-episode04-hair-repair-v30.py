"""Scoped repair after reading every v29 board; no narration/model regeneration."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=lambda p:{'path':p.relative_to(R).as_posix(),'sha256':sha(p)}
def write(p,j):
 assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
plan=read(P/'hair-chapter-review-plan-v29.json');old=read(P/'hair-chapter-review-build-v29.json');ex=read(P/'hair-chapter-review-execution-v29.json')
review=read(P/'hair-encoded-direct-review-v29.json');assert review['allPlannedSamplesDirectlyViewed'] and review['rejected']
assert len(ex['results'])==len(plan['cuts'])==12
changed=[]
for c,ref in zip(plan['cuts'],ex['results']):
 assert c['id']==ref['id'] and c['frames']==ref['frames'] and sha(R/ref['path'])==ref['sha256']
 if c.get('annotation',{}).get('type')=='hair-input-result':
  assert c['annotation']['screenIntervals'][0]['boxes'][0]==[1325,430,285,55,'0xF6D872']
  c['annotation']['screenIntervals'][0]['boxes'][0]=[1264,389,265,28,'0xF6D872']
  c['annotation']['note']+='; yellow rectangle explicitly encloses MelaninMainColor row, sampled full native frame hair-19.png checked at1920x1080'
  changed.append(c['id'])
 else:c['reuseEncodedCut']={**ref,'reusedByteIdentical':True}
cue=next(c for c in plan['cues'] if c['id']==229);previous=cue['text'];cue['text']='빨강이 앞이면 빨강 기여는 영 점 오,\n파랑은 영 점 이오입니다.'
assert ''.join(previous.split())==''.join(cue['text'].split())
plan.update({'preparedAt':datetime.now(timezone.utc).isoformat(),'scope':'Scoped repair: native MelaninMainColor rectangle and cue229 wrapping; preserve11 encoded cuts and full chapter PCM/AAC','supersededPlan':proof(P/'hair-chapter-review-plan-v29.json'),'priorBuild':proof(P/'hair-chapter-review-build-v29.json'),'rejectedReview':proof(P/'hair-encoded-direct-review-v29.json'),'cleanCaptionBoundaryAudit':proof(P/'hair-clean-captioned-boundary-audit-v32.json'),'changes':{'cuts':changed,'cueIds':[229],'timingChanged':False,'pcmChanged':False,'aacReencoded':False,'boundaryFinding':'Full1920pixel direct views f43/f1827 show matching clean/captioned cuts. Numerical audit must disable filter reinit across source metadata changes; v30/v31 raw audits are historical incomplete comparisons.'}})
write(P/'hair-chapter-review-plan-v30.json',plan)
src=R/'production/research/game-lighting-history/build-episode04-hair-chapter-v29.py';s=src.read_text('utf-8').replace('v29','v30').replace('V29','V30')
s=s.replace("for key in ['selection','assembly','captionDraft','nativeReview']:","for key in ['selection','assembly','captionDraft','nativeReview','priorBuild','rejectedReview','cleanCaptionBoundaryAudit']:")
oldAudio=old['outputs'][0]['path']
s=s.replace("'-i',audio,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2'",f"'-i',ROOT/'{oldAudio}','-map','0:v:0','-map','1:a:0','-c','copy'")
s=s.replace("'total':10","'total':12").replace('all107.6s original PCM','all142.96s original PCM')
s=s.replace("'captionCues':34,","'captionCues':34,'reusedEncodedCuts':11,'aacReencoded':False,")
dest=src.with_name('build-episode04-hair-chapter-v30.py');assert not dest.exists();dest.write_text(s,'utf-8');compile(s,str(dest),'exec')
print(json.dumps({'plan':proof(P/'hair-chapter-review-plan-v30.json'),'changedCuts':changed,'reusedCuts':11,'rewrappedCue':229,'newTts':0,'newGitImages':0}))
