"""Interleave new complete passages, retain all original scene PCM hashes."""
from pathlib import Path
import json,math,hashlib,importlib.util
import soundfile as sf
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v3';OLD=P/'production/local'
OUT=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v3/video');OUT.mkdir(parents=True,exist_ok=True)
plan=json.loads((H/'revision-plan.json').read_text('utf8'))['scenes'];original=json.loads((OLD/'timeline.json').read_text('utf8'))
def timeline(require_all=True):
 rows=[];start=2
 for i,row in enumerate(plan):
  ident=row['id'];f=L/'voice/chunks'/f'{ident}-scene.wav'
  if ident.isdigit():f=Path(next(x['source'] for x in original['scenes'] if x['id']==ident))
  elif ident.startswith('R') and not f.exists():f=P/'production/local/room-v2/voice/chunks'/f'{ident}-scene.wav'
  if not f.exists():
   if require_all:raise FileNotFoundError(f)
   break
  info=sf.info(f);digest=hashlib.file_digest(f.open('rb'),'sha256').hexdigest();old=next((x for x in original['scenes'] if x['id']==ident),None)
  if old:assert digest==old['sourceSha256'],ident
  frames=old['frames'] if old else math.ceil((info.duration+.28)*60)
  rows.append({'id':ident,'title':row['title'],'start':start,'speechEnd':start+info.duration,'duration':frames/60,'frames':frames,'source':str(f),'sourceSha256':digest,'sourceDuration':info.duration,'originalPcmPreserved':bool(old)})
  start+=frames/60
 data={'fps':60,'intro':2,'outro':10,'scenes':rows,'duration':start+10,'frames':round((start+10)*60)}
 (L/'timeline.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8');return data
if __name__=='__main__':
 import sys
 if '--timing-only' in sys.argv:print(json.dumps(timeline(False)));raise SystemExit(0)
 engine=H/'audio_engine.py'
 source=(P/'production/build_audio.py').read_text('utf8').replace('Path(__file__).resolve().parents[1]','Path(__file__).resolve().parents[2]').replace('limit=10**(-1.7/20)','limit=10**(-2.6/20)')
 engine.write_text(source,'utf8')
 spec=importlib.util.spec_from_file_location('room_v3_audio_builder',engine);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 mod.L=OUT;mod.timeline=timeline
 import subprocess
 mod.run=lambda args:subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf8',errors='replace',check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 save=mod.save
 def scoped_save(p,j):
  if p==P/'production/audio-qa.json':p=H/'audio-qa.json'
  save(p,j)
 mod.save=scoped_save
 mod.build()
