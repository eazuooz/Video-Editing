"""Correct two sampled word/action mismatches without replacing any current PCM.

Flight is moved from an already reviewed observation tail. Both scenes retain
their native unique frame total, duration and entire speech. A quiet10p1/p2
pause moves the spoken Pepper name to the first Pepper image, not a Plucky boat.
Final mix/join/caption/framing approvals remain separate.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy,hashlib,json
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat(); dest=BASE/'measured-edit-v5';assert not dest.exists()
context_path=BASE/'measured-edit-v4/rocket-flight-context-local/execution.json';context=read(context_path)
assert context['exitCode']==0 and len(context['images'])==12
for r in context['images']+context['sheets']:
 assert sha(ROOT/r['path'])==r['sha256'];r.update(directlyRead=True,directlyReadAt=now)
context.update(status='closed12-flight-context-images-directly-read',updatedAt=now)
context_path.write_text(json.dumps(context,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan=copy.deepcopy(read(BASE/'measured-edit-v4/plan.json'));plan['createdAt']=now
s6=next(s for s in plan['scenes'] if s['id']=='06');s10=next(s for s in plan['scenes'] if s['id']=='10');s12=next(s for s in plan['scenes'] if s['id']=='12')
flight=next(c for c in s6['segments'] if c['id']=='06-p5-action-64-4860-5270')
combat=next(c for c in s12['segments'] if c['id']=='12-p1-action-71-9690-9990')
enemy=next(c for c in s6['segments'] if c['id']=='06-p5-action-63-4542-4710')
def piece(c,sid,p,a,z):
 out=copy.deepcopy(c);assert c['sourceStartFrame']<=a<z<=c['sourceEndFrameExclusive'] and c['nativeFps']==60
 out.update(id=f'{sid}-p{p}-{c["bankCutId"]}-{a}-{z}',paragraph=p,
  sourceStartFrame=a,sourceEndFrameExclusive=z,startFrame=a,endFrameExclusive=z,
  inSeconds=a/60,outSeconds=z/60,nativeSeconds=(z-a)/60,seconds=(z-a)/60,frames=z-a,
  nativeToOutputQuantizationFrames=0,finalApproved=False,captionPixelsApproved=False,mediaCompiled=False)
 return out
#12p1's named rocket phrase now starts over an already observed ascent.
# The remaining distinct desk combat appears only after the specific verbs.
replacement=[piece(flight,'12',1,4960,5080),piece(combat,'12',1,9810,9990)]
idx=s12['segments'].index(combat);s12['segments'][idx:idx+1]=replacement
#06p5 keeps a visible descent/landing at the start of its negative flight claim.
# Distinct preparation/enemy/combat follow under the observed/unconfirmed caution;
# no refill, unlimited flight or causal continuity is inferred across cuts.
ix=s6['segments'].index(enemy)
assert s6['segments'][ix+1]['id']==flight['id']
s6['segments'][ix:ix+2]=[piece(flight,'06',5,5080,5270),piece(flight,'06',5,4860,4960),enemy,piece(combat,'06',5,9690,9810)]
for s in [s6,s12]:
 cursor=0
 for c in s['segments']:
  c.update(localFromFrame=cursor,startFrame=s['startFrame']+cursor);cursor+=c['frames'];c['endFrameExclusive']=s['startFrame']+cursor
 assert cursor==s['frames']
# Preserve10p1/p2 as one PCM run around a new pause in the actual quiet gap.
x,sr=sf.read(ROOT/s10['audio'],dtype='float32');assert sr==24000 and sha(ROOT/s10['audio'])==s10['audioSha256']
choices=[]
for k in range(round(9.92*sr),round(10.10*sr),24):
 q=x[k-192:k+192];choices.append((float(np.sqrt(np.mean(q*q))),k,float(np.max(np.abs(q)))))
rms,boundary,peak=min(choices);assert rms<.001 and 9.84<boundary/sr<10.18
end=s10['speechEvidence'][1]['pcmToSample'];target_frames=sum(c['frames'] for c in s10['segments'] if c['paragraph'] in [1,2]);target_samples=target_frames*400
pause=target_samples-end;assert pause==19720
old=s10['pcmPlacement'];tail=[p for p in old if p.get('fromSample',-1)>=end or p.get('outputFromSample',-1)>=target_samples]
# Exclude the old p2 tail, retaining p3 onward byte-for-byte placement.
tail=[p for p in tail if p['outputFromSample']>=target_samples]
s10['pcmPlacement']=[{'kind':'preserved-current-PCM','fromSample':0,'toSample':boundary,'outputFromSample':0,'outputToSample':boundary},
 {'kind':'inserted-silence','samples':pause,'outputFromSample':boundary,'outputToSample':boundary+pause,'reason':'Quiet pause before the spoken Pepper name; preserve the continuous p1/p2 PCM rather than assigning the game name to a Plucky boat.'},
 {'kind':'preserved-current-PCM','fromSample':boundary,'toSample':end,'outputFromSample':boundary+pause,'outputToSample':target_samples}]+tail
assert s10['pcmPlacement'][-1]['outputToSample']==s10['frames']*400
for s in plan['scenes']:
 kept=[p for p in s['pcmPlacement'] if p['kind']=='preserved-current-PCM']
 assert kept[0]['fromSample']==0 and kept[-1]['toSample']==s['samples']
 assert sum(p['toSample']-p['fromSample'] for p in kept)==s['samples']
 assert all(a['toSample']==b['fromSample'] for a,b in zip(kept,kept[1:]))
cuts=[c for s in plan['scenes'] for c in s['segments'] if c['classification']=='actual-existing-game']
assert len(cuts)==111 and sum(c['frames'] for c in cuts)==18833
for source in {c['sourceVideoId'] for c in cuts}:
 rows=sorted([c for c in cuts if c['sourceVideoId']==source],key=lambda c:c['sourceStartFrame'])
 assert all(a['sourceEndFrameExclusive']<=b['sourceStartFrame'] for a,b in zip(rows,rows[1:]))
evidence={'schemaVersion':1,'reviewedAt':now,'status':'two-word-action-corrections-proposed-current-PCM-preserved',
 'flightContext':context_path.relative_to(ROOT).as_posix(),'imagesRead':context['images'],'sheetsRead':context['sheets'],
 'observations':['4960–5030 show flame-driven upward travel;5060–5090 descend.5100/5130 reach the card,5160/5190 stand/move on it.',
  'Select4960–5080 for12p1; do not label the entire original4860–5270 excerpt as ascent.',
  '12p1 rocket phrase7.96–9.50 now bridges into flight8.10–10.10, followed by distinct combat/blue-surface observations.',
  '06p5 negative flight/refill caution retains a descent/landing, separate preparation and enemy actions. No edit is claimed as one continuous operation.'],
 'newSourceSeconds':0,'repeatedNativeFrames':0,'allCurrent15PcmPreserved':True,'newGitImages':0,
 '10p1p2QuietBoundary':{'sample':boundary,'seconds':boundary/sr,'rms16ms':rms,'peak16ms':peak,'insertedSamples':pause,'insertedSeconds':pause/sr,
 'PepperWordSourceSeconds':10.18,'PepperWordOutputLocalSeconds':10.18+pause/sr,'firstPepperFrameLocal':660,'newJoinAsrApproved':False},
 'finalTimingApproved':False,'finalCaptionPixelsApproved':False,'finalMixCreated':False}
plan.update(actualSourceCuts=111,status='current15-word-aligned-candidate-all-final-framing-and-mix-pending',
 previousCandidate={'path':'projects/avoid-game-comparisons/production/measured-edit-v4/plan.json','sha256':sha(BASE/'measured-edit-v4/plan.json')},
 wordActionCorrections=evidence,finalTimingApproved=False,bodyRatioApproved=False,allCaptionPixelsReviewed=False)
plan['quietInternalBoundaryReviews'].append(evidence['10p1p2QuietBoundary'])
plan['sourceReallocation']['wordAlignment']='Specific fight/stair/desk verbs retained;12p1 now uses4960–5080 actual flight at8.1s. Final source/caption pixels and quiet-join ASR still pending.'
plan['flaggedNativeCorrections']['12p1']='Reallocate the existing distinct flight4960–5080 into the spoken rocket phrase, transfer desk combat9690–9810 to06p5 observation tail; no new actual time or native repeats.'
dest.mkdir();(dest/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(BASE/'word-action-alignment-review-v5.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'actualFrames':18833,'explanationFrames':plan['explanationFrames'],'cuts':111,'ratioErrorFrames':plan['body60_40ErrorFrames'],'newFlightImagesRead':12,'newSourceSeconds':0,'quietPauseSeconds':pause/sr}))
