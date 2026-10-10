"""Narration-timed projected observations over uninterrupted existing gameplay.

Each visible polygon/endpoint comes from editable source-frame observations.
Never bridge a detection gap, a cut, an occlusion or a different object.
Generation is not moving-pixel approval or a game-engine measurement.
"""
from pathlib import Path
import json,math,bisect,hashlib,argparse
import numpy as np
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
 n=round(t*100);h,n=divmod(n,360000);m,n=divmod(n,6000);s,c=divmod(n,100)
 return f'{h}:{m:02}:{s:02}.{c:02}'
def color(c):return ''.join(reversed([c[1:3],c[3:5],c[5:7]]))
def source_at(slot,elapsed):
 if slot.get('preservedOriginal'):return slot['baselineClip'],elapsed
 offset=0
 for seg in slot['cut']['segments']:
  length=seg['frames']/60
  if elapsed<offset+length-1e-8:return seg.get('sourceFile',slot['cut']['sourceFile']),seg['in']+elapsed-offset
  offset+=length
 raise ValueError('Source map exceeds its real-time segments')
def observation(track,t):
 keys=track['keyframes'];times=[x['t'] for x in keys]
 if len(keys)<2 or t<times[0] or t>times[-1]:return None
 if any(a<=t<=z for a,z in track.get('manualHideIntervals',[])):return None
 index=min(len(keys)-2,max(0,bisect.bisect_right(times,t)-1));a,z=keys[index:index+2]
 if z['t']-a['t']>track.get('maxInterpolationGapSeconds',.15)+1e-8:return None
 if a.get('object')!=z.get('object'):return None
 u=(t-a['t'])/(z['t']-a['t']);out={}
 for key in ['left','right','red','blue','teal']:
  if key in a and key in z:
   x,y=np.array(a[key]),np.array(z[key])
   if x.shape==y.shape:out[key]=x*(1-u)+y*u
 return out or None
