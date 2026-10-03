"""Apply directly accepted candidates while preserving every unaffected PCM byte."""
from pathlib import Path
import hashlib, json, shutil, sys
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/motion-sickness-games'
WORK=BASE/'production/repair1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pcm(p):
 x,sr=sf.read(p,dtype='int16');assert sr==24000 and x.ndim==1
 return x
proof_path=WORK/'v2-composite-proof.json'
if proof_path.exists():raise RuntimeError('Composites already exist; inspect their ASR rather than repeating.')
request=read(WORK/'request.json')
for entry in request['inputs']:assert sha(ROOT/entry['path'])==entry['sha256'],entry['path']
review=read(WORK/'direct-review.json')
accepted={entry['scene']:entry for entry in review['scenes'] if entry['decision']=='content-readback-pass'}
expected={edit['id'] for edit in request['edits']}
assert set(accepted)==expected,'All seven candidate paragraphs must pass direct current-hash review.'
candidate=ROOT/'shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1-phrase-repair1'
for sid,entry in accepted.items():assert sha(candidate/'chunks'/f'{sid}-scene.wav')==entry['audio_sha256']
v1=ROOT/'shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1'
v2=ROOT/'shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v2'
if v2.exists() and any(v2.rglob('*.wav')):raise RuntimeError('Do not overwrite an existing v2 speech package.')
splices={s['scene']:s for s in read(WORK/'splice-plan.json')['scenes']}
# Validate every source and duration before writing any partial speech package.
# A short candidate must leave v2 absent so the accepted source remains usable.
for sid in [f'{n:02}' for n in range(1,13)]:
 source=v1/'chunks'/f'{sid}-scene.wav'
 original_info=sf.info(source);assert original_info.samplerate==24000 and original_info.channels==1
 if sid not in splices:
  assert read(v1/'asr'/f'{sid}.json')['audio_sha256']==sha(source)
  continue
 entry=splices[sid];assert sha(source)==entry['sourceSha256']
 expected_frames=original_info.frames;cursor=0
 for patch in sorted(entry['replacements'],key=lambda p:p['from']):
  a,b=round(patch['from']*24000),round(patch['to']*24000)
  assert cursor<=a<b<=original_info.frames
  cp=candidate/'chunks'/f"{patch['candidateId']}-scene.wav"
  ci=sf.info(cp);assert ci.samplerate==24000 and ci.channels==1
  candidate_asr=read(candidate/'asr'/f"{patch['candidateId']}.json")
  assert candidate_asr['audio_sha256']==sha(cp)
  expected_frames+=ci.frames+4800-(b-a);cursor=b
 if int(sid)%2==0 and expected_frames<original_info.frames:
  raise RuntimeError(f'Explanation {sid} would shrink before any output is written. Preserve its duration and replan explicitly before applying.')
(v2/'chunks').mkdir(parents=True,exist_ok=True);(v2/'asr').mkdir(exist_ok=True)
proof=[]
for sid in [f'{n:02}' for n in range(1,13)]:
 source=v1/'chunks'/f'{sid}-scene.wav';dest=v2/'chunks'/source.name
 if sid not in splices:
  shutil.copy2(source,dest);assert sha(dest)==sha(source)
  cached=v1/'asr'/f'{sid}.json';assert read(cached)['audio_sha256']==sha(dest)
  shutil.copy2(cached,v2/'asr'/cached.name)
  proof.append({'scene':sid,'source':source.relative_to(ROOT).as_posix(),
   'sourceSha256':sha(source),'composite':dest.relative_to(ROOT).as_posix(),
   'compositeSha256':sha(dest),'wholeWaveByteIdentical':True,'wholeCompositeAsrReviewed':False})
  continue
 entry=splices[sid];assert sha(source)==entry['sourceSha256']
 original=pcm(source);parts=[];retained=[];replacements=[];cursor=0
 def preserve(a,b):
  if b<=a:return
  segment=original[a:b];offset=sum(len(part) for part in parts);parts.append(segment)
  retained.append({'sourceFromSample':a,'sourceToSample':b,'compositeFromSample':offset,
   'samples':len(segment),'pcmSha256':hashlib.sha256(segment.tobytes()).hexdigest()})
 for patch in sorted(entry['replacements'],key=lambda p:p['from']):
  a,b=round(patch['from']*24000),round(patch['to']*24000);assert cursor<=a<b<=len(original)
  preserve(cursor,a);parts.append(np.zeros(2400,dtype=np.int16))
  cp=candidate/'chunks'/f"{patch['candidateId']}-scene.wav";replacement=pcm(cp)
  offset=sum(len(part) for part in parts);parts.append(replacement);parts.append(np.zeros(2400,dtype=np.int16))
  replacements.append({'candidate':cp.relative_to(ROOT).as_posix(),'sha256':sha(cp),
   'compositeFromSample':offset,'samples':len(replacement),'sourceRemovedSamples':[a,b]})
  cursor=b
 preserve(cursor,len(original));combined=np.concatenate(parts)
 if int(sid)%2==0 and len(combined)<len(original):
  raise RuntimeError(f'Explanation {sid} would shrink. Preserve its duration and replan explicitly before applying.')
 sf.write(dest,combined,24000,subtype='PCM_16');decoded=pcm(dest);assert np.array_equal(decoded,combined)
 for retained_part in retained:
  offset=retained_part['compositeFromSample'];length=retained_part['samples']
  assert hashlib.sha256(decoded[offset:offset+length].tobytes()).hexdigest()==retained_part['pcmSha256']
 proof.append({'scene':sid,'source':entry['source'],'sourceSha256':sha(source),
  'composite':dest.relative_to(ROOT).as_posix(),'compositeSha256':sha(dest),
  'seconds':len(decoded)/24000,'originalSeconds':len(original)/24000,
  'retainedPcm':retained,'replacements':replacements,'wholeCompositeAsrReviewed':False})
manifest=read(BASE/'project.json');manifest['tts'].update(outputDir=v2.relative_to(ROOT).as_posix(),filenameStem='motion-sickness-games-qwen3-1.7b-balanced-v2')
write(WORK/'v2.manifest.json',manifest)
write(proof_path,{'status':'preserved-PCM-composites-awaiting-current-hash-whole-scene-ASR',
 'unchangedParagraphs':53,'originalExplanationClaimsPreserved':True,'humanListening':'pending','scenes':proof})
sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as r
r.np=np;r.sf=sf;r.configure_project('motion-sickness-games',manifest_override=(WORK/'v2.manifest.json').relative_to(ROOT).as_posix())
r._apply_edge_fades=lambda x,sr:x
r.assemble_outputs(r.load_jobs())
print('Separate v2 composites created; full current-hash ASR and timing/cut review remain required.')
