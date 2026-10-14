"""Use the completed per-frame tracking; preserve the source's hard camera cut."""
import importlib.util,math,shutil
from pathlib import Path
p=Path(__file__).with_name('review-media-common-v15.py');s=importlib.util.spec_from_file_location('review_media',p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
source_plan=m.PROD/'native-annotation-plan-v19b.json';plan=m.read(source_plan)
out=m.ROOT/'production/research/game-lighting-history/local/native-annotations-v19c';assert not out.exists();out.mkdir(parents=True)
ray=plan['cuts'][0];tracks=m.read(m.ROOT/ray['tracking'])['samples']
original_ass=m.ROOT/ray['annotations'];head=original_ass.read_text('utf8').split('[Events]')[0]+'[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
def at(f):
 cs=round(f*100/60);return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'
def event(a,b,text,layer=0):return f'Dialogue: {layer},{at(a)},{at(b)},Label,,0,0,0,,{text}\n'
def label(x,y,text,color='FFFFFF'):return r'{\an7\pos('+str(round(x))+','+str(round(y))+r')\1c&H'+color+'&}'+text
def line(a,b,color,width=3):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 if length<1:return ''
 nx,ny=-dy/length*width/2,dx/length*width/2
 pts=[(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)]
 return r'{\an7\pos(0,0)\p1\shad0\bord0\1a&H00&\1c&H'+color+'&}m '+f'{round(pts[0][0])} {round(pts[0][1])}'+' l '+' '.join(f'{round(x)} {round(y)}' for x,y in pts[1:])
ass=head
for t in tracks:
 f=t['localFrame'];h=t['visibleCubeHull'];bx,by=t['bulbCenter'];r=min(80,max(42,t['bulbRadius']+10))
 if not 50<=f<321:continue
 for a,b in zip(h,h[1:]):
  # A crop/caption boundary is not an actual edge of the blue cube.
  if (a[1]>=880 and b[1]>=880) or (a[0]>=1900 and b[0]>=1900):continue
  ass+=event(f,f+1,line(a,b,'C8C850',4))
 circle=[(bx+r*math.cos(i*math.tau/40),by+r*math.sin(i*math.tau/40)) for i in range(41)]
 for a,b in zip(circle,circle[1:]):ass+=event(f,f+1,line(a,b,'5265FF',4))
 ass+=event(f,f+1,label(max(500,bx-230),max(125,by-85),'광원 위치','80D4FF'),2)
 ass+=event(f,f+1,label(min(1500,min(x[0] for x in h)+28),max(145,min(x[1] for x in h)+25),'가리는 상자','C8C850'),2)
ass+=event(50,270,label(34,775,'화면 투영 위치 비교 · 게임 월드 거리 측정 아님'),2)
for c in plan['cuts']:
 ap=out/(c['id']+'.annotations.ass')
 if c==ray:ap.write_text(ass,'utf8')
 else:shutil.copyfile(m.ROOT/c['annotations'],ap)
 c['annotations']=m.rel(ap);c['annotationsSha256']=m.sha(ap);c['output']=m.rel(out/(c['id']+'.annotated.mp4'));c['verification']=m.rel(out/(c['id']+'.annotated.verification.json'))
plan.update(preparedAt=m.stamp(),preparedFrom=dict(path=m.rel(source_plan),sha256=m.sha(source_plan)),cameraJumpResolution=dict(localFrame=278,globalFrame=19929,diagnostic='production/research/game-lighting-history/local/native-annotations-v19b/bulb-camera-jump-278.png',diagnosticSha256=m.sha(m.ROOT/'production/research/game-lighting-history/local/native-annotations-v19b/bulb-camera-jump-278.png'),directlyRead=True,observed='Actual hard camera change moves both cube and bulb; per-frame observed position retained, no interpolation across cut.',priorFailedThresholdPreserved=True),croppedCubeBoundaryNotDrawn=True)
m.save(m.PROD/'native-annotation-plan-v19c.json',plan)
print(m.json.dumps(dict(cuts=2,trackedFrames=360,trackingNotRepeated=True,mediaEncoded=0,movingPixelsApproved=False)))
