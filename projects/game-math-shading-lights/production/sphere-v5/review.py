"""Full encoded-file validation, optical construction from the delivered pixels, and playable review chapters."""
import html,io,re,subprocess
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageDraw
from delivery import DEST,OLD,P,Q,SL,W,B,probe,read,write,sha
def now():return datetime.now(timezone.utc).isoformat()
def grab(path,t,w):
 args=['ffmpeg','-v','error','-ss',f'{t:.6f}','-threads','2','-i',str(path),'-frames:v','1','-vf',f'scale={w}:-1','-c:v','png','-threads','1','-f','image2pipe','-']
 return Image.open(io.BytesIO(subprocess.check_output(args))).convert('RGB')
def audio(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
def t(s,delta):
 c=next(c for c in Q['cuts'] if c['scene']==f'{s:03}' and c['kind']=='explanation')
 return 2+c['globalStartFrame']/60+delta-c['sourceIn']
CHAPTERS=[(1,0,'PBR 재질 구'),(3,7.15,'해 → 구 → 카메라'),(8,0,'N · V · L: 세 방향'),(9,0,'반사 벡터 R 만들기'),(10,1,'반사 방향을 숫자로 확인하기'),(11,0,'카메라와 반짝임'),(16,3.5,'하프웨이 벡터 H'),(51,11.6,'방향성 광원: 위치와 회전')]
def reviewpage():
 old=(OLD/'index.html').read_text(encoding='utf-8');cap=SL+'.captioned.mp4';start=old.index('<h2>');end=old.index('</ul>',start)+5;rows=[]
 for s,sec,label in CHAPTERS:
  at=t(s,sec);stamp=f'{int(at)//60:02}:{int(at)%60:02}';rows.append(f'<li><a href="{cap}#t={at:.3f}" data-t="{at:.3f}">{stamp} · {html.escape(label)}</a></li>')
 page=old[:start]+'<h2>바뀐 장면부터 보기</h2><ul>'+''.join(rows)+'</ul>'+old[start:]
 page=re.sub(r'<p>32분 10초.*?</p>','<p>32분 10초 · 1080p60 · 재질 구와 빛의 경로 수정본 (v5)</p>',page,count=1)
 page=re.sub(r'<p id="newest-revision">.*?</p>','',page)
 page=page.replace('render-v4/index.html','render-v5/index.html').replace("document.querySelectorAll('[data-t]')","if(/^#t=[0-9.]+$/.test(location.hash)){const jump=()=>{v.currentTime=Number(location.hash.slice(3))};v.readyState?jump():v.addEventListener('loadedmetadata',jump,{once:true})};\n"+"document.querySelectorAll('[data-t]')")
 (DEST/'index.html').write_text(page,encoding='utf-8')
 if 'id="newest-revision"' not in old:(OLD/'index.html').write_text(old.replace('<h1>','<p id="newest-revision"><a href="../'+DEST.name+'/index.html">수정본 v5 · 재질 구와 빛의 경로 보기 →</a></p><h1>',1),encoding='utf-8')
def opticalqa(cap):
 def ray(i,sec,box,ch):
  a=np.asarray(grab(cap,t(i,sec),960),dtype=float);x0,y0,x1,y1=box;r,g,b=a[y0:y1,x0:x1].transpose(2,0,1)
  m=(g>155)&(g>r*1.13)&(g>b*1.11) if ch=='normal' else (r>165)&(g>125)&(r>b*1.5) if ch=='incident' else (r>150)&(r>g*1.25)&(r>b*1.28)
  return int(m.sum())
 evidence={}
 for name,s,a,b,c,box,ch in [('normal',8,.04,.68,1.4,(334,123,352,246),'normal'),('sunToSurface',3,7.6,8.3,9,(336,135,448,247),'incident'),('reflection',3,10.9,11.9,12.9,(236,117,344,243),'reflect')]:
  counts=[ray(s,u,box,ch) for u in [a,b,c]];assert counts[1]>counts[0]+10 and counts[2]>counts[1]+10,(name,counts);evidence[name]={'seconds':[t(s,u) for u in [a,b,c]],'pixels':counts}
 cases=[(1,20),(3,7.9),(3,12),(3,14),(8,.7),(8,9),(8,16.4),(9,11),(9,14.8),(10,23.7),(11,6.9),(16,15.5),(15,14),(37,12),(51,16.7),(78,15)]
 sheet=Image.new('RGB',(1500,952),'#121715');dr=ImageDraw.Draw(sheet)
 for n,(s,sec) in enumerate(cases):
  tm=t(s,sec);xx=n%4*375;yy=n//4*238;sheet.paste(grab(cap,tm,375),(xx,yy));dr.text((xx+8,yy+211),f'{s:03} / {tm:.2f}s',fill='white')
 sheet.save(W/'final-mobile.jpg',quality=94);return evidence
def verify():
 expected=Q['bodyFrames']+720;golden=audio(OLD/(SL+'.clean.mp4'));result={}
 for k in ['clean','captioned']:
  f=DEST/(SL+'.'+k+'.mp4');st,astream=probe(f)['streams'];assert (st['width'],st['height'],st['r_frame_rate'],int(st['nb_frames']))==(1920,1080,'60/1',expected)
  assert abs(float(astream['duration'])-float(st['duration']))<.05 and audio(f)==golden
  packet=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts','-of','csv=p=0',str(f)]).decode().splitlines()
  pts=sorted(int(x.strip().split(',')[0]) for x in packet if x.strip());assert len(pts)==expected and pts[0]==0 and all(abs(a-b-1500)<=1 for b,a in zip(pts,pts[1:])),'Nonuniform frame timing'
  subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-threads','3','-i',str(f),'-map','0:v','-map','0:a','-f','null','NUL'],check=True)
  result[k]=dict(path=str(f),sha256=sha(f),duration=st['duration'],frames=expected,fullDecodeExitCode=0,originalAacHash=golden)
 for lang in ['ko','en']:
  f=DEST/(SL+'.'+lang+'.srt');rx=r'^\d{2}:\d{2}:\d{2},\d{3} --> .+$'
  times=re.findall(rx,f.read_text(encoding='utf-8-sig'),re.M);assert times==re.findall(rx,(OLD/f.name).read_text(encoding='utf-8-sig'),re.M)
  result[lang]=dict(path=str(f),sha256=sha(f),cues=len(times))
 checks=opticalqa(DEST/(SL+'.captioned.mp4'))
 tech=dict(createdAt=now(),expectedFrames=expected,files=result,rayConstructionFromEncodedPixels=checks,originalAudioUnchanged=True)
 write(W/'final-qa/report.json',tech);reviewpage()
 bakes={j.stem:read(__import__('pathlib').Path(read(j)['output'])/'actual-bake.json') for j in (W/'bake-jobs').glob('???.json')}
 assert (W/'bake-override.json').is_file() and len(bakes)==4
 write(B/'review-evidence.json',dict(revision='v5',checkedAt=now(),scope='M21 only',engine='59 Unity URP local-lighting/geometry scenes and 4 newly CPU-baked sphere/UV/probe room scenes · isolated D3D11 WARP, reproducible editable scenes',optics='14 on-surface material/geometry scenes: GGX PBR studio swatch, Phong/Blinn, distinct shading camera and observer; our implementation, not Unreal Engine capture.',primaryReference='https://dev.epicgames.com/documentation/en-us/unreal-engine/physically-based-materials-in-unreal-engine',retained='7 independent gameplay cuts and original audio/timeline; closing grid rebuilt.',bakes=bakes,geometry='L=P toward sun; incident=-L; R=2(N·L)N−L; V=P toward camera lens; H=normalize(L+V) when nonzero.',technical=tech,captionChanges=len(read(W/'caption-delta.json')),userReview=False,continuousListening=False))
 write(W/'content-review.json',dict(status='four-files-available-integrated-review-pending',localFinalReviewReady=False,masterSha256=result['captioned']['sha256'],annotationRevision='sphere-v5',humanReview=False))
if __name__=='__main__':verify()