def write_overlay(slug,ident):
 P=ROOT/'projects'/slug;timeline=read(P/'production/timeline.json');slot=next(x for x in timeline['scenes'] if x['id']==ident)
 assert slot['classification']=='actual'
 registry=read(B/'lines-annotation-tracks.json');spec=registry['scenes'][ident]
 tracks=[read(ROOT/x) for x in spec['landmarkSources']]
 files={slot['baselineClip']} if slot.get('preservedOriginal') else {x.get('sourceFile',slot['cut']['sourceFile']) for x in slot['cut']['segments']}
 assert all(x['sourceFile'] in files for x in tracks)
 assert all(hashlib.sha256((ROOT/x['sourceFile']).read_bytes()).hexdigest()==x['sourceSha256'] for x in tracks)
 assert all(x['coordinatePixels']==[800,450] for x in tracks)
 events=[];sx,sy=2.4,2.4
 def event(a,z,style,payload,layer=1):
  if stamp(z)==stamp(a):return
  events.append(f'Dialogue: {layer},{stamp(a)},{stamp(z)},{style},,0,0,0,,{payload}')
 def polygon(a,z,points,c,layer=1):
  points=np.asarray(points)*[sx,sy];path='m '+' l '.join(f'{round(x)} {round(y)}' for x,y in points)
  event(a,z,'Shape',r'{\an7\pos(0,0)\c&H'+color(c)+r'&\p1}'+path+r'{\p0}',layer)
 def line(a,z,p,q,c,width=2.6):
  p,q=np.array(p),np.array(q);v=q-p
  if np.linalg.norm(v)<.5:return
  n=np.array([-v[1],v[0]])/np.linalg.norm(v)*width/2
  polygon(a,z,[p+n,q+n,q-n,p-n],c)
 def outline(a,z,points,c,closed=True):
  for p,q in zip(points,np.roll(points,-1,axis=0) if closed else points[1:]):line(a,z,p,q,c)
 def circle(a,z,p,c,radius=5):
  points=[p+radius*np.array([math.cos(t),math.sin(t)]) for t in np.linspace(0,2*math.pi,21)]
  outline(a,z,points,c)
 def text(a,z,p,words,c='#ffffff',size=14,boxed=False):
  x,y=np.array(p)*[sx,sy]
  event(a,z,'BoxLabel' if boxed else 'Label',r'{\an7\pos('+str(round(x))+','+str(round(y))+r')\fs'+str(round(size*sy))+r'\c&H'+color(c)+r'&}'+words.replace('\n',r'\N'),3)
 starts=slot['lineStarts'];reveal=starts[spec.get('revealAtLine',0)]
 def spoken(keyword,fallback):
  if not slot.get('voice') or not slot.get('ttsScene'):return fallback
  voice=ROOT/slot['voice'];cache=voice.parent.parent/'asr'/f"{slot['ttsScene']}.json"
  raw=read(cache);assert raw['audio_sha256']==slot['voiceSha256']==hashlib.sha256(voice.read_bytes()).hexdigest()
  for word in raw['words']:
   if keyword not in word['text'] or word['timestamp'][0] is None:continue
   at=word['timestamp'][0];mapped=at+sum(p['seconds'] for p in slot.get('observationPauses',[]) if p['rawAt']<=at)
   if mapped>=reveal-.1:return mapped
  return fallback
 red_at=spoken('빨간',starts[spec.get('redAtLine',spec.get('revealAtLine',0))]);blue_at=spoken('파란',starts[spec.get('blueAtLine',spec.get('revealAtLine',0))]);teal_at=spoken('청록',starts[spec.get('tealAtLine',spec.get('revealAtLine',0))])
 note_start=starts[spec.get('mathNoteAtLine',0)];nx,ny=spec.get('mathNotePosition',[390,42])
 assert ny+58<330
 # A note must never cover the very endpoint or object it explains. Cache
 # observations, conservatively suppress intersecting panels, and show only
 # stable runs so an approaching landmark does not make the panel flicker.
 observations=[];note_clear=[]
 for i in range(slot['frames']):
  file,t=source_at(slot,i/60)
  current=[(track,observation(track,t)) for track in tracks if track['sourceFile']==file]
  observations.append(current);clear=i/60>=note_start
  for track,pts in current:
   if not pts:continue
   all_points=np.concatenate([np.asarray(v).reshape(-1,2) for v in pts.values()])
   low=all_points.min(axis=0);high=all_points.max(axis=0)
   if high[0]>=nx-16 and low[0]<=nx+411 and high[1]>=ny-16 and low[1]<=ny+74:clear=False
  note_clear.append(clear)
 panel_runs=[];begin=None
 for i,clear in enumerate([*note_clear,False]):
  if clear and begin is None:begin=i
  if not clear and begin is not None:
   if i-begin>=45:
    a,z=begin/60,i/60;panel_runs.append([a,z])
    polygon(a,z,[[nx,ny],[nx+395,ny],[nx+395,ny+58],[nx,ny+58]],'#171717',0)
    text(a,z,[nx+8,ny+5],'화면 투영 관찰 · 계산 예시는 별도 좌표',size=12)
    text(a,z,[nx+8,ny+26],spec['mathNote'],'#ffe082',size=14)
   begin=None
 counts={'red':0,'blue':0,'teal':0};offset=0;last=None
 for seg in slot.get('cut',{}).get('segments',[]):
  source=seg.get('sourceFile',slot['cut']['sourceFile'])
  # Baseline source credits sit at the lower left. Announce a new cut below
  # the top watermark and above the semantic labels, never over those credits.
  if last is not None and (source!=last[0] or abs(seg['in']-last[1])>.1):text(offset,min(offset+2.8,slot['seconds']),[25,65],'다른 발췌 구간 · 관찰 기준을 다시 잡습니다','#ffe082',14,True)
  offset+=seg['frames']/60;last=(source,seg['in']+seg['frames']/60)
 for i in range(slot['frames']):
  a=i/60;z=(i+1)/60
  if a<reveal:continue
  for track,pts in observations[i]:
   if pts is None:continue
   visible={'red':False,'blue':False,'teal':False}
   if 'left' in pts and 'right' in pts and a>=red_at:
    p,q=pts['left'],pts['right'];line(a,z,p,q,'#ef5350',3);circle(a,z,p,'#ffe082');circle(a,z,q,'#42a5f5');counts['red']+=1;visible['red']=True
   for key,c in [('red','#ef5350'),('blue','#42a5f5'),('teal','#26c6b8')]:
    if key not in pts or a<{'red':red_at,'blue':blue_at,'teal':teal_at}[key]:continue
    # Never draw over fixed captions or attach an outline to an unseen edge.
    if np.any(pts[key][:,1]>360):continue
    outline(a,z,pts[key],c,track.get('closed',True));counts[key]+=1;visible[key]=True
   if visible['red']:text(a,z,[25,101],spec.get('redLabel','빨강: 보이는 두 끝점의 연결'),'#ff8a80',15,True)
   if visible['blue']:text(a,z,[25,124],spec.get('blueLabel','파랑: 화면에서 감싼 관찰 범위'),'#82b1ff',15,True)
   if visible['teal']:text(a,z,[25,147],spec.get('tealLabel','청록: 관찰 부분의 비교 도형'),'#64ffda',15,True)
 header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Shape,Malgun Gothic,36,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Label,Malgun Gothic,36,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1.5,0,7,0,0,0,1
Style: BoxLabel,Malgun Gothic,36,&H00FFFFFF,&H00FFFFFF,&H00171717,&H00171717,-1,0,0,0,100,100,0,0,3,5,0,7,0,0,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
 out=ROOT/'shared/output'/slug/'overlays';out.mkdir(parents=True,exist_ok=True);path=out/f'{ident}.ass';path.write_text(header+'\n'.join(events)+'\n',encoding='utf8')
 record={'scene':ident,'frames':slot['frames'],'trackedFramesByColor':counts,'revealAt':{'base':reveal,'red':red_at,'blue':blue_at,'teal':teal_at},'pointsSource':spec['landmarkSources'],'noteVisibleIntervals':panel_runs,'noteClearance':'suppressed at conservatively intersecting observed landmark bounds; stable visible runs at least0.75s','labelContrast':'bright semantic text, opaque dark backing, bold36px at1080p','sourceMap':'baseline local time or native1x mapped cuts','measurement':'projected observed pixels; no unverified world values or engine bounds','classification':'action-led actual existing-game footage','movingPixelApproval':False}
 (out/f'{ident}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return path
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('slug');p.add_argument('scene');args=p.parse_args();print(write_overlay(args.slug,args.scene))
