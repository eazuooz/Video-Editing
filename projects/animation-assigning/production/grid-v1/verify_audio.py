"""Check every encoded second against the continuous PCM; no listening claim."""
from pathlib import Path
import json,subprocess
import numpy as np
import soundfile as sf
import audio_pipeline as ap
H=Path(__file__).resolve().parent
L=H.parent/'local/grid-v1'

def db(a):return float(20*np.log10(max(1e-12,np.sqrt(np.mean(a.astype('float64')**2)))))

def main():
 edit=L/'edit';build=ap.read(edit/'audio-build.json');plan=ap.read(H/'audio-plan.json')
 aac=edit/'final-mix.m4a';pcm=edit/'final-mix.wav';expected=plan['totalFrames']*800
 known={r['path']:r['sha256'] for r in build['outputs']}
 for p in (aac,pcm):assert known[ap.relative(p)]==ap.sha(p)
 out=L/'qa/final-audio-v1';out.mkdir(parents=True,exist_ok=True)
 decoded=out/'encoded-mix.wav'
 if not decoded.exists():ap.run_ff(['-i',aac,'-vn','-ac',2,'-ar',48000,'-c:a','pcm_f32le',decoded],out/'decode.log')
 rows=[];flags=[]
 with sf.SoundFile(pcm) as f,sf.SoundFile(decoded) as g,sf.SoundFile(edit/'music-stem.wav') as m:
  assert f.samplerate==g.samplerate==m.samplerate==48000
  assert len(f)==expected and abs(len(g)-expected)<=1024
  for start in range(0,expected,48000):
   count=min(48000,expected-start)
   a=f.read(count,dtype='float64');b=g.read(count,dtype='float64');music=m.read(count,dtype='float64')
   assert a.shape==b.shape
   corr=float(np.sum(a*b)/max(1e-18,np.sqrt(np.sum(a*a)*np.sum(b*b))))
   row={'startSeconds':start/48000,'pcmDbfs':db(a),'aacDbfs':db(b),'rmsDeltaDb':db(b)-db(a),'correlation':corr,'musicDbfs':db(music)}
   rows.append(row)
   if row['pcmDbfs']>-65 and (corr<.94 or abs(row['rmsDeltaDb'])>1):flags.append(row)
 stats=ap.loudness(aac,out/'loudness.log',-16,-1.5)
 assert -17<=float(stats['input_i'])<=-15 and float(stats['input_tp'])<=-1.5,stats
 body=[r for r in rows if 3<=r['startSeconds']<=expected/48000-11]
 music_present=sum(r['musicDbfs']>-70 for r in body)/len(body)
 assert music_present>.98
 ap.save(out/'continuity.json',{'status':'pass' if not flags else 'needs-review','aac':ap.artifact(aac),'pcm':ap.artifact(pcm),'audioBuild':ap.artifact(edit/'audio-build.json'),'decoded':ap.artifact(decoded),'rows':rows,'flags':flags,'loudness':stats,'bgmActiveBodySecondShare':music_present,'actualListeningPerformed':False})
 print(json.dumps({'status':'pass' if not flags else 'needs-review','secondsCompared':len(rows),'flags':flags,'lufs':stats['input_i'],'truePeak':stats['input_tp'],'bgmActiveShare':music_present}))

if __name__=='__main__':main()
