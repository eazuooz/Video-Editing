"""Independent CPU readback of the actual pre-limiter fixed-gain waveform.

No media/model/codec output. Compare every retained resampled source sample
against the original current PCM, clip-gain map and exact placement segments.
The nonlinear transient safety stage is recorded and tested separately.
"""
from pathlib import Path
import hashlib,importlib.util,json
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v6_fixed_gain_audio',H/'audio-prepare.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
R,P,O,A=a.R,a.P,a.O,a.A
def main():
 a.selected();timeline=a.read(H/'timeline.json');preparation=a.read(A/'audio-build.json');by={s['scene']:s for s in preparation['scenes']}
 assert preparation['inputs']['timelineSha256']==a.sha(H/'timeline.json')
 fixed=A/'narration-fixed-gain-48k.wav';assert any(x['file']==a.rel(fixed) and x['sha256']==a.sha(fixed) for x in preparation['outputs'])
 rows=[];maximum=0.;count=0
 with sf.SoundFile(fixed) as f:
  assert f.samplerate==48000 and f.channels==2 and f.frames==timeline['totalFrames']*800
  for scene in timeline['scenes']:
   raw=R/scene['rawVoiceFile'];assert a.sha(raw)==scene['rawVoiceSha256'];source,rate=sf.read(raw,dtype='int16');assert rate==24000
   resampled=resample_poly(source.astype(np.float32)/32768.,2,1);expected=resampled*a.g.curve(by[scene['id']]['clipGainPlan'],len(resampled),48000)
   local_maximum=0.;compared=0;last=0
   for segment in scene['voiceSegments']:
    lo,hi,destination=[segment[k]*2 for k in ['sourceSampleStart','sourceSampleEnd','destinationSampleStart']]
    assert lo==last;f.seek(scene['startFrame']*800+destination);actual=f.read(hi-lo,dtype='float32',always_2d=True)
    assert actual.shape==(hi-lo,2)
    local_maximum=max(local_maximum,float(np.max(np.abs(actual-expected[lo:hi,None]))));compared+=hi-lo;last=hi
   assert compared==len(expected) and last==len(expected) and local_maximum<2e-6
   maximum=max(maximum,local_maximum);count+=compared
   rows.append(dict(id=scene['id'],sourceSha256=scene['rawVoiceSha256'],resampledSourceSamplesCompared=compared,maximumAbsoluteError=local_maximum,everySelectedSourceSampleOnceInOrder=True))
 report=dict(schemaVersion=1,revision='article-flow-v6',scope='Independent actual pre-limiter readback; resample the whole current scene once then apply documented group gain curve, compare every placed source sample.',
  inputs=dict(timelineSha256=a.sha(H/'timeline.json'),preparationSha256=a.sha(A/'audio-build.json'),fixedGainFileSha256=a.sha(fixed),implementationSha256=a.sha(Path(__file__))),
  sceneCount=41,resampledSourceSamplesCompared=count,scenes=rows,maximumAbsoluteError=maximum,everySelectedSourceSampleOnceInOrder=True,
  status='numeric-pre-limiter-source-equivalence-complete',limiterProof='Separate preparation.transientLimiter and limiter-stage.json; no claim of nonlinear stage equality to an unprocessed source.',humanWholeListening='pending')
 a.save(A/'source-fixed-gain-equivalence.json',report);print('Actual fixed-gain source equivalence:',count,'samples; max error',maximum)
if __name__=='__main__':main()
