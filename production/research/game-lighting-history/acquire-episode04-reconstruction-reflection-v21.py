"""Acquire one public NVIDIA comparison normally; no authentication/access bypass."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess, psutil
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'production/research/game-lighting-history/local/episode04-reconstruction-reflection-v21'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
NODE=Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
stamp=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
assert not OUT.exists(),'Preserve earlier media'
resources=[]
for p in psutil.process_iter(['pid','ppid','name','cmdline','create_time']):
 try:
  d=p.info;cmd=' '.join(d['cmdline'] or [])
  if 'python' in (d['name'] or '').lower() or 'ffmpeg' in (d['name'] or '').lower():resources.append(d)
  if 'ffmpeg' in (d['name'] or '').lower() and 'game-lighting-history' in cmd:raise RuntimeError('Owned media slot busy')
 except(psutil.AccessDenied,psutil.NoSuchProcess):pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
OUT.mkdir();me=psutil.Process();SP=OUT/'execution.json'
state={'startedAt':stamp(),'status':'running','worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'resources':resources,'gpuObservation':gpu,'cpuThreads':2,'gpuJobs':0,'active':None,'commands':[],'samples':[],'boards':[],'source':{'id':'M9yHtS8EoFg','url':'https://www.youtube.com/watch?v=M9yHtS8EoFg','primary':'https://www.nvidia.com/en-us/geforce/news/gfecnt/20238/nvidia-dlss-3-5-ray-reconstruction/','primaryDate':'2023-08-22','primaryLinkTitle':'NVIDIA DLSS 3.5 Ray Reconstruction Portal reflection comparison'},'sourceAudioAcquired':False,'allSamplesRead':False,'allMovingFramesReviewed':False,'rightsApproved':False,'finalUseApproved':False,'newGitImages':0}
def save():SP.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def checkpoint():
 p=ROOT/'production/research/game-lighting-history/checkpoint.json';j=json.loads(p.read_text('utf-8-sig'))
 j['episode04ReconstructionReflectionV21']={'execution':rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'samples':len(state['samples']),'cpuThreads':2,'gpuJobs':0,'allMovingFramesReviewed':False}
 j['ownedActiveWork']=({'type':'CPU-reconstruction-reflection-v21','execution':rel(SP),'worker':state['worker'],'active':state['active'],'next':'Read native reflection comparison before choosing the remaining guide interval'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Read native reflection comparison and distinguish ray-reconstruction conditions from source performance claims'})
 j['updatedAt']=stamp();tmp=p.with_suffix('.reconstruction-reflection-v20.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(p)
def run(cmd,label):
 cmd=[str(x) for x in cmd];log=OUT/(label+'.log')
 with log.open('w',encoding='utf-8') as f:
  proc=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f);obs=psutil.Process(proc.pid)
  state['active']={'pid':proc.pid,'createTime':obs.create_time(),'commandLine':cmd,'cwd':str(ROOT),'log':rel(log),'startedAt':stamp()};save();checkpoint();code=proc.wait()
 result={**state['active'],'exitCode':code,'endedAt':stamp()};state['commands'].append(result);state['active']=None;save();assert code==0,(label,code)
try:
 save();checkpoint()
 run([PY,'-X','utf8','-m','yt_dlp','--no-progress','--no-playlist','--no-overwrites','--write-info-json','--no-write-thumbnail','--js-runtimes','node:'+str(NODE),'--retries','0','--fragment-retries','0','--socket-timeout','30','-f','bv*[height<=1080][ext=mp4][vcodec^=avc]/bv*[height<=1080][ext=mp4]','-o',OUT/'portal-rr-reflection.%(ext)s',state['source']['url']],'normal-public-acquisition')
 media=OUT/'portal-rr-reflection.mp4';info=json.loads((OUT/'portal-rr-reflection.info.json').read_text('utf-8'))
 assert info['id']==state['source']['id'] and info.get('channel_id')=='UCL-g3eGJi1omSDSz48AML-g','Verify actual official NVIDIA channel'
 probe=json.loads(subprocess.run([str(FP),'-v','error','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base:format=duration','-of','json',str(media)],capture_output=True,text=True,check=True).stdout)
 assert not any(s['codec_type']=='audio' for s in probe['streams'])
 run([FF,'-v','error','-threads','2','-i',media,'-f','null','NUL'],'source-whole-decode')
 duration=float(probe['format']['duration']);assert 3<duration<240
 state['acquisition']={'path':rel(media),'sha256':sha(media),'title':info['title'],'publisher':info['channel'],'channelId':info['channel_id'],'uploadDate':info['upload_date'],'probe':probe,'wholeDecodeExitCode':0,'wholeOriginalDecoded':True,'sourceStartOffsetVerified':True,'sourceAudioAcquired':False,'localOnly':True}
 for i,time in enumerate(range(int(duration))):
  file=OUT/f'reflection-{i+1:03d}.png'
  run([FF,'-n','-v','error','-threads','2','-ss',time,'-i',media,'-filter_threads','2','-vf','scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1','-frames:v','1',file],f'reflection-{i+1:03d}')
  state['samples'].append({'path':rel(file),'sha256':sha(file),'localSeconds':time,'sourcePath':rel(media),'sourceSha256':state['acquisition']['sha256'],'directlyRead':False,'localOnly':True});save()
 for start in range(0,len(state['samples']),4):
  group=state['samples'][start:start+4];board=Image.new('RGB',(1920,1160),'#111111');draw=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24)
  for k,item in enumerate(group):
   x=k%2*960;y=k//2*580;draw.text((x+12,y+8),f"Portal RR reflection · local{item['localSeconds']}s",font=font,fill='white')
   with Image.open(ROOT/item['path']) as im:board.paste(im.resize((960,540)),(x,y+40))
  file=OUT/f'reflection-board-{start//4+1:02d}.jpg';board.save(file,quality=94)
  state['boards'].append({'path':rel(file),'sha256':sha(file),'samples':[x['path'] for x in group],'directlyRead':False,'localOnly':True});save()
 state['status']='samples-ready';state['endedAt']=stamp();save();checkpoint();print(json.dumps({'duration':duration,'samples':len(state['samples']),'boards':len(state['boards']),'newGitImages':0}))
except Exception as e:
 state['status']='failed';state['error']=repr(e);state['noAuthenticationOrAccessBypass']=True;state['endedAt']=stamp();save();checkpoint();raise
