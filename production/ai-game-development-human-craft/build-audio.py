"""One selected-video mix. Original Qwen PCM is immutable.

Phrase gain corrects measured within-take decay. A short lookahead peak guard
protects rare peaks without lowering the entire take. Background alone ducks.
Writes source/stem/mix measurements without claiming that listening occurred.
"""
from pathlib import Path
import json, hashlib, subprocess, re, math
import numpy as np
import soundfile as sf
from scipy.ndimage import gaussian_filter1d, maximum_filter1d
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
from revision_paths import workroot
OUT=workroot(ROOT)/'audio';OUT.mkdir(parents=True,exist_ok=True)
RATE=24000;HOP=.1;WINDOW=.4
FLAGS=subprocess.CREATE_NO_WINDOW
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
    p=subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=FLAGS)
    if p.returncode:raise RuntimeError(p.stderr.decode('utf-8','replace'))
    return p
def levels(p):
    r=run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
    return json.loads(re.findall(r'\{\s*"input_i"[\s\S]+?\}',r.stderr.decode())[-1])
def windows(x):
    x=x.mean(axis=1) if x.ndim==2 else x
    # prefix sums avoid re-reading the same400ms window repeatedly.
    sums=np.r_[0,np.cumsum(x.astype(np.float64)**2)]
    starts=np.arange(0,len(x)-round(WINDOW*RATE)+1,round(HOP*RATE))
    n=round(WINDOW*RATE)
    return starts/RATE+WINDOW/2,10*np.log10(np.maximum((sums[starts+n]-sums[starts])/n,1e-12))

