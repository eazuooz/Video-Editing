from pathlib import Path
import json,math,ast,re
from PIL import ImageFont
R=Path(__file__).resolve().parents[4];P=R/'projects/avoid-game-comparisons';O=P/'production/local/reference-preserving-v2/edit';font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
def seconds(s):
 h,m,tail=s.split(':');v,ms=tail.split(',');return int(h)*3600+int(m)*60+int(v)+int(ms)/1000
def srtstamp(s):
 n=round(s*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def stamp(s):
 n=round(s*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
def parse(p):
 rows=[]
 for block in p.read_text(encoding='utf8').strip().split('\n\n'):
  lines=block.splitlines();a,b=lines[1].split(' --> ');rows.append({'start':seconds(a)+2,'end':seconds(b)+2,'text':'\n'.join(lines[2:])})
 return rows
module=ast.parse((R/'projects/game-reward-planning/production/reference-preserving-v2/build-caption-layout.py').read_text(encoding='utf8'))
ass=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ass' for t in n.targets))
ko=parse(O/'body.ko.srt');en=parse(O/'body.en.srt');assert len(ko)==len(en)
proof=[]
for i,(row,translation) in enumerate(zip(ko,en),1):
 assert row['start']==translation['start'] and row['end']==translation['end']
 lines=row['text'].split('\n');w=math.ceil(max(font.getlength(s) for s in lines))+44;h=len(lines)*62+22;x=round(960-w/2);y=round(970-h/2)
 assert len(lines)<=2 and w<=1640 and y+h+14<=1080,(i,lines,w)
 def event(layer,text):return f'Dialogue: {layer},{stamp(row["start"])},{stamp(row["end"])},Default,,0,0,0,,{text}\n'
 def box(xx,yy,color,border):return f'{{\\an7\\pos({xx},{yy})\\p1\\bord{border}\\shad0\\1c&H{color}&\\3c&H181B16&}}m 0 0 l {w} 0 {w} {h} 0 {h}'
 ass+=event(0,box(x+14,y+14,'323C07',0))+event(1,box(x,y,'FFFFFF',3))
 for k,s in enumerate(lines):ass+=event(2,f'{{\\an5\\pos(960,{y+42+k*62})\\bord0\\shad0}}{s}')
 proof.append({'cue':i,**row,'en':translation['text'],'width':w,'height':h,'x':x,'y':y,'center':[960,970],'duration':row['end']-row['start']})
for language,rows in [('ko',ko),('en',en)]:
 (O/f'captions.{language}.srt').write_text('\n\n'.join(f'{i}\n{srtstamp(r["start"])} --> {srtstamp(r["end"])}\n{r["text"]}' for i,r in enumerate(rows,1))+'\n',encoding='utf8')
(O/'captions.ko.ass').write_text(ass,encoding='utf8');(O/'caption-layout.json').write_text(json.dumps({'style':'boxed-white-forest-v1','fontSize':48,'maxLines':2,'rows':proof,'geometryPassed':True,'actualFinalPixels':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(proof),'caption pairs; fixed center960,970')
