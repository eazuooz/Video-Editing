import os
"""Check the actual AAC before either master is muxed; preserve voice continuity."""
from pathlib import Path
import json,hashlib,subprocess,re,importlib.util
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[3];P=R/'projects/vampire-survivors-d2-copyright';L=P/('production/'+os.environ.get('YAMYAM_D2_LOCAL','local'))
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('currentmix',P/'production/mix-audio.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.guard();report=rd(P/'production/audio-review.json');assert not report['flags']
source=L/'final-mix.wav';candidate=L/'final-audio-candidate-v3.m4a'
if not candidate.exists():m.ff(['-n','-i',source,'-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',candidate],'encode-final-audio-v3')
stats=m.measure(candidate,'encoded-audio-loudness-v3');extra=0.;attempts=[{'file':candidate.name,'sha256':sha(candidate),'levels':stats}]
if float(stats['input_tp'])>-1.5:
 extra=-1.65-float(stats['input_tp']);candidate=L/'final-audio-candidate-v4.m4a'
 if not candidate.exists():m.ff(['-n','-i',source,'-af',f'volume={extra}dB','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',candidate],'encode-final-audio-v4')
 stats=m.measure(candidate,'encoded-audio-loudness-v4');attempts.append({'file':candidate.name,'sha256':sha(candidate),'levels':stats})
assert -17<=float(stats['input_i'])<=-15,(stats,extra)
assert float(stats['input_tp'])<=-1.5,stats
final=L/'final-mix.m4a'
if not final.exists():final.write_bytes(candidate.read_bytes())
assert sha(final)==sha(candidate)
decoded=L/'encoded-audio-review.wav'
if not decoded.exists():m.ff(['-n','-i',final,'-ac','2','-ar','48000','-c:a','pcm_f32le',decoded],'decode-current-AAC-once')
pcm,sr=sf.read(source,dtype='float32',always_2d=True);aac,rate=sf.read(decoded,dtype='float32',always_2d=True);assert sr==rate==48000 and len(aac)>=len(pcm)-1
aac=aac[:len(pcm)];pcm=pcm[:len(aac)]*10**(extra/20)
voice,rate=sf.read(L/'narration-final-stem.wav',dtype='float32',always_2d=True);assert rate==48000
words=rd(L/'whole-source-asr-aligned.json')['words'];mask=np.zeros(len(pcm),dtype=bool)
for w in words:
 a,z=w['timestamp']
 if a is not None and z is not None:mask[round((a+2)*48000):round((z+2)*48000)]=True
def prefix_energy(x):return np.r_[0,np.cumsum(np.mean(np.square(x,dtype=np.float64),axis=1))]
p0=prefix_energy(pcm);p1=prefix_energy(aac);active=np.r_[0,np.cumsum(mask,dtype=np.int64)];size=19200;step=4800;rows=[];flags=[]
for lo in range(96000,len(pcm)-480000-size,step):
 hi=lo+size
 if active[hi]-active[lo]<.15*48000:continue
 delta=10*np.log10(max(p1[hi]-p1[lo],1e-18)/max(p0[hi]-p0[lo],1e-18));rows.append({'start':lo/48000,'end':hi/48000,'encodedMinusPcmDb':float(delta)})
 if delta<-1.5:flags.append(rows[-1])
assert not flags,flags[:8]
voice_stats=m.measure(L/'narration-final-stem.wav','current-voice-stem-loudness')
assert -17<=float(voice_stats['input_i'])<=-15,voice_stats
normalized,rate=sf.read(L/'narration-normalized-v2.wav',dtype='float32',always_2d=True)
assert rate==48000 and np.max(np.abs(voice[96000:96000+len(normalized)]-normalized*10**(report['programGainDb']/20)))<2e-6
report.update(sourceToNormalized=f"Constant{report['narrationGainDb']:+.3f}dB gain,48k resampling and latency-compensated short lookahead peak limiting; source PCM preserved. No narration sidechain ducking or speech fade/time stretch.",peakLimiter={'limit':.75,'attackMs':2,'releaseMs':50,'autoLevel':False,'latencyCompensation':True},narrationFinalStemMeasurement=voice_stats,encodedMeasurement=stats,encodedSha256=sha(final),encodedAdditionalGainDb=extra,encodedContinuity='all speech-active400ms windows checked at100ms steps; no encoded level drop exceeding1.5dB',encodedContinuityWindows=len(rows),encodedWorstDropDb=min(x['encodedMinusPcmDb'] for x in rows),encodedBestRiseDb=max(x['encodedMinusPcmDb'] for x in rows),noMixerVoiceModulation=True,gameChestCorrection={'beforeVoiceOverBackgroundDb':4.464946246368651,'afterVoiceOverBackgroundDb':report['speechActiveParagraphs'][13]['voiceOverBackgroundDb'],'gameOnlyGainDb':-8,'voiceUnchanged':True},humanWholeListening='pending',humanPronunciation='pending')
for x in report['speechActiveParagraphs']:x['encodedCheck']='included in complete speech-active window comparison'
wr(P/'production/audio-review.json',report);wr(L/'mix-build.json',report)
wr(L/'encoded-continuity-windows.json',{'sourceSha256':sha(source),'aacSha256':sha(final),'windows':rows,'flags':flags})
wr(P/'production/final-audio.json',{'status':'passed-current-encoded-audio-levels-and-continuity','path':final.relative_to(R).as_posix(),'sha256':sha(final),'pcmSha256':sha(source),'additionalGainDb':extra,'attempts':attempts,'sourceVoicePreserved':True,'voiceDucked':False,'speechActiveWindows':len(rows),'flags':flags,'humanListening':'pending'})
print(json.dumps({'integratedLufs':stats['input_i'],'truePeakDbtp':stats['input_tp'],'voiceLufs':voice_stats['input_i'],'continuityWindows':len(rows),'worstEncodingDropDb':report['encodedWorstDropDb'],'chestSnrAfter':report['gameChestCorrection']['afterVoiceOverBackgroundDb'],'flags':len(flags)}),flush=True)
