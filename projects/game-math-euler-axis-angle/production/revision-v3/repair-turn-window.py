"""Narrow one guide after direct encoded/source review, preserving all sound/timing."""
from pathlib import Path
import json, hashlib, shutil, subprocess, sys, importlib.util, copy
import soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v3'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
A=O/'before-turn-repair';A.mkdir(exist_ok=True)
assert not (A/'repair-completed.json').exists(),'Already repaired; do not repeat'
for f in [H/'timeline.json',P/'sources/annotation-plan-v3.json',O/'pair-source.json',O/'audio-build.json',O/'assembly-inputs.json',O/'qa/integrity.json',O/'qa/pixel-extraction.json',O/'euler-clean.mp4',O/'euler-captioned.mp4']:
 if not (A/f.name).exists():shutil.copy2(f,A/f.name)
old=read(A/'timeline.json');plan=P/'sources/annotation-plan-v3.json';d=read(plan);w=next(w for w in d['windows'] if w['id']=='14-turn')
assert w['sourceOutExclusive'] in [1122,1121.0]
w['sourceOutExclusive']=1121.0
w['keyframes']=[k for k in w['keyframes'] if k['sourceTime']<=1121.0]
w['encodedReviewCorrection']={'reason':'Final contact19 at output798.05 showed drift to Chain Chomp after the jump. Source1118–1122 reviewed at4fps. Retain the verified facing turn; clear guide before the fast jump instead of marking another object.','originalSourceOutExclusive':1122,'newSourceOutExclusive':1121,'narrationAndCutsUnchanged':True}
save(plan,d)
subprocess.run([sys.executable,str(H/'build-timeline.py')],cwd=R,check=True)
new=read(H/'timeline.json')
spec=importlib.util.spec_from_file_location('audio_proof',P/'production/revision-v2/build-audio.py');audio_proof=importlib.util.module_from_spec(spec);spec.loader.exec_module(audio_proof)
placement=[]
for a,b in zip(old['scenes'],new['scenes']):
 ac,bc=copy.deepcopy(a),copy.deepcopy(b)
 ac.pop('placedVoiceSha256');bc.pop('placedVoiceSha256');assert ac==bc,('Unexpected scene/timing change',a['id'])
 raw,rate=sf.read(R/b['voice'],dtype='float32');placed,pr=sf.read(R/b['placedVoice'],dtype='float32');assert rate==pr==24000
 proof=audio_proof.preserved_placement(raw,placed,b['observationPauses'],rate)
 placement.append({'scene':b['id'],'oldContainerSha256':a['placedVoiceSha256'],'newContainerSha256':b['placedVoiceSha256'],'identicalSourceAndPauses':True,'sourcePlacementProof':proof})
for key in old:
 if key not in ['inputHashes','scenes']:assert old[key]==new[key],('Unexpected nonvisual change',key)
changed=[k for k,v in old['inputHashes'].items() if new['inputHashes'][k]!=v]
assert set(changed)=={'projects/game-math-euler-axis-angle/sources/annotation-plan-v3.json','projects/game-math-euler-axis-angle/production/revision-v3/build-timeline.py'},changed
audio=read(O/'audio-build.json');assert audio['timelineSha256']==sha(A/'timeline.json')
for output in audio['outputs']:assert sha(R/output['file'])==output['sha256']
audio['timelineSha256']=sha(H/'timeline.json')
for scene in audio['scenes']:
 b=next(s for s in new['scenes'] if s['id']==scene['scene']);scene['placedSha256']=b['placedVoiceSha256']
audio['visualOnlyRebind']={'previousTimelineSha256':sha(A/'timeline.json'),'proof':'All source PCM, pauses, cuts, durations and caption/voice/game placements equal. Placed FLOAT WAV containers were rewritten by the timing builder; decoded placement revalidated exactly against identical source PCM and pause list. Builder now preserves existing decoded-identical files. All actual mixed audio output SHA256 unchanged.','record':'production/revision-v3/annotation-repair.json'}
save(O/'audio-build.json',audio)
timing=read(H/'annotation-timing-review.json');timing['timelineSha256']=sha(H/'timeline.json');timing['sourcePlanSha256']=sha(plan)
row=next(v for v in timing['windows'] if v['id']=='14-turn')
for key in ['source','sceneTime','globalTime']:row[key][1]-=1
row['correction']='Guide ends before rapid jump; facing-turn example retained'
save(H/'annotation-timing-review.json',timing)
proof={'changedGuide':'14-turn','affectedScene':'14','sourceRangeChanged':[1121,1122],'globalRangeChanged':[797.15,798.15],'oldCaptionedSha256':sha(A/'euler-captioned.mp4'),'oldTimelineSha256':sha(A/'timeline.json'),'newTimelineSha256':sha(H/'timeline.json'),'allTimingAndSourceFieldsEqual':True,'placedPcmEquivalence':placement,'audioFilesUnchanged':audio['outputs'],'oldIntegrity':'production/local/revision-v3/before-turn-repair/integrity.json','repairedMovingReview':'pending'}
save(H/'annotation-repair.json',proof);save(A/'repair-completed.json',proof)
print('Only14-turn guide shortened; all narration/caption/cut timing and audio preserved.')
