"""Guarded body-only mix: unchanged selected voice master plus quiet licensed music."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,shutil,time,wave
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
P=ROOT/'projects/shorts-journey-sand-sparkle'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
BASE=ROOT/'shared/output/original-tech-twelve-20261115'/P.name/'audio-mix-v10'
s=importlib.util.spec_from_file_location('ot12_mix_guard',HERE/'run-camera-native-v1.py');native=importlib.util.module_from_spec(s);s.loader.exec_module(native)
runtime=native.runtime;PROTOCOL='original-tech-twelve-camera-mix-v5';OWNER='original-tech-twelve-camera-mix';runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER
native.guard.qualifier.BASE=BASE/'resource-observations';read,sha,pin,save=native.read,native.sha,native.pin,native.save
def prepare():
    native.authority();selection=read(P/'production/accepted-voice-selection-v10.json');voice=Path(selection['voice']['path']);assert pin(voice)==selection['voice'];proof=read(voice);review=Path(selection['technicalVoiceReview']['path']);accepted=read(review);assert accepted['approvedForTechnicalDownstream'] and accepted['voice']==pin(voice)
    for row in proof['identity']['sourceInputs']+[proof['canonical']]:assert sha(row['path'])==row['sha256']
    music=ROOT/'shared/assets/music/incompetech/Wholesome.mp3';assert sha(music)=='9eadc79a1a2cb68cd63be1432ebf8f8ae3387cb9d2e85f9b8dbc74ba5a96b231'
    captions=Path(selection['captionTiming']['path']);assert pin(captions)==selection['captionTiming'];c=read(captions);assert c['voice']==pin(voice) and c['technicalVoiceReview']==pin(review) and c['audioOffsetSeconds']==0
    identity=dict(adapter=pin(__file__),voice=pin(voice),voiceReview=pin(review),captionTiming=pin(captions),music=pin(music),musicLicense=pin(ROOT/'shared/assets/music/incompetech/Wholesome.LICENSE.md'),rate=24000,voiceGain=1,musicGain=.03,musicEndFadeSeconds=.25,musicPeakDuck='20ms-lookahead-100ms-release-only-music',voiceDsp=False,insertedVoiceSamples=0,voiceTrimmedSamples=0)
    return dict(fingerprint=native.digest(identity),identity=identity,voice=proof,music=music)
def execute(wait_minutes):
    prepared=prepare();accepted=BASE/'audio-build.json'
    if accepted.exists():assert read(accepted)['fingerprint']==prepared['fingerprint'];return dict(reusedExisting=True,proof=pin(accepted))
    worker=runtime.SingleWorker(path=BASE/'worker.json');owned=None
    try:
        worker.acquire();deadline=time.monotonic()+wait_minutes*60;last=None
        while True:
            assert prepare()['fingerprint']==prepared['fingerprint'];reason=native.busy()
            if not reason:
                token=worker.record['token']
                try:
                    with native.LEASE.open('x',encoding='utf8')as f:json.dump(dict(protocol=PROTOCOL,owner=OWNER,token=token,**native.identity(),phase='audio-mix-reserved',fingerprint=prepared['fingerprint']),f)
                except FileExistsError:reason='Concurrent foreign lease preserved'
                else:
                    owned=token;reason=native.busy(token)
                    if not reason:break
                    if read(native.LEASE).get('token')==owned:native.LEASE.unlink()
                    owned=None
            save(BASE/'status.json',dict(status='finite-audio-mix-resource-wait',reason=reason,audioStarted=False,**native.identity()))
            if reason!=last:print(json.dumps(dict(reason=reason,audioStarted=False)),flush=True);last=reason
            if time.monotonic()>=deadline:return dict(started=False,boundedWaitExpired=True,reason=reason)
            time.sleep(min(30,max(0,deadline-time.monotonic())))
        import av,numpy as np,soundfile as sf
        spec=importlib.util.spec_from_file_location('ot12_mix_unchanged_level_primitive',ROOT/'production/batches/architectural-111-20261106/first-level-continuity-review.py');qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
        voice=prepared['voice'];canonical=voice['canonical'];frames=canonical['frames']
        with wave.open(canonical['path'],'rb')as w:assert(w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,24000);raw=w.readframes(frames)
        assert hashlib.sha256(raw).hexdigest()==canonical['pcmSHA256'];v=np.frombuffer(raw,dtype='<i2').astype(np.float32)/32768
        music=[];resample=av.AudioResampler(format='fltp',layout='stereo',rate=24000)
        with av.open(str(prepared['music']))as c:
            for frame in c.decode(audio=0):
                music.extend(f.to_ndarray().T.copy()for f in resample.resample(frame))
                if sum(len(x)for x in music)>=frames:break
        assert sum(len(x)for x in music)>=frames,'Music must cover body naturally; no loop or padding'
        bgm=np.concatenate(music,axis=0)[:frames].astype(np.float32)*.03;fade=min(frames,round(.25*24000));bgm[-fade:]*=np.linspace(1,0,fade,dtype=np.float32)[:,None]
        # The unchanged voice may approach full scale. Duck music alone before
        # the sum rather than attenuating or limiting the approved raw voice.
        from scipy.ndimage import minimum_filter1d
        ceiling=1-1/65536;allowed=np.ones(frames,dtype=np.float32)
        for ch in range(2):
            music_channel=bgm[:,ch];positive=music_channel>0;negative=music_channel<0;bound=np.ones(frames,dtype=np.float32)
            bound[positive]=np.maximum(0,(ceiling-v[positive])/music_channel[positive]);bound[negative]=np.maximum(0,(-ceiling-v[negative])/music_channel[negative]);allowed=np.minimum(allowed,np.minimum(1,bound))
        protected=minimum_filter1d(allowed,size=961,mode='nearest');envelope=protected.copy();release=np.exp(-1/(.1*24000))
        for j in range(1,frames):envelope[j]=min(envelope[j],release*envelope[j-1]+1-release)
        bgm*=envelope[:,None]
        mixed=v[:,None]+bgm;assert len(mixed)==frames and np.isfinite(mixed).all() and np.max(np.abs(mixed))<1,'Preserve unchanged selected voice master without clipping'
        cues=read(prepared['identity']['captionTiming']['path'])['cues'];windows=[]
        for cue in cues:
            a,b=qa.sample_window(cue['start'],cue['spokenEnd'],24000);vl=qa.levels(v[a:b],24000);ml=qa.levels(bgm[a:b],24000);delta=ml['rmsDbfs']-vl['rmsDbfs'];assert delta<=qa.POLICY['musicToVoiceRmsWarningDb'];windows.append(dict(paragraph=cue['paragraph'],clauseIndex=cue['clauseIndex'],voice=vl,music=ml,musicMinusVoiceDb=delta))
        BASE.mkdir(parents=True,exist_ok=True);out=BASE/'final-mix.wav';assert not out.exists();sf.write(out,mixed,24000,subtype='FLOAT');decoded,rate=sf.read(out,dtype='float32',always_2d=True);assert rate==24000 and decoded.shape==(frames,2)
        residual=qa.residual_summary(decoded,bgm+v[:,None]);assert not residual['exceedsKnownStemTolerance']
        # Keep the selected voice master stem intact for codec and local checks.
        stem=BASE/'voice-unmodified.wav';assert not stem.exists();shutil.copyfile(canonical['path'],stem);assert sha(stem)==canonical['sha256']
        bgmfile=BASE/'music-excerpt.wav';sf.write(bgmfile,bgm,24000,subtype='FLOAT')
        build=dict(fingerprint=prepared['fingerprint'],identity=prepared['identity'],voice=pin(stem),mix=pin(out),musicStem=pin(bgmfile),frames=frames,rate=24000,channels=2,durationSeconds=frames/24000,bodyOnly=True,voiceOffsetSamples=0,voiceGain=1,voiceSamplesInserted=0,voiceSamplesTrimmed=0,voiceDsp=False,musicExcerpt=[0,frames/24000],musicGain=.03,musicEndFadeSeconds=.25,knownStemResidual=residual,wordWindows=windows,independentMixedAsrRequired=True,mixedAsrAccepted=False,actualListening=False,humanApproval=False,finalFilmComplete=False)
        save(accepted,build);save(BASE/'status.json',dict(status='audio-mixed-independent-ASR-pending',proof=pin(accepted),modelStarted=False));return dict(started=True,completed=True,proof=pin(accepted),duration=frames/24000)
    finally:
        if owned and native.LEASE.exists()and read(native.LEASE).get('token')==owned:native.LEASE.unlink()
        if worker.handle is not None:worker.close()
def main():
    global P,BASE,PROTOCOL,OWNER
    p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--execute',action='store_true');p.add_argument('--wait-minutes',type=float,default=0);a=p.parse_args();assert 0<=a.wait_minutes<=180;assert a.project in [x['slug']for x in read(HERE/'batch.json')['projects']]and a.project!='shorts-inside-temporal-antialiasing','INSIDE requires its separately paired original-audio mix';P=ROOT/'projects'/a.project;BASE=ROOT/'shared/output/original-tech-twelve-20261115'/P.name/'audio-mix-v10';PROTOCOL='original-tech-twelve-'+P.name+'-audio-mix-v10';OWNER='original-tech-twelve-'+P.name+'-audio-mix';runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER;native.guard.qualifier.BASE=BASE/'resource-observations'
    if a.execute:r=execute(a.wait_minutes)
    else:r=dict(sourceReady=True,fingerprint=prepare()['fingerprint'],guardReason=native.busy(),audioStarted=False)
    print(json.dumps(r),flush=True)
if __name__=='__main__':main()
