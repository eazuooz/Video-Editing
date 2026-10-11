"""Retake three complete frozen lines; retain every other approved chunk."""
from pathlib import Path
import hashlib,json,runpy,sys,re
from dataclasses import replace
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3'
SLUG='game-math-quaternion-cross-game-additions-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sys.argv[sys.argv.index('--project')+1]==SLUG
audit=read(R/'pretts-frozen-audit.json')
assert read(B/'queue.json')['execution']['mode']=='active'
assert sha(ROOT/f'projects/{SLUG}/project.json')==audit['projectManifestSha256']
for lang,digest in audit['scriptSha256'].items():assert sha(ROOT/f'projects/{SLUG}/script/narration.{lang}.json')==digest
for key,digest in audit['voiceReferenceSha256'].items():assert sha(ROOT/audit['voiceSettingsExact'][key])==digest
for entry in audit['baselineFilesStillExact']:assert sha(ROOT/entry['path'])==entry['sha256']
sys.path.insert(0,str(ROOT/'qwen3-tts'))
from gpu_handoff_guard import schedule_gpu_handoff
schedule_gpu_handoff(SLUG,'cuda:0')
pronunciation_v3='--pronunciation-v3' in sys.argv
if pronunciation_v3:sys.argv.remove('--pronunciation-v3')
pronunciation_v2='--pronunciation-v2' in sys.argv or pronunciation_v3
if '--pronunciation-v2' in sys.argv:sys.argv.remove('--pronunciation-v2')
sys.path.insert(0,str(ROOT/'production/batches/game-math-part2-full-series'))
# Reuse the existing guarded renderer, sampling, approved identity and ending gates.
runpy.run_path(str(ROOT/'production/batches/game-math-part2-full-series/render-voice.py'),run_name='scoped_voice_import')
import render_narration as r
r.configure_project(SLUG)
selected={'14-01'} if pronunciation_v3 else ({'12-02','14-01'} if pronunciation_v2 else {'01-01','12-02','14-01'})
before={p.name:sha(p) for p in r.CHUNK_DIR.glob('??-??.wav')}
assert selected.issubset({p.stem for p in r.CHUNK_DIR.glob('??-??.wav')})
original_items=r.build_render_items;pronunciation_inputs={}
def scoped_items(jobs):
 items=[item for item in original_items(jobs) if item.key in selected]
 if not pronunciation_v2:return items
 result=[]
 for item in items:
  value=item.text
  if item.key=='12-02':value=value.replace('현재 회전 에이','현재 회전, 에이').replace('역원입니다','역 원입니다')
  if item.key=='14-01':value=value.replace('일을','하나를').replace('일은','하나는').replace('일','하나')
  canonical=lambda text:re.sub(r'[^가-힣a-zA-Z0-9]','',text.replace('하나를','일을').replace('하나는','일은').replace('하나','일'))
  assert canonical(value)==canonical(item.text),'Only an equivalent spoken numeral or pronunciation pause may change'
  pronunciation_inputs[item.key]=dict(canonical=item.text,synthesis=value,numericalValuesAndClaimsUnchanged=True)
  result.append(replace(item,text=value))
 return result
r.build_render_items=scoped_items
r.assemble_outputs=lambda jobs:None
arguments=list(sys.argv)
for attempt in range(3):
 sys.argv=arguments+(['--force-scenes','01,12,14'] if attempt==0 else [])
 r.main()
 failed=[key for key in selected if r.needs_render(r.CHUNK_DIR/f'{key}.wav')]
 if not failed:break
assert not failed,failed
assert all(sha(r.CHUNK_DIR/name)==digest for name,digest in before.items() if Path(name).stem not in selected)
records=[]
for scene in read(ROOT/f'projects/{SLUG}/script/narration.ko.json')['scenes']:
 pieces=[];sources=[]
 for line,text in enumerate(scene['lines'],1):
  p=r.CHUNK_DIR/f'{scene["id"]}-{line:02}.wav';a,sr=sf.read(p,dtype='float32')
  assert sr==24000 and a.ndim==1 and r._passes_quality(r._tail_ratio(a,sr),r._tail_decay_ms(a,sr))
  pieces.append(r._apply_edge_fades(a,sr));sources.append(dict(text=text,path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
  if line<len(scene['lines']):pieces.append(np.zeros(round(.28*sr),dtype='float32'))
 target=r.CHUNK_DIR/f'{scene["id"]}-scene.wav';sf.write(target,np.concatenate(pieces),sr)
 records.append(dict(scene=scene['id'],lines=sources,currentSceneSha256=sha(target),lineGapSeconds=.28))
(R/'line-provenance.json').write_text(json.dumps(dict(records=records,approvedVoicePreserved=True,unchangedEndingGatesPassed=True,currentHashAsrAndHumanListening='pending'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
receipt=dict(selectedCompleteLines=sorted(selected),reason='Current raw full/window ASR disagrees on inverse and vector; add pronunciation pauses and say component1 as 하나; every value/claim and frozen canonical script retained',pronunciationInputs=pronunciation_inputs,before=before,after={p.name:sha(p) for p in r.CHUNK_DIR.glob('??-??.wav')},allOtherLineChunksExact=True,original80PcmAndScriptsExact=True,asrAndListening='pending')
receipt_name='critical-vector-pronunciation-retake-v3.json' if pronunciation_v3 else ('critical-pronunciation-retake-v3.json' if pronunciation_v2 else 'critical-line-retake-v3.json')
(R/receipt_name).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Retook only three complete frozen lines; every other line and original lecture retained exactly.',flush=True)
