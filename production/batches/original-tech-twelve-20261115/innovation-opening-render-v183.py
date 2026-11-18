"""Render new openings and remux the unchanged reviewed bodies, one guarded GPU owner."""
from pathlib import Path
import argparse,bisect,hashlib,importlib.util,json,math,subprocess,time
import av
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;ROOT=H.parents[2];M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');C=M/'innovation-openings-v181'
FF=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
n=module('intro183_native_guard',H/'run-camera-native-v1.py');module('intro183_cooperative',H/'cooperative-resource-policy-v19.py').install(n);layout=module('intro183_layout',H/'innovation-opening-layout-v177.py');read,pin,save=n.read,n.pin,n.save
def preparation(require_final=True):
 n.authority();p=C/'all-mixes-v182.json'
 if not p.exists():return None
 plan=read(H/'innovation-opening-plan-v181.json');mixes=read(p);assert len(plan['rows'])==len(mixes['mixes'])==12;rows=[]
 for row,ref in zip(plan['rows'],mixes['mixes']):
  assert pin(ref['path'])==ref;mix=read(ref['path']);assert mix['order']==row['order']and mix['bodyFloatPcmByteExact'];assert pin(mix['mix']['path'])==mix['mix'];assert n.sha(row['introSource']['path'])==row['introSource']['sha256']
  for key in ['captioned','clean']:assert n.sha(row['baseline']['artifacts'][key]['path'])==row['baseline']['artifacts'][key]['sha256']
  identity=dict(project=row['slug'],baseline=row['baseline'],mix=ref,newSource=row['introSource'],sourceWindows=mix['selectedSourceWindows'],sourcePlan=pin(H/'innovation-opening-plan-v181.json'),layout=pin(H/'innovation-opening-layout-v177.py'),renderer=pin(__file__),encoder=pin(FF),fps=60,size=[1080,1920],sourceSpeed=1,bodyVideoReencoded=False,bodyAudioPcmModified=False)
  rows.append(dict(row=row,mix=mix,identity=identity,fingerprint=n.digest(identity)))
 assert n.sha(FF)=='05f4251bce9293c2ab492cb17ca7724a0ffd0d06c881ba2ee83b82a89c2fc740'
 if require_final:
  qa=C/'mixed-content-review-v183.json';visual=C/'preflight-visual-review-v183.json'
  if not qa.exists()or not visual.exists():return None
  assert read(qa)['approvedForReviewRender']and read(visual)['allowedForOpeningRender']and read(visual)['allMixes']==pin(p)
 return rows
def compose(item,frame,composer,reader,captioned=True):
 d=item['mix'];seconds=frame/60;remaining=seconds;sourceTime=None
 for w in d['selectedSourceWindows']:
  if remaining<w['availableSeconds']:sourceTime=w['sourceStartSeconds']+remaining;break
  remaining-=w['availableSeconds']
 assert sourceTime is not None;pixels,pts=reader.frame(sourceTime);starts=[c['start']for c in d['captionCues']];j=bisect.bisect_right(starts,seconds)-1;caption=d['captionCues'][j]['ko']if captioned and j>=0 else'';im=composer.opening(pixels,caption)
 return im,dict(frame=frame,seconds=seconds,sourcePts=pts,sourcePath=item['row']['introSource']['path'],sourceSpeed=1,caption=caption)
def preflight():
 items=preparation(False);assert items is not None;out=C/'preflight-v183';assert not out.exists();out.mkdir();records=[]
 for item in items:
  composer=layout.Composer(item['row']);reader=layout.Reader(item['row']['introSource']['path'])
  for j,cue in enumerate(item['mix']['captionCues']):
   frame=min(item['mix']['introVideoFrames']-1,math.floor((cue['start']+cue['spokenEnd'])*30));im,e=compose(item,frame,composer,reader);p=out/f'{item["row"]["order"]:02}-cue-{j:02}-375.jpg';im.resize((375,667),Image.Resampling.LANCZOS).save(p,quality=94);records.append(dict(order=item['row']['order'],cue=j,evidence=e,image=pin(p)))
  reader.close();composer.close()
 contacts=[]
 for k in range(0,len(records),8):
  im=Image.new('RGB',(1500,1394),'#14221c');dr=ImageDraw.Draw(im)
  for j,r in enumerate(records[k:k+8]):
   x=j%4*375;y=j//4*697;dr.text((x+5,y+5),f'{r["order"]:02} cue{r["cue"]}',fill='white');im.paste(Image.open(r['image']['path']),(x,y+30))
  p=out/f'contact-{k//8:02}.jpg';im.save(p,quality=94);contacts.append(pin(p))
 save(out/'observations.json',dict(allMixes=pin(C/'all-mixes-v182.json'),actualCompositions=records,contacts=contacts,actualListening=False,humanApproval=False));return dict(captionSamples=len(records),contacts=contacts)
