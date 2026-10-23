"""Keep recovered samples; match only replacement paragraphs and synchronized game sound."""
from common import *
import numpy as np,soundfile as sf
from scipy.signal import resample_poly
import runpy
_composition=runpy.run_path(str(B/'compose-m15.py'));SOURCES=_composition['SOURCES'];SHOTS=_composition['SHOTS']
P=R/'projects/game-math-rendering-light';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';A=O/'audio';T=read(H/'timeline.json');rate=48000
authorized('M15')
def level(x):
 x=x.mean(1) if x.ndim==2 else x;f=x[:len(x)//2400*2400].reshape(-1,2400);d=20*np.log10(np.maximum(np.sqrt(np.mean(f.astype(float)**2,axis=1)),1e-12));return float(np.median(d[d>d.max()-25]))
def ff(args):subprocess.run(['ffmpeg','-v','error','-nostdin','-y',*map(str,args)],check=True)
def loudness(path,target):
 p=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af',f'loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf8',errors='replace',check=True)
 return json.loads(p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}')+1])
x,sr=sf.read(A/'narration-full.wav',dtype='float32',always_2d=True);assert sr==rate;before=x.copy();levels=[]
for s in T['scenes']:
 for origin in s['audioOrigins']:
  if origin['kind']!='changed-complete-paragraph':continue
  v,rr=sf.read(R/origin['take'],dtype='float32');assert rr==24000
  v=resample_poly(v,2,1);gain=-20.0-level(v);v*=10**(gain/20)
  raw=A/'gain-staging.wav';limited=A/'limited-staging.wav';sf.write(raw,v,rate,subtype='FLOAT')
  # Rare peaks need headroom; only the newly synthesized paragraph is processed.
  ff(['-i',raw,'-af','alimiter=limit=0.76:attack=5:release=80:level=false:latency=true','-c:a','pcm_f32le',limited])
  y,rr=sf.read(limited,dtype='float32');assert rr==rate and len(y)==origin['outputSamples']
  at=round((s['start']+origin['outputStart'])*rate);old=x[at:at+len(y)];x[at:at+len(y)]=y[:,None]
  levels.append(dict(scene=s['id'],line=origin['line'],sourceSha256=sha(R/origin['take']),targetActiveMedianDbfs=-20.0,beforeActiveMedianDbfs=level(old),afterActiveMedianDbfs=level(y),gainBeforePeakControlDb=gain,peak=float(abs(y).max()),samples=len(y),start=at/rate))
assert len(levels)==14
save(H/'replacement-level-continuity.json',dict(paragraphs=levels,method='50ms active median, max-25dB gate; constant gain then peak control on changed paragraphs only',unchangedParagraphsProcessed=False,actualListening=False,reason='Simple peak-capped gain left new paragraphs 3–7dB quieter than the recovered voice; match speech energy without new TTS or changing duration.'))
normalized=A/'narration-matched.wav';sf.write(normalized,x,rate,subtype='FLOAT')
measured=loudness(normalized,-16);narr_gain=-16-float(measured['input_i']);game=np.zeros_like(x);tracks=[]
for sid,s in SHOTS.items():
 slot=next(t for t in T['scenes'] if t['id']==s.get('scene',sid));raw=A/f'game-{sid}.wav';source=R/SOURCES[s['source']].get('audioPath',SOURCES[s['source']]['path'])
 if SOURCES[s['source']].get('sourceSilent'):
  assert not [x for x in probe(source)['streams'] if x['codec_type']=='audio']
  tracks.append(dict(scene=sid,source=rel(source),sourceStart=s['start'],seconds=s['seconds'],sourceSilent=True,reason='Verified source contains no audio stream; no fabricated replacement sound',actualListening=False));continue
 # Decode before sample-accurate trim: AAC input seeking dropped24ms on the second cut.
 ff(['-i',source,'-vn','-af',f'atrim=start={s["start"]}:end={s["start"]+s["seconds"]},asetpts=PTS-STARTPTS','-ar',rate,'-ac','2','-c:a','pcm_f32le',raw])
 m=loudness(raw,-23);gain=-23-float(m['input_i']);g,rr=sf.read(raw,dtype='float32',always_2d=True);count=round(s['seconds']*rate);assert len(g)>=count;g=g[:count]*10**(gain/20)
 # Tiny edge ramps avoid edit clicks without altering the action or speech.
 ramp=min(480,len(g)//2);g[:ramp]*=np.linspace(0,1,ramp)[:,None];g[-ramp:]*=np.linspace(1,0,ramp)[:,None]
 at=round((slot['start']+s.get('offset',0))*rate);game[at:at+count]+=g
 tracks.append(dict(scene=sid,source=rel(source),sourceStart=s['start'],seconds=s['seconds'],timelineStart=slot['start']+s.get('offset',0),sourceLufs=m['input_i'],gainDb=gain,targetLufs=-23,originalMixPreserved=True,separateMusicStemAvailable=False,actualListening=False))
sf.write(A/'game-synchronized.wav',game,rate,subtype='FLOAT')
graph=f'[0:a]volume={narr_gain:.8f}dB,asplit=2[n][key];[1:a][key]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[g];[n][g]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.80:attack=5:release=80:level=false:latency=true[out]'
ff(['-i',normalized,'-i',A/'game-synchronized.wav','-filter_complex',graph,'-map','[out]','-ar',rate,'-c:a','pcm_f32le',A/'mix.wav'])
ff(['-i',A/'mix.wav','-c:a','aac','-b:a','192k','-ar',rate,'-ac','2',A/'mix.m4a'])
final=loudness(A/'mix.m4a',-16);assert float(final['input_tp'])<=-1.5,(final['input_tp'],'encoded AAC peak')
save(H/'audio-mix.json',dict(updatedAt=now(),path=rel(A/'mix.m4a'),sha256=sha(A/'mix.m4a'),narrationGainDb=narr_gain,narrationInput=measured,encodedOutput=final,tracks=tracks,ducking=dict(threshold=.08,ratio=2.2,attackMs=15,releaseMs=280,makeup=1),addedBgm=False,originalGameMusicAndSfxNotSeparated=True,rawRecoveredAacAndNewTakesPreserved=True,unchangedNarrationBeforeGlobalMixPreserved=True,actualListening=False,targetedListeningPending=['BRDF','복사휘도','복사조도','입체각','replacement paragraph joins','game audio balance']))
print('Matched14 paragraphs; mix AAC',final['input_i'],'LUFS',final['input_tp'],'dBTP',flush=True)
