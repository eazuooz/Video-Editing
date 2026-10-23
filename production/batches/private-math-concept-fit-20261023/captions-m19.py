"""Reuse baseline math captions and align changed game passages to their actual ASR."""
from common import *
import difflib,importlib.util,re
from PIL import ImageFont
from caption_wrap_exact import wrap_exact
P=R/'projects/game-math-mesh-uv';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
spec=importlib.util.spec_from_file_location('math_caption_geometry',R/'projects/game-math-euler-axis-angle/production/revision-v6/captions.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);g.O=O
g.wrap=wrap_exact
font=ImageFont.truetype(str(g.FONT),48);bold=ImageFont.truetype(str(g.BOLD),48)
old=read(P/'production/timeline.json');T=read(H/'timeline.json');edit=read(B/'m19-narration-edits.json')['edits'];scripts={lang:{s['id']:s for s in read(P/f'script/concept-fit-v2/narration.{lang}.json')['scenes']} for lang in ['ko','en']}
def norm(s):return re.sub('[^a-z0-9가-힣]','',s.lower())
def aligned(s):
 a=read(O/f'audio/asr/{s["id"]}.json');assert a['audioSha256']==s['voiceSha256'];chars='';starts=[];ends=[]
 words=list(a['words']);fix=H/'targeted-asr-boundaries.json'
 if fix.exists():
  for r in read(fix)['rows']:
   if r['scene']!=s['id']:continue
   words=[w for w in words if not (r['start']-.1 <= sum(float(t or 0) for t in w['timestamp'])/2 < r['end']+.1)]
   words += [dict(text=w['text'],timestamp=[r['start']+float(t or 0) for t in w['timestamp']]) for w in r['result']['chunks']]
  words.sort(key=lambda w:float(w['timestamp'][0] or 0))
 for w in words:
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
pairedEnglish={}
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
   # Exact paragraph assembly boundaries constrain recognition timestamps at chunk joins.
   paragraph=s['cues'][j-1];u=max(u,paragraph['start']);v=min(v,paragraph['end']);assert v>u,(sid,j,z,u,v)
   rows.append(dict(id=f'{sid}.L{j:02}.S{z}',scene=sid,line=j,start=s['start']+u,end=s['start']+v,ko=k,en=e,origin='actual blind word ASR mapped to complete source sentences'))
   alignment.append(dict(scene=sid,line=j,sentence=z,start=u,end=v,asr=rel(O/f'audio/asr/{sid}.json')))
 assert offset==sum(len(norm(x)) for x in scripts['ko'][sid]['lines'])
rows.sort(key=lambda x:x['start'])
for row in rows:
 for lang in ['ko','en']:
  row[lang+'Lines']=g.wrap(row[lang],font,bold,None);row['emphasis'+lang.title()]=None
 terms=[('법선','normal'),('정점','vertex'),('인덱스','index'),('삼각형','triangle'),('좌표','coordinates'),('보간','interpolation')]
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
save(H/'captions.json',dict(cues=rows,timelineSha256=sha(H/'timeline.json'),alignment=alignment,geometry=geometry,review='Pending encoded pixel/mobile and moving cue inspection',sourceParagraphs=97))
print(len(rows),'paired cues; original math captions retained')
