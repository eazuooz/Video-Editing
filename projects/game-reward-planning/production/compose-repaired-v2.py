"""Create separate current speech chunks; retain original files and unaffected PCM."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-reward-planning';WORK=BASE/'production/repair1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pcm(p):
 x,r=sf.read(p,dtype='int16');assert r==24000 and x.ndim==1;return x
proof_file=WORK/'v2-composite-proof.json'
assert not proof_file.exists(),'Composites already exist; review current ASR instead.'
request=read(WORK/'request.json');review=read(WORK/'direct-review.json')
for x in request['inputLocks']:assert sha(ROOT/x['path'])==x['sha256']
accepted={x['id']:x for x in review['scenes'] if x['decision']=='content-readback-pass'}
assert set(accepted)=={'02a','08b'}
v1=ROOT/'shared/output/narration/game-reward-planning/qwen3-1.7b-balanced-v1'
v2=ROOT/'shared/output/narration/game-reward-planning/qwen3-1.7b-balanced-v2'
assert not v2.exists(),'Never overwrite current speech.'
for sid,h in request['originalWavLocks'].items():assert sha(v1/'chunks'/f'{sid}-scene.wav')==h
for x in accepted.values():
 assert sha(ROOT/x['audio'])==x['audio_sha256']
 assert sha(ROOT/x['asr'])==x['asr_sha256']
 assert read(ROOT/x['asr'])['audio_sha256']==x['audio_sha256']
bound={x['scene']:x for x in read(WORK/'boundaries.json')['scenes']}
patches={'02':('02a',0,bound['02']['quietPoints'][0]['sample']),'08':('08b',bound['08']['quietPoints'][0]['sample'],bound['08']['quietPoints'][1]['sample'])}
for sid in request['originalWavLocks']:
 if sid not in patches:assert read(v1/'asr'/f'{sid}.json')['audio_sha256']==sha(v1/'chunks'/f'{sid}-scene.wav')
(v2/'chunks').mkdir(parents=True);(v2/'asr').mkdir()
rows=[]
for sid in [f'{n:02}' for n in range(1,14)]:
 source=v1/'chunks'/f'{sid}-scene.wav';dest=v2/'chunks'/source.name
 if sid not in patches:
  shutil.copy2(source,dest);shutil.copy2(v1/'asr'/f'{sid}.json',v2/'asr'/f'{sid}.json')
  assert sha(source)==sha(dest)
  rows.append({'scene':sid,'source':source.relative_to(ROOT).as_posix(),'sourceSha256':sha(source),'composite':dest.relative_to(ROOT).as_posix(),'compositeSha256':sha(dest),'wholeWaveByteIdentical':True,'seconds':sf.info(dest).duration,'currentAsrCopiedWithVerifiedHash':True})
  continue
 cid,a,b=patches[sid];old=pcm(source);candidate=pcm(ROOT/accepted[cid]['audio']);assert 0<=a<b<=len(old)
 parts=[];retained=[]
 if a:
  parts.extend([old[:a],np.zeros(2400,dtype=np.int16)]);retained.append({'sourceFromSample':0,'sourceToSample':a,'compositeFromSample':0,'samples':a,'pcmSha256':hashlib.sha256(old[:a].tobytes()).hexdigest()})
 offset=sum(len(x) for x in parts);parts.extend([candidate,np.zeros(2400,dtype=np.int16)])
 after_offset=sum(len(x) for x in parts);parts.append(old[b:])
 retained.append({'sourceFromSample':b,'sourceToSample':len(old),'compositeFromSample':after_offset,'samples':len(old)-b,'pcmSha256':hashlib.sha256(old[b:].tobytes()).hexdigest()})
 combined=np.concatenate(parts);sf.write(dest,combined,24000,subtype='PCM_16');decoded=pcm(dest);assert np.array_equal(decoded,combined)
 for x in retained:assert hashlib.sha256(decoded[x['compositeFromSample']:x['compositeFromSample']+x['samples']].tobytes()).hexdigest()==x['pcmSha256']
 rows.append({'scene':sid,'source':source.relative_to(ROOT).as_posix(),'sourceSha256':sha(source),'composite':dest.relative_to(ROOT).as_posix(),'compositeSha256':sha(dest),'seconds':len(decoded)/24000,'originalSeconds':len(old)/24000,'retainedPcm':retained,'replacement':{'candidateId':cid,'audio':accepted[cid]['audio'],'audioSha256':accepted[cid]['audio_sha256'],'sourceRemovedSamples':[a,b],'compositeFromSample':offset,'samples':len(candidate)},'fullCompositeAsrReviewed':False,'silenceAtInternalSeamsSeconds':0.1})
manifest=read(BASE/'project.json');manifest['tts'].update(outputDir=v2.relative_to(ROOT).as_posix(),filenameStem='game-reward-planning-qwen3-1.7b-balanced-v2')
for field,ext in [('narration','.wav'),('captionsKo','.srt'),('captionsEn','.en.srt')]:manifest['paths'][field]=(v2/('game-reward-planning-qwen3-1.7b-balanced-v2'+ext)).relative_to(ROOT).as_posix()
write(WORK/'v2.manifest.json',manifest)
write(proof_file,{'status':'separate-v2-awaiting-full-current-ASR-and-seams','createdAt':datetime.now(timezone.utc).isoformat(),'unchangedParagraphs':50,'all7ExplanationWholeWavsByteIdentical':True,'candidateReview':(WORK/'direct-review.json').relative_to(ROOT).as_posix(),'candidateReviewSha256':sha(WORK/'direct-review.json'),'allOriginal13WavsRetained':True,'scenes':rows,'humanListening':'pending','finalTimingApproved':False})
print(json.dumps({'status':'separate-v2-created','seconds':[{'scene':x['scene'],'seconds':x['seconds']} for x in rows]},ensure_ascii=False))
