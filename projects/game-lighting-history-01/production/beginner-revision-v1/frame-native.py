"""Frame only the additional reviewed native intervals; preview precedes encoding."""
import pathlib,json,subprocess,importlib.util,sys,os,datetime,hashlib
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/beginner-revision-v1/native-framed'
FF='C:/Users/eazuo/miniconda3/envs/renderformer/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def specification(a):
 k=a['id'];d=dict(crop=None,scaled=[1920,1080],magnifiers=[])
 if a['sourceId']=='epic-robo-performance-2017':d['crop']=[308,120,960,540]
 if a['sourceId']=='epic-lighting-techniques-2017':d['crop']=[0,0,1488,837]
 if k in ['x01','x09']:d.update(crop=[260,316,1080,486],scaled=[1920,864])
 if k=='x29':d['crop']=[250,80,1248,702]
 if k=='x37':d['magnifiers']=[dict(crop=[1435,490,365,140],rect=[1100,150,770,296])]
 if k=='xsh':d['magnifiers']=[dict(crop=[1435,452,365,140],rect=[1100,150,770,296])]
 if k=='x44':d.update(crop=[0,130,852,590],scaled=[1248,864])
 return d
def graph(a,idx,tail):
 d=specification(a);sid=a['sourceId'];spec=importlib.util.spec_from_file_location('baseline_framing',P/'production/final-framing-v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 parts=[];mags=d['magnifiers'];src='[0:v]'
 if mags:parts.append('[0:v]split='+str(len(mags)+1)+'[main]'+''.join(f'[m{i}]' for i in range(len(mags))));src='[main]'
 crop=d['crop'];c=f'crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]},' if crop else ''
 w,h=d['scaled'];parts.append(src+c+f'scale={w}:{h}:flags=lanczos,pad=1920:1080:{(1920-w)//2}:0:black,setsar=1,fps=60:start_time=0[base]');last='base'
 for i,mag in enumerate(mags):
  x,y,w,h=mag['crop'];dx,dy,dw,dh=mag['rect'];parts.append(f'[m{i}]crop={w}:{h}:{x}:{y},scale={dw}:{dh}:flags=lanczos,setsar=1,fps=60:start_time=0[mag{i}]');parts.append(f'[{last}][mag{i}]overlay={dx}:{dy}:shortest=1[over{i}]');last=f'over{i}'
 font=(P/'production/local/final-edit-v1/fonts/YamYamCaptionMedium.ttf').relative_to(R).as_posix()
 for i,t in enumerate([m.NAMES[sid],a['focusKo']]):
  f=O/f'{a["id"]}-{idx}-{i}.txt';f.write_text(t,encoding='utf8');size=32 if i==0 else 27
  parts.append(f"[{last}]drawtext=fontfile='{font}':textfile='{f.relative_to(R).as_posix()}':fontsize={size}:fontcolor={'0xFFE18A' if i==0 else 'white'}:x=48:y={40+i*48}:box=1:boxcolor=black@0.72:boxborderw=12[t{i}]");last=f't{i}'
 parts.append(f'[{last}]{tail}[out]');return ';'.join(parts)
def main():
 mode=sys.argv[1];assert mode in ['preview','render'];O.mkdir(parents=True,exist_ok=True)
 only=sys.argv[sys.argv.index('--only')+1].split(',') if '--only' in sys.argv else None
 suffix=sys.argv[sys.argv.index('--revision')+1] if '--revision' in sys.argv else ''
 control=rd(R/'shared/publishing/video-production-control.json');assert control['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['beginnerRevision']['privateUploadAuthorized']
 adds=rd(H/'native-additions.json');index=[]
 if mode=='render':assert rd(O/'preview-review.json')['allSelectedCropsApproved'] and rd(O/'preview-review.json')['additionsSha256']==sha(H/'native-additions.json')
 target=O/(('previews'+suffix) if mode=='preview' else 'segments');assert not (target/'execution.json').exists();target.mkdir(exist_ok=True)
 import psutil
 state=dict(status='running',mode=mode,pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),startedAt=now(),cpuThreads=2,gpuJobs=0,completed=[])
 def save():wr(target/'execution.json',state)
 save()
 try:
  for a in adds['rows']:
   if only and a['id'] not in only:continue
   for j,cut in enumerate(a['intervals']):
    if '--interval' in sys.argv and j!=int(sys.argv[sys.argv.index('--interval')+1]):continue
    total=cut['endFrame']-cut['startFrame'];positions=[0,total//2,total-1] if mode=='preview' else [0]
    for t in positions:
     key=f'{a["id"]}-{j}';name=key+f'-{t}.png' if mode=='preview' else key+'.mp4';out=target/name
     tail='scale=960:540' if mode=='preview' else f'trim=end_frame={total},setpts=N/(60*TB),format=yuv420p'
     cmd=[FF,'-v','warning','-nostdin','-n','-threads','2','-reinit_filter','0','-ss',f'{(cut["startFrame"]+t)/60:.9f}','-i',str(R/a['path']),'-filter_complex_threads','2','-filter_complex',graph(a,j,tail),'-map','[out]','-an','-frames:v',str(1 if mode=='preview' else total),'-threads','2']
     if mode=='render':cmd+=['-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart']
     cmd+=[str(out)];state['active']=dict(key=key,sourceFrame=cut['startFrame']+t,command=cmd);save()
     with (target/(name+'.log')).open('w') as f:child=subprocess.Popen(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);state['active']['pid']=child.pid;save();rc=child.wait()
     assert rc==0,(name,rc)
     row=dict(key=key,path=out.relative_to(R).as_posix(),sourceFrame=cut['startFrame']+t,frames=1 if mode=='preview' else total,sha256=sha(out),spec=specification(a));index.append(row);state['completed'].append(row);save()
  if mode=='preview':
   boards=[];font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',24)
   for off in range(0,len(index),6):
    b=Image.new('RGB',(1920,1710),'#111');draw=ImageDraw.Draw(b)
    for j,r in enumerate(index[off:off+6]):x=j%2*960;y=j//2*570;b.paste(Image.open(R/r['path']),(x,y+30));draw.text((x+6,y+1),r['key']+' source '+str(r['sourceFrame']/60),fill='white',font=font)
    p=target/f'board-{off//6:02}.jpg';b.save(p,quality=93);boards.append(p.relative_to(R).as_posix())
   state['boards']=boards
  state.update(status='complete-awaiting-direct-review',endedAt=now(),exitCode=0,active=None);save();print(json.dumps(dict(mode=mode,count=len(index))))
 except BaseException as e:state.update(status='failed',error=repr(e),endedAt=now());save();raise
if __name__=='__main__':main()
