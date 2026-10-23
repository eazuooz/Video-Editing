"""Reuse baseline math captions and align changed game passages to their actual ASR."""
from common import *
import difflib,importlib.util,re
from PIL import ImageFont
P=R/'projects/game-math-camera-frustum';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
spec=importlib.util.spec_from_file_location('math_caption_geometry',R/'projects/game-math-euler-axis-angle/production/revision-v6/captions.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);g.O=O
font=ImageFont.truetype(str(g.FONT),48);bold=ImageFont.truetype(str(g.BOLD),48)
old=read(P/'production/timeline.json');T=read(H/'timeline.json');edit=read(B/'m16-narration-edits.json')['edits'];scripts={lang:{s['id']:s for s in read(P/f'script/concept-fit-v2/narration.{lang}.json')['scenes']} for lang in ['ko','en']}
def norm(s):return re.sub('[^a-z0-9가-힣]','',s.lower())
def aligned(s):
 a=read(O/f'audio/asr/{s["id"]}.json');assert a['audioSha256']==s['voiceSha256'];chars='';starts=[];ends=[]
 for w in a['words']:
  word=norm(w['text']);u,v=w['timestamp'];u=float(u or 0);v=float(v if v is not None else s['seconds']-.2)
  for j,c in enumerate(word):chars+=c;starts.append(u+(v-u)*j/max(1,len(word)));ends.append(u+(v-u)*(j+1)/max(1,len(word)))
 expected=''.join(norm(x) for x in scripts['ko'][s['id']]['lines']);mapping={}
 for tag,i,j,k,l in difflib.SequenceMatcher(None,expected,chars,autojunk=False).get_opcodes():
  if tag=='equal':
   for q in range(j-i):mapping[i+q]=(starts[k+q],ends[k+q])
  elif tag=='replace' and l>k:
   for q in range(j-i):mapping[i+q]=(starts[k]+(ends[l-1]-starts[k])*q/(j-i),starts[k]+(ends[l-1]-starts[k])*(q+1)/(j-i))
 for i in range(len(expected)):
  if i not in mapping:
   left=mapping.get(i-1,(0,0))[1];right=next((mapping[j][0] for j in range(i+1,len(expected)) if j in mapping),s['seconds']-.2);mapping[i]=(left,max(left+.01,right))
 return mapping
rows=[];alignment=[]
pairedEnglish={
 ('05',4):['Track the same roof: parts come forward while others are hidden.','Camera position and direction change how the scene reads.'],
 ('05',5):['These pixels alone do not establish the game’s projection matrix.','We will not infer numeric zoom settings either.'],
 ('05',6):['Our diagram holds camera position, field of view and viewport fixed, then changes one condition.','Controlling those conditions lets us identify the cause in the calculation.'],
 ('05',7):['Remember how the building’s three faces overlap.','Next we draw the camera’s potential viewing volume in three dimensions.'],
 ('08',2):['The higher viewpoint reveals roofs and inner terraces.','Entering the view and emerging from behind another object are different events.'],
 ('08',3):['Walls that overlap frontally separate in an oblique view.','Changing camera direction rearranges the same spatial relationship on screen.'],
 ('08',5):['Leaving the image does not prove the building vanished.','Consider which region the viewing volume contains.'],
 ('08',7):['The next diagram fixes camera position and changes only field of view.','This distinguishes movement from a field-of-view change.'],
 ('13',2):['The wide view changes to a closer view.','The roof grows while less surrounding water fits in the image.'],
 ('13',3):['Watch the other roofs in the background too.','Compare both foreground and distant targets to make the observation more precise.'],
 ('16',2):['In close framing, part of the large wall takes up much of the image.','Wide framing includes water and the surrounding structures.'],
 ('16',3):['If viewing direction also changes, visible area is not explained by enlargement alone.','Record viewpoint conditions too.'],
 ('16',6):['We are not claiming which camera function this game calls.','The factors 2 and 4/3 come from our controlled example, not measurements of this footage.'],
 ('16',7):['A readable result matters during gameplay.','In a mathematical example, knowing which variable changed matters.','Connect those roles while keeping the evidence distinct.'],
 ('16',8):['Suppose we want to remove distance-based shrinking.','Maps and modeling drawings can use a different projection.'],
 ('19',2):['Choosing a different face to read may require a different viewing direction.','Enlargement alone cannot reveal every hidden roof or wall.'],
 ('19',3):['The orthographic diagram showed a scale without distance-based shrinking.','It demonstrated a viewing option, not a confirmed property of this game.'],
 ('19',4):['Choose viewing direction, perspective and coverage before dividing the output.','The next problem returns to the two players’ viewport sizes.']}
for s in T['scenes']:
 sid=s['id']
 if sid not in edit:
  shift=s['start']-s['baselineStart']
  for i,(ko,en) in enumerate(zip(old['koCaptions'],old['enCaptions'])):
   if ko['start']>=s['baselineStart']-.001 and ko['start']<s['baselineStart']+s['baselineSeconds']-.001:
    rows.append(dict(id=f'{sid}.baseline.{i}',scene=sid,start=ko['start']+shift,end=ko['end']+shift,ko=ko['text'].replace('\n',' '),en=en['text'].replace('\n',' '),origin='unchanged original caption timing'))
  continue
 mapping=aligned(s);offset=0
 for j,(ko,en) in enumerate(zip(scripts['ko'][sid]['lines'],scripts['en'][sid]['lines']),1):
  ksent=g.sentences(ko);esent=pairedEnglish.get((sid,j),g.sentences(en))
  if len(ksent)!=len(esent):ksent,esent=[ko],[en]
  for z,(k,e) in enumerate(zip(ksent,esent),1):
   n=len(norm(k));u=mapping[offset][0];v=mapping[offset+n-1][1];offset+=n
   rows.append(dict(id=f'{sid}.L{j:02}.S{z}',scene=sid,line=j,start=s['start']+u,end=s['start']+v,ko=k,en=e,origin='actual blind word ASR mapped to complete source sentences'))
   alignment.append(dict(scene=sid,line=j,sentence=z,start=u,end=v,asr=rel(O/f'audio/asr/{sid}.json')))
 assert offset==sum(len(norm(x)) for x in scripts['ko'][sid]['lines'])
rows.sort(key=lambda x:x['start'])
for row in rows:
 for lang in ['ko','en']:
  row[lang+'Lines']=g.wrap(row[lang],font,bold,None);row['emphasis'+lang.title()]=None
 terms=[('시야각','field of view'),('출력 창','viewport'),('직교','orthographic'),('원근','perspective'),('줌','zoom')]
 for ko,en in terms:
  a=row['ko'].find(ko);b=row['en'].lower().find(en)
  if a>=0 and b>=0:
   row['emphasisKo']=dict(start=a,end=a+len(ko),role='focus');row['emphasisEn']=dict(start=b,end=b+len(en),role='focus')
   for lang in ['ko','en']:row[lang+'Lines']=g.wrap(row[lang],font,bold,row['emphasis'+lang.title()])
   break
 assert 2<=row['start']<row['end']<=T['seconds']-10+.01
for a,b in zip(rows,rows[1:]):
 if a['end']>b['start']+.025:raise ValueError(('Overlapping captions require review',a['id'],b['id']))
geometry={}
for lang in ['ko','en']:
 (O/f'captions.{lang}.srt').write_text('\n\n'.join(f'{i+1}\n{g.timestamp(x["start"])} --> {g.timestamp(x["end"])}\n'+'\n'.join(x[lang+'Lines']) for i,x in enumerate(rows))+'\n',encoding='utf8');geometry[lang]=g.ass(rows,lang)
save(H/'captions.json',dict(cues=rows,timelineSha256=sha(H/'timeline.json'),alignment=alignment,geometry=geometry,review='Pending encoded pixel/mobile and moving cue inspection',sourceParagraphs=134))
print(len(rows),'paired cues; original math captions retained')
