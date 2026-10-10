"""Clarify the new +1 operation; retain58 WAVs and all22 original scenes."""
from pathlib import Path
import json,copy,hashlib,shutil,sys
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
OLD='game-math-lines-numeric-retakes-v5';NEW='game-math-lines-unit-retake-v6'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not any((ROOT/f'shared/output/narration/{NEW}').rglob('*.wav'))
change={'tts':'19','id':'LB05','line':2,'ko':'중심은 오이고 반크기는 이입니다. 구간은 삼부터 칠입니다. 각 위치에 음수 이라는 수를 곱하겠습니다. 마지막에는 숫자 하나를 더합니다.','en':'The center is five and the half size is two. The interval runs from three to seven. Multiply every position by the number negative two. Finally add the number one.'}
P=ROOT/'projects'/NEW;oldm=read(ROOT/f'projects/{OLD}/project.json');m=copy.deepcopy(oldm)
m.update(slug=NEW,title='직선과 경계: 숫자 하나를 더하는 새 계산 문장 명료화');m['paths']={k:v.replace(OLD,NEW) for k,v in m['paths'].items()};m['tts']['outputDir']=m['tts']['outputDir'].replace(OLD,NEW);m['tts']['filenameStem']=m['tts']['filenameStem'].replace(OLD,NEW);write(P/'project.json',m)
for lang in ['ko','en']:
 script=read(ROOT/f'projects/{OLD}/script/narration.{lang}.json');script['project']=NEW;script['status']='one new numeric line clarified; all original material preserved';next(s for s in script['scenes'] if s['id']=='19')['lines'][1]=change[lang];write(P/f'script/narration.{lang}.json',script)
 main=ROOT/'projects/game-math-bounds-transform-v2';lesson=read(main/'production/lesson.json');script=read(main/f'script/narration.{lang}.json');next(s for s in lesson['scenes'] if s['id']=='LB05')[lang][1]=change[lang];next(s for s in script['scenes'] if s['id']=='LB05')['lines'][1]=change[lang];write(main/'production/lesson.json',lesson);write(main/f'script/narration.{lang}.json',script)
flow=read(B/'lines-bounds-flow-draft.json')
for lang in ['ko','en']:next(s for s in flow['additions'] if s['id']=='LB05')[lang][1]=change[lang]
write(B/'lines-bounds-flow-draft.json',flow)
base=read(B/'baselines/game-math-lines-bounds/lesson.json');original={s['id']:s for s in base['scenes']};retained=[]
for slug in ['game-math-lines-circles-v2','game-math-bounds-transform-v2']:
 lesson=read(ROOT/f'projects/{slug}/production/lesson.json');assert lesson['contract']==base['contract']
 for s in lesson['scenes']:
  if s['id'] in original:assert s==original[s['id']];retained.append(s['id'])
assert retained==list(original) and len(retained)==22
sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as r;r.np=np;r.sf=sf;r.configure_project(NEW);copies=[]
for s in read(P/'script/narration.ko.json')['scenes']:
 for i,text in enumerate(s['lines'],1):
  if s['id']=='19' and i==2:continue
  source=ROOT/oldm['tts']['outputDir']/'chunks'/f'{s["id"]}-{i:02}.wav';a,sr=sf.read(source,dtype='float32');assert sr==24000 and r._passes_quality(r._tail_ratio(a,sr),r._tail_decay_ms(a,sr))
  target=r.CHUNK_DIR/source.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);assert sha(source)==sha(target);copies.append({'source':source.relative_to(ROOT).as_posix(),'target':target.relative_to(ROOT).as_posix(),'sha256':sha(source)})
assert len(copies)==58
write(B/'lines-unit-tts-map-v6.json',read(B/'lines-numeric-tts-map-v5.json'))
audit=copy.deepcopy(read(B/'lines-numeric-pretts-audit-v5.json'));audit.update(scriptSha256={lang:sha(P/f'script/narration.{lang}.json') for lang in ['ko','en']},projectManifestSha256=sha(P/'project.json'));write(B/'lines-unit-pretts-audit-v6.json',audit)
rejected=ROOT/oldm['tts']['outputDir']/'asr/19.json'
write(B/'lines-unit-retake-plan-v6.json',{'rejectedRawCurrentHashReadback':read(rejected),'reason':'The new +1 instruction was recognized as +2; timing coverage alone cannot approve numerical meaning. Use explicit number one wording.','changedNewLine':change,'passingWavs58ByteIdentical':copies,'allOriginalSceneDictionariesExact':True,'originalOrderAndContractExact':True,'unchangedExample':'xprime=-2*x+1;[3,7] ->[-13,-5], center-9, half4','humanListening':'pending'})
runner=(B/'render-lines-numeric-v5.py').read_text(encoding='utf8').replace(OLD,NEW).replace('lines-numeric-pretts-audit-v5.json','lines-unit-pretts-audit-v6.json').replace('lines-line-provenance-v5.json','lines-line-provenance-v6.json');(B/'render-lines-unit-v6.py').write_text(runner,encoding='utf8')
waiter=(B/'run-lines-numeric-after-lease.ps1').read_text(encoding='utf8').replace(OLD,NEW).replace('render-lines-numeric-v5.py','render-lines-unit-v6.py').replace('two clarified numeric narration lines','one explicit number-one narration line');(B/'run-lines-unit-after-lease.ps1').write_text(waiter,encoding='utf8')
print('58 valid WAVs retained byte-for-byte; only new19-02 is clarified;22 original scenes exact.')
