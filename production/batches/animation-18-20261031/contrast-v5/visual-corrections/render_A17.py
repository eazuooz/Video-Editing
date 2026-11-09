"""A17 same-frame Helix editorial focus. Native clocks/audio offsets stay unchanged."""
from pathlib import Path
import json,subprocess,math,argparse,bisect
from PIL import Image,ImageDraw,ImageFont
from render_A01 import H,R,sha,rel,read,text,encode,BG,WHITE,YELLOW,TEAL
O=H/'local/visual-corrections/A17';O.mkdir(parents=True,exist_ok=True)
SRC=H/'footage/local/arms-helix.mp4'
# Source-image body centres read from the inspected 0.5-second frames.
# Coordinates are in the 640-wide QA contact image, converted to source pixels.
CENTRES=[(9,320,99,90),(9.5,315,97,80),(10,307,105,85),(10.5,300,101,90),(11,314,90,90),(11.5,300,97,70),(12,298,96,50),(12.5,316,112,65),(13,320,120,35),(13.5,321,118,40),(14,318,120,65),(14.5,285,110,70),(15,252,110,70),(15.5,181,56,100),(16,309,122,90),(16.5,304,113,75),(17,326,134,35),(17.5,323,126,40),(18,322,124,80),(18.5,313,115,80),(19,327,119,85),(19.5,312,120,75),(20,335,122,80),(20.5,427,149,50),(21,308,106,75),(21.5,321,107,75),(22,287,127,35),(22.5,351,134,100),(23,324,129,100),(23.5,307,127,100),(24,309,121,100),(24.5,309,123,100),(25,318,128,90),(25.5,315,119,95),(26,311,122,90),(26.5,308,117,90),(27,235,92,100),(27.5,229,142,60),(27.55,274,122,65),(27.6,312,106,85),(27.65,343,108,95),(27.7,348,108,100),(27.733333333333334,346,112,95),(27.75,344,118,100)]
# Conservative visible windows: effect/foreground-obscured intervals retain only
# the complete unmarked native frame, never an old held target or magnifier.
VISIBLE=[(9,10.15),(13.05,14.1),(17.3,18.8),(20.85,21.55),(22.2,23.55),(24.35,25.85),(26.95,27.75)]
def target(t):
 i=max(0,min(len(CENTRES)-2,bisect.bisect_right([q[0] for q in CENTRES],t)-1));a,b=CENTRES[i:i+2];u=max(0,min(1,(t-a[0])/(b[0]-a[0])))
 return tuple((a[k]+(b[k]-a[k])*u)*3 for k in (1,2,3))
def compose(source,t,analysis=False):
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 text(d,(55,34),'ARMS / Helix',56,YELLOW);text(d,(1450,45),'정지화면 · 자세 분석' if analysis else '실제 게임 · 1×',32,WHITE)
 # Complete source frame, unchanged aspect. UI and source content are not cropped.
 im.paste(source.resize((1250,703),Image.Resampling.LANCZOS),(40,150));d=ImageDraw.Draw(im)
 visible=any(a<=t<=b for a,b in VISIBLE)
 if visible:
  cx,cy,height=target(t);side=400;left=max(0,min(1920-side,cx-side/2));top=max(0,min(1080-side,cy-side/2))
  crop=(int(left),int(top),int(left+side),int(top+side));view=source.crop(crop).resize((570,570),Image.Resampling.LANCZOS)
  im.paste(view,(1310,230));d=ImageDraw.Draw(im)
  d.rectangle((1306,226,1884,804),outline='#000000',width=10);d.rectangle((1309,229,1881,801),outline=TEAL,width=4)
  text(d,(1310,142),'헬릭스 · 초록색 몸',40,TEAL);text(d,(1310,194),'확대 · 같은 시점',28,WHITE)
  sx=1250/1920;sy=703/1080;bw=65*3;bh=max(130,height+20)
  box=(int(40+(cx-bw/2)*sx),int(150+(cy-bh/2)*sy),int(40+(cx+bw/2)*sx),int(150+(cy+bh/2)*sy))
  d.rectangle(box,outline='#000000',width=12);d.rectangle(box,outline=TEAL,width=5)
  # Label remains outside the body region and connects to its box.
  lx=max(50,min(1090,box[0]-125));ly=max(154,box[1]-60)
  d.rounded_rectangle((lx-6,ly-3,lx+116,ly+43),radius=7,fill='#000000');text(d,(lx,ly),'헬릭스',34,TEAL)
  p1=(lx+116,ly+25);p2=(box[0],max(box[1],min(box[3],ly+30)))
  d.line((p1,p2),fill='#000000',width=12);d.line((p1,p2),fill=TEAL,width=5)
 return im

