"""CPU2 only: replace one approved guide; retain every other normalized voice sample."""
import os
os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,re,copy,psutil,traceback
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production'
OUT=R/'production/research/game-lighting-history/local/part1-final-v310';OLD=R/'production/research/game-lighting-history/local/part1-final-v289'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
rd=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(R).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.writing-'+str(os.getpid()));t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(t,p)
PP=P/'part1-final-input-plan-v309.json';plan=rd(PP);oldplan=rd(P/'part1-final-input-plan-v288.json');oldmix=rd(P/'part1-final-mix-settings-v289.json')
assert plan['finalFrames']==89148 and plan['actualFrames']==53057 and plan['explanationFrames']==35371
g=next(c for c in plan['cuts'] if c.get('paragraphId')=='texture-dependent-conversion');lo=g['fromFrame']*800;hi=g['toFrame']*800
assert (g['fromFrame'],g['frames'])==(23085,970)
assert rd(P/'part1-vt-direction-direct-review-v309.json')['selectedForPrivateTechnicalProduction']
assert sha(R/oldmix['wav'])==oldmix['wavSha256']
me=psutil.Process();anc={x.pid for x in me.parents()}|{me.pid};resources=[]
for proc in psutil.process_iter(['pid','name','create_time','cmdline']):
 try:
  d=proc.info;cmd=' '.join(d['cmdline'] or [])
  if any(x in (d['name'] or '').lower() for x in ['python','ffmpeg']):resources.append(d)
  if proc.pid not in anc and 'game-lighting-history' in cmd and ('ffmpeg' in (d['name'] or '').lower() or 'build-part1-vt-correction-media-v310.py' in cmd):raise RuntimeError('Owned media slot busy')
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
assert not OUT.exists();OUT.mkdir(parents=True)
SP=P/'part1-final-media-execution-v310.json';assert not SP.exists()
state={'startedAt':now(),'status':'running','worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(R)},'cpuThreads':2,'gpuJobs':0,'resources':{'processes':resources,'gpu':subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True).strip()},'planSha256':sha(PP),'commands':[],'active':None,'finalMixedAsrApproved':False,'qaApproved':False,'uploaded':False,'newGitImages':0}
def checkpoint():
 save(SP,state);cp=R/'production/research/game-lighting-history/checkpoint.json';j=rd(cp)
 j['episode04Part1CurrentMediaV310']={'execution':rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'commands':len(state['commands']),'finalApproved':False}
 j['ownedActiveWork']={'type':'part1-one-guide-media','execution':rel(SP),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Direct changed mixed windows, strict current review pair and complete final pixels/private delivery'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Current mixed-ASR and exact unchanged-window reuse'}
 j['updatedAt']=now();save(cp,j)
def run(args,label):
 cmd=[str(x) for x in [FF,'-n','-hide_banner','-nostdin','-threads','2',*args]];log=OUT/(label+'.log')
 with log.open('w',encoding='utf8') as f:
  p=subprocess.Popen(cmd,cwd=R,stdout=f,stderr=f);obs=psutil.Process(p.pid);state['active']={'pid':p.pid,'createTime':obs.create_time(),'commandLine':cmd,'log':rel(log),'startedAt':now()};checkpoint();code=p.wait()
 row={**state['active'],'exitCode':code,'endedAt':now()};state['commands'].append(row);state['active']=None;checkpoint();assert code==0,(label,code)
 return row
def scan(p,label):
 job=run(['-i',p,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','NUL'],label)
 return {'measurement':json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',(R/job['log']).read_text('utf8')).group()),'command':job}
try:
 checkpoint()
 # New 24k timeline: all original sources, all exact partitions, no regenerated PCM.
 timeline=np.zeros(plan['finalFrames']*400,dtype='float32');placements=[];original={}
 for c in plan['cuts']:
  p=R/c['pcm']['path'];assert sha(p)==c['pcm']['sha256'];v,sr=sf.read(p,dtype='float32');assert sr==24000 and v.ndim==1
  a=c['pcm'].get('firstSample',0);b=c['pcm'].get('exclusiveEndSample',len(v));v=v[a:b];at=c['fromFrame']*400
  assert len(v)<=c['frames']*400;timeline[at:at+len(v)]=v;assert np.array_equal(timeline[at:at+len(v)],v)
  if c.get('originalChapter'):original.setdefault(c['originalChapter'],[]).append([a,b])
  placements.append({'id':c['id'],'fromFrame':c['fromFrame'],'frames':c['frames'],'source':c['pcm'],'samples':[a,b],'allValuesExact':True,'paddingSamples':c['frames']*400-len(v)})
 for ch in plan['chapterRanges']:
  q=original[ch['chapter']];assert q[0][0]==ch['audio']['firstSample'] and q[-1][1]==ch['audio']['exclusiveEndSample'];assert all(a[1]==b[0] for a,b in zip(q,q[1:]));assert sum(b-a for a,b in q)==ch['audio']['samplesInChapter']
 voice=OUT/'narration-timed.wav';sf.write(voice,timeline,24000,subtype='FLOAT')
 oldraw,sr=sf.read(OLD/'narration-timed.wav',dtype='float32');assert np.array_equal(timeline[:g['fromFrame']*400],oldraw[:g['fromFrame']*400]) and np.array_equal(timeline[g['toFrame']*400:],oldraw[g['toFrame']*400:]);del oldraw,timeline
 oldv,sr=sf.read(OLD/'voice-normalized.wav',dtype='float32',always_2d=True);assert sr==48000 and len(oldv)==plan['finalFrames']*800
 oldguide=OUT/'old-normalized-guide.wav';sf.write(oldguide,oldv[lo:hi],48000,subtype='FLOAT');oldscan=scan(oldguide,'01-old-guide-scan')
 raw=R/g['pcm']['path'];up=OUT/'new-guide-48k.wav';run(['-i',raw,'-af','aresample=48000,aformat=channel_layouts=stereo','-c:a','pcm_f32le',up],'02-new-guide-upsample');newscan=scan(up,'03-new-guide-scan')
 m=newscan['measurement'];target=oldscan['measurement'];gain=min(float(target['input_i'])-float(m['input_i']),-2-float(m['input_tp']))
 scaled=OUT/'new-guide-normalized.wav';run(['-i',up,'-af',f'volume={gain:.12f}dB','-c:a','pcm_f32le',scaled],'04-new-guide-gain');newv,sr=sf.read(scaled,dtype='float32',always_2d=True)
 assert sr==48000 and len(newv)==370560*2 and len(newv)<hi-lo
 oldv[lo:hi]=0;oldv[lo:lo+len(newv)]=newv;normalized=OUT/'voice-normalized.wav';sf.write(normalized,oldv,48000,subtype='FLOAT');del oldv,newv
 # Block comparison preserves every other normalized sample without loading two full copies.
 unchanged=True
 with sf.SoundFile(OLD/'voice-normalized.wav') as f,sf.SoundFile(normalized) as z:
  for start,end in [(0,lo),(hi,plan['finalFrames']*800)]:
   f.seek(start);z.seek(start)
   for at in range(start,end,48000*30):
    n=min(48000*30,end-at);unchanged &= np.array_equal(f.read(n,dtype='float32',always_2d=True),z.read(n,dtype='float32',always_2d=True))
 assert unchanged
 proof={'createdAt':now(),'planSha256':sha(PP),'path':rel(voice),'sha256':sha(voice),'sampleRate':24000,'samples':plan['finalFrames']*400,'placements':placements,'allSelectedPcmValuesExact':True,'allOriginalChapterSamplesPartitionedOnce':True,'allOtherRawTimelineSamplesExact':True,'allOtherNormalized48kSamplesExact':True,'changed48kRange':[lo,hi],'oldGuideScan':oldscan,'newGuideScan':newscan,'guideGainDb':gain,'fullCurrentMixApproval':False,'humanWholeListening':'pending','humanPronunciation':'pending'};save(P/'part1-final-pcm-preservation-v310.json',proof)
 bg=R/oldmix['bgmReused']['path'];bgsha=sha(bg);mix=OUT/'final-mix.wav';aac=OUT/'final-mix.m4a'
 filt='[0:a]asplit[n][d];[1:a][d]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[bg];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=0.80:level=false:latency=true[mix]'
 run(['-i',normalized,'-i',bg,'-filter_complex_threads','2','-filter_complex',filt,'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',mix],'05-ducked-mix');assert sf.info(mix).frames==plan['finalFrames']*800
 run(['-i',mix,'-c:a','aac','-b:a','192k',aac],'06-aac');measure=scan(aac,'07-final-aac-scan');m=measure['measurement'];assert abs(float(m['input_i'])+16)<=.6 and float(m['input_tp'])<=-1.5
 decode=run(['-i',aac,'-f','null','NUL'],'08-aac-decode')
 settings={'createdAt':now(),'planSha256':sha(PP),'pcmProofSha256':sha(P/'part1-final-pcm-preservation-v310.json'),'frames':plan['finalFrames'],'durationSeconds':plan['finalFrames']/60,'voiceSha256':sha(voice),'wav':rel(mix),'wavSha256':sha(mix),'aac':rel(aac),'aacSha256':sha(aac),'finalAacMeasurement':measure,'wholeAacDecode':decode,'approvedNimbusReferenceSha256':oldmix['approvedNimbusReferenceSha256'],'continuousApprovedNimbus':True,'bgmReused':{'path':rel(bg),'sha256':bgsha},'sourceAudioStreams':0,'allOtherNormalizedVoiceSamplesExact':True,'finalMixedAsrApproved':False,'allFinalPixelsReviewed':False,'uploaded':False,'humanWholeListening':'pending','humanPronunciation':'pending'};save(P/'part1-final-mix-settings-v310.json',settings)
 # Only bit-exact current-window samples may reuse already-read recognizer evidence.
 reuse=[];fresh=[]
 for r0 in rd(P/'part1-final-current-mixed-asr-direct-review-v292.json')['records']:
  w=copy.deepcopy(r0['window']);w['expectedKo']=[next(p['ko'] for p in plan['paragraphs'] if p['id']==i) for i in w['paragraphIds']]
  with sf.SoundFile(R/oldmix['wav']) as f,sf.SoundFile(mix) as z:
   n=(w['toFrame']-w['fromFrame'])*800;f.seek(w['fromFrame']*800);z.seek(w['fromFrame']*800);a=f.read(n,dtype='int16',always_2d=True);b=z.read(n,dtype='int16',always_2d=True)
  exact=np.array_equal(a,b);record={'window':w,'oldResult':{'label':r0['label'],'path':r0['path'],'sha256':r0['sha256']},'oldDirectReview':r0,'oldDirectReviewFile':{'path':rel(P/'part1-final-current-mixed-asr-direct-review-v292.json'),'sha256':sha(P/'part1-final-current-mixed-asr-direct-review-v292.json')},'stereo48kSamplesExact':bool(exact),'oldMixSha256':oldmix['wavSha256'],'currentMixSha256':settings['wavSha256'],'oldSampleSha256':hashlib.sha256(a.tobytes()).hexdigest(),'currentSampleSha256':hashlib.sha256(b.tobytes()).hexdigest()}
  assert sha(R/record['oldResult']['path'])==record['oldResult']['sha256']
  (reuse if exact else fresh).append(record)
 save(P/'part1-current-mixed-window-reuse-v310.json',{'preparedAt':now(),'planSha256':sha(PP),'mixSha256':settings['wavSha256'],'reusedExactWindows':reuse,'freshRequiredWindows':fresh,'total':36,'reusedCount':len(reuse),'freshCount':len(fresh),'automaticApproval':False,'finalMixedAsrApproved':False})
 print(json.dumps({'mix':settings['wavSha256'],'lufs':m['input_i'],'truePeak':m['input_tp'],'exactReusedWindows':len(reuse),'freshRequired':[r['window']['label'] for r in fresh]}),flush=True)
 # Copy/remux only new guide; all 93 other current reviewed inputs remain identical.
 oldvisual=rd(P/'part1-final-visual-build-v289.json');cuts=copy.deepcopy(oldvisual['cuts']);guide=OUT/'vt-conversion-current-silent.mp4';assert sha(R/g['video']['path'])==g['video']['sha256']
 oldcmd=next(x['commandLine'] for x in rd(P/'part1-final-visual-execution-v244.json')['commands'] if x['commandLine'][-1].endswith('cut-027-native-1.mp4'))
 args=oldcmd[6:];assert args[0]=='-reinit_filter'
 args[args.index('-ss')+1]='207.500000000';args[-1]=str(guide)
 run(args,'09-vt-conversion-current-native')
 oldrow=next(x for x in cuts if x['id']==g['id']);oldrow.update(path=rel(guide),sha256=sha(guide),frames=970,retainedByteIdenticalToV289=False)
 for c in cuts:
  if c['id']!=g['id']:c['retainedByteIdenticalToV289']=True
 for c in cuts:assert sha(R/c['path'])==c['sha256']
 files=[R/plan['branding']['path'],*[R/c['path'] for c in cuts],R/plan['membership']['path']];cat=OUT/'visual.concat.txt';cat.write_text('\n'.join("file '"+str(p).replace('\\','/')+"'" for p in files)+'\n','utf8');visual=OUT/'silent-visual.mp4'
 run(['-f','concat','-safe','0','-i',cat,'-map','0:v:0','-an','-c','copy','-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart',visual],'10-visual-concat')
 run(['-i',visual,'-f','null','NUL'],'11-visual-decode')
 pr=json.loads(subprocess.check_output([str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,nb_read_frames,time_base,width,height,r_frame_rate','-of','json',str(visual)],text=True));v=pr['streams'][0];assert (int(v['nb_read_frames']),v['time_base'],v['width'],v['height'],v['r_frame_rate'])==(89148,'1/90000',1920,1080,'60/1')
 pts=subprocess.check_output([str(FP),'-v','error','-threads','2','-select_streams','v:0','-show_entries','frame=pts','-of','csv=p=0',str(visual)],text=True);values=[int(s.split(',')[0]) for s in pts.splitlines() if s.strip().split(',')[0].isdigit()];assert values==list(range(0,89148*1500,1500))
 save(P/'part1-final-visual-build-v310.json',{'builtAt':now(),'planSha256':sha(PP),'path':rel(visual),'sha256':sha(visual),'frames':89148,'cuts':cuts,'actualFrames':53057,'explanationFrames':35371,'retainedOther93InputsByteIdentical':True,'wholeDecodeExitCode':0,'all89148PtsExact1500':True,'probe':pr,'sourceModelsRerendered':0,'nativeCutsReframed':1,'allFinalPixelsReviewed':False,'qaApproved':False,'uploaded':False})
 state.update(status='complete-awaiting-current-mix-direct-review',exitCode=0,completedAt=now());checkpoint();print(json.dumps({'status':state['status'],'frames':89148}),flush=True)
except BaseException:
 state.update(status='failed',error=traceback.format_exc(),endedAt=now());checkpoint();raise
