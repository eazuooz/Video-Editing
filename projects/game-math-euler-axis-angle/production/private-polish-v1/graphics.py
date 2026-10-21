"""Original code/quiz content, with readable semantic colors and cue highlights."""
import re
from PIL import ImageFont
import common as c
b=c.module('polish_ass',c.P/'production/revision-v2/render-spatial.py')
FONT=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',48)
# ASS BGR, all dark enough on the retained white lecture background.
COLORS={'keyword':'854F6C','function':'805800','variable':'875628','number':'333BA0','plain':'282520','comment':'636358'}

def code_runs(line):
 tokens=re.findall(r'\s+|\d+\.\d+|[A-Za-z_]\w*|.',line)
 result=[]
 for i,t in enumerate(tokens):
  role='plain'
  if t in ['double','constexpr','if','return']:role='keyword'
  elif t in ['wrapPi','remainder']:role='function'
  elif t in ['angle','pi','tau','w','delta','end','start','value','t']:role='variable'
  elif t[0].isdigit():role='number'
  result.append((t,role))
 return result

def code():
 c.authorized();s=c.SCENES['15'];l=c.LESSON['15'];n=s['frames'];ov=b.Overlay()
 ov.text(0,n,l['title'],120,65,54,bold=True)
 ov.text(0,n,'입력·출력: 라디안 (radian) / 유한한 실수',120,150,35)
 for i,line in enumerate(l['code']):
  ov.text(0,n,str(i+1),130,315+i*57,30,color='777777')
  x=200+FONT.getlength(line)
  colored=''.join('{\\c&H'+COLORS[role]+'&}'+token.replace('{',r'\{').replace('}',r'\}') for token,role in code_runs(line))
  ov.text(0,n,'',200,305+i*57,48)
  ov.lines[-1]=ov.lines[-1].replace('\\fs48','\\fnConsolas\\fs48')+colored
  assert x<1830,(i,x)
 rows=[1,3,4,4,7,8]
 for i,row in enumerate(rows):
  a=round(s['lineStarts'][i]*60);z=round(s['lineStarts'][i+1]*60) if i+1<len(rows) else n
  ov.text(a,z,l['beats'][i],120,225,43,'805800',True)
  y=305+row*57
  ov.text(a,z,'▶',75,y,35,'4C8515',True)
  ov.leader(a,z,(194,y+52),(min(1810,200+FONT.getlength(l['code'][row])),y+52),'4C8515',True)
 ov.text(0,n,'문법 색: 키워드 · 함수 · 변수 · 숫자   /   ▶ 현재 설명 줄',120,835,32)
 path=c.O/'code15.ass';ov.save(path)
 c.ff(['-f','lavfi','-i','color=c=white:s=1920x1080:r=60','-vf',f'ass={path.name}',
       '-frames:v',n,'-an',*c.ENC,c.O/'clips/15.mp4'],'code15.log',c.O)
 c.save(c.H/'code-style.json',{'scene':'15','originalCodeUnchanged':True,'font':'Consolas48','colorsAssBgr':COLORS,
  'activeRowMarker':'green triangle + underline; separate from syntax role','originalLineStarts':s['lineStarts']})

def quiz():
 # Correct display-only unit confusion in the retained beat, preserving voice.
 c.authorized();s=c.SCENES['25'];ov=b.Overlay();a=round(s['lineStarts'][1]*60);z=round(s['lineStarts'][2]*60)
 ov.white_band(a,z,(90,238,1830,403))
 ov.text(a,z,'Δ = −340° + 360° = +20°',960,322,48,'875628',True,align=5)
 path=c.O/'quiz25.ass';ov.save(path)
 source=c.O/'manim/videos/flat-scenes/1080p60/Scene25.mp4'
 c.ff(['-i',source,'-vf',f'fps=60,ass={path.name},setsar=1','-frames:v',s['frames'],'-an',*c.ENC,c.O/'clips/25.mp4'],'quiz25.log',c.O)
 c.save(c.H/'display-correction.json',{'scene':'25','old':'wrapPi(-340°)','new':'−340° +360° =+20°',
  'reason':'wrapPi accepts radians. Original narration and worked answer already use degree arithmetic; remove misleading function/unit label only.',
  'voiceOrCaptionChanges':False,'windowSeconds':[a/60,z/60]})

if __name__=='__main__':code();quiz()