def source_frames(start,frames):
 p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-threads','1','-ss',str(start),'-i',str(SRC),'-an','-frames:v',str(frames),'-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 try:
  for f in range(frames):
   data=p.stdout.read(1920*1080*3);assert len(data)==1920*1080*3,(f,len(data));yield Image.frombytes('RGB',(1920,1080),data)
 finally:
  p.stdout.close();assert p.wait()==0

def make_previews():
 for t,*_ in CENTRES[:-1]:
  file=O/f'track-{t:05.2f}.png'
  if file.exists():compose(Image.open(file).convert('RGB'),t).save(O/f'preview-{t:05.2f}.png')
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
 for offset in range(0,38,8):
  batch=CENTRES[offset:offset+8];sheet=Image.new('RGB',(1280,393*math.ceil(len(batch)/2)),BG);d=ImageDraw.Draw(sheet)
  for j,(t,*_)in enumerate(batch):
   p=O/f'preview-{t:05.2f}.png'
   if not p.exists():continue
   x,y=j%2*640,j//2*393
   with Image.open(p)as im:sheet.paste(im.resize((640,360)),(x,y))
   d.text((x+5,y+362),f'{t:.2f}s',font=font,fill='white')
  sheet.save(O/f'preview-contact-{offset//8+1}.jpg',quality=94)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');args=ap.parse_args()
 if not args.render:make_previews();return
 control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert control['renderAuthorized']and'A17'in control['episodes']
 old=next(e for e in read(H/'game-plates-caption-safe.json')['episodes']if e['id']=='A17');rows=[]
 for lo,hi,start in [(14480,15110,9),(17747,18242,19.5),(18242,18248,27.733333333333334)]:
  previous=next(q for q in old['pictureEdits']if q['startFrame']==lo and q['endFrame']==hi);n=hi-lo;analysis=n==6;file=O/f'A17-correction-{lo:06d}-{hi:06d}-helix-focus.mp4'
  if analysis:
   frame=next(source_frames(start,1));image=compose(frame,start,True);encode(file,n,lambda f:image)
  else:
   iterator=source_frames(start,n);encode(file,n,lambda f:compose(next(iterator),start+f/60))
  row={k:v for k,v in previous.items()if k not in ['receipt','id','picture','pictureSha256']};row.update(id=file.stem,picture=rel(file),pictureSha256=sha(file),sourceStartFrame=0,newAudio=False,newTts=False,expectedUnderlyingExplanationIds=[],reason='Focus the actual background Helix body, distinguish it from foreground Dr. Coyle; preserve native frames, speed and exact source audio offsets.',visualEvidence={'source':rel(SRC),'sourceSha256':sha(SRC),'manualObservationSourceTimes':[q[0]for q in CENTRES],'manualBodyCentreAndApproxHeightAt640Width':CENTRES,'magnifierVisibleSourceWindows':VISIBLE,'fullNativeSourceFrameAlwaysVisible':True,'occlusionRule':'Hide both target annotation and magnifier during marked effect/foreground occlusion; never hold a previous target image.','coordinatesMeaning':'Editorial manually observed body region only, not game joints or detector measurements.','newGameMechanicOrInternalMeasurementClaim':False},captionSafeBottomY=892)
  rows.append(row)
 result={'schemaVersion':1,'episode':'A17','clock':'relations-v4','readyForAssembly':False,'pictureEdits':rows,'sourceCode':rel(Path(__file__)),'sourceCodeSha256':sha(__file__),'humanFullWatch':False,'patchQa':'Pending actual encoded current-caption 1080p/375px sample and motion-keyframe review.'}
 (H/'visual-corrections/A17.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print('A17 three patches encoded; ready remains false pending QA',flush=True)
if __name__=='__main__':main()
