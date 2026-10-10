"""Two unsafe numeric takes replaced;57 valid new lines and22 originals retained."""
from pathlib import Path
import json,copy,hashlib,shutil,sys
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
OLD='game-math-lines-opening-retake-v4';NEW='game-math-lines-numeric-retakes-v5'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not any((ROOT/f'shared/output/narration/{NEW}').rglob('*.wav')),'Never reset synthesized takes'
changes=[{'tts':'12','id':'LP02','line':3,'ko':'다음 점은 중심에서 삼만큼 떨어져 있습니다. 삼을 제곱하면 구입니다. 반지름 이의 제곱인 사보다 커서 바깥입니다. 세 축의 차이를 각각 제곱해 더하면 어느 방향에서도 같은 검사를 할 수 있습니다.','en':'The next point is three units from the center. Squaring three gives nine. It is greater than four, the square of radius two, so the point is outside. Squaring and adding all three component differences performs the same test in any direction.'},
 {'tts':'19','id':'LB05','line':2,'ko':'중심은 오이고 반크기는 이입니다. 구간은 삼부터 칠입니다. 각 위치에 음수 이라는 수를 곱하겠습니다. 이어서 일을 더합니다.','en':'The center is five and the half size is two. The interval runs from three to seven. Multiply every position by the number negative two. Then add one.'}]
P=ROOT/'projects'/NEW;oldm=read(ROOT/f'projects/{OLD}/project.json');m=copy.deepcopy(oldm)
m.update(slug=NEW,title='직선과 경계: 새 계산 설명 두 문장의 숫자 명료화')
m['paths']={k:v.replace(OLD,NEW) for k,v in oldm['paths'].items()};m['tts']['outputDir']=oldm['tts']['outputDir'].replace(OLD,NEW);m['tts']['filenameStem']=oldm['tts']['filenameStem'].replace(OLD,NEW);write(P/'project.json',m)
for lang in ['ko','en']:
 script=read(ROOT/f'projects/{OLD}/script/narration.{lang}.json');script['project']=NEW;script['status']='only two rejected new numeric lines clarified;22 original scenes preserved'
 for change in changes:next(s for s in script['scenes'] if s['id']==change['tts'])['lines'][change['line']-1]=change[lang]
 write(P/f'script/narration.{lang}.json',script)
 main=ROOT/'projects/game-math-bounds-transform-v2';lesson=read(main/'production/lesson.json');script=read(main/f'script/narration.{lang}.json')
 for change in changes:
  next(s for s in lesson['scenes'] if s['id']==change['id'])[lang][change['line']-1]=change[lang]
  next(s for s in script['scenes'] if s['id']==change['id'])['lines'][change['line']-1]=change[lang]
 write(main/'production/lesson.json',lesson);write(main/f'script/narration.{lang}.json',script)
# The scene text consumed by the independent visual script also stays coherent.
flow=read(B/'lines-bounds-flow-draft.json')
for change in changes:
 for lang in ['ko','en']:next(s for s in flow['additions'] if s['id']==change['id'])[lang][change['line']-1]=change[lang]
write(B/'lines-bounds-flow-draft.json',flow)
base=read(B/'baselines/game-math-lines-bounds/lesson.json');original={s['id']:s for s in base['scenes']};retained=[]
for slug in ['game-math-lines-circles-v2','game-math-bounds-transform-v2']:
 lesson=read(ROOT/f'projects/{slug}/production/lesson.json');assert lesson['contract']==base['contract']
 for s in lesson['scenes']:
  if s['id'] in original:assert s==original[s['id']];retained.append(s['id'])
assert retained==list(original) and len(retained)==22
sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as r;r.np=np;r.sf=sf;r.configure_project(NEW);copies=[];reject={(c['tts'],c['line']) for c in changes}
for scene in read(P/'script/narration.ko.json')['scenes']:
 for i,text in enumerate(scene['lines'],1):
  if (scene['id'],i) in reject:continue
  source=ROOT/oldm['tts']['outputDir']/'chunks'/f'{scene["id"]}-{i:02}.wav';a,sr=sf.read(source,dtype='float32');assert sr==24000 and r._passes_quality(r._tail_ratio(a,sr),r._tail_decay_ms(a,sr))
  target=r.CHUNK_DIR/source.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);assert sha(source)==sha(target);copies.append({'source':source.relative_to(ROOT).as_posix(),'target':target.relative_to(ROOT).as_posix(),'sha256':sha(source)})
assert len(copies)==57
write(B/'lines-numeric-tts-map-v5.json',read(B/'lines-opening-tts-map-v4.json'))
audit=copy.deepcopy(read(B/'lines-opening-pretts-audit-v4.json'));audit.update(scriptSha256={lang:sha(P/f'script/narration.{lang}.json') for lang in ['ko','en']},projectManifestSha256=sha(P/'project.json'));write(B/'lines-numeric-pretts-audit-v5.json',audit)
write(B/'lines-numeric-retake-plan-v5.json',{'rejections':read(B/'lines-critical-numeral-readback.json'),'changedNewLines':changes,'passingWavs57ByteIdentical':copies,'allOriginalSceneDictionariesExact':True,'originalOrderAndContractExact':True,'unchangedNumericalExamples':['distance3 squared9 exceeds radius2 squared4','affine interval xprime=-2*x+1 transforms[3,7] to[-13,-5], center-9 half4'],'humanListening':'pending'})
runner=(B/'render-lines-opening-v4.py').read_text(encoding='utf8').replace(OLD,NEW).replace('lines-opening-pretts-audit-v4.json','lines-numeric-pretts-audit-v5.json').replace('lines-line-provenance-v4.json','lines-line-provenance-v5.json');(B/'render-lines-numeric-v5.py').write_text(runner,encoding='utf8')
waiter=(B/'run-lines-opening-after-lease.ps1').read_text(encoding='utf8').replace(OLD,NEW).replace('render-lines-opening-v4.py','render-lines-numeric-v5.py').replace('one clarified new narration opening','two clarified numeric narration lines');(B/'run-lines-numeric-after-lease.ps1').write_text(waiter,encoding='utf8')
print('57 passing WAVs preserved; new12-03/19-02 only; numerical examples and22 original scenes exact.')
