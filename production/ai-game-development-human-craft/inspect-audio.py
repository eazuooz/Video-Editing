"""Aligned source/stem/encoded-mix level evidence. Does not invent listening QA."""
from pathlib import Path
import json, hashlib, subprocess, argparse, sys
import numpy as np
import soundfile as sf
from scipy.ndimage import median_filter
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
from revision_paths import workroot
OUT=workroot(ROOT)/'audio';RATE=24000;STEP=2400;WIN=9600
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(p):
 # Explicit arithmetic stereo average avoids FFmpeg's default equal-power
 # downmix adding3dB relative to the original mono narration stem.
 r=subprocess.run(['ffmpeg','-v','error','-i',str(p),'-af','pan=mono|c0=0.5*c0+0.5*c1','-ar',str(RATE),'-f','f32le','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 return np.frombuffer(r.stdout,np.float32)
def rolling(x,starts):
 sums=np.r_[0,np.cumsum(x.astype(np.float64)**2)]
 return np.maximum((sums[starts+WIN]-sums[starts])/WIN,1e-12)
def groups(mask):
 ids=np.flatnonzero(mask)
 if not len(ids):return []
 return np.split(ids,np.where(np.diff(ids)>1)[0]+1)

p=argparse.ArgumentParser();p.add_argument('--mix-only',action='store_true');args=p.parse_args()
m=read(ROOT/f'projects/{SLUG}/project.json');report=read(OUT/'mix-report.json')
prior=OUT/'level-continuity.json';integrityFile=OUT.parent/'encoded-integrity.json'
if not args.mix_only and prior.exists() and integrityFile.exists():
 previous=read(prior);integrity=read(integrityFile)
 sourcePath=ROOT/m['tts']['outputDir']/(m['tts']['filenameStem']+'.wav')
 if (previous['finalSha256']==sha(OUT/'mix.m4a') and previous['sourceSha256']==sha(sourcePath)
     and previous['stemSha256']==sha(OUT/'narration-stem.wav') and integrity['identicalAAC']
     and all(r['fullAudioDecode']=='pass' and r['sha256']==sha(ROOT/r['path']) for r in integrity['outputs'])):
  previous['encodedAudioEquivalence']={'method':'Complete AAC packet identity against measured mix, full audio decode, current master SHA verification','outputs':[{'path':r['path'],'sha256':r['sha256'],'aacAdtsSha256':r['aacAdtsSha256']} for r in integrity['outputs']]}
  previous['encodedScope']='Measured AAC mix retained bit-identically in current clean and captioned masters'
  prior.write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print('Reused identical complete aligned audio evidence; current output integrity independently passed.')
  sys.exit(0)
stem,rate=sf.read(OUT/'narration-stem.wav',dtype='float32');assert rate==RATE
final=OUT/'mix.m4a' if args.mix_only else ROOT/m['paths']['videoClean'];assert final.exists(),'Analyze the actual encoded audio'
audio=decode(final);n=min(len(audio),len(stem));audio=audio[:n];stem=stem[:n]
tts=ROOT/m['tts']['outputDir'];name=m['tts']['filenameStem']
original,sr=sf.read(tts/(name+'.wav'),dtype='float32');assert sr==RATE
source=np.zeros(n,np.float32);source[48000:48000+len(original)]=original[:n-48000]
starts=np.arange(0,n-WIN+1,STEP);centers=(starts+WIN/2)/RATE
srcpower=rolling(source,starts);stempower=rolling(stem,starts);mixpower=rolling(audio,starts)
cross=np.r_[0,np.cumsum((stem.astype(np.float64)*audio))]
beta=((cross[starts+WIN]-cross[starts])/WIN)/stempower
voice_transfer=20*np.log10(np.maximum(beta,1e-8))
srcdb=10*np.log10(srcpower);stemdb=10*np.log10(stempower)
words=read(tts/(name+'.asr-review.timestamps.json'))['chunks']
speech=np.zeros(len(centers),bool)
for w in words:
 a,b=w['timestamp'];speech|=(centers>=a+2)&(centers<=b+2)
nearby=median_filter(srcdb,size=31,mode='nearest')
flags=[]
for g in groups(speech&((nearby-srcdb)>=6)):
 if len(g)*.1<.5:continue
 a=max(0,float(centers[g[0]]-.2));b=float(centers[g[-1]]+.2)
 text=''.join(w['text'] for w in words if w['timestamp'][1]+2>=a-2 and w['timestamp'][0]+2<=b+2)
 flags.append({'start':a,'end':b,'maxDropDb':float(np.max(nearby[g]-srcdb[g])),
               'sourceToStemGainRangeDb':[float(np.min(stemdb[g]-srcdb[g])),float(np.max(stemdb[g]-srcdb[g]))],
               'mixVoiceTransferMedianDb':float(np.median(voice_transfer[g])),
               'context':text,'listening':'pending','resolution':'pending-contextual-listening'})
paragraphs=[]
for para in report['paragraphGains']:
 mask=speech&(centers>=para['start']+2)&(centers<para['end']+2)
 paragraphs.append(dict(para,sourceMedianDbfs=float(np.median(srcdb[mask])),stemMedianDbfs=float(np.median(stemdb[mask])),encodedVoiceTransferDb=float(np.median(voice_transfer[mask]))))
joins=[]
for prev,now in zip(paragraphs,paragraphs[1:]):
 delta=now['stemMedianDbfs']-prev['stemMedianDbfs']
 joins.append({'scene':now['scene'],'paragraph':now['paragraph'],'kind':'scene' if prev['scene']!=now['scene'] else 'paragraph','seconds':2+now['start'],'sourceDifferenceDb':now['sourceMedianDbfs']-prev['sourceMedianDbfs'],'stemDifferenceDb':delta,'flag':abs(delta)>=3})
decay=[]
for scene in report['sceneMeasurements']:
 rows=[p for p in paragraphs if p['scene']==scene['scene']]
 decay.append({'scene':scene['scene'],'sourceLastMinusFirstDb':rows[-1]['sourceMedianDbfs']-rows[0]['sourceMedianDbfs'],'stemLastMinusFirstDb':rows[-1]['stemMedianDbfs']-rows[0]['stemMedianDbfs']})
attenuation=[]
for g in groups(speech&(voice_transfer<-1.0)):
 if len(g)*.1>=.5:attenuation.append({'start':float(centers[g[0]]),'end':float(centers[g[-1]]),'medianDb':float(np.median(voice_transfer[g]))})
result={'method':'400ms RMS windows,100ms hop; ASR word-time speech mask; matched stem projection in encoded mix',
 'sourceSha256':sha(tts/(name+'.wav')),'stemSha256':sha(OUT/'narration-stem.wav'),'finalSha256':sha(final),
 'windowSeconds':.4,'hopSeconds':.1,'scope':'complete speech plus every scene join',
 'sourceLowLevelFlags':flags,'paragraphMeasurements':paragraphs,'paragraphAndSceneJoins':joins,'withinTakeDecayBeforeAfter':decay,'encodedVoiceAttenuationFlags':attenuation,
 'speechWindows':int(speech.sum()),'voiceTransferMedianDb':float(np.median(voice_transfer[speech])),
 'processingAttenuationStatus':'pass' if not attenuation and not any(j['flag'] for j in joins) else 'fail',
 'sourceProsodyListening':'pending' if flags else 'no-threshold-flags; full-listening-pending',
 'fullHumanListening':'pending','encodedScope':'reviewed AAC mix before video mux' if args.mix_only else 'actual encoded video master'}
(OUT/'level-continuity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
np.savez_compressed(OUT/'level-windows.npz',seconds=centers,sourceDbfs=srcdb,stemDbfs=stemdb,mixDbfs=10*np.log10(mixpower),voiceTransferDb=voice_transfer,speech=speech)
print(json.dumps({'sourceFlags':len(flags),'processingAttenuation':result['processingAttenuationStatus'],'humanListening':'pending'}))
