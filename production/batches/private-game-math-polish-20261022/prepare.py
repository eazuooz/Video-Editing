"""Reuse original words/cues and recovered audio, apply current caption geometry."""
import sys,shutil
from PIL import ImageFont
from polish_common import *
e=Episode(sys.argv[1]);e.authorized()
g=module('polish_caption_geometry',R/'projects/game-math-euler-axis-angle/production/revision-v6/captions.py');g.O=e.O
font=ImageFont.truetype(str(g.FONT),48);bold=ImageFont.truetype(str(g.BOLD),48);cues=[]
assert len(e.T['koCaptions'])==len(e.T['enCaptions'])
for i,(ko,en) in enumerate(zip(e.T['koCaptions'],e.T['enCaptions'])):
 assert abs(ko['start']-en['start'])<.001 and abs(ko['end']-en['end'])<.001
 row={'id':f'original-{i+1:04}','start':ko['start'],'end':ko['end']}
 for lang,text in [('ko',ko['text']),('en',en['text'])]:
  text=text.replace('\n',' ');row[lang]=text;row[lang+'Lines']=g.wrap(text,font,bold,None);row['emphasis'+lang.title()]=None
 cues.append(row)
for lang in ['ko','en']:
 (e.O/f'captions.{lang}.srt').write_text('\n\n'.join(f'{i+1}\n{g.timestamp(x["start"])} --> {g.timestamp(x["end"])}\n'+'\n'.join(x[lang+'Lines']) for i,x in enumerate(cues))+'\n',encoding='utf8');g.ass(cues,lang)
save(e.H/'caption-restoration.json',{'cueCount':len(cues),'timelineSha256':sha(e.P/'production/timeline.json'),'wordsAndTimesUnchanged':True,'fontPx':48,'center':[960,970],'geometry':'boxed-white-forest-v1','visualReview':'pending'})
(e.O/'clips').mkdir(exist_ok=True)
for sid,count in [('intro',120),('outro',600)]:
 src=R/f'projects/game-math-euler-axis-angle/production/local/private-polish-v1/clips/{sid}.mp4';e.verify(src,count);dst=e.O/'clips'/src.name;shutil.copy2(src,dst)
print(e.id,len(cues),'caption pairs restored; brand clips reused; visual review pending',flush=True)
