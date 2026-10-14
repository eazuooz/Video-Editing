"""Resume completed v60 videos only; eliminate movie-timescale audio rounding."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, psutil, wave
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
BASE=ROOT/'production/research/game-lighting-history/local/episode04-physical-framing-v60'
OUT=ROOT/'production/research/game-lighting-history/local/episode04-physical-framing-v61'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
old=read(P/'physical-framing-review-execution-v60.json')
assert old['status']=='failed' and len(old['commands'])==3 and all(x['exitCode']==0 for x in old['commands'])
assert old['error']=='AssertionError()' and not OUT.exists()
plan=read(ROOT/old['plan']['path']);assembly=read(ROOT/old['assembly']['path'])
assert sha(ROOT/old['plan']['path'])==old['plan']['sha256'] and sha(ROOT/old['assembly']['path'])==old['assembly']['sha256']
source=ROOT/old['sourceVideo']['path'];audio=ROOT/assembly['path'];caption_video=BASE/'captioned-video-only.mp4';layout=BASE/'caption-layout.json'
assert sha(source)==old['sourceVideo']['sha256'] and sha(audio)==assembly['sha256']
assert len(read(layout)['cues'])==28 and plan['jobs'][0]['frames']==5320
resources=[]
for proc in psutil.process_iter(['pid','name','cmdline','create_time']):
 try:
  d=proc.info;cmd=' '.join(d['cmdline']or[])
  if any(n in (d['name']or'').lower() for n in ['python','ffmpeg']):resources.append(d)
  if 'ffmpeg' in (d['name']or'').lower() and 'game-lighting-history' in cmd:raise RuntimeError('Owned media slot busy')
 except(psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
OUT.mkdir();SP=P/'physical-framing-review-execution-v61.json';assert not SP.exists()
me=psutil.Process();state={'startedAt':stamp(),'status':'running','worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'resources':{'processes':resources,'gpu':gpu},'historicalFailure':{'path':rel(P/'physical-framing-review-execution-v60.json'),'sha256':sha(P/'physical-framing-review-execution-v60.json'),'reason':'v60 strict audio-sample check found32 samples of MP4 movie-timescale rounding; all speech present but exact duration pending'},'reusedCaptionVideo':{'path':rel(caption_video),'sha256':sha(caption_video)},'plan':old['plan'],'assembly':old['assembly'],'cpuThreads':2,'gpuJobs':0,'active':None,'commands':[],'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'qaApproved':False,'uploaded':False,'newGitImages':0}
def save():SP.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def checkpoint():
 p=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(p)
 j['episode04PhysicalFramingReviewV61']={'execution':rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'allFinalPixelsReviewed':False,'sourceModelsRerendered':0,'captionVideosReencoded':0}
 j['ownedActiveWork']={'status':state['status'],'type':'CPU-exact-aac-source-review-v61','execution':rel(SP),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Extract and directly review all28 cues and5 independent scenes; expand actual game examples and measured physical timelines'}
 j['updatedAt']=stamp();tmp=p.with_suffix('.framing-v61.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(p)
def run(cmd,label):
 cmd=[str(x) for x in cmd];log=OUT/(label+'.log')
 with log.open('w',encoding='utf-8')as f:
  proc=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f);obs=psutil.Process(proc.pid)
  state['active']={'pid':proc.pid,'createTime':obs.create_time(),'commandLine':cmd,'cwd':str(ROOT),'log':rel(log),'startedAt':stamp()};save();checkpoint();code=proc.wait()
 proof={**state['active'],'exitCode':code,'endedAt':stamp()};state['commands'].append(proof);state['active']=None;save();assert code==0,label
 return proof
def probe(file):
 j=json.loads(subprocess.run([str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,start_pts,duration_ts,duration,sample_rate,channels:format=duration','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)
 v=next(s for s in j['streams']if s['codec_type']=='video');a=next(s for s in j['streams']if s['codec_type']=='audio')
 assert(v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']),v['start_pts'],v['duration_ts'])==(1920,1080,'60/1','1/90000',5320,0,7980000)
 assert(a['codec_name'],a['sample_rate'],a['channels'],a['time_base'],a['start_pts'],a['duration_ts'])==('aac','48000',2,'1/48000',0,4256000)
 vp=json.loads(subprocess.run([str(FP),'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets']
 assert sorted(p['pts']for p in vp)==list(range(0,7980000,1500)) and all(p['duration']==1500 for p in vp if 'duration'in p)
 ap=json.loads(subprocess.run([str(FP),'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts,duration,data_hash','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets']
 assert ap[-1]['pts']+ap[-1]['duration']==4256000
 return {'path':rel(file),'sha256':sha(file),'probe':j,'frames':5320,'allPresentationPtsContinuous':True,'completeAudioDurationVerified':True,'aacLastEndSample':4256000,'aacPacketsPtsDurationPayloadSha256':hashlib.sha256(json.dumps(ap,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
try:
 save();checkpoint()
 clean=OUT/'physical-framing.clean.mp4';cap=OUT/'physical-framing.captioned.mp4'
 run([FF,'-n','-hide_banner','-threads','2','-i',source,'-i',audio,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart',clean],'exact-aac-clean')
 run([FF,'-n','-hide_banner','-i',caption_video,'-i',clean,'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart',cap],'exact-aac-captioned')
 outputs=[]
 for file in[clean,cap]:
  proof=probe(file);proof['wholeDecode']=run([FF,'-v','error','-threads','2','-i',file,'-f','null','NUL'],file.stem+'-whole-decode');outputs.append(proof)
 assert outputs[0]['aacPacketsPtsDurationPayloadSha256']==outputs[1]['aacPacketsPtsDurationPayloadSha256']
 assert sha(caption_video)==state['reusedCaptionVideo']['sha256'] and sha(source)==old['sourceVideo']['sha256']
 record={'builtAt':stamp(),'scope':'Five physical framing source scenes, voice-only review pair; not final episode delivery','execution':rel(SP),'plan':state['plan'],'assembly':state['assembly'],'captionLayout':{'path':rel(layout),'sha256':sha(layout)},'outputs':outputs,'identicalAacPayloadAndPtsAndDuration':True,'exactAudioDurationSamples':4256000,'allSelectedPcm16ByteIdentical':assembly['allSelectedPcm16ByteIdentical'],'sourceModelsRerendered':0,'captionVideosReencoded':0,'frames':5320,'captionCues':28,'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'qaApproved':False,'collected':False,'uploaded':False,'humanWholeListening':'pending','newGitImages':0}
 (P/'physical-framing-review-build-v61.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
 state['status']='technical-source-review-pair-ready';state['endedAt']=stamp();save();checkpoint();print(json.dumps({'status':state['status'],'exactAudioSamples':4256000,'sameAac':True,'twoWholeDecodes':0,'finalApproved':False}),flush=True)
except Exception as e:
 state['status']='failed';state['error']=repr(e);state['endedAt']=stamp();save();checkpoint();raise
