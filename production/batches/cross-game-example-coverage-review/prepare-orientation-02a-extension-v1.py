"""Prepare one unique normal-speed observation continuation; no rendering here."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,py_compile
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(O/'additional-bank-native-v1/manifest.json')
samples=[s for s in m['samples'] if s['game']=='superflight' and 3960<=s['nativeFrame']<=4470]
# Directly read board001..004 640x360 tiles. A torso feature, never an engine origin.
xy=[(321,219),(319,210),(315,197),(315,196),(320,193),(326,187),None,None,None,None,
    (356,176),(381,166),(359,192),(348,205),(302,198),(291,189),(296,183),(309,191)]
assert len(samples)==len(xy)==18
anchors=[]
for s,p in zip(samples,xy):
 assert sha(ROOT/s['path'])==s['sha256']
 anchors.append(dict(sourceFrame=s['nativeFrame'],sourcePts=s['pts'],inspectedImage=s['path'],inspectedImageSha256=s['sha256'],visible=p is not None,screenPoint=None if p is None else [v*3 for v in p]))
source=next(x for x in m['sources'] if x['game']=='superflight');assert sha(ROOT/source['sourcePath'])==source['sourceSha256']
v=read(O/'02a-observation-track-plan-v1.json')['voice'];assert sha(ROOT/v['path'])==v['sha256']
p=O/'02aext-observation-track-plan-v1.json';assert not p.exists()
p.write_text(json.dumps(dict(preparedAt=datetime.now(timezone.utc).isoformat(),sceneId='02aext',source=source['sourcePath'],sourceSha256=source['sourceSha256'],nativeIn=3960,nativeOutExclusive=4446,nativeFrames=486,sceneFrames=486,roundingHoldFrames=0,
 coordinateBasis='Manually read 640x360 tile points multiplied by3 to native1920x1080. Audit PNGs1280x720.',anchors=anchors,hideSeconds=[[68.75,71]],reveals=dict(observationPoint=0,screenDisplacement=.5),voice=v,
 continuationOf='02a',narrationAlreadyIntroduced='02a invites comparing screen position and body tilt and identifies the guide as a screen observation. This related unique action continues after its voice; no new speech is claimed.',
 action='Approach the tower, pass between foreground structures, emerge and visibly change body attitude while continuing to fly.',
 classification='actual',normalSpeed=True,uniqueNativeFrames=486,sourceWindowSeconds=[66,74.1],baselineOverlapFrames=0,otherNewSourceOverlapFrames=0,screenOnly=True,physicalCentroid=False,engineWorldAxes=False,rigidRollMeasurement=False,
 actualRenderApproved=False,allBetweenFramesApproved=False,finalCueApproved=False,finalRatioApproved=False,newImageGit=0),ensure_ascii=False,indent=2)+'\n','utf-8')
r=(B/'render-orientation-02a-tracked-v1.py').read_text('utf-8')
start=r.index('def drawing(');end=r.index('def main():',start)
draw='''def drawing(im,frame,p):
 layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
 label(d,(64,28),'Superflight · NCR Gameplay · 화면 관찰','#ffffff',22)
 label(d,(64,90),'화면 위치와 몸의 기울기를 비교하세요',GOLD,30)
 label(d,(64,153),'청록: 몸통의 화면 관찰점 p',TEAL,26)
 label(d,(64,210),'빨강: 0.5초 동안의 화면 위치 변화',RED,26)
 label(d,(64,268),'카메라 움직임도 포함 · 게임 내부 좌표값 아님','#ffffff',26)
 point=point_at(frame,p);previous=point_at(max(0,frame-30),p)
 if point is not None:
  x,y=point;d.ellipse((x-15,y-15,x+15,y+15),outline='#10191c',width=6)
  d.ellipse((x-12,y-12,x+12,y+12),outline=TEAL,width=4);d.ellipse((x-3,y-3,x+3,y+3),fill=TEAL)
 if frame>=30 and point is not None and previous is not None:
  if all(point_at(i,p) is not None for i in range(frame-30,frame+1)):arrow(d,previous,point)
 assert layer.getbbox()[3]<900
 return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB'),point
'''
r=r[:start]+draw+r[end:]
r=r.replace('02a','02aext').replace("'79.5'","'66.0'").replace('4770','3960').replace('5802','4446').replace('5801','4445').replace('1033','486').replace('1032','486')
r=r.replace('roundingHold=frame==486','roundingHold=False')
render=B/'render-orientation-02aext-tracked-v1.py';assert not render.exists();render.write_text(r,'utf-8');py_compile.compile(str(render),doraise=True)
q=(B/'extract-orientation-02a-tracked-pixels-v1.py').read_text('utf-8').replace('02a','02aext')
q=q.replace('1033','486').replace('1032','485').replace('79.5','66.0').replace('4770','3960').replace('5801','4445').replace('roundingHold=f==485','roundingHold=False')
extract=B/'extract-orientation-02aext-tracked-pixels-v1.py';assert not extract.exists();extract.write_text(q,'utf-8');py_compile.compile(str(extract),doraise=True)
r=(B/'record-orientation-10b-worker-exit-v1.py').read_text('utf-8').replace('10b','02aext')
r=r.replace("for x in s['decoders']:exact_dead(x['pid'],x['createTime'])","exact_dead(s['decodePid'],s['decodeCreateTime'])")
r=r.replace("reg=read(p.with_name(p.name.replace('.json','.session.json')));assert reg['actualSession']==a.session","\n if a.session is not None:\n  reg=read(p.with_name(p.name.replace('.json','.session.json')));assert reg['actualSession']==a.session")
r=r.replace("p=O/f'02aext-tracked-{a.mode}-execution-v1.json'","p=O/f\"02aext-tracked-{'render' if a.mode=='render' else 'pixel'}-execution-v1.json\"")
rec=B/'record-orientation-02aext-worker-exit-v1.py';assert not rec.exists();rec.write_text(r,'utf-8');py_compile.compile(str(rec),doraise=True)
print(json.dumps(dict(preparedOnly=True,frames=486,anchors=len(anchors),visible=sum(x['visible'] for x in anchors),render=render.name,extract=extract.name)))
