"""Reuse baseline math captions and align changed game passages to their actual ASR."""
from common import *
import difflib,importlib.util,re
from PIL import ImageFont
P=R/'projects/game-math-projection-depth';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
spec=importlib.util.spec_from_file_location('math_caption_geometry',R/'projects/game-math-euler-axis-angle/production/revision-v6/captions.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);g.O=O
font=ImageFont.truetype(str(g.FONT),48);bold=ImageFont.truetype(str(g.BOLD),48)
old=read(P/'production/timeline.json');T=read(H/'timeline.json');edit=read(B/'m18-narration-edits.json')['edits'];scripts={lang:{s['id']:s for s in read(P/f'script/concept-fit-v2/narration.{lang}.json')['scenes']} for lang in ['ko','en']}
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
 ('03',2):['Surfaces at similar screen positions may cover one another.','Screen x and y alone cannot determine their front-to-back relationship.'],
 ('03',4):['Computed depth is the output of our chosen mapping, not a distance label.','A depth of 0.825 does not mean 0.825 world units.'],
 ('03',6):['We have not established that the game uses this depth representation.','The footage connects the need for occlusion handling to our explicit calculation.'],
 ('03',7):['Compare depth values produced by the same camera and projection.','Values from different views are not directly comparable.'],
 ('06',3):['Our edge calculation explains why the screen midpoint needs u = 0.2.','That number was not measured from this game.'],
 ('06',4):['We do not infer which shader creates this roof pattern.','We observe why surface and image locations need a correspondence.'],
 ('09',3):['Adding blocks changes terrace height and structure.','Distinguish these moments from camera-only movement.'],
 ('09',5):['In a development project, name a point attached to the object and log its local position.','Then record world and view values in order.'],
 ('09',6):['Log all four clip components before division.','Omitting w obscures the connection between clipping and the projected result.'],
 ('09',7):['Record viewport origin, width and height when they change.','Using full-screen dimensions for a split window misplaces the marker.'],
 ('09',8):['These game pixels do not reveal intermediate numbers.','Practice with actual values accessible in your own project.'],
 ('09',9):['Depth and surface patterns take the chain beyond moving one point.','Occlusion and interpolation use the same sequence of calculations.'],
 ('09',10):['When the result is wrong, inspect the first incorrect transform.','Carry that method into the upcoming mesh and texture exercises.']}
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
 terms=[('클리핑','clipping'),('좌표','coordinates'),('시야각','field of view'),('출력 창','viewport'),('직교','orthographic'),('원근','perspective'),('줌','zoom')]
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
save(H/'captions.json',dict(cues=rows,timelineSha256=sha(H/'timeline.json'),alignment=alignment,geometry=geometry,review='Pending encoded pixel/mobile and moving cue inspection',sourceParagraphs=66))
print(len(rows),'paired cues; original math captions retained')
