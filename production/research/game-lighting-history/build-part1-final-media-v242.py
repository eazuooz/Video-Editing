"""One CPU2/GPU0 phase. Mix and silent inputs precede direct current-mix approval."""
from pathlib import Path
from datetime import datetime, timezone
import os, sys, json, hashlib, subprocess, re, math, shutil, argparse
os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
import numpy as np, soundfile as sf, psutil
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/game-lighting-history-04/production'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
OUT=ROOT/'production/research/game-lighting-history/local/part1-final-v242'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
hashes={}
def sha(p):
 p=Path(p)
 if p not in hashes:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
  hashes[p]=h.hexdigest()
 return hashes[p]
def save(p,j):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.writing-'+str(os.getpid()));tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
args=argparse.ArgumentParser();args.add_argument('--phase',choices=['mix','visual','pair'],required=True);a=args.parse_args()
PP=P/'part1-final-input-plan-v240.json';plan=read(PP);N=plan['finalFrames'];duration=N/60
assert N==89148 and abs(plan['ratioErrorFrames'])<=1
for r in plan['bindings']:
 assert sha(ROOT/r['path'])==r['sha256'],r['path']
for c in plan['cuts']:
 assert sha(ROOT/c['video']['path'])==c['video']['sha256']
 assert sha(ROOT/c['pcm']['path'])==c['pcm']['sha256']
for r in [plan['branding'],plan['membership']]:assert sha(ROOT/r['path'])==r['sha256']
if a.phase=='pair':
 approval=read(P/'part1-final-mixed-asr-direct-review-v243.json');mix=read(P/'part1-final-mix-settings-v242.json')
 assert approval['allWholeAndIndependentTextsDirectlyCompared'] and approval['finalMixedAsrApproved']
 assert approval['currentMixSha256']==mix['wavSha256']==sha(ROOT/mix['wav'])
 assert approval['planSha256']==sha(PP)
