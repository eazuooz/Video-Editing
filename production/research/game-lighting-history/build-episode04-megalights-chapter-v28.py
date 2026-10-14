"""CPU2 chapter review using completed spatial sources and original PCM."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import ImageFont, Image, ImageDraw
import json, hashlib, subprocess, psutil, wave, math, shutil
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
PP=P/'megalights-chapter-review-plan-v28.json'
OUT=ROOT/'production/research/game-lighting-history/local/episode04-megalights-chapter-v28'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
plan=read(PP);N=plan['totals']['frames']
assert N==6456 and len(plan['cuts'])==10 and len(plan['entries'])==7 and len(plan['cues'])==22
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
OUT.mkdir();me=psutil.Process();SP=P/'megalights-chapter-review-execution-v28.json';assert not SP.exists()
state={'startedAt':stamp(),'status':'running','worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'plan':{'path':rel(PP),'sha256':sha(PP)},'resourceObservation':{'processes':resources,'gpu':gpu},'cpuThreads':2,'gpuJobs':0,'active':None,'commands':[],'results':[],'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'finalMixedAsrApproved':False,'qaApproved':False,'collected':False,'uploaded':False,'newTts':0,'newGitImages':0}
def save():SP.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def checkpoint():
 p=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(p)
 j['episode04MegaLightsChapterV28']={'execution':rel(SP),'plan':rel(PP),'status':state['status'],'worker':state['worker'],'active':state['active'],'results':len(state['results']),'allFinalPixelsReviewed':False}
 j['ownedActiveWork']=({'type':'CPU-megalights-chapter-review-v28','execution':rel(SP),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Review22 encoded cues/cuts/annotations, then transparency/hair chapter'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Direct path chapter encoded review; all moving/full episode approvals pending'})
 j['updatedAt']=stamp();tmp=p.with_suffix('.megalights-chapter-v28.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(p)
def run(cmd,label):
 cmd=[str(x) for x in cmd];log=OUT/(label+'.log')
 with log.open('w',encoding='utf-8') as f:
  proc=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f);obs=psutil.Process(proc.pid)
  state['active']={'pid':proc.pid,'createTime':obs.create_time(),'commandLine':cmd,'cwd':str(ROOT),'log':rel(log),'startedAt':stamp()};save();checkpoint();code=proc.wait()
 result={**state['active'],'exitCode':code,'endedAt':stamp()};state['commands'].append(result);state['active']=None;save();assert code==0,(label,code)
 return result
def label(text,x,y,size=28,color='white',name='label'):
 f=OUT/(name+'.txt');f.write_text(text,'utf-8')
 return f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{rel(f)}':expansion=none:x={x}:y={y}:fontsize={size}:fontcolor={color}:box=1:boxcolor=black@0.78:boxborderw=8"
def ts(t):
 cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'
def probe(file):
 cmd=[str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,duration,sample_rate,channels:format=duration','-of','json',str(file)]
 j=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout);v=next(x for x in j['streams'] if x['codec_type']=='video')
 assert(v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',N)
 assert abs(float(v['duration'])-N/60)<1/90000
 pkt=json.loads(subprocess.run([str(FP),'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets']
 assert sorted(x['pts'] for x in pkt)==list(range(0,N*1500,1500));explicit=[x['duration'] for x in pkt if 'duration' in x];assert all(x==1500 for x in explicit)
 ap=json.loads(subprocess.run([str(FP),'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts,duration,data_hash','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets']
 return {'path':rel(file),'sha256':sha(file),'probe':j,'probeCommand':cmd,'frames':N,'aacPacketCount':len(ap),'allPresentationPtsContinuous':True,'explicitPacketDurationCount':len(explicit),'missingPacketDurationCount':len(pkt)-len(explicit),'aacPacketsPtsDurationPayloadSha256':hashlib.sha256(json.dumps(ap,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
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
 audio=OUT/'megalights-chapter-original-pcm.wav';samples=plan['audio']['samplesInChapter']
 with wave.open(str(ROOT/plan['audio']['path']),'rb') as src:
  assert(src.getframerate(),src.getnchannels(),src.getsampwidth())==(24000,1,2);src.setpos(plan['audio']['firstSample']);pcm=src.readframes(samples)
 assert len(pcm)==samples*2
 with wave.open(str(audio),'wb') as dst:dst.setnchannels(1);dst.setsampwidth(2);dst.setframerate(24000);dst.writeframes(pcm)
 with wave.open(str(audio),'rb') as check:assert check.readframes(samples)==pcm
 state['pcm']={'path':rel(audio),'sha256':sha(audio),'samples':samples,'firstSample':plan['audio']['firstSample'],'exclusiveEndSample':plan['audio']['exclusiveEndSample'],'allChapterPcmByteIdentical':True};save()
 pieces=[]
 for i,c in enumerate(plan['cuts']):
  file=OUT/f'cut-{i+1:02d}-{c["id"]}.mp4';frames=c['frames'];vf=[]
  if c.get('reuseEncodedCut'):
   ref=c['reuseEncodedCut'];file=ROOT/ref['path'];assert sha(file)==ref['sha256'];pieces.append(file);state['results'].append({**ref,'reusedByteIdentical':True});save();continue
  if c.get('cropTopPixels'):
   top=c['cropTopPixels'];vf += [f'crop=1920:{1080-top}:0:{top}','pad=1920:1080:0:0:black']
  if c.get('shiftUpPixels'):vf+=['crop=1920:1020:0:60','pad=1920:1080:0:0:black']
  vf+=['scale=1920:1080:force_original_aspect_ratio=decrease','pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black','setsar=1','fps=60','setpts=PTS-STARTPTS']
  if c.get('freezeFrameOnly'):vf+=['trim=end_frame=1','setpts=PTS-STARTPTS',f'tpad=stop_mode=clone:stop_duration={frames/60:.9f}']
  elif c['kind']=='explanation':
   span=c['sourceSpanFrames'];vf+=[f'trim=end_frame={span[1]-span[0]}','setpts=PTS-STARTPTS','tpad=stop_mode=clone:stop_duration=0.016666667']
  vf+=[f'trim=end_frame={frames}','settb=1/90000','setpts=N*1500']
  if c.get('annotation'):
   a=c['annotation']
   if a['type']=='tracked-observed-light-surface':
    def track_expr(track,col):
     result=str(track[-1][col]-35)
     for left,right in reversed(list(zip(track,track[1:]))):
      expr=f"({left[col]-35}+({right[col]-left[col]})*(t-{left[0]})/{right[0]-left[0]})"
      result=f"if(lt(t,{right[0]}),{expr},{result})"
     return result
    for key,color in [('lightTrack','0xF6D872'),('surfaceTrack','0x43D7CC')]:
     # Hollow Unicode marker follows measured screen coordinates frame by frame.
     f=OUT/(key+'.txt');f.write_text('○','utf-8')
     x=track_expr(a[key],1);y=track_expr(a[key],2)
     vf.append(f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{rel(f)}':expansion=none:x='{x}':y='{y}':fontsize=80:fontcolor={color}:enable='gte(t,{a['from']})*lt(t,{a['to']})'")
    vf.append(label('노랑: 광원 · 청록: 금속 표면',1150,130,size=26,color='white',name='observed-object-role')+f":enable='gte(t,{a['from']})*lt(t,{a['to']})'")
   elif a['type']=='native-light-surface':
    for window in a['screenIntervals']:
     for x,y,w,h,color in window['boxes']:
      vf.append(f"drawbox=x={x}:y={y}:w={w}:h={h}:color={color}:t=4:enable='gte(t,{window['from']})*lt(t,{window['to']})'")
   elif a['type']=='candidate-versus-visibility':
    mark=OUT/'candidate-annotation.png'
    im=Image.new('RGBA',(1920,1080),(0,0,0,0));d=ImageDraw.Draw(im);x,y=a['fromXY'];tx,ty=a['toXY'];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',28)
    for k in range(0,28,2):
     u,v=k/28,min((k+1)/28,1);d.line((x+(tx-x)*u,y+(ty-y)*u,x+(tx-x)*v,y+(ty-y)*v),fill=(246,216,114,255),width=4)
    d.text((930,300),'노랑 점선: 후보 연결 · 도달 미확인',font=font,fill=(246,216,114,255))
    d.text((1140,560),'초록: 검사 후 도달',font=font,fill=(170,211,156,255))
    d.text((425,645),'빨강: 벽에서 종료',font=font,fill=(236,137,147,255))
    im.save(mark)
  if c.get('opaqueHeaderStrip'):vf.append('drawbox=x=0:y=0:w=iw:h=76:color=black:t=fill')
  if c.get('label'):vf.append(label(c['label'],32,24,name='source-identity'))
  if c.get('secondaryLabel'):vf.append(label(c['secondaryLabel'],32,66,name='source-limit'))
  vfString=','.join(vf)
  if c.get('annotation',{}).get('type')=='candidate-versus-visibility':
   last=c['annotation']['exclusiveEndFrame'];vfString=f"[in]{vfString}[base];movie={rel(mark)}[mark];[base][mark]overlay=0:0:enable='lt(n,{last})':eof_action=repeat:repeatlast=1[out]"
  cmd=[FF,'-n','-hide_banner','-threads','2','-reinit_filter','0','-ss',str(c['sourceStart']),'-i',ROOT/c['path'],'-filter_threads','2','-vf',vfString,'-frames:v',str(frames),'-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',file]
  run(cmd,f'cut-{i+1:02d}');pieces.append(file)
  measured=json.loads(subprocess.run([str(FP),'-v','error','-count_frames','-show_entries','stream=nb_read_frames','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)
  assert int(measured['streams'][0]['nb_read_frames'])==frames,(c['id'],'frame count')
  state['results'].append({'id':c['id'],'path':rel(file),'sha256':sha(file),'frames':frames,'kind':c['kind']});save();print(json.dumps({'cut':i+1,'total':10,'frames':frames}),flush=True)
 concat=OUT/'concat.txt';concat.write_text('\n'.join("file '"+str(f).replace('\\','/')+"'" for f in pieces)+'\n','utf-8')
 clean=OUT/'game-lighting-history-04-megalights-chapter.clean.mp4';cap=OUT/'game-lighting-history-04-megalights-chapter.captioned.mp4'
 # Preserve all107.6s original PCM; cumulative global timing rounds within one frame.
 # Encode caption video separately and remux the complete AAC from clean.
 run([FF,'-n','-hide_banner','-threads','2','-f','concat','-safe','0','-i',concat,'-i',ROOT/'production/research/game-lighting-history/local/episode04-megalights-chapter-v26/game-lighting-history-04-megalights-chapter.clean.mp4','-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',clean],'clean-pair')
 video=OUT/'captioned-video-only.mp4'
 run([FF,'-n','-hide_banner','-threads','2','-reinit_filter','0','-i',clean,'-filter_threads','2','-vf','ass='+rel(ass),'-frames:v',str(N),'-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',video],'captioned-video-only')
 run([FF,'-n','-hide_banner','-i',video,'-i',clean,'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',cap],'captioned-complete-aac-remux')
 outputs=[]
 for file in [clean,cap]:
  proof=probe(file);proof['wholeDecode']=run([FF,'-v','error','-threads','2','-i',file,'-f','null','NUL'],file.stem+'-whole-decode');outputs.append(proof)
 assert outputs[0]['aacPacketsPtsDurationPayloadSha256']==outputs[1]['aacPacketsPtsDurationPayloadSha256']
 record={'builtAt':stamp(),'scope':plan['scope'],'plan':{'path':rel(PP),'sha256':sha(PP)},'execution':rel(SP),'outputs':outputs,'identicalAacPayloadAndPtsAndDuration':True,'preservedPcm':state['pcm'],'totals':plan['totals'],'captionCues':22,'captionCenter':[960,970],'sourceModelsRerendered':0,'newTts':0,'newGitImages':0,'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'causalFlowApproved':False,'captionTimingApproved':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'qaApproved':False,'collected':False,'uploaded':False,'humanWholeListening':'pending'}
 (P/'megalights-chapter-review-build-v28.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
 state['status']='technical-review-pair-ready';state['endedAt']=stamp();save();checkpoint();print(json.dumps({'status':state['status'],'frames':N,'sameAac':True,'finalApproved':False}),flush=True)
except Exception as e:
 state['status']='failed';state['error']=repr(e);state['endedAt']=stamp();save();checkpoint();raise
