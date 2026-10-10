"""Editable ASS vectors from observed landmarks and measured narration cues.

No game-world coordinates or engine state are inferred from image coordinates.
Overlay generation is a draft; final moving pixels/captions need direct review.
"""
from pathlib import Path
import argparse,json,math,bisect,hashlib
import numpy as np
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
 n=round(t*100);h,n=divmod(n,360000);m,n=divmod(n,6000);s,c=divmod(n,100)
 return f'{h}:{m:02}:{s:02}.{c:02}'
def color(c):return ''.join(reversed([c[1:3],c[3:5],c[5:7]]))
def at_points(d,t):
 k=d['keyframes'];times=[p['t'] for p in k]
 if len(k)<2:return None
 if t<times[0] or t>times[-1] or any(a<=t<=b for a,b in d.get('hideIntervals',[])):return None
 j=min(len(k)-2,max(0,bisect.bisect_right(times,t)-1));a,b=k[j:j+2];u=(t-a['t'])/(b['t']-a['t'])
 keys=(['left','right'] if 'left' in a else ['upper','lower'] if 'upper' in a else [])+(['wheel'] if 'wheel' in a and 'wheel' in b else [])
 return {key:np.array(a[key])*(1-u)+np.array(b[key])*u for key in keys}
def source_at(slot,elapsed):
 if slot.get('preservedOriginal'):return slot['baselineClip'],elapsed
 offset=0
 for segment in slot['cut']['segments']:
  seconds=segment['frames']/60
  if elapsed<offset+seconds-1e-8:return segment.get('sourceFile',slot['cut']['sourceFile']),segment['in']+elapsed-offset
  offset+=seconds
 raise ValueError('Source-frame mapping exceeded the real-time cut')
