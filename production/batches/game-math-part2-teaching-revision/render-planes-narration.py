"""New-only, hash-frozen narration through the unchanged exclusive GPU guard."""
from pathlib import Path
import json,hashlib,sys,subprocess
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;slug='game-math-planes-teaching-additions-v2'
assert sys.argv[sys.argv.index('--project')+1]==slug
read=lambda p:json.loads(p.read_text(encoding='utf8'))
q=read(B/'queue.json');assert q['execution']['mode']=='active'
audit=read(B/'planes-pretts-audit.json');assert audit['allOriginalSceneDictionariesExact'] and audit['originalOrderAndContractExact'] and audit['gameplayComparedBeforeDependentNarration']
assert hashlib.sha256((ROOT/f'projects/{slug}/project.json').read_bytes()).hexdigest()==audit['projectManifestSha256']
for key,sha in audit['voiceReferenceSha256'].items():assert hashlib.sha256((ROOT/audit['voiceSettingsExact'][key]).read_bytes()).hexdigest()==sha
assert all(c['passed'] for c in audit['checks'])
for lang,sha in audit['scriptSha256'].items():assert hashlib.sha256((ROOT/f'projects/{slug}/script/narration.{lang}.json').read_bytes()).hexdigest()==sha
command=[sys.executable,'-X','utf8',str(ROOT/'production/batches/game-math-part2-full-series/render-voice.py'),*sys.argv[1:]]
import numpy as np,soundfile as sf
sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as r
r.np=np;r.sf=sf;r.configure_project(slug);scenes=read(ROOT/f'projects/{slug}/script/narration.ko.json')['scenes']
for attempt in range(3):
 subprocess.run(command,cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW);failed=[]
 for scene in scenes:
  for line in range(1,len(scene['lines'])+1):
   path=r.CHUNK_DIR/f'{scene["id"]}-{line:02}.wav';a,sr=sf.read(path,dtype='float32')
   if not r._passes_quality(r._tail_ratio(a,sr),r._tail_decay_ms(a,sr)):failed.append(path.name)
 if not failed:break
 print('Resume only failed complete lines:',failed,flush=True)
assert not failed,('Ending gates failed; retain takes without approval',failed)
records=[]
for scene in scenes:
 pieces=[];sources=[]
 for line,text in enumerate(scene['lines'],1):
  p=r.CHUNK_DIR/f'{scene["id"]}-{line:02}.wav';a,sr=sf.read(p,dtype='float32');assert sr==24000 and a.ndim==1
  pieces.append(r._apply_edge_fades(a,sr));sources.append({'text':text,'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  if line<len(scene['lines']):pieces.append(np.zeros(round(.28*sr),dtype='float32'))
 target=r.CHUNK_DIR/f'{scene["id"]}-scene.wav';sf.write(target,np.concatenate(pieces),sr)
 records.append({'scene':scene['id'],'lines':sources,'currentSceneSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'lineGapSeconds':.28})
(B/'planes-line-provenance.json').write_text(json.dumps({'records':records,'approvedVoicePreserved':True,'unchangedEndingGatesPassed':True,'currentHashAsrAndHumanListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('New scene chunks assembled; original PCM untouched; current-hash ASR and listening required.',flush=True)
