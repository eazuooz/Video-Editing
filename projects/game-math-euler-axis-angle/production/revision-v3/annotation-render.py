"""Source-frame editorial annotations; no invented internal angles or telemetry."""
import math

def stamp(s):
 h,t=divmod(round(s*100),360000);m,t=divmod(t,6000);sec,cs=divmod(t,100)
 return f'{h}:{m:02}:{sec:02}.{cs:02}'

HEADER='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Label,Malgun Gothic,46,&H0057D5F4,&H0057D5F4,&H00101010,&H00101010,-1,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
Style: Credit,Malgun Gothic,24,&H00FFFFFF,&H00FFFFFF,&H00101010,&H00101010,0,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1
Style: Guide,Malgun Gothic,46,&H00FFFFFF,&H00FFFFFF,&H0057D5F4,&H00000000,0,0,0,0,100,100,0,0,1,5,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''

def interpolate(keys,t):
 if t<keys[0]['sourceTime'] or t>keys[-1]['sourceTime']:return None
 for a,b in zip(keys,keys[1:]):
  if a['sourceTime']<=t<=b['sourceTime']:
   if not(a.get('visible',True) and b.get('visible',True)):return None
   u=(t-a['sourceTime'])/(b['sourceTime']-a['sourceTime'])
   fields=['points'] if 'points' in a else ['center','ellipseRadius']
   def mix(x,y):return [mix(v,w) for v,w in zip(x,y)] if isinstance(x,list) else x+(y-x)*u
   return {k:mix(a[k],b[k]) for k in fields}
 return keys[-1] if keys[-1].get('visible',True) else None

def poly(points,progress=1):
 # Reveal a real traced boundary in spatial order, then retain its full shape.
 count=max(2,min(len(points),math.ceil(len(points)*progress)));shown=points[:count]
 # ASS closes drawing contours. Retrace open paths to their start so brackets
 # and curved boundaries do not acquire an unwanted diagonal closing edge.
 if shown[-1]!=shown[0]:shown=shown+list(reversed(shown[:-1]))
 return 'm '+f'{shown[0][0]:.2f} {shown[0][1]:.2f}'+''.join(f' l {x:.2f} {y:.2f}' for x,y in shown[1:])

def shape(p,kind,progress):
 if 'points' in p:return poly(p['points'],progress)
 cx,cy=p['center'];rx,ry=p['ellipseRadius']
 if kind=='brackets':
  return ' '.join(poly(v) for v in [
   [(cx-rx,cy-ry*.55),(cx-rx,cy-ry),(cx-rx*.65,cy-ry)],
   [(cx+rx*.65,cy-ry),(cx+rx,cy-ry),(cx+rx,cy-ry*.55)],
   [(cx-rx,cy+ry*.55),(cx-rx,cy+ry),(cx-rx*.65,cy+ry)],
   [(cx+rx*.65,cy+ry),(cx+rx,cy+ry),(cx+rx,cy+ry*.55)]])
 return poly([(cx+rx*math.cos(i*math.tau/64),cy+ry*math.sin(i*math.tau/64)) for i in range(65)],progress)

def event(a,b,path,color,layer,width,occluded=None):
 # Clipping reserves the fixed caption area; shapes are always hollow.
 clip='\\clip(0,0,1920,878)'
 if occluded:
  cx,cy=occluded['center'];rx,ry=occluded['ellipseRadius'];clip=f'\\iclip({round(cx-rx)},{round(cy-ry)},{round(cx+rx)},{round(cy+ry)})'
 return f'Dialogue: {layer},{stamp(a)},{stamp(b)},Guide,,0,0,0,,{{\\an7\\pos(0,0){clip}\\1a&HFF&\\bord{width}\\3c&H{color}&\\p1}}'+path

def cut_ass(c,annotations):
 duration=c['frames']/60
 credit=c['credit'].replace('{','').replace('}','')
 events=[f'Dialogue: 1,0:00:00.00,{stamp(duration)},Credit,,0,0,0,,{{\\pos(42,835)}}'+credit]
 marks=[]
 for w in annotations['windows']:
  if w['scene']!=c['scene'] or w['sourceId']!=c['sourceId']:continue
  low=max(w['sourceIn'],c['sourceStart']);high=min(w['sourceOutExclusive'],c['sourceStart']+duration)
  if high<=low:continue
  a,b=low-c['sourceStart'],high-c['sourceStart'];rgb=annotations['colors'][w['color']].lstrip('#');color=rgb[4:6]+rgb[2:4]+rgb[0:2]
  x,y=w.get('labelPosition',annotations['labelPosition'])
  if w.get('label'):
   events.append(f'Dialogue: 4,{stamp(a)},{stamp(b)},Label,,0,0,0,,{{\\pos({x},{y})\\1c&H{color}&}}'+w['label'])
  marks.append(dict(id=w['id'],sourceIn=low,sourceOutExclusive=high,label=w.get('label'),meaning=w['meaning'],keyframeSource='sources/annotation-plan-v3.json'))
  for f in range(max(0,math.ceil(a*60)),min(c['frames'],math.ceil(b*60))):
   t=c['sourceStart']+f/60;p=interpolate(w['keyframes'],t)
   if not p:continue
   path=shape(p,w['shape'],min(1,(t-low)/.25+.08))
   mask=None
   if w.get('occlusionTracker'):
    body=next(v for v in annotations['windows'] if v['id']==w['occlusionTracker']);mask=interpolate(body['keyframes'],t)
   events.append(event(f/60,(f+1)/60,path,'101010',1,10,mask))
   events.append(event(f/60,(f+1)/60,path,color,2,7,mask))
   if w.get('screenTrace'):
    past=[k['center'] for k in w['keyframes'] if low<=k['sourceTime']<=t and k.get('visible',True)]+[p['center']]
    if len(past)>1:
     events.append(event(f/60,(f+1)/60,poly(past),'101010',1,8))
     events.append(event(f/60,(f+1)/60,poly(past),color,2,5))
 return HEADER+'\n'.join(events)+'\n',marks
