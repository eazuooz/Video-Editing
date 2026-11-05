"""Bind retained source paragraphs, specific observed game examples and aligned KO/EN units."""
from pathlib import Path
import json,hashlib,re
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/grid-v1'
read=lambda f:json.loads(f.read_text(encoding='utf-8-sig'))
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rel=lambda x:x.relative_to(R).as_posix()
S=P/'script/grid-v1';orig=read(S/'caption-units.json')['byScene'];chapters=read(S/'narration.ko.json')['scenes']
insert={
 ('01',0):[('몬스터 헌터 와일즈의 훈련장입니다.','This is the training area in Monster Hunter Wilds.'),('대검을 든 헌터가 검을 들어 올리고,','The hunter raises the great sword,'),('표적을 내리친 뒤 자세를 추스릅니다.','strikes the dummy, then recovers.')],
 ('01',1):[('슈퍼 스매시브라더스 얼티밋에서는 링크가','In Super Smash Bros. Ultimate, watch Link'),('발판에 서다가 공중으로 뜰 때 다리 모양이 달라집니다.','change his leg position as he leaves the platform.')],
 ('02',1):[('대검을 어깨 위로 끌어올리는 순간을 보세요.','Watch the instant the great sword rises over the hunter’s shoulder.'),('아직 표적과 칼 사이에 공간이 있습니다.','There is still a gap between the blade and the target.')],
 ('03',0):[('헌터가 훈련용 표적에 칼을 맞히면','When the hunter connects with the training dummy,'),('닿은 자리에 타격 효과가 나타납니다.','a hit effect flashes at the contact point.')],
 ('04',0):[('다시 헌터의 칼끝을 따라가 보세요.','Follow the tip of the hunter’s sword again.'),('표적을 지난 뒤에도 검을 거두는 움직임이 이어집니다.','It continues moving after it passes the target.')]}
spoken_alias={'36':'서른여섯','48':'마흔여덟','60':'예순','0.8':'영 점 팔','0.6':'영 점 육','0.2':'영 점 이','FHD':'풀 에이치 디'}
groups=[];spoken=[];captions=[];en=[];meta=[]
for ch in chapters:
 cid=ch['id']
 for pi,rows in enumerate(orig[cid].values()):
  pairs=insert.get((cid,pi),[])+[(a['ko'],a['en']) for a in rows]
  group=[];i=0
  for unit in pairs:
   group.append(unit);i+=1
   if i<len(pairs) and (len(' '.join(k for k,e in group))<190 or not unit[0].endswith(('.','?','!'))):continue
   n=f'{len(groups)+1:02}';txt=' '.join(k for k,e in group);phon=txt
   for a,b in spoken_alias.items():phon=phon.replace(a,b)
   title=ch['title'];groups.append(group);meta.append({'id':n,'chapter':cid,'paragraph':pi,'title':title})
   for bag,data in [(spoken,phon),(captions,txt),(en,' '.join(e for k,e in group))]:bag.append({'id':n,'title':title,'lines':[data]})
   group=[]
for lang,items in [('spoken-ko',spoken),('ko',captions),('en',en)]:save(H/f'final.{lang}.json',{'scenes':items})
save(H/'units-final.json',{'groups':groups,'paragraphs':meta})
m=read(R/'projects/unreal-engine-6-verse-gameplay/production/newsroom-v3/tts-manifest.json')
m.update(slug=P.name,title=read(P/'project.json')['title'],revision='grid-v1',format='animation-series',titles={'ko':read(P/'project.json')['title']},sourceReference='https://www.youtube.com/watch?v=LewXWM7HDd8',sources=['https://www.youtube.com/watch?v=VnFpz7ZwNq8','https://www.youtube.com/watch?v=H69UChNQW0U'])
m['paths']={'script':rel(H/'final.spoken-ko.json'),'scriptEn':rel(H/'final.en.json')};m['tts'].update(outputDir=rel(L/'voice'),filenameStem='narration');m['tts']['sceneGapSeconds']=.25
m['delivery']={'localStorageRoot':rel(L/'delivery')};m['authorization']=rel(H/'authorization.json')
m['editing']={'narrationPlacement':'continuous-across-example-and-explanation','ratioPolicy':'actual60-explanation40','captionStyle':'boxed-white-forest-v1'}
save(H/'tts-manifest.json',m)
print('Narration units',len(groups))
