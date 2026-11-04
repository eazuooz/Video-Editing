"""Track inspected M24–M33 source targets on CPU; never auto-approve tracks."""
from pathlib import Path
import argparse,json,math,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
sys.path.insert(0,str(R/'projects/game-math-euler-axis-angle/production/local/revision-v3/deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
boards=B/'local/annotation-targets-v1';manifest=read(boards/'manifest.json');byid={x['id']:x for x in manifest['records']}
# Coordinates were selected from actual nine-frame source boards. Tracking
# results remain candidates until the temporal sheets have been inspected.
# (board id, seed sample, seconds, x/y/width/height, visible teaching target)
SEEDS=[
 ('M24-000',0,3.6,[1000,310,110,145],'이동하는 위치'),
 ('M24-015',1,4.5,[1620,850,275,215],'매 순간 바뀌는 속력 · mph'),
 ('M24-032',3,4.0,[855,480,270,510],'뗏목에 대한 위치'),
 ('M25-000',5,4.8,[650,500,625,540],'도약 → 하강 → 착지'),
 ('M25-018',1,3.5,[900,630,120,150],'올라갔다 내려오는 점프'),
 ('M25-021',4,3.4,[500,430,360,460],'이륙과 착지의 높이'),
 ('M26-000',3,4.7,[650,520,650,470],'커브에서 바뀌는 진행 방향'),
 ('M26-011',5,1.8,[805,70,385,530],'돛의 자세를 바꾸는 회전'),
 ('M26-017',4,3.0,[790,40,230,235],'회전 중심과 날개'),
 ('M27-000',2,3.5,[890,635,170,245],'바퀴와 바위의 접촉'),
 ('M27-012',1,4.5,[830,420,255,270],'발사와 차체의 움직임'),
 ('M27-018',2,2.2,[865,460,150,270],'발밑의 지지가 사라진 뒤'),
 ('M28-000',1,4.0,[920,630,150,190],'바퀴와 차체의 상대 움직임'),
 ('M28-001',4,2.8,[660,350,435,430],'당겼다가 놓기'),
 ('M28-016',3,3.4,[485,260,300,590],'선수를 따라가는 화면'),
 ('M29-000',4,2.6,[870,540,600,360],'충돌 전후의 움직임'),
 ('M29-014',0,2.8,[615,120,650,270],'포탄이 닿는 성벽'),
 ('M29-018',2,1.8,[660,300,580,660],'벽을 향해 놓아 보내기'),
 ('M30-003',2,3.5,[900,420,265,460],'붙은 부분이 함께 이동'),
 ('M30-027',1,4.0,[940,605,150,230],'연결된 바퀴의 움직임'),
 ('M31-000',1,4.0,[520,490,830,500],'경로를 따라 바뀌는 방향'),
 ('M31-005',5,3.0,[705,515,425,110],'경로는 고정 · 위치는 이동'),
 ('M31-012',2,2.0,[570,65,470,650],'출발 방향을 정하는 스타'),
 ('M31-027',4,2.3,[810,410,350,200],'끝점을 옮기면 경로가 바뀝니다'),
 ('M33-008',3,5.4,[840,490,405,330],'각진 연결에서 둥근 연결로'),
]
ap=argparse.ArgumentParser();ap.add_argument('--only',nargs='*');a=ap.parse_args()
out=B/'local/annotation-tracking-v1';out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
index=[]
for sid,sample,duration,bbox,label in SEEDS:
 if a.only and sid not in a.only:continue
 record=byid[sid];target=out/(sid+'.json')
 if target.exists():print(sid,'existing candidate preserved',flush=True);continue
 cap=cv2.VideoCapture(str(R/record['sourceFile']));assert cap.isOpened();fps=cap.get(cv2.CAP_PROP_FPS)
 begin=round(record['samples'][sample]['time']*fps);end=min(round((record['end']-.02)*fps),begin+round(duration*fps));cap.set(cv2.CAP_PROP_POS_FRAMES,begin)
 tracker=cv2.TrackerCSRT_create();keys=[];images=[]
 fixed=sid in ('M24-015','M29-014','M33-008')
 for f in range(begin,end):
  ok,frame=cap.read();assert ok;small=cv2.resize(frame,(960,540))
  if f==begin:tracker.init(small,tuple(round(v/2) for v in bbox));good=True;box=bbox
  elif fixed:good=True;box=bbox
  else:good,b=tracker.update(small);box=[2*float(v) for v in b]
  x,y,w,h=box;visible=bool(good and x>=5 and y>=32 and x+w<=1915 and y+h<=1070)
  keys.append(dict(time=f/fps,bbox=[round(v,2) for v in box],visible=visible))
  if (f-begin)%max(1,round(fps/4))==0:
   im=Image.fromarray(cv2.cvtColor(small,cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(im)
   if visible:d.ellipse([x/2,y/2,(x+w)/2,(y+h)/2],outline='#73C7C2',width=4)
   d.rectangle((0,0,960,32),fill='black');d.text((8,2),f'{sid} {f/fps:.3f}s '+('' if visible else 'HIDDEN'),font=font,fill='white');images.append(im.resize((480,270)))
 cap.release();sheets=[]
 for n in range(0,len(images),16):
  tiles=images[n:n+16];board=Image.new('RGB',(1920,math.ceil(len(tiles)/4)*270))
  for j,im in enumerate(tiles):board.paste(im,((j%4)*480,(j//4)*270))
  path=out/f'{sid}-{n//16+1:02}.jpg';board.save(path,quality=96);sheets.append(path.relative_to(R).as_posix())
 uses=list(record['uses'])
 if sid=='M27-012':uses+=byid['M30-000']['uses']
 if sid=='M33-008':uses+=byid['M32-000']['uses']
 data=dict(id=sid,sourceId=record['sourceId'],sourceFile=record['sourceFile'],sourceSha256=record['sourceSha256'],start=begin/fps,end=end/fps,bbox=bbox,label=label,shape='hollow-ellipse',coordinates='1920x1080 native decoded source',fps=fps,method='Fixed observed screen-region' if fixed else 'CPU CSRT at native source fps; editorial target guide, not game measurement',keyframes=keys,uses=uses,visualQa='pending',failedSamples=sum(not k['visible'] for k in keys),sheets=sheets,initialTargetEvidence=record['samples'][sample])
 save(target,data);index.append(dict(id=sid,file=target.relative_to(R).as_posix(),samples=len(images),failedSamples=data['failedSamples']));print(sid,len(keys),'frames, failed',data['failedSamples'],flush=True)
save(out/'latest-run.json',dict(status='candidate-tracks-awaiting-temporal-inspection',records=index,humanReview=False))
