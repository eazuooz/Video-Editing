"""Distribute real-footage observation time between spoken lines, preserving samples.

Only insert silence at an observed quiet seam near a sentence boundary. Preserve
the complete original waveform and ASR, with explicit time mapping for both SRTs.
Never freeze, repeat or slow gameplay. Long slots require more narration instead.
"""
import math,hashlib
import numpy as np

def quiet_sentence_seams(audio,sr,cues):
 count=len(cues)-1
 candidates=[];rms=float(np.sqrt(np.mean(audio**2)));window=round(.080*sr)
 for i in range(count):
  intended=(cues[i]['end']+cues[i+1]['start'])/2
  left=max(round((intended-.20)*sr),round((cues[i]['start']+.1)*sr))
  right=min(round((intended+.20)*sr),round((cues[i+1]['end']-.1)*sr),len(audio)-window)
  choices=[]
  for at in range(left,right,round(.005*sr)):
   if at<window:continue
   energy=float(np.sqrt(np.mean(audio[at-window//2:at+window//2]**2)))
   choices.append((energy+abs(at/sr-intended)*rms*.015,energy,at))
  if not choices:continue
  _,energy,at=min(choices)
  if energy>min(.004,rms*.14):continue
  # An80ms quiet window avoids choosing a short intra-word stop consonant.
  # Pick a nearly-zero sample inside that window. No trimming.
  neighborhood=audio[at-round(.004*sr):at+round(.004*sr)]
  at=at-round(.004*sr)+int(np.argmin(np.abs(neighborhood)))
  if at>0 and (not candidates or at>candidates[-1]['rawSample']):candidates.append({'afterLine':i+1,'rawSample':at,'rawAt':at/sr,'seamRms':energy})
 return candidates

def observation_capacity_seconds(audio,sr,cues):
 return len(audio)/sr+.6+6*len(quiet_sentence_seams(audio,sr,cues))

def place_observation_pauses(audio,sr,cues,slot_seconds):
 duration=len(audio)/sr;extra=max(0.,slot_seconds-duration-.6)
 if extra<.35:return audio,[],{'status':'not-needed','rawSamplesPreserved':True}
 candidates=quiet_sentence_seams(audio,sr,cues)
 if len(candidates)<math.ceil(extra/6):raise ValueError('Insufficient quiet sentence seams; inspect audio or add narration, never cut a spoken word.')
 silence_samples=round(extra*sr);pieces=[];kept=[];last=0;remaining=silence_samples
 for j,p in enumerate(candidates):
  count=round(remaining/(len(candidates)-j));remaining-=count
  p['silenceSamples']=count;p['seconds']=count/sr
  segment=audio[last:p['rawSample']];pieces.extend([segment,np.zeros(count,dtype=audio.dtype)]);kept.append(segment);last=p['rawSample']
 pieces.append(audio[last:]);kept.append(audio[last:]);placed=np.concatenate(pieces)
 restored=np.concatenate(kept)
 assert np.array_equal(restored,audio) and len(placed)==len(audio)+silence_samples
 return placed,candidates,{'status':'distributed-at-observed-quiet-sentence-seams','quietWindowMilliseconds':80,'rawSamplesPreserved':True,'rawSampleSha256':hashlib.sha256(audio.tobytes()).hexdigest(),'restoredSampleSha256':hashlib.sha256(restored.tobytes()).hexdigest(),'observationSeconds':silence_samples/sr,'maximumPauseSeconds':max(p['seconds'] for p in candidates),'trailingSeconds':slot_seconds-len(placed)/sr,'sourceSpeed':1,'gameplayFreezeOrLoop':False}

def mapped_time(raw_time,pauses):
 return raw_time+sum(p['seconds'] for p in pauses if p['rawAt']<=raw_time)