control=read(ROOT/'shared/publishing/video-production-control.json')
assert control['selectedVideo']==SLUG
m=read(ROOT/f'projects/{SLUG}/project.json')
data=read(ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json')
assert data['captionTimingStatus']=='asr-aligned'
tts=ROOT/m['tts']['outputDir'];stem=m['tts']['filenameStem']
source=tts/(stem+'.wav');original,sr=sf.read(source,dtype='float32')
assert sr==RATE and original.ndim==1
assert not (OUT/'mix.m4a').exists(),'Existing mix preserved; version a revised mix explicitly'
timing=read(tts/(stem+'.timing.json'))
asr=read(tts/(stem+'.asr-review.timestamps.json'))
assert asr['audio_sha256']==sha(source)
times,srcdb=windows(original)
speech=np.zeros(len(times),bool)
for w in asr['chunks']:
    a,b=w['timestamp'];speech|=(times>=a)&(times<=b)
assert speech.any()
medians=[];ranges=[]
for s in data['scenes']:
    origin=next(e['start'] for e in timing['entries'] if e['scene_id']==s['id'])
    duration=sf.info(tts/'chunks'/f"{s['id']}-scene.wav").duration
    mask=speech&(times>=origin)&(times<origin+duration)
    medians.append(float(np.median(srcdb[mask])));ranges.append((origin,duration))
reference=float(np.median(medians));voice=original.copy();scene_gains=[]
for s,median,(origin,duration) in zip(data['scenes'],medians,ranges):
    gain=float(np.clip(reference-median,-6,6))
    scene_gains.append({'scene':s['id'],'origin':origin,'duration':duration,'speechMedianDbfs':median,'constantGainDb':gain})
# Source inspection found 10--15dB progressive decay inside several takes.
# Measure each complete spoken paragraph; keep silence and syllabic prosody.
phrase_gains=[];gain_times=[];gain_values=[]
for s in data['scenes']:
 for i,p in enumerate(s['paragraphs']):
    a=s['start']+p['start'];b=s['start']+p['end'];mask=speech&(times>=a)&(times<b)
    measure=float(np.median(srcdb[mask]))
    gain=float(np.clip(-23-measure,-6,18))
    # Constant inside a paragraph with a 300ms transition at a boundary.
    gain_times.extend([a+min(.15,(b-a)/4),b-min(.15,(b-a)/4)])
    gain_values.extend([gain,gain])
    phrase_gains.append({'scene':s['id'],'paragraph':i,'start':a,'end':b,'sourceSpeechMedianDbfs':measure,'gainDb':gain})
envelope=np.interp(np.arange(len(voice))/sr,gain_times,gain_values).astype(np.float32)
voice*=10**(envelope/20);del envelope
sf.write(OUT/'scene-balanced.wav',voice,sr,subtype='FLOAT')
pre=levels(OUT/'scene-balanced.wav')
global_gain=-18-float(pre['input_i'])
voice*=10**(global_gain/20)
# 5ms lookahead, 60ms release. Apply before the unmodified background sum.
# Work at 1ms blocks to retain waveform shape rather than hard clipping.
block=24;count=math.ceil(len(voice)/block)
peaks=np.max(np.abs(np.pad(voice,(0,count*block-len(voice)))).reshape(count,block),axis=1)
ceiling=10**(-2.5/20)
target=np.minimum(1,ceiling/np.maximum(maximum_filter1d(peaks,size=11,mode='nearest'),1e-12))
guard=target.copy();release=math.exp(-.001/.060)
for i in range(1,len(guard)):guard[i]=min(target[i],release*guard[i-1]+(1-release))
guard_samples=np.interp(np.arange(len(voice))/block,np.arange(count),guard).astype(np.float32)
voice*=guard_samples
peak_guard={'lookaheadMs':5,'releaseMs':60,'ceilingDbfs':-2.5,'maximumReductionDb':float(-20*np.log10(max(1e-9,guard.min()))),'fractionOver1dB':float(np.mean(guard<10**(-1/20))),'fractionOver3dB':float(np.mean(guard<10**(-3/20)))}
del guard_samples
body_frames=sum(round(s['duration']*60) for s in data['scenes']);total_frames=body_frames+720
n=round(total_frames/60*sr);pad=round(2*sr)
processed=np.zeros(n,np.float32);processed[pad:pad+len(voice)]=voice[:min(len(voice),n-pad)]
sf.write(OUT/'narration-stem.wav',processed,sr,subtype='PCM_24')
music=ROOT/'shared/assets/music/incompetech/Wholesome.mp3'
assert sha(music)=='9eadc79a1a2cb68cd63be1432ebf8f8ae3387cb9d2e85f9b8dbc74ba5a96b231'
raw=run(['ffmpeg','-v','error','-i',str(music),'-ar',str(sr),'-ac','2','-f','f32le','-']).stdout
track=np.frombuffer(raw,np.float32).reshape(-1,2).copy();music_measure=levels(music)
music_gain=-31-float(music_measure['input_i']);track*=10**(music_gain/20)
bg=np.zeros((n,2),np.float32);fade=sr;step=len(track)-fade
for start in range(0,n,step):
    count=min(len(track),n-start);part=track[:count].copy()
    if start:part[:min(fade,count)]*=np.linspace(0,1,min(fade,count),dtype=np.float32)[:,None]
    if start+len(track)<n:part[-fade:]*=np.linspace(1,0,fade,dtype=np.float32)[:,None]
    bg[start:start+count]+=part
grid=np.arange(math.ceil(n/(sr*.02)))*.02;activity=np.zeros(len(grid),np.float32)
for w in asr['chunks']:
    a,b=w['timestamp'];activity[(grid>=a+2-.1)&(grid<=b+2+.4)]=1
activity=np.clip(gaussian_filter1d(activity,7.5),0,1)
duck=np.interp(np.arange(n)/sr,grid,1-activity*(1-10**(-6/20))).astype(np.float32)
bg*=duck[:,None]
f=round(.45*sr);bg[:f]*=np.linspace(0,1,f,dtype=np.float32)[:,None];bg[-f:]*=np.linspace(1,0,f,dtype=np.float32)[:,None]
del duck
sfx=np.zeros(n,np.float32)
s9=next(s for s in data['scenes'] if s['id']=='09')
chime_at=2+s9['start']+max(0,s9['paragraphs'][5]['end']-20.5)+10+230/60
for frequency,delay in [(523.25,0),(659.25,.10),(783.99,.20)]:
    t=np.arange(round(.4*sr))/sr;tone=(np.sin(2*np.pi*frequency*t)*np.exp(-t*10)*np.minimum(t/.01,1)*10**(-31/20)).astype(np.float32)
    start=round((chime_at+delay)*sr);sfx[start:start+len(tone)]+=tone
mix=bg+processed[:,None]+sfx[:,None]
peak=float(np.max(np.abs(mix)));assert peak<10**(-1.8/20),f'Peak {20*math.log10(peak):.2f}dBFS requires review, not automatic voice limiting'
sf.write(OUT/'background-stem.wav',bg,sr,subtype='PCM_24');sf.write(OUT/'effects-stem.wav',sfx,sr,subtype='PCM_24')
sf.write(OUT/'mix.wav',mix,sr,subtype='PCM_24')
run(['ffmpeg','-v','error','-n','-i',str(OUT/'mix.wav'),'-ar','48000','-ac','2','-c:a','aac','-b:a','192k',str(OUT/'mix.m4a')])
encoded=levels(OUT/'mix.m4a');assert float(encoded['input_tp'])<=-1.5
report={'sourceSha256':sha(source),'completeAsrSha256':sha(tts/(stem+'.asr-review.timestamps.json')),
    'totalFrames':total_frames,'duration':total_frames/60,'sampleRateWorking':sr,
    'sceneMeasurements':scene_gains,'paragraphGains':phrase_gains,'globalConstantGainDb':global_gain,'narrationLoudnessBeforeGlobalGain':pre,'peakGuard':peak_guard,
    'bgmSourceSha256':sha(music),'bgmInitialTargetLufs':-31,'bgmConstantGainDb':music_gain,'voiceDrivenDuckingDb':-6,
    'bgmLoopCrossfadeSeconds':1,'bgmOnlyEdgeFadeSeconds':.45,'chimeSeconds':chime_at,
    'narrationDucking':False,'narrationProcessing':'paragraph-level speech median gain, 300ms joins, short peak guard','sumNormalization':False,'encodedMix':encoded,
    'mixSha256':sha(OUT/'mix.m4a'),'stemSha256':sha(OUT/'narration-stem.wav'),
    'fullListening':'pending','localLevelContinuity':'pending-aligned-source-stem-final-analysis'}
(OUT/'mix-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'duration':total_frames/60,'mixLUFS':encoded['input_i'],'mixTruePeak':encoded['input_tp'],'fullListening':'pending'}))