def command(args,log,worker,lease):
 with log.open('wb')as f:
  p=subprocess.Popen([str(FF),'-hide_banner','-loglevel','warning','-nostdin',*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=n.CREATE);worker.update(child=n.identity(p.pid));lease.update(child=n.identity(p.pid));save(n.LEASE,lease);assert p.wait()==0,'Retain failed candidate and encoder log: '+str(log)
def render_one(item,worker,lease):
 row,d=item['row'],item['mix'];out=C/row['slug'];proof=out/'render-proof-v183.json'
 if proof.exists():
  p=read(proof);assert p['fingerprint']==item['fingerprint']
  for f in p['masters'].values():assert pin(f['path'])==f
  return pin(proof)
 targets=[out/(x+'-v183.mp4')for x in ['intro-captioned','intro-clean','captioned','clean']];assert not any(p.exists()for p in targets),'Preserve partial render; inspect before a separate identity'
 intro,cleanIntro,captioned,clean=targets;composer=layout.Composer(row);reader=layout.Reader(row['introSource']['path']);log=out/'intro-encoder-v183.log';frames=d['introVideoFrames'];samples=[]
 args=[str(FF),'-hide_banner','-loglevel','warning','-nostdin','-f','rawvideo','-pixel_format','rgb24','-video_size','1080x1920','-framerate','60','-i','pipe:0','-an','-c:v','h264_nvenc','-preset','p6','-cq','18','-b:v','0','-g','120','-pix_fmt','yuv420p','-video_track_timescale','15360',str(intro)];save(out/'intro-encoder-command-v183.json',dict(argv=args,frames=frames))
 with log.open('wb')as f:
  child=subprocess.Popen(args,cwd=ROOT,stdin=subprocess.PIPE,stdout=f,stderr=subprocess.STDOUT,creationflags=n.CREATE);worker.update(child=n.identity(child.pid));lease.update(phase='rendering-new-opening',order=row['order'],child=n.identity(child.pid));save(n.LEASE,lease)
  try:
   for frame in range(frames):
    im,e=compose(item,frame,composer,reader);child.stdin.write(im.tobytes())
    if frame%60==0 or frame==frames-1:samples.append(e)
   child.stdin.close();assert child.wait()==0,'Retain failed opening and log'
  finally:
   if child.stdin and not child.stdin.closed:child.stdin.close()
   child.wait();reader.close();composer.close()
 command(['-i',str(intro),'-vf','drawbox=x=0:y=1470:w=1080:h=270:color=black:t=fill','-an','-c:v','h264_nvenc','-preset','p6','-rc','constqp','-qp','10','-pix_fmt','yuv420p','-video_track_timescale','15360',str(cleanIntro)],out/'intro-clean-encoder-v183.log',worker,lease)
 audio=out/'audio-v183.m4a';assert not audio.exists();command(['-threads','2','-i',d['mix']['path'],'-vn','-c:a','aac','-b:a','192k','-ar','48000','-ac','2',str(audio)],out/'audio-encoder-v183.log',worker,lease)
 for key,prefix,target in [('captioned',intro,captioned),('clean',cleanIntro,clean)]:
  listing=out/(key+'-concat-v183.txt');assert not listing.exists();body=Path(row['baseline']['artifacts'][key]['path']);listing.write_text("file '"+str(prefix).replace('\\','/')+"'\nduration "+str(frames/60)+"\nfile '"+str(body).replace('\\','/')+"'\n",'utf8')
  command(['-f','concat','-safe','0','-auto_convert','1','-i',str(listing),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','15360','-movflags','+faststart',str(target)],out/(key+'-remux-v183.log'),worker,lease)
 with av.open(row['baseline']['artifacts']['captioned']['path'])as c:bodyFrames=c.streams.video[0].frames;assert bodyFrames>0
 result=dict(fingerprint=item['fingerprint'],identity=item['identity'],order=row['order'],slug=row['slug'],introVideoFrames=frames,baselineVideoFrames=bodyFrames,expectedTotalVideoFrames=frames+bodyFrames,mixSamples=d['frames'],mixDuration=d['durationSeconds'],masters=dict(captioned=pin(captioned),clean=pin(clean)),newIntro=dict(captioned=pin(intro),clean=pin(cleanIntro)),audio=pin(audio),samples=samples,bodyVideoStreamCopied=True,bodyFloatPcmByteExact=True,newWholeEncodedDecodeAndBodyEquivalenceReviewRequired=True,actualFullListening=False,humanApproval=False)
 save(proof,result);print(json.dumps(dict(order=row['order'],renderComplete=True,proof=pin(proof))),flush=True);return pin(proof)
def entry(script,pilot):
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--execute',action='store_true');ap.add_argument('--wait-minutes',type=float,default=0);ap.add_argument('--preflight',action='store_true');a=ap.parse_args();assert a.project=='shorts-mario64-lakitu-camera'
 if a.preflight:assert not a.execute;print(json.dumps(preflight()));return
 base=C/('film-pilot-v183'if pilot else'film-batch-v183');protocol='original-tech-twelve-innovation-film-'+('pilot'if pilot else'batch')+'-v183';owner='original-tech-twelve-innovation-film';n.runtime.PROTOCOL=protocol;n.runtime.OWNER=owner;n.guard.qualifier.BASE=base/'resource-observations'
 if not a.execute:print(json.dumps(dict(sourceReady=preparation()is not None,guardReason=n.busy(),videoStarted=False)));return
 assert a.wait_minutes==15;pins=module('intro183_bootstrap',H/'bootstrap-parent-identity-v1.py').install(n,script,a.project,base,protocol,owner);worker=n.runtime.SingleWorker(path=base/'worker.json');owned=None;deadline=time.monotonic()+15*60
 try:
  worker.acquire();argv=n.guard.psutil.Process().cmdline();worker.update(project=a.project,stage='targeted-source',argv=argv,commandSHA256=n.digest(argv),**pins);last=''
  while True:
   items=preparation();reason='Awaiting reviewed exact new mixes and preflight'if items is None else n.busy()
   if reason is None:
    token=worker.record['token'];lease=dict(protocol=protocol,owner=owner,token=token,**n.identity(),phase='reserved',child=None)
    try:
     with n.LEASE.open('x',encoding='utf8')as f:json.dump(lease,f)
    except FileExistsError:reason='Foreign lease preserved'
    else:
     owned=token;reason=n.busy(token)
     if reason is None:break
     if read(n.LEASE).get('token')==owned:n.LEASE.unlink()
     owned=None
   if reason!=last:print(json.dumps(dict(wait=reason,videoStarted=False)),flush=True);last=reason
   if time.monotonic()>=deadline:print(json.dumps(dict(started=False,boundedWaitExpired=True,reason=reason)));return
   time.sleep(20)
  if not pilot:
   pilotqa=C/items[1]['row']['slug']/'encoded-qa-v184.json';assert read(pilotqa)['allowedForUserReview'],'Review actual pilot concatenation before other eleven'
  chosen=[items[1]]if pilot else [x for x in items if x['row']['order']!=2];proofs=[render_one(item,worker,lease)for item in chosen];save(base/'complete.json',dict(proofs=proofs,selectedOrders=[x['row']['order']for x in chosen],actualListening=False,humanApproval=False));print(json.dumps(dict(completed=True,count=len(proofs))))
 finally:
  if owned and n.LEASE.exists()and read(n.LEASE).get('token')==owned:n.LEASE.unlink()
  if worker.handle is not None:worker.close()
