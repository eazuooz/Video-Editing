from pathlib import Path
import json,math
from PIL import ImageFont
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';O=P/'production/local/reference-preserving-v2/edit';rows=json.loads((O/'caption-tracks.json').read_text(encoding='utf8'));font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
def time(s):
 n=round(s*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
ass='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
proof=[]
for i,row in enumerate(rows,1):
 lines=row['ko'].split('\n');width=math.ceil(max(font.getlength(s) for s in lines))+44;height=len(lines)*62+22;x=round(960-width/2);y=round(970-height/2)
 assert len(lines)<=2 and width<=1640 and x>=2 and x+width+16<=1920 and y+height+16<=1080,(i,width,lines)
 def event(layer,text):return f'Dialogue: {layer},{time(row["start"])},{time(row["end"])},Default,,0,0,0,,{text}\n'
 def box(xx,yy,color,border):return f'{{\\an7\\pos({xx},{yy})\\p1\\bord{border}\\shad0\\1c&H{color}&\\3c&H181B16&}}m 0 0 l {width} 0 {width} {height} 0 {height}'
 ass+=event(0,box(x+14,y+14,'323C07',0))+event(1,box(x,y,'FFFFFF',3))
 for k,s in enumerate(lines):ass+=event(2,f'{{\\an5\\pos(960,{y+42+k*62})\\bord0\\shad0}}{s}')
 proof.append(dict(cue=i,start=row['start'],end=row['end'],scene=row['scene'],line=row['line'],lines=lines,width=width,height=height,x=x,y=y,center=[960,970]))
(O/'captions.ko.ass').write_text(ass,encoding='utf8');(O/'caption-layout.json').write_text(json.dumps({'style':'boxed-white-forest-v1','fontSize':48,'maxLines':2,'geometryPassed':True,'actualPixels':'pending','rows':proof},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('153 caption layouts measured; maxwidth',max(x['width'] for x in proof))
