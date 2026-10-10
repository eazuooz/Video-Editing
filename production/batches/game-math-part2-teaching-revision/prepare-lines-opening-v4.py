"""Replace one rejected new opening; preserve58 passing lines and all22 originals."""
from pathlib import Path
import json,copy,hashlib,shutil,sys
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
OLD='game-math-lines-narration-retakes-v3';NEW='game-math-lines-opening-retake-v4'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not any((ROOT/f'shared/output/narration/{NEW}').rglob('*.wav')),'Never reset a synthesized project'
words={'ko':'파란 적의 새 장면입니다. 빨간 윤곽으로 둥근 머리와 긴 팔다리를 비교하세요.','en':'We have changed to a new shot of the blue enemy. Compare its round head and long limbs using the red outlines.'}
P=ROOT/'projects'/NEW;oldm=read(ROOT/f'projects/{OLD}/project.json');m=copy.deepcopy(oldm)
m.update(slug=NEW,title='직선과 경계: 새 게임 예시 도입 한 문장 재검수')
m['paths']={k:v.replace(OLD,NEW) for k,v in oldm['paths'].items()};m['tts']['outputDir']=oldm['tts']['outputDir'].replace(OLD,NEW);m['tts']['filenameStem']=oldm['tts']['filenameStem'].replace(OLD,NEW);write(P/'project.json',m)
for lang in ['ko','en']:
 script=read(ROOT/f'projects/{OLD}/script/narration.{lang}.json');script['project']=NEW;script['status']='only rejected new LG04 opening revised; original22 scenes unchanged';assert script['scenes'][10]['id']=='11';script['scenes'][10]['lines'][0]=words[lang];write(P/f'script/narration.{lang}.json',script)
 main=ROOT/'projects/game-math-bounds-transform-v2';lesson=read(main/'production/lesson.json');next(s for s in lesson['scenes'] if s['id']=='LG04')[lang][0]=words[lang];write(main/'production/lesson.json',lesson)
 script=read(main/f'script/narration.{lang}.json');next(s for s in script['scenes'] if s['id']=='LG04')['lines'][0]=words[lang];write(main/f'script/narration.{lang}.json',script)
 sources=read(B/'lines-game-insertions.json');next(s for s in sources['scenes'] if s['id']=='LG04')[lang][0]=words[lang];write(B/'lines-game-insertions.json',sources)
base=read(B/'baselines/game-math-lines-bounds/lesson.json');original={s['id']:s for s in base['scenes']}
retained=[]
for slug in ['game-math-lines-circles-v2','game-math-bounds-transform-v2']:
 lesson=read(ROOT/f'projects/{slug}/production/lesson.json');assert lesson['contract']==base['contract']
 for s in lesson['scenes']:
  if s['id'] in original:assert s==original[s['id']];retained.append(s['id'])
assert retained==list(original) and len(retained)==22
sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as r;r.np=np;r.sf=sf;r.configure_project(NEW)
copies=[]
for scene in read(P/'script/narration.ko.json')['scenes']:
 for i,text in enumerate(scene['lines'],1):
  if scene['id']=='11' and i==1:continue
  source=ROOT/oldm['tts']['outputDir']/'chunks'/f'{scene["id"]}-{i:02}.wav';a,sr=sf.read(source,dtype='float32');assert sr==24000 and r._passes_quality(r._tail_ratio(a,sr),r._tail_decay_ms(a,sr))
  target=r.CHUNK_DIR/source.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);assert sha(source)==sha(target);copies.append({'source':source.relative_to(ROOT).as_posix(),'target':target.relative_to(ROOT).as_posix(),'sha256':sha(source)})
assert len(copies)==58
write(B/'lines-opening-tts-map-v4.json',read(B/'lines-retake-tts-map-v3.json'))
audit=copy.deepcopy(read(B/'lines-retake-pretts-audit-v3.json'));audit.update(scriptSha256={lang:sha(P/f'script/narration.{lang}.json') for lang in ['ko','en']},projectManifestSha256=sha(P/'project.json'));write(B/'lines-opening-pretts-audit-v4.json',audit)
write(B/'lines-opening-retake-plan-v4.json',{'rejectedScene':'LG04','rejectedReason':'V3 read-back omitted 구간/파란 opening, despite aggregate timing coverage; duration16.76 plus0.6 exceeds17-second secured source','newWords':words,'58PassingWavsCopiedByteExact':copies,'allOriginalSceneDictionariesExact':True,'originalOrderAndContractExact':True,'humanListening':'pending'})
runner=(B/'render-lines-retakes-v3.py').read_text(encoding='utf8').replace(OLD,NEW).replace('lines-retake-pretts-audit-v3.json','lines-opening-pretts-audit-v4.json').replace('lines-line-provenance-v3.json','lines-line-provenance-v4.json');(B/'render-lines-opening-v4.py').write_text(runner,encoding='utf8')
waiter=(B/'run-lines-retakes-after-lease.ps1').read_text(encoding='utf8').replace(OLD,NEW).replace('render-lines-retakes-v3.py','render-lines-opening-v4.py').replace('three reviewed narration retakes','one clarified new narration opening');(B/'run-lines-opening-after-lease.ps1').write_text(waiter,encoding='utf8')
print('58 passing WAVs preserved; only new11-01 changed;22 original scenes/order/contract exact.')
