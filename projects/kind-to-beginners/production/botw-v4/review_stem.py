"""Measure identical speech samples in source and mastered narration, once."""
import json,math,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import soundfile as sf
from storage_paths import HERE,LOCAL,repo_path,relative
from audio_pipeline import mask_words
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def db(a):return float(20*np.log10(max(1e-12,np.sqrt(np.mean(a.astype('float64')**2)))))
def main():
 build=read(LOCAL/'edit/audio-build.json');stem,rate=sf.read(LOCAL/'edit/narration-stem.wav',always_2d=True,dtype='float32');assert rate==48000
 rows=[];flags=[]
 for scene in build['scenes']:
  source=LOCAL/f"voice/chunks/{scene['scene']}-scene.wav";a,rs=sf.read(source,dtype='float32');assert rs==rate and sha(source)==scene['sourceSha256']
  recognition=read(LOCAL/f"voice/asr/{scene['scene']}.json");mask=mask_words(len(a),rate,recognition['words'])
  offset=scene['voiceStartSample'];b=stem[offset:offset+len(a),0];assert len(a)==len(b)
  gain=scene['fixedGainDb']+build['globalGainDb'];expected=a*10**(gain/20)
  for start in range(0,len(a),rate//2):
   end=min(len(a),start+rate);active=mask[start:end]
   if active.sum()<rate//4:continue
   x=expected[start:end][active];y=b[start:end][active]
   correlation=float(np.dot(x.astype('float64'),y)/(max(1e-18,np.sqrt(np.sum(x.astype('float64')**2)*np.sum(y.astype('float64')**2)))))
   delta=db(y)-db(x)
   row={'scene':scene['scene'],'sceneLocalStart':start/rate,'timelineStart':(offset+start)/rate,'speechActiveSamples':int(active.sum()),
        'expectedAfterConstantGainDbfs':db(x),'actualMatchedStemDbfs':db(y),'differenceDb':delta,'correlation':correlation,
        'expectedPeakDbfs':float(20*np.log10(max(1e-12,np.max(np.abs(x))))),'stemPeakDbfs':float(20*np.log10(max(1e-12,np.max(np.abs(y)))))}
   rows.append(row)
   if delta < -3.0 or delta>.2 or correlation<.95:flags.append(row)
 record={'status':'needs-contextual-review'if flags else'passed-source-to-stem','scope':'All overlapping one-second speech-active windows at0.5s stride; identical ASR word masks in preserved source and current mastered stem.',
         'audioBuildSha256':sha(LOCAL/'edit/audio-build.json'),'records':rows,'remainingFlags':flags,'wholeWindowDiagnosticCount':len(build['diagnosticContinuityFlags']),
         'finalEncodedMixContinuity':'Separate verify_audio.py after final encoding','humanListening':'pending','reviewedAt':datetime.now(timezone.utc).isoformat()}
 (HERE/'source-stem-continuity-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
 print(json.dumps({'status':record['status'],'speechWindows':len(rows),'flagCount':len(flags),'flags':flags},ensure_ascii=False))
if __name__=='__main__':main()