def write_overlay(slug,ident):
 P=ROOT/'projects'/slug;t=read(P/'production/timeline.json');slot=next(s for s in t['scenes'] if s['id']==ident)
 assert slot['classification']=='actual'
 registry=read(B/'interpolation-annotation-tracks.json');spec=registry['scenes'][ident]
 landmark_sources=[read(ROOT/x) for x in spec.get('landmarkSources',[spec.get('landmarks')])]
 board_sources=[read(ROOT/x) for x in spec.get('blueLandmarkSources',[])]
 source_files=({slot['baselineClip']} if slot.get('preservedOriginal') else {x.get('sourceFile',slot['cut']['sourceFile']) for x in slot['cut']['segments']})
 assert all(x['sourceFile'] in source_files for x in landmark_sources+board_sources)
 landmarks=landmark_sources[0]
 labels=read(B/'interpolation-on-footage-math.json')['labels'];math_note=next(x for x in labels if x['scene']==ident)
 sx,sy=1920/landmarks['coordinatePixels'][0],1080/landmarks['coordinatePixels'][1]
 events=[]
 def event(a,b,style,payload,layer=1):events.append(f'Dialogue: {layer},{stamp(a)},{stamp(b)},{style},,0,0,0,,{payload}')
 def polygon(a,b,points,c,layer=1):
  points=np.asarray(points);points=points*np.array([sx,sy]);path='m '+' l '.join(f'{round(x)} {round(y)}' for x,y in points)
  event(a,b,'Shape',r'{\an7\pos(0,0)\c&H'+color(c)+r'&\p1}'+path+r'{\p0}',layer)
 def line(a,b,p,q,c,width=3):
  p=np.array(p);q=np.array(q);v=q-p
  if np.linalg.norm(v)<1:return
  n=np.array([-v[1],v[0]])/np.linalg.norm(v)*width/2
  polygon(a,b,[p+n,q+n,q-n,p-n],c)
 def text(a,b,p,words,c='#ffffff',size=14,layer=3):
  x,y=np.array(p)*[sx,sy]
  event(a,b,'Label',r'{\an7\pos('+str(round(x))+','+str(round(y))+r')\fs'+str(round(size*sy))+r'\c&H'+color(c)+r'&}'+words.replace('\n',r'\N'),layer)
 # Cue starts are mapped after sentence observation pauses by plan-episodes.
 starts=slot['lineStarts'];reveal_line=spec.get('revealAtLine',0)
 reveal=starts[reveal_line]
 def spoken_start(keyword,fallback):
  if not slot.get('voice') or not slot.get('ttsScene'):return fallback
  voice=ROOT/slot['voice'];cache=voice.parent.parent/'asr'/f"{slot['ttsScene']}.json"
  if not cache.exists():return fallback
  raw_cache=read(cache)
  assert raw_cache['audio_sha256']==slot['voiceSha256']==hashlib.sha256(voice.read_bytes()).hexdigest(),'Stale ASR cannot drive annotation timing'
  for word in raw_cache['words']:
   if keyword not in word['text']:continue
   raw=word['timestamp'][0]
   if raw is None:continue
   mapped=raw+sum(p['seconds'] for p in slot.get('observationPauses',[]) if p['rawAt']<=raw)
   if mapped>=reveal-.1:return mapped
  return fallback
 red_at=spoken_start('빨간',starts[spec.get('redAtLine',reveal_line)])
 blue_at=spoken_start('파란',starts[spec.get('blueAtLine',reveal_line)])
 teal_at=spoken_start('청록',starts[spec.get('tealAtLine',min(reveal_line+1,len(starts)-1))])
 arc_at=spoken_start('기울기',max(red_at,teal_at))
 note_start=starts[math_note['line']]
 # A small fixed mathematical reminder leaves the rider, HUD and y>=880
 # caption band free. It states the defined example, not measured game values.
 note_x,note_y=spec.get('mathNotePosition',[407,124])
 polygon(note_start,slot['seconds'],[[note_x,note_y],[note_x+378,note_y],[note_x+378,note_y+65],[note_x,note_y+65]],'#171717',0)
 words=math_note['text'].replace(' / ','\n')
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',round(15*sy))
 wrapped=[]
 for paragraph in words.split('\n'):
  row=''
  for char in paragraph:
   if row and font.getlength(row+char)>880:wrapped.append(row);row=''
   row+=char
  if row:wrapped.append(row)
 words='\n'.join(wrapped)
 assert len(wrapped)<=2,'Keep the on-footage reminder brief and caption-safe'
 text(note_start,slot['seconds'],[note_x+9,note_y+6],'수학 예시 · 화면 투영선',size=13)
 text(note_start,slot['seconds'],[note_x+9,note_y+27],words,'#ffe082',size=15)
 active=0;blue_active=0
 offset=0;last_source=None;last_end=None
 for seg in slot['cut']['segments']:
  src=seg.get('sourceFile',slot['cut']['sourceFile'])
  if last_source is not None and (src!=last_source or abs(seg['in']-last_end)>.1):
   text(offset,min(offset+3,slot['seconds']),[30,350],'별도 발췌 · 같은 순간의 전후 아님','#ffe082',size=14)
  offset+=seg['frames']/60;last_source=src;last_end=seg['in']+seg['frames']/60
 for i in range(slot['frames']):
  elapsed=i/60;a=elapsed;b=(i+1)/60
  if elapsed<reveal:continue
  source_file,source_time=source_at(slot,elapsed)
  matching=[x for x in landmark_sources if x['sourceFile']==source_file and x['keyframes'][0]['t']<=source_time<=x['keyframes'][-1]['t']]
  points=at_points(matching[0],source_time) if matching else None
  board_matching=[x for x in board_sources if len(x['keyframes'])>=2 and x['sourceFile']==source_file and x['keyframes'][0]['t']<=source_time<=x['keyframes'][-1]['t']]
  board=at_points(board_matching[0],source_time) if board_matching else None
  if points is None and board is None:continue
  if points is not None and 'left' in points:
   p,q=points['left'],points['right'];center=(p+q)/2
   if elapsed>=red_at:
    active+=1
    line(a,b,p,q,'#ef5350',4)
    text(a,b,spec.get('wingLabelPosition',[center[0]-50,max(100,min(p[1],q[1])-24)]),spec.get('redLabel','보이는 몸체 가로방향'),'#ef5350')
   if elapsed>=teal_at and spec.get('showScreenReference',True):
    for x in range(-90,91,12):line(a,b,center+[x,0],center+[x+6,0],'#26c6b8',2)
   if elapsed>=arc_at and spec.get('showProjectedAngle',True):
    theta=math.atan2((q-p)[1],(q-p)[0]);arc=[center+34*np.array([math.cos(theta*j/16),math.sin(theta*j/16)]) for j in range(17)]
    for p,q in zip(arc,arc[1:]):line(a,b,p,q,'#ffe082',2)
  elif points is not None and 'upper' in points:
   p,q=points['lower'],points['upper'];v=q-p;n=np.array([-v[1],v[0]])/np.linalg.norm(v);u=v/np.linalg.norm(v)
   if elapsed>=red_at:
    active+=1
    line(a,b,p,q,'#ef5350',4);polygon(a,b,[q,q-10*u+4*n,q-10*u-4*n],'#ef5350')
    text(a,b,[max(20,min(p[0],q[0])-93),max(100,min(p[1],q[1])-25)],spec.get('redLabel','몸체 방향'),'#ef5350')
   if elapsed>=teal_at and spec.get('showScreenReference',True):
    for dy in range(-45,46,12):line(a,b,p+[60,dy],p+[60,dy+6],'#26c6b8',2)
    text(a,b,[p[0]+65,max(120,p[1]-60)],'화면 기준','#26c6b8',13)
  blue_hidden=any(x<=source_time<=y for x,y in spec.get('blueHideSourceIntervals',[]))
  wheel=(board or {}).get('wheel', (points or {}).get('wheel'))
  if elapsed>=blue_at and wheel is not None and spec.get('showWheel',True) and not blue_hidden:
   blue_active+=1
   line(a,b,wheel[0],wheel[1],'#42a5f5',4)
   text(a,b,[min(570,min(wheel[0][0],wheel[1][0])+22),min(346,min(wheel[0][1],wheel[1][1])-24)],spec.get('blueLabel','보이는 보드 방향'),'#42a5f5',13)
 header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Shape,Malgun Gothic,36,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Label,Malgun Gothic,36,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1.4,0,7,0,0,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
 if spec.get('labelOutline'):
  header=header.replace(',1,1.4,0,7,0,0,0,1',f",1,{spec['labelOutline']},0,7,0,0,0,1")
 out=ROOT/'shared/output'/slug/'overlays';out.mkdir(parents=True,exist_ok=True)
 (out/f'{ident}.ass').write_text(header+'\n'.join(events)+'\n',encoding='utf8')
 (out/f'{ident}.json').write_text(json.dumps({'scene':ident,'slotFrames':slot['frames'],'trackedVisibleFrames':active,'trackedBlueFrames':blue_active,'revealAt':{'baseLine':reveal,'red':red_at,'blue':blue_at,'teal':teal_at,'arc':arc_at},'mathNoteAt':note_start,'sourceMap':('preserved native60fps baseline clip local time' if slot.get('preservedOriginal') else 'native1x real-time source segments'),'pointsSource':spec.get('landmarkSources',[spec.get('landmarks')]),'bluePointsSource':spec.get('blueLandmarkSources',[]),'measurement':'projected image landmarks only; no engine/world calibration','classification':'action-led actual existing-game footage','movingPixelAndCaptionApproval':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return out/f'{ident}.ass'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('slug');p.add_argument('scene');a=p.parse_args();print(write_overlay(a.slug,a.scene))
