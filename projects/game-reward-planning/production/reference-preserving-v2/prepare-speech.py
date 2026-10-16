"""Preserve source PCM; correct slow gain drift using speech-timed evidence.

This does not approve pronunciation/listening. All hashes and local levels are
recorded for comparison with the final mix. No syllables or pauses are cut.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import soundfile as sf
from scipy.ndimage import gaussian_filter1d

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'shared/output/narration/game-reward-planning/reference-preserving-v2'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def speech_windows(samples,rate,words):
    size=round(rate*.4);hop=round(rate*.1)
    pos=np.arange(0,len(samples)-size+1,hop);times=(pos+size/2)/rate
    energy=np.concatenate(([0.],np.cumsum(samples.astype(np.float64)**2)))
    db=10*np.log10(np.maximum((energy[pos+size]-energy[pos])/size,1e-14))
    # Timestamp-derived speech coverage, not an amplitude-based silence gate:
    # quiet but recognized syllables remain in the analysis.
    mask=np.zeros(len(samples),dtype=bool)
    for w in words:
        a,b=w['timestamp']
        if a is None or b is None:continue
        mask[max(0,round((a-.08)*rate)):min(len(mask),round((b+.08)*rate))]=True
    covered=np.concatenate(([0],np.cumsum(mask,dtype=np.int64)))
    active=(covered[pos+size]-covered[pos])>=size*.3
    return times,db,active

def process(scene):
    source=BASE/'chunks'/f'{scene}-scene.wav';asr=BASE/'asr'/f'{scene}.json'
    data=json.loads(asr.read_text(encoding='utf8'));digest=sha(source)
    if data['audio_sha256']!=digest:raise RuntimeError(f'Stale speech timing: {scene}')
    a,sr=sf.read(source,dtype='float32');assert a.ndim==1
    times,db,active=speech_windows(a,sr,data['words'])
    # Robust5-second estimate follows a gradual paragraph-level fall rather
    # than levelling the loudness of each individual syllable.
    reference=np.empty(len(times))
    for j,t in enumerate(times):
        use=(abs(times-t)<=2.5)&active
        reference[j]=np.percentile(db[use],70) if np.any(use) else np.percentile(db[active],70)
    gain=np.clip(-22-reference,-6,16)
    gain=gaussian_filter1d(gain,15,mode='nearest') #1.5s smoothing at100ms hop
    # Keep changes slower than0.9dB/s; preserve local accents and end decay.
    for j in range(1,len(gain)):gain[j]=np.clip(gain[j],gain[j-1]-.09,gain[j-1]+.09)
    for j in range(len(gain)-2,-1,-1):gain[j]=np.clip(gain[j],gain[j+1]-.09,gain[j+1]+.09)
    last=max(float(w['timestamp'][1] or 0) for w in data['words'])
    if np.any(times>=last):gain[times>=last]=np.interp(last,times,gain)
    sample_gain=np.interp(np.arange(len(a))/sr,times,gain)
    leveled=a*np.power(10,sample_gain/20)
    out=BASE/'leveled';out.mkdir(exist_ok=True)
    destination=out/f'{scene}-float.wav'
    sf.write(destination,leveled,sr,subtype='FLOAT')
    _,after,_=speech_windows(leveled,sr,data['words'])
    windows=[]
    for start in np.arange(0,len(a)/sr,3):
        use=active&(times>=start)&(times<start+3)
        if not np.any(use):continue
        windows.append({'start':round(float(start),3),'end':round(min(float(start+3),len(a)/sr),3),'sourceSpeechMedianDbfs':round(float(np.median(db[use])),2),'leveledSpeechMedianDbfs':round(float(np.median(after[use])),2),'medianGainDb':round(float(np.median(gain[use])),2)})
    report={'scene':scene,'source':str(source.relative_to(ROOT)),'sourceSha256':digest,'output':str(destination.relative_to(ROOT)),'outputSha256':sha(destination),'sampleRate':sr,'samples':len(a),'duration':len(a)/sr,'sourcePcmUnchanged':sha(source)==digest,'outputStage':'float intermediate; final compressor/normalization/peak protection still required','method':'400ms RMS/100ms hop, ASR speech mask, local5s70th percentile,1.5s smooth,0.9dB/s limit; -22dBFS reference; gain[-6,+16]dB','gainDbRange':[float(gain.min()),float(gain.max())],'sourcePeakDbfs':float(20*np.log10(max(abs(a).max(),1e-12))),'leveledPeakDbfs':float(20*np.log10(max(abs(leveled).max(),1e-12))),'windows':windows,'contextualListening':'pending; measurements do not claim listening or final approval'}
    (out/f'{scene}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'scene':scene,'gainDbRange':report['gainDbRange'],'first':windows[0],'last':windows[-1]}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scenes',required=True);args=p.parse_args()
    for s in args.scenes.split(','):process(s.zfill(2))
