"""One guarded audio replacement; preserve compressed pictures and captions."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math,shutil,subprocess,time
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
FF=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
CREDIT='Wholesome Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttp://creativecommons.org/licenses/by/4.0/'
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
n=module('remux152_guard',H/'run-camera-native-v1.py');module('remux152_policy',H/'cooperative-resource-policy-v19.py').install(n)
read,pin,save=n.read,n.pin,n.save
def prepare(slug):
 n.authority();row=next(x for x in read(H/'audible-bgm-baseline-bindings-v144.json')['projects']if x['slug']==slug);assert row['order']not in[1,2]
 mp=M/slug/'camera-music-v139/audio-mix-v144/audio-build.json';mix=read(mp);rp=mp.parent/'mixed-content-review-v149.json';review=read(rp)
 assert review['approvedForRemux']and review['mixProof']==pin(mp)
 for x in [mix['mix'],mix['voice'],mix['musicStem']]:assert pin(x['path'])==x
 for x in row['baseline']['artifacts'].values():assert pin(x['path'])['sha256']==x['sha256']
 return row,mix,dict(adapter=pin(__file__),baseline=row['baseline'],mixProof=pin(mp),mixedReview=pin(rp),encoder=pin(FF),executionResourcePolicy=n.cooperative_policy_proof)
def packet_signature(path,kind):
 import av
 digest=hashlib.sha256();count=0;pts=[]
 with av.open(str(path))as c:
  st=c.streams.video[0]if kind=='video'else c.streams.audio[0]
  for p in c.demux(st):
   if not p.size:continue
   b=bytes(p);digest.update(len(b).to_bytes(8,'little'));digest.update(b);count+=1;pts.append([p.pts,p.dts,p.duration,str(st.time_base)])
 return dict(payloadSha256=digest.hexdigest(),packets=count,timing=pts)
def audio_qa(video,mix,words):
 import av,numpy as np,soundfile as sf
 from scipy.signal import resample_poly
 q=module('remux152_levels',ROOT/'production/batches/architectural-111-20261106/first-level-continuity-review.py')
 chunks=[];resampler=av.AudioResampler(format='fltp',layout='stereo',rate=24000);first=None
 with av.open(str(video))as c:
  a=c.streams.audio[0];duration=float(a.duration*a.time_base);assert abs(duration-mix['frames']/24000)<=1/24000+1e-6
  for f in c.decode(a):
   if first is None:first=f.time
   chunks.extend(x.to_ndarray().T.copy()for x in resampler.resample(f))
  chunks.extend(x.to_ndarray().T.copy()for x in resampler.resample(None))
 data=np.concatenate(chunks);reference,rate=sf.read(mix['mix']['path'],dtype='float32',always_2d=True);assert rate==24000 and abs(first)<=1/24000 and len(data)>=len(reference)
 alignment=q.estimate_alignment(reference,data,rate);assert alignment['supported'],alignment;offset=alignment['decodedMinusReferenceSamples'];assert offset==0,alignment
 rows=[]
 for w in words:
  a,b=w['startSample'],w['endSample'];assert 0<=a<b<=len(reference)
  before=q.levels(reference[a:b],rate);after=q.levels(data[a:b],rate);delta=after['bodyDbfs']-before['bodyDbfs'];assert abs(delta)<=q.POLICY['encodedWordLevelDeltaWarningDb'],(w,delta)
  rows.append(dict(text=w['text'],startSample=a,endSample=b,encodedBodyDeltaDb=delta))
 truepeak=float(np.max(np.abs(resample_poly(data,4,1,axis=0))));tp=20*math.log10(max(truepeak,1e-12));assert tp<=-1.5,tp
 return dict(audioTrackSeconds=duration,bodyMixFrames=len(reference),codecDecodedFrames=len(data),codecTrailingSamples=len(data)-len(reference),audioContentAlignment=alignment,truePeakDbtp=tp,wordLevelWindows=rows,allAutomaticChecksPassed=True,actualListening=False,humanApproval=False)
def run_child(args,worker,base,name):
 log=base/(name+'.log')
 with log.open('xb')as f:
  child=subprocess.Popen(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=n.CREATE);worker.update(child=n.identity(child.pid));lease=read(n.LEASE);lease.update(child=n.identity(child.pid),phase=name);save(n.LEASE,lease);assert child.wait()==0,log
 return pin(log)
def build(slug,base,worker):
 import av
 row,mix,identity=prepare(slug);out=base/'local-review-v5';out.mkdir(parents=True,exist_ok=True);old=row['baseline']['artifacts'];captioned=out/'captioned-v162.mp4';clean=out/'clean-v162.mp4';assert not captioned.exists()and not clean.exists()
 logs=[]
 logs.append(run_child([str(FF),'-hide_banner','-loglevel','warning','-nostdin','-threads','2','-i',old['captioned']['path'],'-i',mix['mix']['path'],'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-ar','48000','-b:a','192k','-movflags','+faststart',str(captioned)],worker,base,'captioned-remux'))
 logs.append(run_child([str(FF),'-hide_banner','-loglevel','warning','-nostdin','-threads','2','-i',old['clean']['path'],'-i',str(captioned),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-movflags','+faststart',str(clean)],worker,base,'clean-remux'))
 signatures={}
 for kind,path in [('captioned',captioned),('clean',clean)]:
  before=packet_signature(old[kind]['path'],'video');after=packet_signature(path,'video');assert before==after,'Compressed pictures or presentation times changed'
  with av.open(str(path))as c:
   st=c.streams.video[0];assert(st.width,st.height)==(1080,1920)and st.average_rate==60 and st.frames==math.ceil(mix['durationSeconds']*60)
  signatures[kind]=dict(payloadSha256=after['payloadSha256'],packetCount=after['packets'],allPacketTimesByteEquivalent=True)
 assert packet_signature(captioned,'audio')==packet_signature(clean,'audio')
 qa=audio_qa(captioned,mix,read(mix['oldEncodedQa']['path'])['wordLevelWindows']);qa.update(captioned=pin(captioned),clean=pin(clean),identity=identity,compressedVideoAndPtsUnchanged=True,videoPacketEvidence=signatures,aacPacketsByteExact=True,priorVisualReview=row['baseline']['checks'].get('technicalVisual',row['baseline']['checks']),visualQaReuseReason='Video packet bytes, complete timing list and stream geometry match the previously decoded and visually reviewed version exactly.')
 qp=base/'encoded-audio-and-picture-equivalence-v162.json';save(qp,qa);files=dict(captioned=pin(captioned),clean=pin(clean))
 for lang,meta,subs in [('ko','metadataKo','subtitlesKo'),('en','metadataEn','subtitlesEn')]:
  text=Path(old[meta]['path']).read_text('utf8');assert text.strip().endswith(CREDIT)
  change=('배경음악 수정: 음성에 맞춰 음악 음량을 조절하고, 시작과 끝에 0.45초 페이드를 적용했습니다.'if lang=='ko'else'Music adaptation: level adjusted under narration, with 0.45-second fades at the beginning and end.')
  target=out/('metadata-'+lang+'.txt');assert not target.exists();target.write_text(text.rstrip()[:-len(CREDIT)].rstrip()+'\n\n'+change+'\n\n'+CREDIT+'\n','utf8');files[meta]=pin(target)
  target=out/('captions.'+lang+'.srt');assert not target.exists();shutil.copyfile(old[subs]['path'],target);files[subs]=pin(target);assert files[subs]['sha256']==old[subs]['sha256']
 bundle=dict(slug=slug,version='audible-bgm-v162',titleKo=Path(old['metadataKo']['path']).read_text('utf8').splitlines()[0],durationSeconds=mix['durationSeconds'],artifacts=files,evidence=[pin(qp),identity['mixProof'],identity['mixedReview'],*logs],localFinalBundleComplete=True,oldBundlePreserved=row['baseline']['bundle'],unchangedApprovedVoiceRawPcm=True,uniformMasterGain=mix['masterConstantGain'],internalNarrationEnvelopeChanged=False,videoPacketsAndCaptionFilesUnchanged=True,musicMedianDbBelowVoice=mix['medianMusicMinusVoiceDb'],actualFullListening=False,actualRealtimePlayback=False,humanApproval=False,platformActions=[])
 save(out/'bundle-v5.json',bundle);return dict(bundle=pin(out/'bundle-v5.json'),truePeakDbtp=qa['truePeakDbtp'],wordWindows=len(qa['wordLevelWindows']))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--execute',action='store_true');ap.add_argument('--wait-minutes',type=float,default=0);a=ap.parse_args();base=M/a.project/'camera-music-v139/remux-v162';prepare(a.project)
 if not a.execute:print(json.dumps(dict(sourceReady=True,guardReason=n.busy(),videoStarted=False)));return
 assert a.wait_minutes==15;protocol='original-tech-twelve-'+a.project+'-bgm-remux-v162';owner='original-tech-twelve-'+a.project+'-bgm-remux';n.runtime.PROTOCOL=protocol;n.runtime.OWNER=owner;n.guard.qualifier.BASE=base/'resource-observations';bootstrap=module('remux152_bootstrap',H/'bootstrap-parent-identity-v1.py').install(n,__file__,a.project,base,protocol,owner)
 worker=n.runtime.SingleWorker(path=base/'worker.json');owned=None;deadline=time.monotonic()+a.wait_minutes*60
 try:
  worker.acquire();argv=n.guard.psutil.Process().cmdline();worker.update(project=a.project,stage='targeted-source',argv=argv,commandSHA256=n.digest(argv),**bootstrap);last=''
  assert not(base/'local-review-v5/bundle-v5.json').exists()
  while True:
   reason=n.busy()
   if reason is None:
    token=worker.record['token']
    try:
     with n.LEASE.open('x',encoding='utf8')as f:json.dump(dict(protocol=protocol,owner=owner,token=token,**n.identity(),phase='reserved'),f)
    except FileExistsError:reason='Concurrent foreign lease preserved'
    else:
     owned=token;reason=n.busy(token)
     if reason is None:break
     if read(n.LEASE).get('token')==token:n.LEASE.unlink()
     owned=None
   if reason!=last:print(json.dumps(dict(wait=reason,videoStarted=False)),flush=True);last=reason
   if time.monotonic()>=deadline:raise TimeoutError(reason)
   time.sleep(20)
  print(json.dumps(build(a.project,base,worker)),flush=True)
 finally:
  if owned and n.LEASE.exists()and read(n.LEASE).get('token')==owned:n.LEASE.unlink()
  if worker.handle is not None:worker.close()
if __name__=='__main__':main()
