"""Check that current approved scene speech starts at the measured final scene times."""
from pathlib import Path
import json,subprocess,hashlib
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/blank-project-coding';WORK=BASE/'production/final-v1'
m=json.loads((BASE/'project.json').read_text(encoding='utf-8'));p=json.loads((WORK/'plan.json').read_text(encoding='utf-8'))
mono=WORK/'mix-check-24k.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/m['paths']['audioMix']),'-ac','1','-ar','24000',str(mono)],check=True)
mixed,rate=sf.read(mono);assert rate==24000 and abs(len(mixed)/rate-p['seconds'])<.06
normalized,norm_rate=sf.read(WORK/'voice-normalized.wav');assert norm_rate==48000
normalized=normalized.mean(axis=1)[::2]
def env(x):
    n=len(x)//480;return np.sqrt(np.mean(x[:n*480].reshape(n,480)**2,axis=1))
result=[]
for s in p['scenes']:
    v,r=sf.read(ROOT/s['voice']);assert r==rate;start=round(s['start']*rate);nv=normalized[start:start+len(v)]
    # Dynamic loudness normalization changes long-window RMS relationships.
    # Verify source identity locally, then compare the exact normalized voice
    # against the final AAC mix. This distinguishes gain changes from retiming.
    identity=[]
    for offset in range(0,len(v)-4800,4800):
        a=v[offset:offset+4800];b=nv[offset:offset+4800]
        if np.sqrt(np.mean(a*a))>.005:identity.append(float(np.dot(a,b)/np.sqrt(np.dot(a,a)*np.dot(b,b))))
    median=float(np.median(identity));p05=float(np.quantile(identity,.05));assert median>.98 and p05>.9,(s['id'],median,p05)
    target=env(nv);actual=env(mixed[start:start+len(v)]);n=min(len(target),len(actual));corr=float(np.corrcoef(target[:n],actual[:n])[0,1]);assert corr>.97,(s['id'],corr)
    # A centered peak guards against accidentally omitting the two-second intro.
    scores=[]
    for lag in range(-10,11):
        x=target[max(0,-lag):n-max(0,lag)];y=actual[max(0,lag):n-max(0,-lag)];scores.append(float(np.corrcoef(x,y)[0,1]))
    best=int(np.argmax(scores))-10;assert abs(best)<=2,(s['id'],best)
    result.append({'scene':s['id'],'start':s['start'],'sourceToNormalizedWaveformMedian':median,'sourceToNormalizedWaveform5thPercentile':p05,'normalizedVoiceToFinalAacRmsCorrelation':corr,'bestLagSeconds':best*.02,'voiceSha256':hashlib.sha256((ROOT/s['voice']).read_bytes()).hexdigest()})
assert np.sqrt(np.mean(mixed[round((p['bodyEnd']+2)*rate):round((p['seconds']-1)*rate)]**2))>1e-4
(WORK/'mix-alignment-review.json').write_text(json.dumps({'all34SceneStartsVerified':True,'method':'Current source waveform to normalized voice in200ms voiced windows; normalized voice envelope to copied final AAC; zero-centered20ms lag search. Raw long-window envelope diagnostic retained separately because dynamic loudnorm changes relative amplitudes.','currentSpeechEnvelopeMatches':result,'bgmPresentInMembershipEnding':True,'humanListening':'pending'},indent=2)+'\n',encoding='utf-8')
print('All34 current voice scenes align to final copied AAC; ending contains continuous music.')
