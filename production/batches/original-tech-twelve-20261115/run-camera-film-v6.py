"""Guarded source-bound local pilot, then a reviewed clean/captioned bundle."""
from pathlib import Path
import argparse,bisect,datetime,hashlib,importlib.util,json,math,shutil,subprocess,time
import av
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
P=ROOT/'projects/shorts-mario64-lakitu-camera'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');BASE=MEDIA/P.name/'film-v6'
ENCODER=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
native=module('ot12_local_film_guard',HERE/'run-camera-native-v1.py');layout=module('ot12_local_film_layout',HERE/'shorts-layout-v3.py')
read,sha,pin,save=native.read,native.sha,native.pin,native.save;runtime=native.runtime
PROTOCOL='original-tech-twelve-camera-film-v6';OWNER='original-tech-twelve-camera-film';runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER;native.guard.qualifier.BASE=BASE/'resource-observations'
def prepare(mode):
    native.authority();needed=[P/'production/caption-timing-v5.json',MEDIA/P.name/'audio-mix-v5/audio-build.json',MEDIA/P.name/'audio-mix-v5/mixed-content-review.json',MEDIA/P.name/'native-stream-v2/accepted-full.json',MEDIA/P.name/'native-stream-v2/full-visual-review-v2.json']
    missing=[str(p)for p in needed if not p.exists()]
    if missing:return None,'Awaiting actual reviewed inputs: '+', '.join(Path(p).name for p in missing)
    captions,mix,mixreview,capture,visual=map(read,needed)
    assert mixreview['approvedForPilot'] and mixreview['mixProof']==pin(needed[1]);assert visual['allowedForFilm'] and visual['actualSourceFramesInspected'] and visual['fullProof']==pin(needed[3])
    assert capture['purpose']=='full' and capture['framesPerCamera']==720 and capture['allPixelsRoundTripVerified']
    for row in [mix['mix'],mix['voice'],captions['voice'],captions['technicalVoiceReview']]:assert sha(row['path'])==row['sha256']
    planpath=P/'planning/film-beats-v5.json';plan=read(planpath);assert plan['semanticClauses']==captions['clauses'];duration=mix['durationSeconds'];assert duration==read(captions['voice']['path'])['canonical']['duration']
    cues=captions['cues'];beats=[]
    for para in plan['paragraphs']:
        for b in para['beats']:
            cue=next(c for c in cues if c['paragraph']==para['id']and c['clauseIndex']==b['firstClauseIndex']);beats.append(dict(b,start=cue['start'],paragraph=para['id']))
    assert beats[0]['start']==0
    for i,b in enumerate(beats):
        b['end']=beats[i+1]['start']if i+1<len(beats)else duration;assert b['end']>b['start']
        if b['kind']=='native':
            b['clip']=next(c for c in capture['clips']if c['mode']==b['mode']and c['camera']==b['view']);assert b['startFrame']+math.ceil((b['end']-b['start'])*60)<=720,'Choose another real source beat; no native looping/padding'
        elif b['kind']=='game':assert sha(b['source']['path'])==b['source']['sha256']
    assert sha(ENCODER)=='05f4251bce9293c2ab492cb17ca7724a0ffd0d06c881ba2ee83b82a89c2fc740'
    paths=needed+[planpath,HERE/'shorts-layout-v3.py',HERE/'lockon-layout-v1.py',HERE/'tech-diagrams-v1.py',HERE/'tech-diagrams-v2.py',Path(__file__)]
    identity=dict(inputs=[pin(p)for p in paths],encoder=pin(ENCODER),beats=beats,captionCues=cues,fps=60,size=[1080,1920],duration=duration,bodyAudioSamples=mix['frames'],visualFrames=math.ceil(duration*60),sourceSpeed=1,gameAspectPreserved=True,voiceOffsetSamples=0,codec=dict(video='h264_nvenc',preset='p6',cq=18,pixelFormat='yuv420p',audio='aac',rate=24000))
    fp=native.digest(identity)
    if mode=='full':
        review=BASE/'pilot-visual-review.json';pilot=BASE/'pilot-proof.json'
        if not review.exists()or not pilot.exists():return None,'Awaiting actual full-length pilot and separate technical visual review'
        r=read(review);assert r['allowedForFinalBundle'] and r['pilotProof']==pin(pilot)and read(pilot)['fingerprint']==fp
    return dict(fingerprint=fp,identity=identity,mix=mix,capture=capture),None
