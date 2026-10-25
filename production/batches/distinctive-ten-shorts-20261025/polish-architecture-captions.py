"""Caption-only clause splits; spoken paragraph PCM text remains unchanged."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[3]
edits={
'shorts-d2r-renderer-logic-separation':{
 'p1-1':'One button restores the classic look.',
 'p3-1':'D2R builds on the original game.',
 'p4-3':'Different looks share one game state.',
 'p5-3':'One game state, another presentation.'
},
'shorts-d2r-controller-input-adapter':{
 'p2-3':'A stick sets the current direction.',
 'p4-2':'Controller movement turns pathfinding off.',
 'p5-1':'Our demo uses the same destination.',
 'p6-2':'Movement changes make the pad feel right.'
}}
splits={
'p3-2':[
 ('스틱과 버튼을,','스틱과 버튼을,','Sticks and buttons'),
 ('기존 게임이 이해하는 행동으로 연결한 거예요.','기존 게임이 이해하는 행동으로 연결한 거예요.','trigger actions the old game understands.')],
'p6-1':[
 ('입력 변환 계층으로','입력 변환 계층으로','An input adaptation layer'),
 ('옛 게임과 새 조작기를 연결하고,','옛 게임과 새 조작기를 연결하고,','connects the old game to the new device.')]
}
for slug,changes in edits.items():
 p=R/'projects'/slug/'script/clauses.json';doc=json.loads(p.read_text(encoding='utf8'));out=[]
 for c in doc['clauses']:
  if slug.endswith('input-adapter') and c['id'] in splits:
   for i,(spoken,ko,en) in enumerate(splits[c['id']]):out.append(dict(**{**c,'id':c['id']+('b' if i else ''),'spoken':spoken,'ko':ko,'en':en}))
  elif slug.endswith('input-adapter') and c['id'] in ['p3-2b','p6-1b']:continue
  else:
   if c['id'] in changes:c['en']=changes[c['id']]
   out.append(c)
 doc['clauses']=out;p.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(slug,len(out))
