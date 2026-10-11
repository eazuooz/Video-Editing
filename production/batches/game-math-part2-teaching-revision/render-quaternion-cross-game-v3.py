"""Synthesize the fourteen frozen additions through the existing exclusive guard."""
from pathlib import Path
import hashlib,json,sys,subprocess
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3';slug='game-math-quaternion-cross-game-additions-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sys.argv[sys.argv.index('--project')+1]==slug
assert read(B/'queue.json')['execution']['mode']=='active'
audit=read(R/'pretts-frozen-audit.json')
assert audit['original80DictionariesAndOrderExact'] and not audit['baselineAudioOverwritten']
assert all(c['passed'] for c in audit['checks']) and audit['sourceTracksPrepared']
assert sha(ROOT/f'projects/{slug}/project.json')==audit['projectManifestSha256']
for lang,value in audit['scriptSha256'].items():assert sha(ROOT/f'projects/{slug}/script/narration.{lang}.json')==value
for key,value in audit['voiceReferenceSha256'].items():assert sha(ROOT/audit['voiceSettingsExact'][key])==value
for entry in audit['baselineFilesStillExact']:assert sha(ROOT/entry['path'])==entry['sha256']
sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as r
r.np=np;r.sf=sf;r.configure_project(slug)
scenes=read(ROOT/f'projects/{slug}/script/narration.ko.json')['scenes'];assert len(scenes)==14
from gpu_handoff_guard import schedule_gpu_handoff
schedule_gpu_handoff(slug,'cuda:0')
command=[sys.executable,'-X','utf8',str(ROOT/'production/batches/game-math-part2-full-series/render-voice.py'),*sys.argv[1:]]
for attempt in range(3):
 subprocess.run(command,cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW);failed=[]
 for scene in scenes:
  for line in range(1,len(scene['lines'])+1):
   path=r.CHUNK_DIR/f'{scene["id"]}-{line:02}.wav';a,sr=sf.read(path,dtype='float32')
   if not r._passes_quality(r._tail_ratio(a,sr),r._tail_decay_ms(a,sr)):failed.append(path.name)
 if not failed:break
 print('Retry only failed new complete lines:',failed,flush=True)
assert not failed,('Ending gate failed; retain takes without approval',failed)
records=[]
for scene in scenes:
 pieces=[];sources=[]
 for line,text in enumerate(scene['lines'],1):
  p=r.CHUNK_DIR/f'{scene["id"]}-{line:02}.wav';a,sr=sf.read(p,dtype='float32');assert sr==24000 and a.ndim==1
  pieces.append(r._apply_edge_fades(a,sr));sources.append(dict(text=text,path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
  if line<len(scene['lines']):pieces.append(np.zeros(round(.28*sr),dtype='float32'))
 target=r.CHUNK_DIR/f'{scene["id"]}-scene.wav';sf.write(target,np.concatenate(pieces),sr)
 records.append(dict(scene=scene['id'],lines=sources,currentSceneSha256=sha(target),lineGapSeconds=.28))
(R/'line-provenance.json').write_text(json.dumps(dict(records=records,approvedVoicePreserved=True,unchangedEndingGatesPassed=True,currentHashAsrAndHumanListening='pending'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Fourteen new scene chunks assembled; approved original PCM untouched; current-hash ASR/listening still required.',flush=True)