class GameReader:
    def __init__(self,path):
        self.c=av.open(str(path));self.s=self.c.streams.video[0];assert self.s.width>=1920 and self.s.height>=1080;self.decoder=None;self.current=None;self.next=None;self.last=None
    def frame(self,seconds):
        if self.decoder is None or self.last is not None and seconds<self.last:
            self.c.seek(int(seconds/self.s.time_base),stream=self.s,backward=True);self.decoder=self.c.decode(self.s);self.current=None;self.next=None
        while self.next is None or self.next.time<=seconds:
            if self.next is not None:self.current=self.next
            self.next=next(self.decoder)
        if self.current is None:self.current=self.next
        assert self.current.time<=seconds+1/float(self.s.average_rate)+.0001
        self.last=seconds;return self.current.to_image(),self.current.time
    def close(self):self.c.close()
def render(prep,mode,worker,lease,token):
    attempt=BASE/('pilot'if mode=='pilot'else'full');attempt.mkdir(parents=True,exist_ok=False);captioned=mode=='pilot';final_dir=MEDIA/P.name/'final-review-v1';final_dir.mkdir(parents=True,exist_ok=True);target=final_dir/('captioned.mp4'if captioned else'clean.mp4');assert not target.exists(),'Preserve existing encoded candidate';log=attempt/'encoder.log';count=prep['identity']['visualFrames'];composer=layout.Composer(P.name);readers={};samples=[]
    audio=Path(prep['mix']['mix']['path'])if captioned else Path(read(BASE/'pilot-proof.json')['video']['path']);codec=['-c:a','aac','-b:a','192k','-ar','24000']if captioned else['-c:a','copy']
    args=[str(ENCODER),'-hide_banner','-loglevel','warning','-nostdin','-f','rawvideo','-pixel_format','rgb24','-video_size','1080x1920','-framerate','60','-i','pipe:0','-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','h264_nvenc','-preset','p6','-cq','18','-b:v','0','-g','120','-pix_fmt','yuv420p',*codec,'-movflags','+faststart','-video_track_timescale','15360','-shortest',str(target)]
    save(attempt/'encoder-command.json',dict(argv=args,rawFrames=count,voiceOffset=0,bodyOnly=True))
    with log.open('wb')as out:
        child=subprocess.Popen(args,cwd=ROOT,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,creationflags=native.CREATE);worker.update(child=native.identity(child.pid));lease.update(phase='encoding',child=native.identity(child.pid));save(native.LEASE,lease)
        try:
            beats=prep['identity']['beats'];cues=prep['identity']['captionCues'];starts=[b['start']for b in beats];cue_starts=[c['start']for c in cues]
            for frame in range(count):
                seconds=min(frame/60,prep['identity']['duration']);b=beats[bisect.bisect_right(starts,seconds)-1];elapsed=seconds-b['start'];c=cues[bisect.bisect_right(cue_starts,seconds)-1];caption=c['ko']if captioned else''
                if b['kind']=='native':
                    key=b['clip']['video']['path']
                    if key not in readers:readers[key]=layout.NativeStreamReader(b['clip'])
                    index=b['startFrame']+int(math.floor(elapsed*60+1e-7));assert index<720;pixels,digest=readers[key].frame(index);im=composer.base(b.get('label','해설용 모형 · 직접 만든 비교 장면'));im.paste(pixels.resize((984,984),Image.Resampling.LANCZOS),(0,396));source=dict(kind='native',mode=b['mode'],view=b['view'],frame=index,rgbSHA256=digest)
                elif b['kind']=='game':
                    key=b['source']['path']
                    if key not in readers:readers[key]=GameReader(key)
                    pixels,pts=readers[key].frame(b['sourceStartSeconds']+elapsed);im=composer.base(b['label']);height=round(984*pixels.height/pixels.width);assert height<=984;im.paste(pixels.resize((984,height),Image.Resampling.LANCZOS),(0,396+(984-height)//2));source=dict(kind='game',path=key,sourcePts=pts,fullSourceAspectPreserved=True)
                else:im,source=composer.diagram(b['key'],b['localModelStartSeconds']+elapsed)
                if frame<180 or seconds>prep['identity']['duration']-4:composer.reaction(im,'puzzled'if frame<180 else'realize')
                composer.captioned(im,caption);child.stdin.write(im.tobytes())
                if frame%60==0 or frame==count-1:
                    samples.append(dict(frame=frame,seconds=frame/60,paragraph=c['paragraph'],clause=c['clauseIndex'],source=source))
                if frame%120==0:
                    image=attempt/f'sample-{frame:05}.jpg';im.save(image,quality=90);im.resize((375,667),Image.Resampling.LANCZOS).save(attempt/f'sample-{frame:05}-375.jpg',quality=92);save(BASE/'status.json',dict(status='rendering-'+mode,frame=frame,frames=count,videoComplete=False))
            child.stdin.close();code=child.wait();assert code==0,'Encoder failed; retain partial and logs'
        except:
            if child.stdin and not child.stdin.closed:child.stdin.close()
            child.wait();raise
        finally:
            for reader in readers.values():reader.close()
    with av.open(str(target))as c:
        v=c.streams.video[0];a=c.streams.audio[0];assert(v.width,v.height)==(1080,1920)and v.average_rate==60;decoded=sum(1 for f in c.decode(v));assert decoded==count
    proof=dict(fingerprint=prep['fingerprint'],identity=prep['identity'],mode=mode,video=pin(target),encoderLog=pin(log),actualVideoFrames=decoded,actualMix=prep['mix']['mix'],audioSource=('reviewed-pilot-aac-copy'if mode=='full'else'body-only-reviewed-mix'),samples=samples,technicalVisualReviewPending=True,humanApproval=False,finalDelivery=False)
    save(BASE/('pilot-proof.json'if mode=='pilot'else'clean-proof.json'),proof);return proof
def execute(mode,wait_minutes):
    waiter=runtime.SingleWorker(path=BASE/('waiter-'+mode+'.json'));waiter.acquire();deadline=time.monotonic()+wait_minutes*60;owned=None;worker=None
    try:
        last=None
        while True:
            prep,reason=prepare(mode)
            if prep:
                proof=BASE/('pilot-proof.json'if mode=='pilot'else'clean-proof.json')
                if proof.exists():assert read(proof)['fingerprint']==prep['fingerprint'];return dict(reusedExisting=True,proof=pin(proof))
                assert not(BASE/('pilot'if mode=='pilot'else'full')).exists(),'Partial render retained; inspect before a separate repair identity'
                reason=native.busy()
                if shutil.disk_usage(BASE.parent).free<2*1073741824:reason='Preserve2GiB media reserve'
            if reason is None:
                worker=runtime.SingleWorker(path=BASE/'worker.json');worker.acquire();token=worker.record['token'];lease=dict(protocol=PROTOCOL,owner=OWNER,token=token,**native.identity(),phase='reserved',fingerprint=prep['fingerprint'])
                try:
                    with native.LEASE.open('x',encoding='utf8')as f:json.dump(lease,f)
                except FileExistsError:reason='Concurrent foreign lease preserved'
                else:
                    owned=token;reason=native.busy(token)
                    if reason is None:
                        assert prepare(mode)[0]['fingerprint']==prep['fingerprint'];p=render(prep,mode,worker,lease,token);return dict(started=True,completed=True,proof=pin(BASE/('pilot-proof.json'if mode=='pilot'else'clean-proof.json')))
                    if read(native.LEASE).get('token')==owned:native.LEASE.unlink()
                    owned=None
                worker.close();worker=None
            state=dict(status='finite-film-'+mode+'-wait',reason=reason,modelStarted=False,videoStarted=False,**native.identity());save(BASE/('wait-status-'+mode+'.json'),state)
            if reason!=last:print(json.dumps(state),flush=True);last=reason
            if time.monotonic()>=deadline:return dict(started=False,boundedWaitExpired=True,reason=reason)
            time.sleep(min(30,max(0,deadline-time.monotonic())))
    finally:
        if owned and native.LEASE.exists()and read(native.LEASE).get('token')==owned:native.LEASE.unlink()
        if worker is not None and worker.handle is not None:worker.close()
        waiter.close()
def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--mode',choices=['pilot','full'],default='pilot');p.add_argument('--wait-minutes',type=float,default=0);a=p.parse_args();assert 0<=a.wait_minutes<=180
    if a.execute:r=execute(a.mode,a.wait_minutes)
    else:prep,reason=prepare(a.mode);r=dict(sourceReady=prep is not None,reason=reason,videoStarted=False)
    print(json.dumps(r),flush=True)
if __name__=='__main__':main()
