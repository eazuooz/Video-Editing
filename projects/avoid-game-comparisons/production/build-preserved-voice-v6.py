"""Place reviewed PCM samples once, inserting only the measured quiet intervals."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v6';DEST=WORK/'placed-voice-local'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
assert not DEST.exists();DEST.mkdir()
plan=read(WORK/'plan.json');results=[]
for s in plan['scenes']:
 p=ROOT/s['audio'];assert sha(p)==s['audioSha256'];x,sr=sf.read(p,dtype='int16',always_2d=True)
 assert sr==24000 and len(x)==s['samples'] and sf.info(p).subtype=='PCM_16'
 y=np.zeros((s['frames']*400,x.shape[1]),dtype=np.int16);coverage=[]
 for a in s['pcmPlacement']:
  if a['kind']=='preserved-current-PCM':
   fragment=x[a['fromSample']:a['toSample']];y[a['outputFromSample']:a['outputToSample']]=fragment
   coverage.append(dict(sourceFrom=a['fromSample'],sourceTo=a['toSample'],outputFrom=a['outputFromSample'],outputTo=a['outputToSample'],pcmSha256=hashlib.sha256(fragment.tobytes()).hexdigest()))
 assert sum(a['sourceTo']-a['sourceFrom'] for a in coverage)==len(x)
 out=DEST/f"{s['id']}-placed.wav";sf.write(out,y,sr,subtype='PCM_16');z,rate=sf.read(out,dtype='int16',always_2d=True)
 assert rate==sr and np.array_equal(z,y)
 for a in coverage:assert np.array_equal(z[a['outputFrom']:a['outputTo']],x[a['sourceFrom']:a['sourceTo']])
 results.append(dict(sceneId=s['id'],path=rel(out),sha256=sha(out),sourcePath=s['audio'],sourceSha256=s['audioSha256'],sourceSamples=len(x),outputSamples=len(z),seconds=len(z)/sr,preservedSpans=coverage,allCurrentPcmSamplesIdentical=True))
state=dict(schemaVersion=1,createdAt=datetime.now(timezone.utc).isoformat(),plan=rel(WORK/'plan.json'),planSha256=sha(WORK/'plan.json'),sampleRate=24000,results=results,newSynthesis=0,all15CurrentPcmPreserved=True,editedVoiceCreated=True,finalMixBuilt=False,editedJoinAsrApproved=False)
(WORK/'placed-voice-index.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
contexts=[]
for sid in ['10','12','13']:
 s=next(s for s in plan['scenes'] if s['id']==sid);r=next(r for r in results if r['sceneId']==sid)
 contexts.append(dict(id=f'{sid}-whole-edited-voice',audioPath=r['path'],audioSha256=r['sha256'],fromSeconds=0,toSeconds=r['seconds'],expectedKo='\n\n'.join(p['ko'] for p in s['speechEvidence']),scope='Entire edited scene; current PCM retained and newly inserted quiet joins checked.'))
for sid,a,z,label in [('10',7.5,15,'quiet-before-Pepper'),('12',1.5,7,'general-to-specific'),('12',20,31,'observed-to-cost')]:
 r=next(r for r in results if r['sceneId']==sid)
 contexts.append(dict(id=f'{sid}-{label}',audioPath=r['path'],audioSha256=r['sha256'],fromSeconds=a,toSeconds=z,expectedKo='',scope='Independent context without expected-text prompting; compare the whole-script context directly.'))
(WORK/'edited-join-asr-request.json').write_text(json.dumps(dict(createdAt=state['createdAt'],planSha256=state['planSha256'],contexts=contexts,protectedInputs=[dict(path=r['sourcePath'],sha256=r['sourceSha256']) for r in results]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(scenes=len(results),preservedSamples=sum(r['sourceSamples'] for r in results),newSynthesis=0,asrRequests=len(contexts),finalMixBuilt=False)))
