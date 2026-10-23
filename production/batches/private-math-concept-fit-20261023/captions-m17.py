"""Reuse baseline math captions and align changed game passages to their actual ASR."""
from common import *
import difflib,importlib.util,re
from PIL import ImageFont
P=R/'projects/game-math-camera-projection';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
spec=importlib.util.spec_from_file_location('math_caption_geometry',R/'projects/game-math-euler-axis-angle/production/revision-v6/captions.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);g.O=O
font=ImageFont.truetype(str(g.FONT),48);bold=ImageFont.truetype(str(g.BOLD),48)
old=read(P/'production/timeline.json');T=read(H/'timeline.json');edit=read(B/'m17-narration-edits.json')['edits'];scripts={lang:{s['id']:s for s in read(P/f'script/concept-fit-v2/narration.{lang}.json')['scenes']} for lang in ['ko','en']}
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
pairedEnglish={('05', 6): ['Orbiting a camera does not require rewriting every building’s world coordinates.', 'A later step changes the viewing frame.'], ('08', 3): ['New blocks also change the structure.', 'Persistent windows or railings help compare the surrounding moments.'], ('08', 4): ['Wide and close framing change a corner’s image extent.', 'Calculations should retain view coordinates and projection parameters separately.'], ('08', 5): ['Multiplying a3D value by a matrix does not immediately produce the final pixel.', 'Clipping,division and viewport mapping remain.'], ('08', 6): ['A tower near the top of the image cannot use worldy directly as screeny.', 'Camera up and screen down also differ.'], ('11', 1): ['Carrying the cube changes its location in the chamber.', 'Compare it with the fixed pillars.'], ('11', 2): ['The player sets down the cube from another view and connects the laser.', 'World placement and image position are different information.'], ('11', 3): ['Compare the large close cube with wider chamber views.', 'Image proportions alone do not reveal its exact viewz.'], ('11', 4): ['The portal view is another viewing problem.', 'We use visible cube and pillar landmarks without inferring portal rendering internals.'], ('11', 6): ['Real gameplay mixes changes.', 'A one-point calculation isolates world placement,camera and projection one at a time.'], ('14', 6): ['The image does not establish the game’s near distance or depth format.', 'Our defined triangle supplies the numeric clipping proof.'], ('14', 7): ['Keep the same landmark through closer or wider views.', 'Switching to another roof changes the object of comparison.'], ('14', 8): ['Next we map the surviving points to final screen coordinates.', 'Here too, distinguish camera-space axes from pixel-space axes.']}
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
save(H/'captions.json',dict(cues=rows,timelineSha256=sha(H/'timeline.json'),alignment=alignment,geometry=geometry,review='Pending encoded pixel/mobile and moving cue inspection',sourceParagraphs=100))
print(len(rows),'paired cues; original math captions retained')
