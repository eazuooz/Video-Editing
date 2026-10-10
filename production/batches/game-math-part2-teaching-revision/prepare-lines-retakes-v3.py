"""Retain56 passing new WAVs; regenerate only two endings and one omitted line."""
from pathlib import Path
import json,copy,hashlib,shutil,sys
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;OLD='game-math-lines-bounds-teaching-additions-v2';NEW='game-math-lines-narration-retakes-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
P=ROOT/'projects'/NEW;oldm=read(ROOT/f'projects/{OLD}/project.json');m=copy.deepcopy(oldm)
assert not any((ROOT/f'shared/output/narration/{NEW}').rglob('*.wav')),'Never reset generated retakes'
m.update(slug=NEW,title='직선과 경계: 세 문장만 재생성하고 나머지 새 음성 보존')
m['paths']={k:v.replace(OLD,NEW) for k,v in oldm['paths'].items()};m['tts']['outputDir']=oldm['tts']['outputDir'].replace(OLD,NEW);m['tts']['filenameStem']=oldm['tts']['filenameStem'].replace(OLD,NEW);write(P/'project.json',m)
for lang in ['ko','en']:
 script=read(ROOT/f'projects/{OLD}/script/narration.{lang}.json');script['project']=NEW;script['status']='same supplied new words; three rejected takes only';write(P/f'script/narration.{lang}.json',script)
sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as r;r.np=np;r.sf=sf;r.configure_project(NEW)
reject={('07',3),('19',2),('11',1)};copies=[];rejections=read(B/'lines-failed-narration-v2.json')['rows']
for scene in read(P/'script/narration.ko.json')['scenes']:
 for i,text in enumerate(scene['lines'],1):
  if (scene['id'],i) in reject:continue
  source=ROOT/oldm['tts']['outputDir']/'chunks'/f'{scene["id"]}-{i:02}.wav';a,sr=sf.read(source,dtype='float32');assert sr==24000 and r._passes_quality(r._tail_ratio(a,sr),r._tail_decay_ms(a,sr))
  target=r.CHUNK_DIR/source.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);assert sha(source)==sha(target);copies.append({'source':source.relative_to(ROOT).as_posix(),'target':target.relative_to(ROOT).as_posix(),'sha256':sha(source)})
assert len(copies)==56
mapping=read(B/'lines-addition-tts-map.json');write(B/'lines-retake-tts-map-v3.json',mapping)
original=read(B/'lines-pretts-audit.json');audit=copy.deepcopy(original);audit.update(scriptSha256={lang:sha(P/f'script/narration.{lang}.json') for lang in ['ko','en']},projectManifestSha256=sha(P/'project.json'),voiceSettingsExact={k:v for k,v in m['tts'].items() if k in original['voiceSettingsExact']},voiceReferenceSha256={k:sha(ROOT/m['tts'][k]) for k in ['reference','referenceText']})
write(B/'lines-retake-pretts-audit-v3.json',audit);write(B/'lines-retake-plan-v3.json',{'rejections':rejections,'passingWavsCopiedByteExact':copies,'onlyThreeNewLinesRequired':True,'wordsUnchanged':True,'original22ScenesAndOriginalAudioUnchanged':True,'humanListening':'pending'})
runner=(B/'render-lines-narration.py').read_text(encoding='utf8').replace(OLD,NEW).replace('lines-pretts-audit.json','lines-retake-pretts-audit-v3.json').replace('lines-line-provenance.json','lines-line-provenance-v3.json');(B/'render-lines-retakes-v3.py').write_text(runner,encoding='utf8')
print('56 passing WAVs copied exactly; only07-03,19-02,11-01 require synthesis with unchanged scripts/voice/gates.')
