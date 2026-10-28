"""Bounded unprompted recheck of a concrete full-ASR chunk-boundary failure."""
from pathlib import Path
import json
import soundfile as sf
import audio_pipeline as a
def main():
 a.require_authorized('bounded-asr-concrete-failure')
 raw=a.NARRATION/'narration-source.wav';out=a.NARRATION/'bounded-asr-02p01';out.mkdir(exist_ok=True)
 clip=out/'source-42.5-57.4.wav';rate=48000;start,end=42.5,57.4
 data,sr=sf.read(raw,start=round(start*rate),stop=round(end*rate),always_2d=True,dtype='float32');assert sr==rate
 if not clip.exists():sf.write(clip,data,rate,subtype='FLOAT')
 else:
  prior,pr=sf.read(clip,dtype='float32',always_2d=True);assert pr==rate and (prior==data).all()
 a.save(out/'source-window.json',{'source':a.artifact(raw),'clip':a.artifact(clip),'sourceStart':start,'sourceEnd':end,'exactPcmSlice':True,'reason':'Whole unprompted ASR at49.98s emitted consecutive zero-duration repeated red/green fragments and lost expected words. Recheck local context without a prompt before deciding whether speech is faulty.','expectedPrompt':None})
 a.full_asr(clip,out/'asr.json')
 print('Bounded raw ASR saved; no canonical ASR or original PCM overwritten.')
if __name__=='__main__':main()
