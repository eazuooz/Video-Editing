"""One new-only correction: observed snowboard is not a pair of skis."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-quaternion-teaching-additions-v7';P=ROOT/'projects'/slug
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert not any((ROOT/f'shared/output/narration/{slug}').rglob('*.wav'))
ko='빨간 몸체 선과 파란 보드 선은 시간에 따른 방향 기록입니다.'
en='The red torso line and blue snowboard line record the changing directions over time.'
m=json.loads(json.dumps(read(ROOT/'projects/game-math-quaternion-teaching-additions-v6/project.json')).replace('additions-v6','additions-v7'))
m['title']='관찰한 스노보드에 맞춘 새 설명 한 문장 수정';m['tts']['renderMode']='line';m['preservation']['allOriginalNarrationUnchanged']=True
write(P/'project.json',m)
for lang,text in [('ko',ko),('en',en)]:write(P/f'script/narration.{lang}.json',{'title':m['title'],'scenes':[{'id':'01','title':'몸체와 보드의 시간에 따른 방향','lines':[text]}]})
marker=Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/done/train_wireframe_fullft_43.json')
done=read(marker);assert done['validation']['numerically_finite'] and done['validation']['checkpoint_finite']
write(B/'quaternion-v7-pretts-audit.json',{'original26ScenesAnd155KoLinesExact':True,'newLineOnly':True,'originalPhrase':'파란 스키 선','observedEquipment':'single snowboard; TOXIC GRAB and board outline observed at source169.25–171.75','scriptSha256':{lang:hashlib.sha256((P/f'script/narration.{lang}.json').read_bytes()).hexdigest() for lang in ['ko','en']},'completedTrainingMarker':marker.as_posix(),'completedTrainingMarkerSha256':hashlib.sha256(marker.read_bytes()).hexdigest(),'checkpointSha256':done['validation']['checkpoint_sha256'],'finalMixAndMotionReview':False})
wrapper=(B/'render-narration-v6.py').read_text(encoding='utf8').replace('additions-v6','additions-v7').replace('v6-pretts','v7-pretts').replace('v6-line-provenance','v7-line-provenance')
(B/'render-narration-v7.py').write_text(wrapper,encoding='utf8')
print('Frozen one observed-equipment correction; original audio and completed training marker preserved.')
