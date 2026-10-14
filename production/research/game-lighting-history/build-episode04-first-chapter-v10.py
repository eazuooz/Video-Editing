"""One CPU2 review composition of existing PCM/models/native, never a final approval."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import ImageFont
import json,hashlib,subprocess,psutil,math,wave,shutil
ROOT=Path(__file__).resolve().parents[3]
PROD=ROOT/'projects/game-lighting-history-04/production'
PP=PROD/'first-chapter-review-plan-v10.json'
OUT=ROOT/'production/research/game-lighting-history/local/episode04-first-chapter-review-v10'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.relative_to(ROOT).as_posix()
plan=read(PP)
assert plan['totals']['frames']==11664 and len(plan['entries'])==12 and len(plan['cuts'])==18 and len(plan['cues'])==44
for key in ['selection','assembly','nativeObservation','captionDraft']:assert sha(ROOT/plan[key]['path'])==plan[key]['sha256'],key
assert sha(ROOT/plan['audio']['path'])==plan['audio']['sha256']
cache={}
for c in plan['cuts']:
 if c['path']not in cache:cache[c['path']]=sha(ROOT/c['path'])
 assert cache[c['path']]==c['sha256'],c['id']
 if 'verification' in c:
  assert sha(ROOT/c['verification']['path'])==c['verification']['sha256'];v=read(ROOT/c['verification']['path'])
  assert v['wholeDecodeExitCode']==0 and v['allPacketPtsAndDurationsApproved']
assert not OUT.exists(),'Preserve already executed media'
assert shutil.disk_usage(ROOT).free>4*1024**3
resources=[]
for p in psutil.process_iter(['pid','ppid','name','cmdline','create_time']):
 try:
  d=p.info;cmd=' '.join(d['cmdline']or[])
  if d['name']and any(n in d['name'].lower()for n in ['ffmpeg','python','node']):resources.append(d)
  if d['name']and 'ffmpeg' in d['name'].lower()and 'game-lighting-history' in cmd:raise RuntimeError('Owned media slot busy')
 except(psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
OUT.mkdir();me=psutil.Process()
state={'startedAt':stamp(),'status':'running','worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'planSha256':sha(PP),'resourceObservation':{'processes':resources,'gpu':gpu},'cpuThreads':2,'gpuJobs':0,'active':None,'commands':[],'results':[],'allFinalPixelsReviewed':False,'finalMixedAsrApproved':False,'qaApproved':False,'collected':False,'uploaded':False}
SP=PROD/'first-chapter-review-execution-v10.json';assert not SP.exists()
def save():SP.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def checkpoint():
 p=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(p)
 j['episode04FirstChapterReview']={'execution':rel(SP),'plan':rel(PP),'status':state['status'],'worker':state['worker'],'active':state['active'],'results':len(state['results']),'allFinalPixelsReviewed':False}
 j['ownedActiveWork']={'type':'CPU-first-chapter-review-v10','execution':rel(SP),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Read encoded44 cue/cut/crop pixels and continuous causal motion; whole episode not complete'}if state['status']=='running'else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Direct first-chapter encoded review; continue remaining99 paragraphs'}
 j['updatedAt']=stamp();tmp=p.with_suffix('.v10.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(p)
def run(cmd,label):
 log=OUT/(label+'.log')
 with log.open('w',encoding='utf-8')as f:
  p=subprocess.Popen([str(x)for x in cmd],cwd=ROOT,stdout=f,stderr=f);proc=psutil.Process(p.pid)
  state['active']={'pid':p.pid,'createTime':proc.create_time(),'commandLine':[str(x)for x in cmd],'cwd':str(ROOT),'log':rel(log),'startedAt':stamp()};save();checkpoint();code=p.wait()
 result={**state['active'],'exitCode':code,'endedAt':stamp()};state['commands'].append(result);state['active']=None;save();assert code==0,label+' exit'+str(code)
 return result
def ts(t):
 cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'
try:
 save();checkpoint()
 fontPath=Path('C:/Windows/Fonts/malgun.ttf');font=ImageFont.truetype(str(fontPath),48)
 header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
 events=[];metrics=[]
 for c in plan['cues']:
  lines=c['text'].split('\n');assert len(lines)<=2 and not any(any(ch in line for ch in ['{','}','\\'])for line in lines)
  widths=[font.getlength(x)for x in lines];w=math.ceil(max(widths)+44);h=len(lines)*62+22;assert w<=1570,'Split cue rather than moving/shrinking it'
  x=math.floor(960-w/2);y=970-h/2;start,end=ts(c['from']),ts(c['to']);assert start!=end
  rect=f'm 0 0 l {w} 0 {w} {h} 0 {h}'
  for layer,text in [(0,f'{{\\an7\\pos({x+14},{y+14:g})\\p1\\bord0\\shad0\\1c&H323C07&}}'+rect),(1,f'{{\\an7\\pos({x},{y:g})\\p1\\bord3\\shad0\\1c&HFFFFFF&\\3c&H181B16&}}'+rect)]:events.append(f'Dialogue: {layer},{start},{end},Default,,0,0,0,,{text}')
  for i,line in enumerate(lines):events.append(f'Dialogue: 2,{start},{end},Default,,0,0,0,,{{\\an5\\pos(960,{970-(len(lines)-1)*31+i*62})\\bord0\\shad0}}'+line)
  af=math.ceil(round(c['from']*100)/100*60-1e-7);ef=math.ceil(round(c['to']*100)/100*60-1e-7);assert abs(af-c['firstFrame'])<=1 and abs(ef-c['exclusiveEndFrame'])<=1
  metrics.append({'id':c['id'],'text':c['text'],'box':{'x':x,'y':y,'width':w,'height':h,'center':[960,970]},'firstFrame':af,'exclusiveEndFrame':ef,'encodedPixelsReviewed':False})
 ass=OUT/'captions.ko.ass';ass.write_text(header+'\n'.join(events)+'\n','utf-8')
 (OUT/'caption-layout.json').write_text(json.dumps({'font':str(fontPath),'fontSha256':sha(fontPath),'fontSize':48,'maximumLines':2,'center':[960,970],'metrics':metrics,'assSha256':sha(ass),'allFinalPixelsReviewed':False},ensure_ascii=False,indent=2)+'\n','utf-8')
 sourceAudio=ROOT/plan['audio']['path'];audio=OUT/'first-chapter-original-pcm.wav'
 with wave.open(str(sourceAudio),'rb')as src:
  assert(src.getframerate(),src.getnchannels(),src.getsampwidth())==(24000,1,2);pcm=src.readframes(4665600)
 with wave.open(str(audio),'wb')as dst:dst.setnchannels(1);dst.setsampwidth(2);dst.setframerate(24000);dst.writeframes(pcm)
 assert len(pcm)==4665600*2
 with wave.open(str(audio),'rb')as check:assert check.readframes(4665600)==pcm
 state['pcm']={'path':rel(audio),'sha256':sha(audio),'samples':4665600,'originalFirstSamplesByteIdentical':True};save()
 pieces=[]
 for i,c in enumerate(plan['cuts']):
  file=OUT/f'cut-{i+1:02d}-{c["id"]}.mp4';frames=c['frames'];vf=[]
  if c.get('crop'):
   x,y,w,h=c['crop'];vf.append(f'crop={w}:{h}:{x}:{y}')
  vf.extend(['scale=1920:1080:force_original_aspect_ratio=decrease','pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black','setsar=1','fps=60'])
  if c.get('freezeFrameOnly'):vf.extend(['trim=end_frame=1','setpts=PTS-STARTPTS',f'tpad=stop_mode=clone:stop_duration={frames/60:.9f}'])
  else:vf.append('tpad=stop_mode=clone:stop_duration=0.016666667')
  vf.extend([f'trim=end_frame={frames}','settb=1/90000','setpts=N*1500'])
  if c.get('label'):
   label=OUT/f'label-{i+1:02d}.txt';label.write_text(c['label'],'utf-8');vf.append(f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{rel(label)}':x=32:y=54:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.75:boxborderw=10")
  cmd=[FF,'-n','-hide_banner','-threads','2','-ss',str(c['sourceStart']),'-i',ROOT/c['path'],'-filter_threads','2','-vf',','.join(vf),'-frames:v',str(frames),'-an','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',file]
  run(cmd,'cut-'+str(i+1).zfill(2));pieces.append(file);state['results'].append({'id':c['id'],'path':rel(file),'sha256':sha(file),'frames':frames,'kind':c['kind']});save();print(json.dumps({'cut':i+1,'total':18,'frames':frames}),flush=True)
 concat=OUT/'concat.txt';concat.write_text('\n'.join("file '"+str(p).replace('\\','/')+"'"for p in pieces)+'\n','utf-8')
 clean=OUT/'game-lighting-history-04-first-chapter.clean.mp4';captioned=OUT/'game-lighting-history-04-first-chapter.captioned.mp4'
 run([FF,'-n','-hide_banner','-threads','2','-f','concat','-safe','0','-i',concat,'-i',audio,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t','194.4','-video_track_timescale','90000','-movflags','+faststart',clean],'clean-pair')
 run([FF,'-n','-hide_banner','-threads','2','-i',clean,'-filter_threads','2','-vf','ass='+rel(ass)+',settb=1/90000,setpts=N*1500','-frames:v','11664','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','copy','-video_track_timescale','90000','-movflags','+faststart',captioned],'captioned-pair')
 proof=[]
 for file in [clean,captioned]:
  probeCmd=[str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,duration,sample_rate,channels:format=duration','-of','json',str(file)]
  probe=json.loads(subprocess.run(probeCmd,capture_output=True,text=True,check=True).stdout);v=next(x for x in probe['streams']if x['codec_type']=='video');assert(v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',11664);assert abs(float(v['duration'])-194.4)<1/90000
  pv=json.loads(subprocess.run([str(FP),'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets'];assert sorted(p['pts']for p in pv)==list(range(0,11664*1500,1500))
  pa=json.loads(subprocess.run([str(FP),'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets'];ah=hashlib.sha256('\n'.join(p['data_hash']for p in pa).encode()).hexdigest()
  decoded=run([FF,'-v','error','-threads','2','-i',file,'-f','null','NUL'],file.stem+'-whole-decode')
  proof.append({'path':rel(file),'sha256':sha(file),'frames':11664,'probe':probe,'probeCommand':probeCmd,'allPresentationPtsContinuous':True,'aacPayloadSha256':ah,'wholeDecode':decoded})
 assert proof[0]['aacPayloadSha256']==proof[1]['aacPayloadSha256']
 record={'builtAt':stamp(),'scope':plan['scope'],'plan':{'path':rel(PP),'sha256':sha(PP)},'execution':rel(SP),'outputs':proof,'identicalAacPayload':True,'originalPcmFirstSamplesByteIdentical':True,'firstChapterFrames':11664,'firstChapterSeconds':194.4,'captionCues':44,'captionCenter':[960,970],'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'causalFlowApproved':False,'captionTimingApproved':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'collected':False,'uploaded':False,'humanWholeListening':'pending','sourceAudioStreams':0,'newTts':0,'newGitImages':0}
 (PROD/'first-chapter-review-build-v10.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8');state['status']='technical-review-pair-ready';state['endedAt']=stamp();save();checkpoint();print(json.dumps({'status':state['status'],'seconds':194.4,'frames':11664,'decodedBoth':True,'sameAac':True,'finalApproved':False}),flush=True)
except Exception as e:
 state['status']='failed';state['error']=repr(e);state['endedAt']=stamp();save();checkpoint();raise
