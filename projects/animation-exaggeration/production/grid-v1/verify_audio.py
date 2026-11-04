"""A02: current encoded AAC versus PCM, BGM coverage; no listening claim."""
from pathlib import Path
import json
import numpy as np
import soundfile as sf
import audio_pipeline as ap
from storage_paths import HERE as H,LOCAL as L

def db(a):
    return float(20*np.log10(max(1e-12,np.sqrt(np.mean(a.astype('float64')**2)))))

def main():
    edit=L/'edit';build=ap.read(edit/'audio-build.json');plan=ap.read(H/'audio-plan.json')
    aac=edit/'final-mix.m4a';pcm=edit/'final-mix.wav';music_path=edit/'music-stem.wav'
    expected=plan['totalFrames']*800
    known={r['path']:r['sha256'] for r in build['outputs']}
    for p in (aac,pcm,music_path):assert known[ap.relative(p)]==ap.sha(p)
    out=L/'qa/audio-v1';out.mkdir(parents=True,exist_ok=True)
    decoded=out/'encoded-mix.wav';receipt=out/'decode-receipt.json'
    decode_input={'aac':ap.artifact(aac),'settings':'stereo48000pcm_f32le'}
    if decoded.exists():
        cached=ap.read(receipt)
        assert cached['input']==decode_input and cached['decoded']==ap.artifact(decoded)
    else:
        ap.run_ff(['-i',aac,'-vn','-ac',2,'-ar',48000,'-c:a','pcm_f32le',decoded],out/'decode.log')
        ap.save(receipt,{'input':decode_input,'decoded':ap.artifact(decoded),'createdAt':ap.now()})
    rows=[];flags=[]
    with sf.SoundFile(pcm) as f,sf.SoundFile(decoded) as g,sf.SoundFile(music_path) as m:
        assert f.samplerate==g.samplerate==m.samplerate==48000
        assert len(f)==expected and abs(len(g)-expected)<=1024 and len(m)==expected
        decoded_samples=len(g)
        for start in range(0,expected,48000):
            count=min(48000,expected-start)
            a=f.read(count,dtype='float64');b=g.read(count,dtype='float64');music=m.read(count,dtype='float64')
            assert a.shape==b.shape
            corr=float(np.sum(a*b)/max(1e-18,np.sqrt(np.sum(a*a)*np.sum(b*b))))
            row={'startSeconds':start/48000,'pcmDbfs':db(a),'aacDbfs':db(b),'rmsDeltaDb':db(b)-db(a),'correlation':corr,'musicDbfs':db(music)}
            rows.append(row)
            if row['pcmDbfs']>-65 and (corr<.94 or abs(row['rmsDeltaDb'])>1):flags.append(row)
    stats=ap.loudness(aac,out/'loudness.log',-16,-1.5)
    loudness_ok=-17<=float(stats['input_i'])<=-15 and float(stats['input_tp'])<=-1.5
    body=[r for r in rows if 3<=r['startSeconds']<=expected/48000-11]
    music_present=sum(r['musicDbfs']>-70 for r in body)/len(body)
    status='pass' if not flags and loudness_ok and music_present>.98 else 'needs-review'
    ap.save(out/'continuity.json',{'status':status,'scope':'Every encoded second compared with same-position pre-encode PCM; BGM stem measured on body seconds excluding end transitions.','aac':ap.artifact(aac),'pcm':ap.artifact(pcm),'audioBuild':ap.artifact(edit/'audio-build.json'),'decoded':ap.artifact(decoded),'musicStem':ap.artifact(music_path),'expectedPcmSamples':expected,'decodedAacSamples':decoded_samples,'rows':rows,'flags':flags,'loudness':stats,'loudnessWithinTarget':loudness_ok,'bgmActiveBodySecondShare':music_present,'actualListeningPerformed':False,'reviewedAt':ap.now()})
    print(json.dumps({'status':status,'secondsCompared':len(rows),'flags':flags,'lufs':stats['input_i'],'truePeak':stats['input_tp'],'bgmActiveShare':music_present}))

if __name__=='__main__':main()
