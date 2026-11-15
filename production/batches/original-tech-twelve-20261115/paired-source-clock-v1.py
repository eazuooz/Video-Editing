"""Extract original game sound on the same source clock as the real video cuts."""
import math
import av,numpy as np
def extract(audio_path,start_sample,end_sample,rate=24000):
 assert 0<=start_sample<end_sample;out=np.zeros((end_sample-start_sample,2),dtype=np.float32);covered=np.zeros(len(out),dtype=bool);resampler=av.AudioResampler(format='fltp',layout='stereo',rate=rate)
 with av.open(str(audio_path))as c:
  st=c.streams.audio[0];assert st.start_time==0
  # Decode from the shared zero origin. Seeking into44.1k AAC resets the
  # resampler phase and can produce different fractional-sample waveforms.
  # Streaming up to the selected end keeps one global24k sample grid.
  for frame in c.decode(st):
   for f in resampler.resample(frame):
    assert f.time is not None;at=round(f.time*rate);data=f.to_ndarray().T.copy();lo=max(at,start_sample);hi=min(at+len(data),end_sample)
    if lo<hi:out[lo-start_sample:hi-start_sample]=data[lo-at:hi-at];covered[lo-start_sample:hi-start_sample]=True
   if covered.all():break
 assert covered.all(),'Incomplete original audio source interval; never fill it with silence'
 assert np.isfinite(out).all();return out
def paired_stem(plan,cues,frames,clock):
 beats=[]
 for p in plan['paragraphs']:
  for b in p['beats']:
   cue=next(c for c in cues if c['paragraph']==p['id']and c['clauseIndex']==b['firstClauseIndex']);beats.append(dict(b,start=cue['start']))
 stem=np.zeros((frames,2),dtype=np.float32);mapping=[]
 for i,b in enumerate(beats):
  if b['kind']!='game':continue
  assert b['source']==clock['video']and b['sourceSpeed']==1 and b['sourceAudio']=='paired-original'
  first=math.ceil(b['start']*60-1e-8);next_frame=math.ceil(beats[i+1]['start']*60-1e-8)if i+1<len(beats)else math.ceil(frames/24000*60);lo=first*400;hi=min(frames,next_frame*400);assert lo<hi
  source=round((b['sourceStartSeconds']+first/60-b['start'])*24000);data=extract(clock['audio']['path'],source,source+hi-lo);stem[lo:hi]=data
  mapping.append(dict(outputSampleRange=[lo,hi],sourceSampleRange=[source,source+hi-lo],rate=24000,videoFirstFrame=first,videoSourceSeconds=b['sourceStartSeconds']+first/60-b['start'],audioSourceSeconds=source/24000,clockDifferenceSamples=abs(source-(b['sourceStartSeconds']+first/60-b['start'])*24000)))
 assert mapping and all(x['clockDifferenceSamples']<=.500001 for x in mapping);return stem,mapping
