"""Repair three missing literal-percent labels; preserve other nine cuts and AAC."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess, psutil, shutil
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
OUT=ROOT/'production/research/game-lighting-history/local/episode04-upscaling-label-v15'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'); FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
bp=P/'upscaling-chapter-review-build-v14.json'; old=read(bp)
pp=ROOT/old['plan']['path']; plan=read(pp); assert sha(pp)==old['plan']['sha256']
oldState=read(P/'upscaling-chapter-review-execution-v13.json')
assert len(oldState['results'])==12 and old['identicalAacPayload']
clean=ROOT/old['outputs'][0]['path']; assert sha(clean)==old['outputs'][0]['sha256']
for item in oldState['results']:assert sha(ROOT/item['path'])==item['sha256']
assert not OUT.exists() and shutil.disk_usage(ROOT).free>3*1024**3
resources=[]
for proc in psutil.process_iter(['pid','ppid','name','cmdline','create_time']):
 try:
  d=proc.info;cmd=' '.join(d['cmdline']or[])
  if any(n in (d['name']or'').lower() for n in ['python','ffmpeg']):resources.append(d)
  if 'ffmpeg' in (d['name']or'').lower() and 'game-lighting-history' in cmd:raise RuntimeError('Owned media slot busy')
 except(psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
OUT.mkdir();me=psutil.Process();sp=P/'upscaling-label-repair-execution-v15.json';assert not sp.exists()
state={'status':'running','startedAt':stamp(),'worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'resourceObservation':{'processes':resources,'gpu':gpu},'cpuThreads':2,'gpuJobs':0,'active':None,'commands':[],'results':[],'inputBuild':{'path':rel(bp),'sha256':sha(bp)},'repairReason':'Literal 50% caused drawtext expansion failure; three source-condition labels missing in directly viewed encoded samples. Use expansion=none.','newTts':0,'newGitImages':0,'allFinalPixelsReviewed':False}
def save():sp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def checkpoint():
 p=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(p)
 j['episode04UpscalingLabelRepairV15']={'execution':rel(sp),'status':state['status'],'worker':state['worker'],'active':state['active'],'allFinalPixelsReviewed':False}
 j['ownedActiveWork']=({'type':'CPU-upscaling-label-repair-v15','execution':rel(sp),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Direct encoded29 cues and three repaired labels; remaining90 paragraphs'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':rel(sp),'next':'Direct current encoded samples; continue visibility/mobile chapter'})
 j['updatedAt']=stamp();tmp=p.with_suffix('.label-v15.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(p)
def run(cmd,label):
 cmd=[str(x) for x in cmd];log=OUT/(label+'.log')
 with log.open('w',encoding='utf-8') as f:
  proc=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f);obs=psutil.Process(proc.pid)
  state['active']={'pid':proc.pid,'createTime':obs.create_time(),'commandLine':cmd,'cwd':str(ROOT),'log':rel(log),'startedAt':stamp()};save();checkpoint();code=proc.wait()
 r={**state['active'],'exitCode':code,'endedAt':stamp()};state['commands'].append(r);state['active']=None;save();assert code==0,label
 return r
def packets(path,selector):
 return json.loads(subprocess.run([str(FP),'-v','error','-select_streams',selector,'-show_packets','-show_data_hash','sha256','-show_entries','packet=pts,duration,data_hash','-of','json',str(path)],capture_output=True,text=True,check=True).stdout)['packets']
def probe(path):
 j=json.loads(subprocess.run([str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,duration,sample_rate,channels:format=duration','-of','json',str(path)],capture_output=True,text=True,check=True).stdout)
 v=next(x for x in j['streams'] if x['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',8006)
 vp=packets(path,'v:0');assert sorted(x['pts'] for x in vp)==list(range(0,8006*1500,1500))
 dur=[x['duration'] for x in vp if 'duration' in x];assert all(x==1500 for x in dur)
 ap=packets(path,'a:0')
 return {'path':rel(path),'sha256':sha(path),'probe':j,'frames':8006,'allPresentationPtsContinuous':True,'explicitPacketDurationCount':len(dur),'missingPacketDurationCount':len(vp)-len(dur),'aacPacketCount':len(ap),'aacPayloadSha256':hashlib.sha256('\n'.join(x['data_hash'] for x in ap).encode()).hexdigest()},ap
try:
 save();checkpoint();label=OUT/'source-identity.txt';label.write_text('공식 TSR 시연 · 가려짐 해제 · 50% 입력 / Epic AA','utf-8')
 vf=f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{rel(label)}':expansion=none:x=32:y=54:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.78:boxborderw=8,settb=1/90000,setpts=N*1500"
 pieces=[]
 for i,item in enumerate(oldState['results']):
  source=ROOT/item['path'];file=source
  if i in [7,8,9]:
   file=OUT/source.name
   run([FF,'-n','-hide_banner','-threads','2','-i',source,'-filter_threads','2','-vf',vf,'-frames:v',str(item['frames']),'-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',file],f'repair-cut-{i+1:02d}')
  pieces.append(file);state['results'].append({**item,'path':rel(file),'sha256':sha(file),'repaired':i in [7,8,9],'sourceCut':{'path':item['path'],'sha256':item['sha256']},'byteIdenticalReuse':i not in [7,8,9]});save()
 concat=OUT/'concat.txt';concat.write_text('\n'.join("file '"+str(f).replace('\\','/')+"'" for f in pieces)+'\n','utf-8')
 newClean=OUT/'game-lighting-history-04-upscaling-chapter.clean.mp4';newCap=OUT/'game-lighting-history-04-upscaling-chapter.captioned.mp4';video=OUT/'captioned-video-only.mp4'
 run([FF,'-n','-hide_banner','-threads','2','-f','concat','-safe','0','-i',concat,'-i',clean,'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',newClean],'clean-full-aac-copy')
 ass=ROOT/'production/research/game-lighting-history/local/episode04-upscaling-chapter-v13/captions.ko.ass'
 run([FF,'-n','-hide_banner','-threads','2','-reinit_filter','0','-i',newClean,'-filter_threads','2','-vf','ass='+rel(ass),'-frames:v','8006','-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',video],'caption-video-only')
 run([FF,'-n','-hide_banner','-threads','2','-i',video,'-i',clean,'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',newCap],'caption-full-aac-copy')
 originalAudio=packets(clean,'a:0');outputs=[]
 for file in [newClean,newCap]:
  proof,ap=probe(file);assert len(ap)==len(originalAudio)==6256
  assert all(x['data_hash']==y['data_hash'] and x['pts']==y['pts'] and x.get('duration')==y.get('duration') for x,y in zip(ap,originalAudio))
  proof['wholeDecode']=run([FF,'-v','error','-threads','2','-i',file,'-f','null','NUL'],file.stem+'-whole-decode');outputs.append(proof)
 record={**old,'builtAt':stamp(),'execution':rel(sp),'outputs':outputs,'previousBuild':state['inputBuild'],'repairReason':state['repairReason'],'changedCleanCuts':3,'byteIdenticalCleanCuts':9,'sourceLabelExpansion':'none','captionAss':{'path':rel(ass),'sha256':sha(ass),'byteIdenticalToV13':True},'allAacPayloadPtsDurationsIdenticalToV14':True,'captionedVideoPayloadAndPtsByteIdenticalToV13':False,'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'causalFlowApproved':False,'captionTimingApproved':False,'qaApproved':False,'collected':False,'uploaded':False}
 (P/'upscaling-chapter-review-build-v15.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
 state['status']='technical-label-repaired-pair-ready';state['endedAt']=stamp();state['build']=rel(P/'upscaling-chapter-review-build-v15.json');save();checkpoint();print(json.dumps({'status':state['status'],'repairedCuts':3,'reusedCuts':9,'aacPackets':6256,'frames':8006,'finalApproved':False}),flush=True)
except Exception as e:
 state['status']='failed';state['error']=repr(e);state['endedAt']=stamp();save();checkpoint();raise
