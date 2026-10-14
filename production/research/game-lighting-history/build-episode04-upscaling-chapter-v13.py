"""CPU2 chapter review using completed spatial sources and original PCM."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import ImageFont
import json, hashlib, subprocess, psutil, wave, math, shutil
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
PP=P/'upscaling-chapter-review-plan-v13.json'
OUT=ROOT/'production/research/game-lighting-history/local/episode04-upscaling-chapter-v13'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
plan=read(PP);N=plan['totals']['frames']
assert N==8006 and len(plan['cuts'])==12 and len(plan['entries'])==9 and len(plan['cues'])==29
for key in ['selection','assembly','captionDraft','nativeReview']:assert sha(ROOT/plan[key]['path'])==plan[key]['sha256']
assert sha(ROOT/plan['audio']['path'])==plan['audio']['sha256']
cache={}
for cut in plan['cuts']:
 if cut['path'] not in cache:cache[cut['path']]=sha(ROOT/cut['path'])
 assert cache[cut['path']]==cut['sha256']
 if 'verification' in cut:
  v=read(ROOT/cut['verification']['path']);assert sha(ROOT/cut['verification']['path'])==cut['verification']['sha256']
  assert v['wholeDecodeExitCode']==0 and v['allPacketPtsAndDurationsApproved']
assert not OUT.exists(),'Preserve earlier review media'
assert shutil.disk_usage(ROOT).free>4*1024**3
resources=[]
for proc in psutil.process_iter(['pid','ppid','name','cmdline','create_time']):
 try:
  d=proc.info;cmd=' '.join(d['cmdline'] or [])
  if any(n in (d['name'] or '').lower() for n in ['python','ffmpeg']):resources.append(d)
  if 'ffmpeg' in (d['name'] or '').lower() and 'game-lighting-history' in cmd:raise RuntimeError('Owned media slot busy')
 except(psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
OUT.mkdir();me=psutil.Process();SP=P/'upscaling-chapter-review-execution-v13.json';assert not SP.exists()
state={'startedAt':stamp(),'status':'running','worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'plan':{'path':rel(PP),'sha256':sha(PP)},'resourceObservation':{'processes':resources,'gpu':gpu},'cpuThreads':2,'gpuJobs':0,'active':None,'commands':[],'results':[],'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'finalMixedAsrApproved':False,'qaApproved':False,'collected':False,'uploaded':False,'newTts':0,'newGitImages':0}
def save():SP.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def checkpoint():
 p=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(p)
 j['episode04UpscalingChapterV13']={'execution':rel(SP),'plan':rel(PP),'status':state['status'],'worker':state['worker'],'active':state['active'],'results':len(state['results']),'allFinalPixelsReviewed':False}
 j['ownedActiveWork']=({'type':'CPU-upscaling-chapter-review-v13','execution':rel(SP),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Review29 encoded cues and every cut; then remaining90 paragraphs'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Direct upscaling chapter encoded review; all moving/full episode approvals pending'})
 j['updatedAt']=stamp();tmp=p.with_suffix('.upscaling-chapter-v13.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(p)
def run(cmd,label):
 cmd=[str(x) for x in cmd];log=OUT/(label+'.log')
 with log.open('w',encoding='utf-8') as f:
  proc=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f);obs=psutil.Process(proc.pid)
  state['active']={'pid':proc.pid,'createTime':obs.create_time(),'commandLine':cmd,'cwd':str(ROOT),'log':rel(log),'startedAt':stamp()};save();checkpoint();code=proc.wait()
 result={**state['active'],'exitCode':code,'endedAt':stamp()};state['commands'].append(result);state['active']=None;save();assert code==0,(label,code)
 return result
def label(text,x,y,size=28,color='white',name='label'):
 f=OUT/(name+'.txt');f.write_text(text,'utf-8')
 return f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{rel(f)}':x={x}:y={y}:fontsize={size}:fontcolor={color}:box=1:boxcolor=black@0.78:boxborderw=8"
def ts(t):
 cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'
def probe(file):
 cmd=[str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,duration,sample_rate,channels:format=duration','-of','json',str(file)]
 j=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout);v=next(x for x in j['streams'] if x['codec_type']=='video')
 assert(v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',N)
 assert abs(float(v['duration'])-N/60)<1/90000
 pkt=json.loads(subprocess.run([str(FP),'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets']
 assert sorted(x['pts'] for x in pkt)==list(range(0,N*1500,1500));explicit=[x['duration'] for x in pkt if 'duration' in x];assert all(x==1500 for x in explicit)
 ap=json.loads(subprocess.run([str(FP),'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets']
 return {'path':rel(file),'sha256':sha(file),'probe':j,'probeCommand':cmd,'frames':N,'allPresentationPtsContinuous':True,'explicitPacketDurationCount':len(explicit),'missingPacketDurationCount':len(pkt)-len(explicit),'aacPayloadSha256':hashlib.sha256('\n'.join(x['data_hash'] for x in ap).encode()).hexdigest()}
try:
 save();checkpoint()
 # Reuse the already reviewed caption box construction; all pixels remain pending.
 fontPath=Path('C:/Windows/Fonts/malgun.ttf');font=ImageFont.truetype(str(fontPath),48)
 oldAss=ROOT/'production/research/game-lighting-history/local/episode04-first-chapter-review-v10/captions.ko.ass'
 header=oldAss.read_text('utf-8').split('Dialogue:')[0];events=[];metrics=[]
 for c in plan['cues']:
  lines=c['text'].split('\n');assert len(lines)<=2 and not any(any(ch in line for ch in ['{','}','\\']) for line in lines)
  w=math.ceil(max(font.getlength(x) for x in lines)+44);h=len(lines)*62+22;assert w<=1570
  x=math.floor(960-w/2);y=970-h/2;start,end=ts(c['from']),ts(c['to']);assert start!=end
  rect=f'm 0 0 l {w} 0 {w} {h} 0 {h}'
  for layer,text in [(0,f'{{\\an7\\pos({x+14},{y+14:g})\\p1\\bord0\\shad0\\1c&H323C07&}}'+rect),(1,f'{{\\an7\\pos({x},{y:g})\\p1\\bord3\\shad0\\1c&HFFFFFF&\\3c&H181B16&}}'+rect)]:events.append(f'Dialogue: {layer},{start},{end},Default,,0,0,0,,{text}')
  for i,line in enumerate(lines):events.append(f'Dialogue: 2,{start},{end},Default,,0,0,0,,{{\\an5\\pos(960,{970-(len(lines)-1)*31+i*62})\\bord0\\shad0}}'+line)
  af=math.ceil(round(c['from']*100)/100*60-1e-7);ef=math.ceil(round(c['to']*100)/100*60-1e-7);assert abs(af-c['firstFrame'])<=1 and abs(ef-c['exclusiveEndFrame'])<=1
  metrics.append({'id':c['id'],'text':c['text'],'box':{'x':x,'y':y,'width':w,'height':h,'center':[960,970]},'firstFrame':af,'exclusiveEndFrame':ef,'encodedPixelsReviewed':False})
 ass=OUT/'captions.ko.ass';ass.write_text(header+'\n'.join(events)+'\n','utf-8')
 (OUT/'caption-layout.json').write_text(json.dumps({'font':str(fontPath),'fontSha256':sha(fontPath),'fontSize':48,'maximumLines':2,'center':[960,970],'metrics':metrics,'assSha256':sha(ass),'allFinalPixelsReviewed':False},ensure_ascii=False,indent=2)+'\n','utf-8')
 audio=OUT/'upscaling-chapter-original-pcm.wav';samples=plan['audio']['samplesInChapter']
 with wave.open(str(ROOT/plan['audio']['path']),'rb') as src:
  assert(src.getframerate(),src.getnchannels(),src.getsampwidth())==(24000,1,2);src.setpos(plan['audio']['firstSample']);pcm=src.readframes(samples)
 assert len(pcm)==samples*2
 with wave.open(str(audio),'wb') as dst:dst.setnchannels(1);dst.setsampwidth(2);dst.setframerate(24000);dst.writeframes(pcm)
 with wave.open(str(audio),'rb') as check:assert check.readframes(samples)==pcm
 state['pcm']={'path':rel(audio),'sha256':sha(audio),'samples':samples,'firstSample':4665600,'exclusiveEndSample':7868160,'allChapterPcmByteIdentical':True};save()
 pieces=[]
 for i,c in enumerate(plan['cuts']):
  file=OUT/f'cut-{i+1:02d}-{c["id"]}.mp4';frames=c['frames'];vf=[]
  if c.get('shiftUpPixels'):vf+=['crop=1920:1020:0:60','pad=1920:1080:0:0:black']
  vf+=['scale=1920:1080:force_original_aspect_ratio=decrease','pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black','setsar=1','fps=60','setpts=PTS-STARTPTS']
  if c.get('freezeFrameOnly'):vf+=['trim=end_frame=1','setpts=PTS-STARTPTS',f'tpad=stop_mode=clone:stop_duration={frames/60:.9f}']
  elif c['kind']=='explanation':vf+=['tpad=stop_mode=clone:stop_duration=0.016666667']
  vf+=[f'trim=end_frame={frames}','settb=1/90000','setpts=N*1500']
  if c.get('label'):vf.append(label(c['label'],32,54,name='source-identity'))
  if c.get('annotation')=='before':vf.append(label('이동 전 · 뒤 건물 일부가 전경에 가려져 있습니다.',32,110,name='before-label'))
  if c.get('annotation')=='history-validity':
   vf+=['drawbox=x=875:y=160:w=130:h=610:color=0xf39a4b:t=4',label('새로 보이는 뒤 건물',1110,350,32,'0xf39a4b','revealed-label')]
   vf.append(label('멈춘 화면 분석 · 이전 색이 같은 표면의 값인가?',32,110,32,name='held-analysis-label'))
   vf+=['drawbox=x=575:y=260:w=165:h=490:color=0x36aaa4:t=3',label('전경',505,215,30,'0x36aaa4','foreground-label')]
   vf.append(label('과거 전경 색을 그대로 복사? → 다른 표면',1110,430,29,'0xdd3434','history-warning')+":enable='gte(t,3.583333333)'" )
  cmd=[FF,'-n','-hide_banner','-threads','2','-reinit_filter','0','-ss',str(c['sourceStart']),'-i',ROOT/c['path'],'-filter_threads','2','-vf',','.join(vf),'-frames:v',str(frames),'-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',file]
  run(cmd,f'cut-{i+1:02d}');pieces.append(file)
  measured=json.loads(subprocess.run([str(FP),'-v','error','-count_frames','-show_entries','stream=nb_read_frames','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)
  assert int(measured['streams'][0]['nb_read_frames'])==frames,(c['id'],'frame count')
  state['results'].append({'id':c['id'],'path':rel(file),'sha256':sha(file),'frames':frames,'kind':c['kind']});save();print(json.dumps({'cut':i+1,'total':12,'frames':frames}),flush=True)
 concat=OUT/'concat.txt';concat.write_text('\n'.join("file '"+str(f).replace('\\','/')+"'" for f in pieces)+'\n','utf-8')
 clean=OUT/'game-lighting-history-04-upscaling-chapter.clean.mp4';cap=OUT/'game-lighting-history-04-upscaling-chapter.captioned.mp4'
 # Preserve the full133.44s PCM. Video rounds by0.4frame; no audio -t clipping.
 run([FF,'-n','-hide_banner','-threads','2','-f','concat','-safe','0','-i',concat,'-i',audio,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-video_track_timescale','90000','-movflags','+faststart',clean],'clean-pair')
 run([FF,'-n','-hide_banner','-threads','2','-reinit_filter','0','-i',clean,'-filter_threads','2','-vf','ass='+rel(ass),'-frames:v',str(N),'-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','copy','-video_track_timescale','90000','-movflags','+faststart',cap],'captioned-pair')
 outputs=[]
 for file in [clean,cap]:
  proof=probe(file);proof['wholeDecode']=run([FF,'-v','error','-threads','2','-i',file,'-f','null','NUL'],file.stem+'-whole-decode');outputs.append(proof)
 assert outputs[0]['aacPayloadSha256']==outputs[1]['aacPayloadSha256']
 record={'builtAt':stamp(),'scope':plan['scope'],'plan':{'path':rel(PP),'sha256':sha(PP)},'execution':rel(SP),'outputs':outputs,'identicalAacPayload':True,'preservedPcm':state['pcm'],'totals':plan['totals'],'captionCues':29,'captionCenter':[960,970],'sourceModelsRerendered':0,'newTts':0,'newGitImages':0,'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'causalFlowApproved':False,'captionTimingApproved':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'qaApproved':False,'collected':False,'uploaded':False,'humanWholeListening':'pending'}
 (P/'upscaling-chapter-review-build-v13.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
 state['status']='technical-review-pair-ready';state['endedAt']=stamp();save();checkpoint();print(json.dumps({'status':state['status'],'frames':N,'sameAac':True,'finalApproved':False}),flush=True)
except Exception as e:
 state['status']='failed';state['error']=repr(e);state['endedAt']=stamp();save();checkpoint();raise