SP=P/f'part1-final-{a.phase}-execution-v242.json';assert not SP.exists(),'Preserve prior phase; resume explicit completed steps only'
assert shutil.disk_usage(ROOT).free>12*1024**3
me=psutil.Process();ancestors={p.pid for p in me.parents()}|{me.pid};resources=[]
for proc in psutil.process_iter(['pid','name','create_time','cmdline']):
 try:
  d=proc.info;cmd=' '.join(d['cmdline'] or [])
  if any(n in (d['name'] or '').lower() for n in ['python','ffmpeg']):resources.append(d)
  if proc.pid not in ancestors and 'game-lighting-history' in cmd and ('ffmpeg' in (d['name'] or '').lower() or 'build-part1-final-media-v242.py' in cmd or 'review-part1-final-mix-v243.py' in cmd):raise RuntimeError('Owned exclusive media slot busy')
 except(psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
OUT.mkdir(parents=True,exist_ok=True)
state={'startedAt':stamp(),'status':'running','phase':a.phase,'worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'plan':{'path':rel(PP),'sha256':sha(PP)},'resources':{'processes':resources,'gpu':gpu},'active':None,'commands':[],'results':[],'cpuThreads':2,'gpuJobs':0,'newTts':0,'allFinalPixelsReviewed':False,'finalMixedAsrApproved':False,'qaApproved':False,'collected':False,'uploaded':False,'newGitImages':0}
def checkpoint():
 save(SP,state);p=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(p)
 j['episode04Part1FinalMediaV146']={'phase':a.phase,'execution':rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'results':len(state['results']),'finalApproved':False}
 j['ownedActiveWork']={'type':'part1-final-'+a.phase,'execution':rel(SP),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Current mixed-ASR direct comparison, final clean/captioned pixels, local collection and private upload'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Direct current mixed audio/final pixels before QA/private completion'}
 j['updatedAt']=stamp();save(p,j)
def run(cmd,label):
 cmd=[str(x) for x in cmd];log=OUT/(label+'.log');assert not log.exists(),label
 with log.open('w',encoding='utf8') as f:
  proc=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f);obs=psutil.Process(proc.pid)
  state['active']={'pid':proc.pid,'createTime':obs.create_time(),'commandLine':cmd,'cwd':str(ROOT),'log':rel(log),'startedAt':stamp()};checkpoint();code=proc.wait()
 result={**state['active'],'exitCode':code,'endedAt':stamp()};state['commands'].append(result);state['active']=None;checkpoint();assert code==0,(label,code)
 return result
def ff(t,label):return run([FF,'-n','-hide_banner','-nostdin','-threads','2',*t],label)
def scan(file,label,target=-2):
 job=ff(['-i',file,'-af',f'loudnorm=I=-16:TP={target}:LRA=11:print_format=json','-f','null','NUL'],label)
 return {'measurement':json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',(ROOT/job['log']).read_text('utf8')).group()),'command':job}
def source_label(text,name,x=32,y=22,size=28):
 p=OUT/(name+'.txt');p.write_text(text,'utf8')
 return f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{rel(p)}':expansion=none:x={x}:y={y}:fontsize={size}:fontcolor=white:box=1:boxcolor=black@0.82:boxborderw=8"
def encode(source,start,frames,file,label,crop=0,labels=(),tail=0,annotation=None,rect=None,matte=0):
 vf=([f'crop={rect[2]}:{rect[3]}:{rect[0]}:{rect[1]}'] if rect else [])+['scale=1920:1080:force_original_aspect_ratio=decrease','pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black','setsar=1','fps=60','setpts=PTS-STARTPTS']
 if matte:vf += [f'crop=1920:{1080-matte}:0:{matte}',f'pad=1920:1080:0:0:black']
 if crop:vf += [f'crop=1920:{1080-crop}:0:{crop}',f'pad=1920:1080:0:0:black']
 if tail:vf += [f'tpad=stop_mode=clone:stop_duration={tail/60:.9f}']
 vf += [f'trim=end_frame={frames}','settb=1/90000','setpts=N*1500']
 for i,t in enumerate(labels):
  if t:vf.append(source_label(t,label+f'-label-{i}',y=22+42*i,size=28 if i==0 else 24))
 if annotation:
  assert annotation['type']=='native-light-surface'
  for w in annotation['screenIntervals']:
   for x,y,ww,hh,col in w['boxes']:vf.append(f"drawbox=x={x}:y={y}:w={ww}:h={hh}:color={col}:t=4:enable='gte(t,{w['from']})*lt(t,{w['to']})'")
 ff(['-reinit_filter','0','-ss',f'{start:.9f}','-i',source,'-filter_threads','2','-vf',','.join(vf),'-frames:v',str(frames),'-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',file],label)
 pr=json.loads(subprocess.run([str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,nb_read_frames,time_base','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)
 v=next(s for s in pr['streams'] if s['codec_type']=='video');assert int(v['nb_read_frames'])==frames and v['time_base']=='1/90000',(label,pr)
def concat(files,target,label,audio=None):
 p=OUT/(label+'.concat.txt');p.write_text('\n'.join("file '"+str(x).replace('\\','/')+"'" for x in files)+'\n','utf8')
 args=['-f','concat','-safe','0','-i',p]
 if audio:args+=['-i',audio,'-map','0:v:0','-map','1:a:0']
 else:args+=['-map','0:v:0','-an']
 args+=['-c','copy','-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart',target];ff(args,label)
try:
 checkpoint()
 if a.phase=='mix':
  timeline=np.zeros(N*400,dtype='float32');placements=[];sources={};original_ranges={}
  for c in plan['cuts']:
   p=ROOT/c['pcm']['path']
   if p not in sources:
    v,sr=sf.read(p,dtype='float32');assert sr==24000 and v.ndim==1;sources[p]=v
   src=sources[p];pcm=c['pcm'];lo=pcm.get('firstSample',0);hi=pcm.get('exclusiveEndSample',len(src));v=src[lo:hi]
   assert len(v)==(pcm.get('samples') if 'samples' in pcm and not c.get('originalChapter') else hi-lo)
   assert len(v)<=c['frames']*400,(c['id'],len(v),c['frames']*400)
   at=c['fromFrame']*400;timeline[at:at+len(v)]=v;assert np.array_equal(timeline[at:at+len(v)],v)
   if c.get('originalChapter'):original_ranges.setdefault(c['originalChapter'],[]).append([lo,hi])
   placements.append({'id':c['id'],'fromFrame':c['fromFrame'],'frames':c['frames'],'source':{'path':rel(p),'sha256':sha(p)},'samples':[lo,hi],'paddingSamples':c['frames']*400-len(v),'allValuesExact':True})
  for c in plan['chapterRanges']:
   ranges=original_ranges[c['chapter']];assert ranges[0][0]==c['audio']['firstSample'] and ranges[-1][1]==c['audio']['exclusiveEndSample'];assert all(x[1]==z[0] for x,z in zip(ranges,ranges[1:]));assert sum(z-x for x,z in ranges)==c['audio']['samplesInChapter']
  assert not np.count_nonzero(timeline[:120*400]) and not np.count_nonzero(timeline[-600*400:])
  voice=OUT/'narration-timed.wav';assert not voice.exists();sf.write(voice,timeline,24000,subtype='FLOAT');back,sr=sf.read(voice,dtype='float32');assert sr==24000 and np.array_equal(back,timeline)
  proof={'createdAt':stamp(),'planSha256':sha(PP),'path':rel(voice),'sha256':sha(voice),'sampleRate':24000,'samples':len(timeline),'placements':placements,'allOriginalChapterSamplesPartitionedOnce':True,'allSelectedPcmValuesExact':True,'roundTripExact':True,'humanWholeListening':'pending','finalMixedAsrApproved':False};save(P/'part1-final-pcm-preservation-v242.json',proof)
  del sources,timeline,back
  rawscan=scan(voice,'mix-01-voice-scan');raw=rawscan['measurement'];normal=OUT/'voice-normalized-pass.wav'
  filt=f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={raw['input_i']}:measured_TP={raw['input_tp']}:measured_LRA={raw['input_lra']}:measured_thresh={raw['input_thresh']}:offset={raw['target_offset']}:linear=true,aresample=48000,aformat=channel_layouts=stereo"
  ff(['-i',voice,'-af',filt,'-c:a','pcm_f32le',normal],'mix-02-normalize')
  v,sr=sf.read(normal,dtype='float32',always_2d=True);assert sr==48000 and len(v)==N*800;outside=int(np.count_nonzero(v[:120*800])+np.count_nonzero(v[-600*800:]));v[:120*800]=0;v[-600*800:]=0
  body=OUT/'voice-body-only.wav';sf.write(body,v,48000,subtype='FLOAT');del v
  normalizedscan=scan(body,'mix-03-normalized-scan');m=normalizedscan['measurement'];gain=min(-16-float(m['input_i']),-2-float(m['input_tp']))
  normalized=OUT/'voice-normalized.wav';ff(['-i',body,'-af',f'volume={gain}dB','-c:a','pcm_f32le',normalized],'mix-04-gain')
  music_data=read(P.parent/'project.json')['audio']['backgroundMusic'];music=ROOT/music_data['file'];assert music_data['approvalStatus']=='approved' and sha(music)==music_data['restoration']['sha256']
  musicsha=sha(music);pr=json.loads(subprocess.run([str(FP),'-v','error','-show_format','-of','json',str(music)],capture_output=True,text=True,check=True).stdout);n=math.ceil((duration-1)/(float(pr['format']['duration'])-1))
  if n>1:
   chain=';'.join(f"{'[0:a]' if k==1 else '[b'+str(k-1)+']'}[{k}:a]acrossfade=d=1:c1=tri:c2=tri[b{k}]" for k in range(1,n));continuous=OUT/'nimbus-continuous.wav';ff([*sum((['-i',music] for _ in range(n)),[]),'-filter_complex_threads','2','-filter_complex',chain,'-map',f'[b{n-1}]','-c:a','pcm_f32le',continuous],'mix-05-continuous-music');music=continuous
  bg=OUT/'bgm-before-ducking.wav';ff(['-i',music,'-af',f'atrim=duration={duration:.9f},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.45,afade=t=out:st={duration-.45}:d=0.45','-c:a','pcm_f32le',bg],'mix-06-background')
  mix=OUT/'final-mix.wav';aac=OUT/'final-mix.m4a';filt='[0:a]asplit[n][d];[1:a][d]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[bg];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=0.80:level=false:latency=true[mix]'
  ff(['-i',normalized,'-i',bg,'-filter_complex_threads','2','-filter_complex',filt,'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',mix],'mix-07-ducked');assert sf.info(mix).frames==N*800
  ff(['-i',mix,'-c:a','aac','-b:a','192k',aac],'mix-08-aac');finalscan=scan(aac,'mix-09-aac-scan',-1.5);m=finalscan['measurement'];assert abs(float(m['input_i'])+16)<=.6 and float(m['input_tp'])<=-1.5,m
  decode=ff(['-i',aac,'-f','null','NUL'],'mix-10-decode');settings={'createdAt':stamp(),'planSha256':sha(PP),'pcmProofSha256':sha(P/'part1-final-pcm-preservation-v242.json'),'frames':N,'durationSeconds':duration,'voiceSha256':sha(voice),'rawScan':rawscan,'normalizedScan':normalizedscan,'constantVoiceGainDb':gain,'outsideVoiceNonzeroBeforeRepair':outside,'wav':rel(mix),'wavSha256':sha(mix),'aac':rel(aac),'aacSha256':sha(aac),'finalAacMeasurement':finalscan,'wholeAacDecode':decode,'approvedNimbusReferenceSha256':musicsha,'continuousApprovedNimbus':True,'originalNimbusFileVerified':False,'sourceAudioStreams':0,'newTts':0,'finalMixedAsrApproved':False,'allFinalPixelsReviewed':False,'uploaded':False,'humanWholeListening':'pending','humanPronunciation':'pending'};save(P/'part1-final-mix-settings-v242.json',settings);state['results'].append({'mix':settings['wav'],'lufs':m['input_i'],'truePeak':m['input_tp']})
 elif a.phase=='visual':
  files=[ROOT/plan['branding']['path']]
  for i,c in enumerate(plan['cuts']):
   file=OUT/f'cut-{i+1:03d}.mp4';source=ROOT/c['video']['path'];frames=c['frames'];start=c.get('sourceStartFrame',0)
   if c.get('originalChapter') and not start and not c.get('oneSilentVideoTailFrame'):
    file=source;reused=True
   elif c.get('nativeBoundaryExtension'):
    q=c['nativeBoundaryExtension'];encode(ROOT/q['source']['path'],q['sourceStartSeconds'],frames,file,f'visual-{i+1:03d}',rect=q.get('cropRect'),labels=[q.get('label')]);reused=False
   elif c['kind']=='explanation' or c.get('originalChapter'):
    encode(source,start/60,frames,file,f'visual-{i+1:03d}',tail=c.get('oneSilentVideoTailFrame',0));reused=False
   else:
    pieces=[]
    for k,cut in enumerate(c['proposedCuts']):
     segment=OUT/f'cut-{i+1:03d}-native-{k+1}.mp4';encode(source,cut['inFrame']/60,cut['outFrame']-cut['inFrame'],segment,f'visual-{i+1:03d}-native-{k+1}',rect=c.get('cropRect'),matte=c.get('captionMatteHeight',0),labels=[c['identityLabel'],c.get('onScreenConditionLabel')]);pieces.append(segment)
    assert sum(x['outFrame']-x['inFrame'] for x in c['proposedCuts'])==frames
    if len(pieces)>1:concat(pieces,file,f'visual-{i+1:03d}-join')
    else:file=pieces[0]
    reused=False
   files.append(file);state['results'].append({'id':c['id'],'path':rel(file),'sha256':sha(file),'frames':frames,'kind':c['kind'],'fromFrame':c['fromFrame'],'toFrame':c['toFrame'],'reusedByteIdentical':reused});checkpoint();print(json.dumps({'cut':i+1,'total':len(plan['cuts']),'id':c['id'],'reused':reused}),flush=True)
  files.append(ROOT/plan['membership']['path']);visual=OUT/'silent-visual.mp4';concat(files,visual,'visual-master-concat')
  ff(['-i',visual,'-f','null','NUL'],'visual-whole-decode');pr=json.loads(subprocess.run([str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,nb_read_frames,time_base,duration,width,height,r_frame_rate','-of','json',str(visual)],capture_output=True,text=True,check=True).stdout);v=pr['streams'][0];assert int(v['nb_read_frames'])==N and v['time_base']=='1/90000'
  save(P/'part1-final-visual-build-v242.json',{'builtAt':stamp(),'planSha256':sha(PP),'path':rel(visual),'sha256':sha(visual),'probe':pr,'frames':N,'cuts':state['results'],'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'qaApproved':False,'uploaded':False,'sourceModelsRerendered':0,'newGitImages':0})
 else:
  raise RuntimeError('Pair phase must use the separately reviewed caption layout and current mixed-ASR gate; prepare after direct review')
 state['status']='complete-'+a.phase+'-awaiting-direct-review';state['endedAt']=stamp();state['active']=None;checkpoint();print(json.dumps({'phase':a.phase,'status':state['status'],'frames':N,'finalApproved':False}),flush=True)
except BaseException as e:
 state['status']='failed';state['error']=repr(e);state['endedAt']=stamp();checkpoint();raise
