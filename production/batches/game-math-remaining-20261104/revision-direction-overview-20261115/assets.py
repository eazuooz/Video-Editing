"""Extract genuine side / high-angle views; retain source and editing provenance."""
import sys,json,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];PREV=HERE.parent/'revision-game-subjects-20261115'
sys.path.insert(0,str(PREV));import subject_revision as old
sys.path.insert(0,str(ROOT/'production/batches/animation-18-20261031/research/A10/ocr-deps'))
import cv2,numpy as np
SOURCES={
 'kart-side':('production/batches/game-math-remaining-20261104/revision-teaching-sync-20261115/sources/CrbHin3jDqM.mp4',219.5),
 'forza-high':('projects/game-math-shading-lights/production/local/footage-review/forza5-xPnKcvo8A1E-000-070.mp4',63),
 'beamng-side':('projects/game-math-springs-damping/production/local/footage-review/beamng-suspension-cKarsLzGuFE.mp4',145),
 'mario-left':('projects/game-math-euler-axis-angle/production/local/revision-v3/sources/_wH_-1saHnw-hls.mp4',724)}
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def cut(name,box,height,flip=False,square=False):
 source,at=SOURCES[name];source=ROOT/source;frame=HERE/'local'/f'{name}.png'
 if not frame.exists():subprocess.run([str(old.FF),'-v','error','-nostdin','-n','-ss',str(at),'-i',str(source),'-frames:v','1',str(frame)],check=True)
 im=cv2.imread(str(HERE/'local'/f'{name}.png'));x,y,w,h=box;pad=8
 crop=im[y-pad:y+h+pad,x-pad:x+w+pad].copy();mask=np.zeros(crop.shape[:2],np.uint8)
 cv2.grabCut(crop,mask,(pad,pad,w,h),np.zeros((1,65)),np.zeros((1,65)),7,cv2.GC_INIT_WITH_RECT)
 alpha=np.where((mask==1)|(mask==3),255,0).astype(np.uint8)
 if name=='kart-side':
  # A green guardrail touches Luigi's cap. A colour-only segmentation would
  # remove his face and retain the rail; use the inspected real silhouette.
  poly=[(1376,280),(1415,286),(1442,343),(1425,356),(1434,414),(1460,444),(1459,498),(1504,512),(1501,566),(1596,572),(1662,627),(1677,735),(1644,798),(1573,830),(1514,819),(1474,771),(1304,800),(1229,785),(1144,757),(1108,689),(1115,640),(1162,598),(1202,561),(1243,543),(1282,469),(1292,431),(1309,424),(1295,395),(1296,367),(1320,345),(1343,310)]
  alpha[:]=0;cv2.fillPoly(alpha,[np.array([(px-x+pad,py-y+pad) for px,py in poly],np.int32)],255)
 count,labels,stats,_=cv2.connectedComponentsWithStats(alpha);alpha=np.where(labels==1+np.argmax(stats[1:,4]),alpha,0).astype(np.uint8)
 im=Image.fromarray(cv2.cvtColor(np.dstack([crop,alpha]),cv2.COLOR_BGRA2RGBA));im=im.crop(im.getbbox())
 if flip:im=ImageOps.mirror(im)
 im.thumbnail((height*4,height),Image.Resampling.LANCZOS)
 if square:
  side=max(im.size)+18;canvas=Image.new('RGBA',(side,side));canvas.paste(im,((side-im.width)//2,(side-im.height)//2));im=canvas
 out=HERE/'local/assets'/f'{name}.png';out.parent.mkdir(exist_ok=True);im.save(out)
 return dict(file=str(out),dimensions=list(im.size),sha256=sha(out),sourceFile=str(source),sourceSha256=sha(source),sourceFrame=str(frame),sourceFrameSha256=sha(frame),crop=box,mirrored=flip,squareCanvas=square,mask='Inspected silhouette polygon for Luigi; GrabCut largest connected component for other subjects')
def main():
 a=json.loads((PREV/'assets.json').read_text(encoding='utf8'));a={x['id']:x for x in a}
 configs=[('kart','kart-side',[1090,280,610,560],180,True,False,'CrbHin3jDqM',219.5,'Left-facing genuine side view; editorial horizontal mirror yields right-facing profile'),('forza','forza-high',[730,445,445,520],165,False,True,'xPnKcvo8A1E',63,'High camera view; visible hood at top and rear at bottom; planar tangent diagram, not measured car physics'),('beamng','beamng-side',[600,435,750,315],130,False,False,'cKarsLzGuFE',145,'Genuine right-facing side view; fixed facing during spring oscillation'),('mario-left','mario-left',[895,530,112,142],170,False,False,'_wH_-1saHnw',724,'Genuine left-facing side view; no rotating upright character to indicate falling')]
 for key,name,box,height,flip,square,sid,t,meaning in configs:
  a[key]=dict(id=key,**cut(name,box,height,flip,square),sourceId=sid,sourceIn=t,recordingUrl='https://www.youtube.com/watch?v='+sid,orientationMeaning=meaning,rightsEvidence='Existing CC BY / reusable recording evidence in preceding revision; no new downloaded recording.')
 save(HERE/'assets.json',list(a.values()))
 board=Image.new('RGB',(1500,500),'#111111');d=ImageDraw.Draw(board)
 for i,key in enumerate(['mario','mario-left','kart','forza','beamng']):
  im=Image.open(a[key]['file']);im.thumbnail((285,350));x=i*300;board.paste(im,(x+(285-im.width)//2,70),im);d.text((x+12,25),key,fill='white')
 board.save(HERE/'local/assets/contact.png')
if __name__=='__main__':main()
