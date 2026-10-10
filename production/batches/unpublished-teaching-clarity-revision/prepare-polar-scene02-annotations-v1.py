"""Editable, manually keyed observation brackets and illustrative components.

The bracket identifies a whole visible rider. The separate component/camera
glyphs are explanatory diagrams, not recovered world coordinates.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, math
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/scene02-annotations-v1'
COLORS={'horizontal':'#e64a4a','height':'#77bb64','radius':'#609cec','focus':'#ffda69'}
FONT='C:/Windows/Fonts/malgun.ttf'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def label(d,xy,text,color='white',size=30):
 font=ImageFont.truetype(FONT,size);box=d.textbbox(xy,text,font=font)
 d.rounded_rectangle((box[0]-12,box[1]-8,box[2]+12,box[3]+8),radius=6,fill=(12,18,24,205))
 d.text(xy,text,font=font,fill=color)
def line(d,a,b,color,width=6):
 d.line((a,b),fill=(8,12,18,220),width=width+4);d.line((a,b),fill=color,width=width)
def arrow(d,a,b,color,width=6):
 line(d,a,b,color,width);angle=math.atan2(b[1]-a[1],b[0]-a[0]);length=21
 p=[b,(b[0]-length*math.cos(angle-.48),b[1]-length*math.sin(angle-.48)),(b[0]-length*math.cos(angle+.48),b[1]-length*math.sin(angle+.48))]
 d.polygon(p,fill=color)
def point_at(frame,keys,cuts):
 section=next(c for c in cuts if c['sceneStartFrame']<=frame<c['sceneStartFrame']+c['frames'])
 k=[v for v in keys if section['sceneStartFrame']<=v[0]<section['sceneStartFrame']+section['frames']]
 if frame<=k[0][0]:return [3*k[0][1],3*k[0][2]]
 for a,b in zip(k,k[1:]):
  if a[0]<=frame<=b[0]:
   t=(frame-a[0])/(b[0]-a[0]);return [3*(a[1]+t*(b[1]-a[1])),3*(a[2]+t*(b[2]-a[2]))]
 return [3*k[-1][1],3*k[-1][2]]
def annotate(im,frame,plan):
 layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);t=frame/60
 x,y=point_at(frame,plan['observationKeyframes640'],plan['cuts'])
 # Whole-rider observation bracket; no false helmet/world-coordinate precision.
 if t<22.72 or t>=34.78:
  w,h=90,120
  for sx in [-1,1]:
   for sy in [-1,1]:
    a=(x+sx*w,y+sy*h)
    line(d,a,(a[0]-sx*28,a[1]),COLORS['focus'],4)
    line(d,a,(a[0],a[1]-sy*28),COLORS['focus'],4)
  label(d,(x+135,max(150,y-125)),'관찰 대상',COLORS['focus'],27)
 # Narrated preview before the detailed coordinate lesson; not an engine claim.
 if t<7.98:
  label(d,(70,150),'먼저 점프와 착지를 보세요',size=35)
 elif t<15:
  label(d,(70,150),'바닥 방향만으로는 높이를 표현할 수 없습니다',size=32)
  glyph(d,x-420,y+45,'높이 성분',False)
 elif t<22.72:
  label(d,(70,150),'대상의 위치와 카메라의 시점은 다릅니다',size=32)
  cx,cy=x-440,y+30
  d.rounded_rectangle((cx-36,cy-25,cx+36,cy+25),radius=7,outline=COLORS['radius'],width=6)
  d.polygon([(cx+36,cy-18),(cx+62,cy-32),(cx+62,cy+32),(cx+36,cy+18)],outline=COLORS['radius'])
  arrow(d,(cx+78,cy),(x-110,y),COLORS['radius'])
  label(d,(cx-125,cy+66),'카메라 관계도',COLORS['radius'],27)
 elif t<29.08:
  label(d,(70,150),'같은 위치를 표현하는 두 가지 도구',size=34)
  label(d,(70,225),'원통: 바닥 방향 + 높이',COLORS['height'],30)
  label(d,(70,280),'구면: 거리 + 두 방향각',COLORS['radius'],30)
 elif t<34.78:
  label(d,(70,150),'거리 · 높이 · 시점을 구분해 보세요',size=34)
 elif t<42.5:
  label(d,(70,150),'착지해도 수평 이동은 이어집니다',size=34)
  glyph(d,x-430,min(y+30,620),'높이',True)
 else:
  label(d,(70,150),'화면 중앙에 있어도 세계에서는 움직입니다',size=32)
  # Actual image-center guide, explicitly an image-space reference.
  d.rectangle((900,370,1020,770),outline=(96,156,236,150),width=3)
  label(d,(70,225),'화면 중앙 기준선',COLORS['radius'],27)
 # Distinct source intervals must not be mistaken for one continuous run.
 for c in plan['cuts'][1:]:
  if c['sceneStartFrame']<=frame<c['sceneStartFrame']+120:
   label(d,(1320,145),'다른 주행 구간',size=28)
 return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
def glyph(d,x,y,title,landing):
 # A labelled component triangle floats beside the action, never on terrain.
 x=max(120,x);y=max(340,min(620,y));a=(x,y+100);b=(x+200,y+100);c=(x+200,y-70)
 arrow(d,a,b,COLORS['horizontal']);arrow(d,b,c,COLORS['height']);line(d,a,c,COLORS['radius'])
 label(d,(x-10,y+140),'수평 방향',COLORS['horizontal'],27)
 label(d,(x+220,y-5),title,COLORS['height'],27)
 label(d,(x-10,y-125),'성분 구분 · 설명용',size=26)
def main():
 LOCAL.mkdir(parents=True,exist_ok=True)
 selected=json.loads((OUT/'selected-scene02-execution-v1.json').read_text(encoding='utf-8'))
 assert selected['exitCode']==0
 # Manually placed whole-rider centers in 640x360 image pixels, inspected on
 # source boards. Interpolation is a proposal and still needs moving review.
 coords=[(313,184),(310,145),(321,220),(322,193),(340,186),(320,165),
 (319,222),(318,183),(314,189),(314,184),(319,185),(319,180),
 (323,198),(320,205),(328,219),(319,224),(319,211),(331,204),
 (339,195),(327,184),(310,186),(322,197),(309,206),(305,205),
 (311,192),(323,199),(338,214),(337,191),(357,203),(308,194),
 (313,185),(324,190),(310,194),(300,204),(320,205),(320,200),
 (320,202),(308,196),(307,191),(320,158),(319,207),(319,252),
 (325,183),(320,205),(307,188),(320,188),(319,220),(320,216),
 (305,187),(292,183),(287,191),(333,204),(322,212),(325,224),
 (318,202),(314,194),(306,209),(325,204),(319,202),(325,199),
 (320,194),(327,196),(348,204)]
 assert len(coords)==len(selected['samples'])==63
 plan={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),
 'source':selected['sourceCandidate'],'sourceSha256':selected['sourceCandidateSha256'],
 'frames':3403,'fps':60,'timebase':'1/90000','cuts':selected['cuts'],
 'observationKeyframes640':[[r['frame'],*xy] for r,xy in zip(selected['samples'],coords)],
 'target':'Whole visible rider bracket; manually keyed image-space observation, not a measured world point',
 'semanticColors':COLORS,'preservedExplanationColors':'red horizontal; green height; blue radius/relative vector',
 'stagesSeconds':[0,7.98,15,22.72,29.08,34.78,42.5,3403/60],
 'geometryInterpretation':'Component triangle and camera icon are labelled explanatory diagrams beside the action. Image motion is not a game-world height measurement.',
 'approvedPcmChanged':False,'automaticTrackVersionsHeld':['scene02-visible-track-v1.json','scene02-visible-track-v2.json'],
 'movingTrackApproved':False,'finalCaptionPixelsApproved':False,'allVideoApproved':False}
 p=OUT/'scene02-editorial-annotations-v1.json';assert not p.exists()
 p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 records=[]
 for r in selected['samples']:
  assert sha(ROOT/r['path'])==r['sha256']
  with Image.open(ROOT/r['path']) as im:res=annotate(im,r['frame'],plan)
  target=LOCAL/f"annotation-f{r['frame']:04d}.png";res.save(target)
  records.append({'frame':r['frame'],'path':rel(target),'sha256':sha(target)})
 boards=[]
 for n in range(0,len(records),6):
  board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
  for j,r in enumerate(records[n:n+6]):
   x=j%3*640;y=j//3*390
   with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
   d.text((x+8,y+7),f"editorial overlay f{r['frame']}",fill='white')
  b=LOCAL/f'board-{n//6+1:02d}.png';board.save(b);boards.append({'path':rel(b),'sha256':sha(b)})
 proof=OUT/'scene02-editorial-annotation-preparation-v1.json';assert not proof.exists()
 proof.write_text(json.dumps({'plan':rel(p),'planSha256':sha(p),'samples':records,'boards':boards,'preparedOnly':True,'currentMovingPixelReviewApproved':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'preparedSamples':len(records),'boards':len(boards),'movingApproval':False}),flush=True)
if __name__=='__main__':main()
