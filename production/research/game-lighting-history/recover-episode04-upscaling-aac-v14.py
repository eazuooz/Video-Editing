"""Reuse completed v13 caption pixels; restore the final copied AAC packet."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/game-lighting-history-04/production'
OLD=ROOT/'production/research/game-lighting-history/local/episode04-upscaling-chapter-v13'
OUT=ROOT/'production/research/game-lighting-history/local/episode04-upscaling-aac-v14'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
old=read(P/'upscaling-chapter-review-execution-v13.json');planPath=P/'upscaling-chapter-review-plan-v13.json';plan=read(planPath)
assert old['status']=='failed' and old['error']=='AssertionError()' and len(old['results'])==12
assert all(x['exitCode']==0 for x in old['commands']) and old['commands'][-2]['log'].endswith('clean-whole-decode.log') and old['commands'][-1]['log'].endswith('captioned-whole-decode.log')
assert sha(planPath)==old['plan']['sha256']
clean=OLD/'game-lighting-history-04-upscaling-chapter.clean.mp4';previous=OLD/'game-lighting-history-04-upscaling-chapter.captioned.mp4'
def packets(file,stream):
 return json.loads(subprocess.run([str(FP),'-v','error','-select_streams',stream,'-show_packets','-show_data_hash','sha256','-show_entries','packet=pts,duration,data_hash','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets']
ca,pa=packets(clean,'a:0'),packets(previous,'a:0')
assert (len(ca),len(pa))==(6256,6255) and all(a['data_hash']==b['data_hash'] for a,b in zip(ca,pa))
oldVideo=packets(previous,'v:0');assert len(oldVideo)==8006
assert not OUT.exists()
resources=[]
for proc in psutil.process_iter(['pid','ppid','name','cmdline','create_time']):
 try:
  d=proc.info;cmd=' '.join(d['cmdline']or[])
  if any(n in (d['name']or'').lower() for n in ['python','ffmpeg']):resources.append(d)
  if 'ffmpeg' in (d['name']or'').lower() and 'game-lighting-history' in cmd:raise RuntimeError('Owned slot busy')
 except(psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
OUT.mkdir();me=psutil.Process();SP=P/'upscaling-aac-recovery-execution-v14.json';assert not SP.exists()
state={'status':'running','startedAt':stamp(),'worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'resourceObservation':{'processes':resources,'gpu':gpu},'cpuThreads':2,'gpuJobs':0,'active':None,'commands':[],'historicalFailure':{'path':rel(P/'upscaling-chapter-review-execution-v13.json'),'sha256':sha(P/'upscaling-chapter-review-execution-v13.json'),'retained':True},'inputs':[{'path':rel(x),'sha256':sha(x)} for x in [clean,previous]],'diagnosis':{'cleanAacPackets':6256,'previousCaptionedAacPackets':6255,'sharedPrefixPayloadIdentical':True,'cause':'-frames:v ended the caption encoding before the final copied AAC packet; no audio resynthesis required'},'allFinalPixelsReviewed':False}
def save():SP.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def checkpoint():
 p=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(p)
 j['episode04UpscalingAacRecoveryV14']={'execution':rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'allFinalPixelsReviewed':False}
 j['ownedActiveWork']=({'type':'CPU-upscaling-aac-remux-v14','execution':rel(SP),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Review29 encoded cues and every cut'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Direct29cue chapter encoded samples; remaining90 paragraph production'})
 j['updatedAt']=stamp();tmp=p.with_suffix('.aac-v14.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(p)
def run(cmd,label):
 cmd=[str(x) for x in cmd];log=OUT/(label+'.log')
 with log.open('w',encoding='utf-8') as f:
  proc=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f);obs=psutil.Process(proc.pid)
  state['active']={'pid':proc.pid,'createTime':obs.create_time(),'commandLine':cmd,'cwd':str(ROOT),'log':rel(log),'startedAt':stamp()};save();checkpoint();code=proc.wait()
 r={**state['active'],'exitCode':code,'endedAt':stamp()};state['commands'].append(r);state['active']=None;save();assert code==0,label
 return r
def probe(file):
 j=json.loads(subprocess.run([str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,duration,sample_rate,channels:format=duration','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)
 v=next(x for x in j['streams'] if x['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',8006)
 vp=packets(file,'v:0');assert sorted(x['pts'] for x in vp)==list(range(0,8006*1500,1500))
 dur=[x['duration'] for x in vp if 'duration' in x];assert all(x==1500 for x in dur)
 ap=packets(file,'a:0')
 return {'path':rel(file),'sha256':sha(file),'probe':j,'frames':8006,'allPresentationPtsContinuous':True,'explicitPacketDurationCount':len(dur),'missingPacketDurationCount':len(vp)-len(dur),'aacPacketCount':len(ap),'aacPayloadSha256':hashlib.sha256('\n'.join(x['data_hash'] for x in ap).encode()).hexdigest()},vp,ap
try:
 save();checkpoint();cap=OUT/'game-lighting-history-04-upscaling-chapter.captioned.mp4'
 run([FF,'-n','-hide_banner','-threads','2','-i',previous,'-i',clean,'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',cap],'restore-full-aac')
 cProof,cv,cAudio=probe(clean);pProof,pv,pAudio=probe(cap)
 assert len(cAudio)==len(pAudio)==6256 and all(x['data_hash']==y['data_hash'] and x['pts']==y['pts'] and x.get('duration')==y.get('duration') for x,y in zip(cAudio,pAudio))
 assert all(x['data_hash']==y['data_hash'] and x['pts']==y['pts'] for x,y in zip(oldVideo,pv))
 assert cProof['aacPayloadSha256']==pProof['aacPayloadSha256']
 cProof['wholeDecode']=old['commands'][-2];cProof['existingCleanDecodeReused']=True
 pProof['wholeDecode']=run([FF,'-v','error','-threads','2','-i',cap,'-f','null','NUL'],'recovered-captioned-whole-decode')
 record={'builtAt':stamp(),'scope':plan['scope'],'plan':{'path':rel(planPath),'sha256':sha(planPath)},'execution':rel(SP),'historicalFailure':state['historicalFailure'],'outputs':[cProof,pProof],'identicalAacPayload':True,'captionedVideoPayloadAndPtsByteIdenticalToV13':True,'preservedPcm':old['pcm'],'totals':plan['totals'],'captionCues':29,'captionCenter':[960,970],'sourceModelsRerendered':0,'newTts':0,'newGitImages':0,'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'causalFlowApproved':False,'captionTimingApproved':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'qaApproved':False,'collected':False,'uploaded':False,'humanWholeListening':'pending'}
 (P/'upscaling-chapter-review-build-v14.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
 state['status']='technical-recovered-pair-ready';state['endedAt']=stamp();state['build']=rel(P/'upscaling-chapter-review-build-v14.json');save();checkpoint();print(json.dumps({'status':state['status'],'aacPackets':6256,'frames':8006,'videoRerendered':False,'finalApproved':False}),flush=True)
except Exception as e:
 state['status']='failed';state['error']=repr(e);state['endedAt']=stamp();save();checkpoint();raise
