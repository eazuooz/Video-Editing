"""Compose manually observed screen guides on the unchanged original clock."""
import math,sys
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();p=e.H/'observed-guides.json';plan=read(p);events=[]
def stamp(t):
 c=round(t*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'
def color(hexcolor):return '&H'+hexcolor[5:7]+hexcolor[3:5]+hexcolor[1:3]+'&'
def event(start,end,layer,style,text):events.append(f'Dialogue: {layer},{stamp(start)},{stamp(end)},{style},,0,0,0,,{text}')
for g in plan['guides']:
 s=next(x for x in e.T['scenes'] if x['id']==g['scene']);keys=g['keyframes'];a=keys[0][0];z=keys[-1][0]
 assert s['classification']=='actual' and 0<=a<z<=s['seconds']
 boundary=0
 for part in s['cut']['segments'][:-1]:
  boundary+=part['frames']/60;assert not a<boundary<z,'Guide must clear at source cuts'
 for boundary in plan.get('internalCutBoundaries',{}).get(s['id'],[]):
  assert not a<boundary<z,'Guide must clear at reviewed replacement cuts'
 scale,ox,oy=plan['renderMapping']['inset' if s['id'] in plan['captionClearanceScenes'] else 'full']
 lx,ly=g['labelPosition'];lx=lx*scale+ox;ly=ly*scale+oy
 tint=color({'focus':'#F0D379','body':'#FF6A72','board':'#67B8FF'}.get(g['role'],'#79D7BD'))
 event(s['start']+a,s['start']+z,4,'GuideText',rf'{{\an5\pos({lx:.1f},{ly:.1f})\c{tint}\fad(100,100)}}'+g['label'])
 for frame in range(round(a*60),round(z*60)):
  t=frame/60
  k=next((i for i in range(len(keys)-1) if keys[i][0]<=t<keys[i+1][0]),len(keys)-2)
  left,right=keys[k],keys[k+1];u=min(1,max(0,(t-left[0])/(right[0]-left[0])))
  cx,cy,rx,ry=[(left[j]*(1-u)+right[j]*u)*scale for j in range(1,5)];cx+=ox;cy+=oy
  reveal=min(1,(t-a+.0167)/.2)
  # An open ring points out a region without claiming an exact segmentation.
  pts=[(cx+rx*math.cos(v),cy+ry*math.sin(v)) for v in [math.radians(35+290*reveal*i/32) for i in range(33)]]
  # Short leader ends outside the ring; it does not paint over the target.
  dx,dy=lx-cx,ly-cy;norm=math.hypot(dx,dy) or 1
  tx,ty=cx+dx/norm*(rx+9),cy+dy/norm*(ry+9)
  if g.get('shape')=='direction':
   # Two observed screen endpoints; no inferred world axis or measured angle.
   x1,y1=cx,cy;x2,y2=rx+ox,ry+oy
   x2=x1+(x2-x1)*reveal;y2=y1+(y2-y1)*reveal
   segments=[((x1,y1),(x2,y2))]
   dx2,dy2=x2-x1,y2-y1;length=math.hypot(dx2,dy2) or 1
   nx,ny=-dy2/length*8,dx2/length*8
   for x,y in [(x1,y1),(x2,y2)]:segments.append(((x-nx,y-ny),(x+nx,y+ny)))
  elif g.get('shape')=='corners':
   # Screen-space output-region brackets, not a claimed camera frustum.
   segments=[];arm=min(rx,ry)*.24*reveal
   for sx in [-1,1]:
    for sy in [-1,1]:
     x,y=cx+sx*rx,cy+sy*ry
     segments.extend([((x,y),(x-sx*arm,y)),((x,y),(x,y-sy*arm))])
  else:segments=list(zip(pts,pts[1:]))
  if g.get('leader',True):segments.append(((lx,ly-31 if ly>cy else ly+31),(tx,ty)))
  # Filled narrow quads keep the ring genuinely open. ASS outlines otherwise
  # close an open polygon with an unwanted straight chord across the target.
  for layer,width,ink in [(1,8,'&H101010&'),(2,4.5,tint)]:
   paths=[]
   for (x1,y1),(x2,y2) in segments:
    length=math.hypot(x2-x1,y2-y1) or 1;nx=-(y2-y1)/length*width;ny=(x2-x1)/length*width
    corners=[(x1+nx,y1+ny),(x2+nx,y2+ny),(x2-nx,y2-ny),(x1-nx,y1-ny)]
    paths.append('m '+' l '.join(f'{x:.1f} {y:.1f}' for x,y in corners))
   event(s['start']+t,s['start']+(frame+1)/60,layer,'GuideShape',rf'{{\an7\pos(0,0)\1a&H00&\c{ink}\bord0\p1}}'+' '.join(paths)+r'{\p0}')
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: GuideText,Malgun Gothic,50,&H00FFFFFF,&H00FFFFFF,&H00101010,&H00101010,1,0,0,0,100,100,0,0,1,4,0,5,0,0,0,1
Style: GuideShape,Malgun Gothic,50,&HFF000000,&HFF000000,&H00101010,&H00101010,0,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
dst=e.O/'composition-polish.ass';dst.write_text(header+'\n'.join(events)+'\n',encoding='utf8')
save(e.H/'observed-guide-composition.json',{'timelineSha256':sha(e.P/'production/timeline.json'),'plan':rel(p),'planSha256':sha(p),'globalAss':rel(dst),'globalAssSha256':sha(dst),'guides':len(plan['guides']),'eventCount':len(events),'pixelReview':'pending','captionClearanceScenes':plan['captionClearanceScenes']})
print(e.id,'observed guides prepared; not final-review approved',flush=True)
