"""Natural clause splits retain the exact Korean voice paragraphs."""
from pathlib import Path
import json,hashlib
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[3]
FONT=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',60)
SPLITS={
 'shorts-d2r-ultrawide-ai-range':{
  'p2-1':[('이천이십일 년 테스트에서는','2021년 테스트에서는','In the 2021 test,'),('화면을 스물하나 대 아홉까지 넓혔습니다.','화면을 21:9까지 넓혔습니다.','the view widened to 21:9.')],
  'p3-2':[('몬스터가 플레이어에게 반응하는 범위는',None,"and the monster's reaction range"),('다른 규칙입니다.',None,'follow separate rules.')],
  'p5-1':[('그래서 개발진은 출시 때',None,'For release, the team'),('보이는 폭을 십구 대 구로 제한했습니다.','보이는 폭을 19:9로 제한했습니다.','limited the view to 19:9.')],
  'p6-2':[('게임 속 적이 반응하는 방식까지',None,'had to account for enemy reactions'),('함께 설계해야 했던 겁니다.',None,'in its design.')]
 },
 'shorts-d2r-loot-grass-clearance':{
  'p2-1':[('디아블로 투 레저렉션에서는 그래픽을 바꾸며','디아블로 II: 레저렉션에서는\n그래픽을 바꾸며',"Resurrected's new visuals"),('풀이 입체적으로 늘어났습니다.',None,'added physical grass.')],
  'p6-2':[('전리품을 찾는 재미까지 지켜야',None,'Preserving the joy of finding loot'),('그래픽 개선이 된 거죠.',None,'was part of the visual upgrade.')]
 },
 'shorts-d2-modular-sprite-equipment':{
  'p6-2':[('속에서는 여러 그림이',None,'Inside, several images'),('같은 동작으로 맞물리고 있었던 겁니다.',None,'moved together in the same action.')]
 }
}
EN={
 'shorts-d2r-ultrawide-ai-range':{'p2-3':'A wider view reveals a distant enemy.','p4-1':'Players could hit those distant enemies,','p4-3':'You could fire; the target stayed passive.'},
 'shorts-d2r-loot-grass-clearance':{'p4-3':"The scene stays; the item's outline appears.",'p5-3':'The key was what players needed to see.'},
 'shorts-d2-modular-sprite-equipment':{'p1-2':'redrawn for every armor combination?','p4-1':'Use parts for the same moving pose','p5-2':'recombine the images of each part'}
}
def wrap(text):
 lines=[]
 for paragraph in text.splitlines():
  current=''
  for word in paragraph.split():
   assert FONT.getlength(word)<=796,word
   new=(current+' '+word).strip()
   if current and FONT.getlength(new)>796:lines.append(current);current=word
   else:current=new
  if current:lines.append(current)
 assert len(lines)<=2,(text,lines)
 return lines
for slug,splits in SPLITS.items():
 p=ROOT/'projects'/slug;path=p/'script/clauses.json';data=json.loads(path.read_text(encoding='utf8'));result=[]
 for old in data['clauses']:
  if old['id'] in splits:
   pieces=splits[old['id']];assert ' '.join(x[0] for x in pieces)==old['spoken']
   for i,(spoken,ko,en) in enumerate(pieces):result.append(dict(**{k:v for k,v in old.items() if k not in ['id','spoken','ko','en']},id=old['id']+('b' if i else ''),spoken=spoken,ko=ko or spoken,en=en))
  else:
   if old['id'] in EN[slug]:old['en']=EN[slug][old['id']]
   result.append(old)
 for c in result:
  for lang in ['ko','en']:wrap(c[lang])
 data['clauses']=result
 lines=json.loads((p/'script/narration.spoken.ko.json').read_text(encoding='utf8'))['scenes'][0]['lines']
 for i,line in enumerate(lines):assert ' '.join(c['spoken'] for c in result if c['lineIndex']==i)==line
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 eng=[' '.join(c['en'] for c in result if c['lineIndex']==i) for i in range(len(lines))]
 (p/'script/narration.en.txt').write_text('\n\n'.join(eng)+'\n',encoding='utf8')
 ledger=p/'production/review-ledger.json';review=json.loads(ledger.read_text(encoding='utf8'))
 review['checks'].append({'name':'caption-clause-native-width-preflight','status':'pass','font':'Malgun Gothic Bold60','textWidth':796,'maxLines':2,'koEnClauses':len(result)*2,'exactSpokenParagraphPreserved':True,'actualCaptionTimingVerified':False})
 ledger.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'slug':slug,'clauses':len(result),'captionLayout':'pass'}))
