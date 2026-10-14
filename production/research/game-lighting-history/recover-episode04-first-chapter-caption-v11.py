"""Recover only failed caption burn; preserve v10 clean, PCM and all18 cuts."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess, psutil, sys
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
OLD=ROOT/'production/research/game-lighting-history/local/episode04-first-chapter-review-v10'
OUT=ROOT/'production/research/game-lighting-history/local/episode04-first-chapter-caption-v11'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'); FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
previous=read(P/'first-chapter-review-execution-v10.json')
assert previous['status']=='failed' and previous['active'] is None
assert len(previous['results'])==18 and all(x['exitCode']==0 for x in previous['commands'])
assert previous['commands'][-1]['log'].endswith('clean-whole-decode.log')
clean=OLD/'game-lighting-history-04-first-chapter.clean.mp4'; ass=OLD/'captions.ko.ass'
planPath=P/'first-chapter-review-plan-v10.json'; plan=read(planPath)
assert sha(planPath)==previous['planSha256'] and sha(ass)==read(OLD/'caption-layout.json')['assSha256']
resume=sys.argv[1:]==['--resume-after-duration-field']
SP=P/'first-chapter-caption-recovery-execution-v11.json'
if resume:
 prior=read(SP)
 assert prior['status']=='failed' and prior['error']=="KeyError('duration')" and prior['active'] is None
 assert len(prior['commands'])==1 and prior['commands'][0]['exitCode']==0
 assert (OUT/'first-boundary-test.mp4').exists() and not (OUT/'game-lighting-history-04-first-chapter.captioned.mp4').exists()
 assert sha(clean)==prior['preservedClean']['sha256']
else:assert not OUT.exists() and not SP.exists()
resources=[]
for p in psutil.process_iter(['pid','ppid','name','cmdline','create_time']):
 try:
  d=p.info; cmd=' '.join(d['cmdline'] or [])
  if d['name'] and any(n in d['name'].lower() for n in ['ffmpeg','python']):resources.append(d)
  if d['name'] and 'ffmpeg' in d['name'].lower() and 'game-lighting-history' in cmd:raise RuntimeError('Owned media slot busy')
 except(psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
if not resume:OUT.mkdir()
me=psutil.Process()
state={'status':'running','startedAt':stamp(),'worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'resourceObservation':{'processes':resources,'gpu':gpu},'commands':[],'active':None,'cpuThreads':2,'gpuJobs':0,'preservedClean':{'path':rel(clean),'sha256':sha(clean)},'preserved18Cuts':previous['results'],'preservedPcm':previous['pcm'],'priorFailure':{'execution':rel(P/'first-chapter-review-execution-v10.json'),'oldCaptioned':rel(OLD/'game-lighting-history-04-first-chapter.captioned.mp4'),'actualVideoFrames':10300,'expectedVideoFrames':11664,'actualVideoSeconds':171.666667,'actualAudioSeconds':184.384,'dropLogFrames':1364},'repair':'Prevent filter state reset across concatenated input changes, and retain existing exact input PTS instead of reassigning per-filter N. Verify all decoded PTS, frame count, duration and AAC.','primaryDocumentation':'https://ffmpeg.org/ffmpeg.html#Main-options','allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'finalMixedAsrApproved':False,'qaApproved':False,'collected':False,'uploaded':False}
if resume:
 state['verificationRepairHistory']=[{'worker':prior['worker'],'startedAt':prior['startedAt'],'endedAt':prior['endedAt'],'error':prior['error'],'commands':prior['commands'],'preservedTestSha256':sha(OUT/'first-boundary-test.mp4'),'reason':'Some packets in the new no-reinit test omit duration. Validate every PTS plus exact final stream duration; validate every explicit duration and disclose missing fields.'}]
 state['commands']=prior['commands']
def save():SP.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def checkpoint():
 p=ROOT/'production/research/game-lighting-history/checkpoint.json'; j=read(p)
 j['episode04FirstChapterCaptionRecovery']={'execution':rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'previousFailurePreserved':True,'allFinalPixelsReviewed':False}
 j['ownedActiveWork']={'type':'CPU-caption-recovery-v11','execution':rel(SP),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Encoded44 cue/cut/framing review; complete remaining99 paragraphs'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Direct encoded first-chapter cue/cut review; whole episode incomplete'}
 j['updatedAt']=stamp(); tmp=p.with_suffix('.v11.tmp'); tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8'); tmp.replace(p)
def run(cmd,label):
 log=OUT/(label+'.log')
 with log.open('w',encoding='utf-8') as f:
  p=subprocess.Popen([str(x) for x in cmd],cwd=ROOT,stdout=f,stderr=f); proc=psutil.Process(p.pid)
  state['active']={'pid':p.pid,'createTime':proc.create_time(),'commandLine':[str(x) for x in cmd],'cwd':str(ROOT),'log':rel(log),'startedAt':stamp()}; save(); checkpoint(); code=p.wait()
 r={**state['active'],'exitCode':code,'endedAt':stamp()}; state['commands'].append(r);state['active']=None;save(); assert code==0,label
 return r
def probe(file,frames,seconds):
 cmd=[str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,duration,sample_rate,channels:format=duration','-of','json',str(file)]
 j=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout);v=next(x for x in j['streams'] if x['codec_type']=='video')
 assert(v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',frames),(file,v)
 assert abs(float(v['duration'])-seconds)<1/90000
 pts=json.loads(subprocess.run([str(FP),'-v','error','-threads','2','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets']
 assert sorted(x['pts'] for x in pts)==list(range(0,frames*1500,1500))
 explicit=[x['duration'] for x in pts if 'duration'in x];assert all(d==1500 for d in explicit)
 pa=json.loads(subprocess.run([str(FP),'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets']
 ah=hashlib.sha256('\n'.join(x['data_hash'] for x in pa).encode()).hexdigest()
 return {'path':rel(file),'sha256':sha(file),'probe':j,'probeCommand':cmd,'frames':frames,'allPresentationPtsAndDurationsContinuous':True,'explicitPacketDurationCount':len(explicit),'missingPacketDurationCount':len(pts)-len(explicit),'durationValidation':'Every presentation PTS at1500tick spacing, final stream duration, and every available explicit packet duration','aacPayloadSha256':ah}
try:
 save(); checkpoint()
 # Verify the preserved input, then test the first parameter-changing boundary.
 cp=probe(clean,11664,194.4);cp['wholeDecode']=previous['commands'][-1]
 test=OUT/'first-boundary-test.mp4'
 if not resume:run([FF,'-n','-hide_banner','-threads','2','-reinit_filter','0','-i',clean,'-filter_threads','2','-vf','ass='+rel(ass),'-frames:v','1500','-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000',test],'first-boundary-test')
 tp=probe(test,1500,25.0); state['firstBoundaryTest']=tp; save()
 captioned=OUT/'game-lighting-history-04-first-chapter.captioned.mp4'
 run([FF,'-n','-hide_banner','-threads','2','-reinit_filter','0','-i',clean,'-filter_threads','2','-vf','ass='+rel(ass),'-frames:v','11664','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','copy','-video_track_timescale','90000','-movflags','+faststart',captioned],'captioned-pair')
 cap=probe(captioned,11664,194.4); cap['wholeDecode']=run([FF,'-v','error','-threads','2','-i',captioned,'-f','null','NUL'],'captioned-whole-decode')
 assert cp['aacPayloadSha256']==cap['aacPayloadSha256'] and sha(clean)==state['preservedClean']['sha256']
 r={'builtAt':stamp(),'scope':plan['scope'],'plan':{'path':rel(planPath),'sha256':sha(planPath)},'execution':rel(SP),'outputs':[cp,cap],'identicalAacPayload':True,'originalPcmFirstSamplesByteIdentical':True,'firstChapterFrames':11664,'firstChapterSeconds':194.4,'captionCues':44,'captionCenter':[960,970],'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'causalFlowApproved':False,'captionTimingApproved':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'collected':False,'uploaded':False,'humanWholeListening':'pending','newTts':0,'newGitImages':0,'priorFailurePreserved':state['priorFailure']}
 (P/'first-chapter-review-build-v11.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8');state['status']='technical-review-pair-ready';state['endedAt']=stamp();save();checkpoint();print(json.dumps({'status':state['status'],'frames':11664,'seconds':194.4,'sameAac':True,'allFinalPixelsReviewed':False}),flush=True)
except Exception as e:
 state['status']='failed';state['error']=repr(e);state['endedAt']=stamp();save();checkpoint();raise
