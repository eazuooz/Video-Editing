"""Two new-only ending retakes; reuse every gate-passing unchanged line."""
from pathlib import Path
import json,hashlib,shutil,sys
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as r
r.np=np;r.sf=sf
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
v5='game-math-quaternion-teaching-additions-v5';slug='game-math-quaternion-teaching-additions-v6';P=ROOT/'projects'/slug
old=read(ROOT/f'projects/{v5}/project.json');oldout=ROOT/old['tts']['outputDir']
assert not any((ROOT/f'shared/output/narration/{slug}').rglob('*.wav')),'Freeze script after audio exists'
ko=read(ROOT/f'projects/{v5}/script/narration.ko.json')['scenes'];en=read(ROOT/f'projects/{v5}/script/narration.en.json')['scenes']
scenes=[
 {'id':'01','additionId':'B23','title':'계산 결과에서 화면 기준으로 연결하기','sourceType':'bridge','ko':[ko[1]['lines'][0],'이제 실제 몸체의 방향을 관찰해 보겠습니다.','그 방향을 화면에 보여 주는 카메라 기준과 분리해서 생각하겠습니다.'],'en':[en[1]['lines'][0],'We now observe the visible body direction.','We separate it from the camera frame that projects that direction on screen.'],'reuse':{1:('02',1)}},
 {'id':'02','additionId':'GA04','title':'몸체와 바퀴에서 항등 회전으로','sourceType':'actual-footage','ko':ko[3]['lines'][:2]+['빨간 선은 몸체 방향입니다.','파란 선은 보이는 바퀴 방향입니다.','경사와 커브에서 두 방향이 함께 바뀝니다.']+ko[3]['lines'][3:],'en':en[3]['lines'][:2]+['The red line shows the torso direction.','The blue line shows a visible wheel direction.','Both directions change through slopes and bends.']+en[3]['lines'][3:],'reuse':{1:('04',1),2:('04',2),6:('04',4),7:('04',5),8:('04',6),9:('04',7)}}
]
m=json.loads(json.dumps(old).replace(v5,slug));m['title']='쿼터니언 새 연결 문장 두 장면의 끝맺음 재녹음';m['preservation']['v5AudioOverwritten']=False
write(P/'project.json',m)
for lang in ['ko','en']:write(P/f'script/narration.{lang}.json',{'title':m['title'],'scenes':[{'id':s['id'],'title':s['title'],'lines':s[lang]} for s in scenes]})
chunks=ROOT/m['tts']['outputDir']/'chunks';chunks.mkdir(parents=True,exist_ok=True);reuse=[]
for scene in scenes:
 for new_index,(old_id,old_index) in scene['reuse'].items():
  old_scene=next(s for s in ko if s['id']==old_id);assert scene['ko'][new_index-1]==old_scene['lines'][old_index-1]
  src=oldout/f'chunks/{old_id}-{old_index:02}.wav';a,sr=sf.read(src,dtype='float32')
  assert r._passes_quality(r._tail_ratio(a,sr),r._tail_decay_ms(a,sr)),src
  dst=chunks/f'{scene["id"]}-{new_index:02}.wav';shutil.copy2(src,dst)
  reuse.append({'text':scene['ko'][new_index-1],'from':src.relative_to(ROOT).as_posix(),'to':dst.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'unchangedEndingGatesPassed':True})
write(B/'quaternion-v6-tts-map.json',[{'ttsScene':s['id'],'additionId':s['additionId'],'sourceType':s['sourceType']} for s in scenes])
write(B/'quaternion-retakes-v6.json',{'scope':'Only two newly authored additions; original26 scenes and155 Korean lines unchanged','overrides':[{k:s[k] for k in ['additionId','title','sourceType','ko','en']} for s in scenes],'passedV5LineReuse':reuse,'fiveNewLineSynthesisRequired':True})
audit=read(B/'quaternion-v5-pretts-audit.json');audit['scriptSha256']={lang:hashlib.sha256((P/f'script/narration.{lang}.json').read_bytes()).hexdigest() for lang in ['ko','en']};audit['v5UnchangedPassingLinesReused']=reuse
write(B/'quaternion-v6-pretts-audit.json',audit)
wrapper=(B/'render-narration-v5.py').read_text(encoding='utf8').replace('additions-v5','additions-v6').replace('v5-pretts','v6-pretts').replace('v5-line-provenance','v6-line-provenance')
(B/'render-narration-v6.py').write_text(wrapper,encoding='utf8')
print(json.dumps({'newSynthesisLines':5,'passedLinesReused':len(reuse),'originalMaterialPreserved':True}))
