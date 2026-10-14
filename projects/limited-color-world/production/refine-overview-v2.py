"""Refine the prepared overview to four sentences before any voice request."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
T=Path(__file__).resolve().parent.parent;B=T/'production'
assert not (B/'narration-tts-request-v1.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=[T/'script/narration.ko.json',T/'script/narration.en.json',T/'planning/outline.md',T/'planning/scene-intents-v1.json']
before=[{'path':str(p),'sha256':sha(p)} for p in paths]
ko=json.loads(paths[0].read_text(encoding='utf-8'));en=json.loads(paths[1].read_text(encoding='utf-8'))
ko['scenes'][0]['title']='색이 달라도 다음 행동을 읽을 수 있을까'
ko['scenes'][0]['lines']=[
 '게임에서 색을 구별하기 어렵더라도, 어디로 가고 무엇을 누를지 알 수 있는 화면은 어떻게 만들까요?',
 '치커리의 실제 플레이에서 집의 윤곽, 식물의 높이와 움직임, 어두운 공간의 대비를 차례로 보겠습니다.',
 '실제 장면과 도식을 연결해 중요한 정보에 다른 단서를 더하는 방법을 정리해 보겠습니다. 먼저 색칠해도 사라지지 않는 집의 선부터 보죠.']
en['scenes'][0]['title']=ko['scenes'][0]['title']
en['scenes'][0]['lines']=[
 'How can a game screen communicate where to go and what to interact with, even when colors are difficult to distinguish?',
 'In actual Chicory gameplay, we will look at house outlines, plant height and motion, and contrast in dark spaces, in that order.',
 'We will connect actual scenes to diagrams and add other cues to important information. Let us begin with the lines that remain when a house is painted.']
for p,d in zip(paths[:2],[ko,en]):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
outline=paths[2].read_text(encoding='utf-8').replace('안내3문장:','안내4문장/3문단:').replace('색 없이도 다음 행동을 읽을 수 있을까','색이 달라도 다음 행동을 읽을 수 있을까')
paths[2].write_text(outline,encoding='utf-8')
intents=json.loads(paths[3].read_text(encoding='utf-8'));intents['scenes'][0]['title']=ko['scenes'][0]['title'];paths[3].write_text(json.dumps(intents,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
audit={'preparedAt':datetime.now(timezone.utc).isoformat(),'reason':'Four natural sentences in3paired paragraphs; preserve question, order, value and first-example connection.',
 'before':before,'after':[{'path':str(p),'sha256':sha(p)} for p in paths],
 'overviewCharacters':sum(map(len,ko['scenes'][0]['lines'])),'koCharacters':sum(len(t) for s in ko['scenes'] for t in s['lines']),
 'voiceMeasured':False,'newPcm':0,'narrationTtsRequestCreated':False}
out=B/'overview-refinement-v2.json';assert not out.exists();out.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:audit[k] for k in ['overviewCharacters','koCharacters','newPcm']}))
