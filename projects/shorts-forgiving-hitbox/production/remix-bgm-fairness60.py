"""BGM-only revision: retain exact speech, timing, captions and encoded video."""
from pathlib import Path
import importlib.util,json,math,sys,shutil
import numpy as np,soundfile as sf
from scipy.signal import stft,find_peaks
s=importlib.util.spec_from_file_location('base',Path(__file__).with_name('finish-fairness60.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
R,P,S=f.R,f.P,f.S;OLD=f.L;L=P/'production/local/fairness-60s-bgm';N=f.N
def check():
 c=f.read(R/'shared/publishing/video-production-control.json')['shortsRecurringAuthorization'];assert c['selectedShort']==S and c['latestSelection']['selectedRevision']=='fairness-60s-bgm'
def audio():
 check();assert not (L/'final-mix.m4a').exists(),'Preserve successful mixes'
 voice=f.pcm(OLD/'narration-stem.wav');effects=f.pcm(OLD/'background-stem.wav');assert len(voice)==len(effects)==N
 music=R/'shared/assets/music/incompetech/Pixel-Peeker-Polka-faster.mp3';assert f.sha(music)=='b2609a077fae292679f25b83519f470ed308abb40d11f89bff8c6f896deefed3'
 song=f.pcm(music)[:61*48000];mono=song.mean(axis=1)
 # Align one real, strong source onset to the existing actual Unity HP decrement.
 freq,t,z=stft(mono,48000,nperseg=1024,noverlap=784,boundary=None)
 spectral=np.abs(z[freq>=180]);flux=np.maximum(np.diff(spectral,axis=1),0).sum(axis=0);times=t[1:];peaks,_=find_peaks(flux,distance=30)
 hit=36.016666666666666;near=[int(i) for i in peaks if hit<=times[i]<=hit+60/144]
 assert near,'No actual rhythmic onset found near hit';onset=max(near,key=lambda i:flux[i]);offset=round((float(times[onset])-hit)*48000)/48000
 start=round(offset*48000);bed=song[start:start+N].copy();assert len(bed)==N
 sf.write(L/'music-excerpt.wav',bed,48000,subtype='FLOAT');meter=f.loud(L/'music-excerpt.wav');musicGain=10**((-29-float(meter['input_i']))/20);bed*=musicGain
 # Narration is never sidechained: only the music gain follows speech.
 block=480;count=N//block;activity=np.array([f.db(voice[i*block:(i+1)*block])>-43 for i in range(count)],float)
 from scipy.ndimage import maximum_filter1d
 activity=maximum_filter1d(activity,size=11,mode='nearest');envelope=np.empty(count);level=0.
 for i,target in enumerate(activity):
  coef=math.exp(-.01/(.03 if target>level else .35));level=coef*level+(1-coef)*target;envelope[i]=level
 duck=10**((-4.5*envelope)/20);control=np.interp(np.arange(N),np.arange(count)*block,duck);bed*=control[:,None]
 dense=np.ones(N);a,b=round(25.8166666667*48000),round(33.0166666667*48000);n=12000;dense[a:a+n]=np.linspace(1,10**(-2/20),n);dense[a+n:b-n]=10**(-2/20);dense[b-n:b]=np.linspace(10**(-2/20),1,n);bed*=dense[:,None]
 n=3840;bed[:n]*=np.linspace(0,1,n)[:,None];n=21600;bed[-n:]*=np.linspace(1,0,n)[:,None]
 # Preserve voice/effect PCM even when more headroom is needed; lower music only.
 attenuation=1.
 for _ in range(30):
  mix=voice+effects+bed*attenuation
  if abs(mix).max()<=.80:break
  attenuation*=.94
 else:raise RuntimeError('Music cannot fit without changing approved voice')
 bed*=attenuation;mix=voice+effects+bed;assert np.isfinite(mix).all();assert np.max(abs((mix-bed-effects)-voice))<2e-7
 sf.write(L/'music-stem.wav',bed,48000,subtype='FLOAT');sf.write(L/'final-mix.wav',mix,48000,subtype='FLOAT')
 f.run([f.FF,'-v','warning','-n','-i',str(L/'final-mix.wav'),'-t','60','-c:a','aac','-b:a','192k',str(L/'final-mix.m4a')]);meter=f.loud(L/'final-mix.m4a');assert float(meter['input_tp'])<=-1.5,meter
 f.save(L/'audio-build.json',dict(kind='BGM-only revision',seconds=60,narrationStem=str((OLD/'narration-stem.wav').relative_to(R)),narrationSha256=f.sha(OLD/'narration-stem.wav'),narrationPcmUnchanged=True,noSpeechRetiming=True,noSpeechFades=True,priorMix=f.sha(OLD/'final-mix.m4a'),musicFile=str(music.relative_to(R)),musicSha256=f.sha(music),licenseRecord='shared/assets/music/incompetech/Pixel-Peeker-Polka-faster.LICENSE.md',musicStartSeconds=offset,musicDurationSeconds=60,musicTargetBeforeDuckLufs=-29,voiceDuckDb=4.5,denseCodeMusicReductionDb=2,attackSeconds=.03,releaseSeconds=.35,musicOnlyHeadroomAttenuationDb=20*math.log10(attenuation),musicFadesSeconds=[.08,.45],sourceOnsetSeconds=float(times[onset]),existingActualHitSeconds=hit,onsetAlignmentErrorSeconds=float(times[onset])-offset-hit,addedMusicStem=f.sha(L/'music-stem.wav'),finalMixSha256=f.sha(L/'final-mix.m4a'),finalMeasured=meter,humanListening='pending'));print(json.dumps(meter))
def pair():
 check();assert (L/'final-mix.m4a').exists()
 for kind in ['clean','captioned']:
  f.run([f.FF,'-v','warning','-n','-i',str(OLD/f'{S}.{kind}.mp4'),'-i',str(L/'final-mix.m4a'),'-map','0:v:0','-map','1:a:0','-t','60','-c','copy','-movflags','+faststart',str(L/f'{S}.{kind}.mp4')])
 for lang in ['ko','en']:shutil.copy2(OLD/f'captions.{lang}.srt',L/f'captions.{lang}.srt')
 f.save(L/'pair-build.json',dict(cleanSha256=f.sha(L/f'{S}.clean.mp4'),captionedSha256=f.sha(L/f'{S}.captioned.mp4'),mixSha256=f.sha(L/'final-mix.m4a'),frames=3600,seconds=60,videoReencoded=False,captionsRetimed=False));print('Existing encoded videos copied with new BGM mix')
def packets(p,kind):
 return json.loads(f.run([f.FP,'-v','error','-select_streams',kind,'-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(p)]).stdout)['packets']
def qa():
 q=L/'qa';q.mkdir(exist_ok=True);assert not (q/'technical.json').exists(),'Reuse successful integrity result'
 entries={}
 for kind in ['clean','captioned']:
  v=L/f'{S}.{kind}.mp4';old=OLD/f'{S}.{kind}.mp4';meta=json.loads(f.run([f.FP,'-v','error','-show_streams','-of','json',str(v)]).stdout);vs=next(x for x in meta['streams'] if x['codec_type']=='video');assert(vs['width'],vs['height'],vs['r_frame_rate'],int(vs['nb_frames']))==(1080,1920,'60/1',3600);assert float(vs['duration'])==60
  vp=packets(v,'v:0');assert vp==packets(old,'v:0');ap=packets(v,'a:0');assert ap==packets(L/'final-mix.m4a','a:0')
  h=q/f'{kind}.framehash';d=q/f'{kind}-decoded.wav';f.run([f.FF,'-v','error','-n','-i',str(v),'-map','0:v:0','-f','framehash',str(h),'-map','0:a:0','-c:a','pcm_f32le',str(d)])
  lines=[x for x in h.read_text().splitlines() if not x.startswith('#')];assert len(lines)==3600 and [int(x.split(',')[2]) for x in lines]==list(range(3600));original=OLD/'qa/2ddb4aa29c53d849'/f'{kind}.framehash';assert lines==[x for x in original.read_text().splitlines() if not x.startswith('#')]
  entries[kind]=dict(sha256=f.sha(v),videoPacketsIdenticalToPrevious=True,decodedFramesIdenticalToPrevious=True,frames=3600,fullDecode=True,uniformPts=True,aacPayloadMatchesAsrMix=True)
 stem=f.pcm(OLD/'narration-stem.wav');music=f.pcm(L/'music-stem.wav');effects=f.pcm(OLD/'background-stem.wav');decoded=f.pcm(q/'captioned-decoded.wav');assert N<=len(decoded)<=N+1024;decoded=decoded[:N];rows=[];flags=[]
 for i in range(0,N-19200,4800):
  voice=stem[i:i+19200];level=f.db(voice)
  if level<-45:continue
  recovered=decoded[i:i+19200]-music[i:i+19200]-effects[i:i+19200];gain=float(np.sum(voice*recovered)/max(np.sum(voice*voice),1e-12));change=20*math.log10(max(gain,1e-9));row=dict(start=i/48000,stemDbfs=level,musicDbfs=f.db(music[i:i+19200]),encodedSpeechTransferDb=change);rows.append(row)
  if change<-3:flags.append(row)
 sustained=[a for a,b in zip(flags,flags[1:]) if b['start']-a['start']<.101];assert not sustained,sustained
 for lang in ['ko','en']:assert f.sha(OLD/f'captions.{lang}.srt')==f.sha(L/f'captions.{lang}.srt')
 f.save(q/'audio-continuity.json',dict(narrationPcmUnchanged=True,windowSeconds=.4,stepSeconds=.1,speechAttenuationFlags=sustained,windows=rows,voiceProcessingEvidenceReused='../fairness-60s/qa/2ddb4aa29c53d849/source-stem-final-levels.json',humanListening='pending'))
 f.save(q/'technical.json',dict(status='technical pass; new full-mix ASR and Drive review recorded separately',seconds=60,format=[1080,1920,60],files=entries,visualAndCaptionEvidenceReused='production/local/fairness-60s/qa/2ddb4aa29c53d849/technical.json',visualReuseReason='All3600 decoded frames and compressed packet payloads are identical; SRT hashes unchanged',speechAttenuationFlags=len(sustained),humanWholeListening='pending'));print('Full integrity and unchanged visual/caption evidence passed')
if __name__=='__main__':globals()[sys.argv[1]]()
