"""Measure original→fixed gain→current narration with timestamp-active windows."""
from pathlib import Path
import importlib.util,math
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v7_continuity_prepare',H/'audio-prepare.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);c=a.c
def measure(source,expected,actual,mask,lo,hi):
 lo=max(0,lo);hi=min(len(source),hi);active=mask[lo:hi]
 assert active.sum()>0
 x,y,z=[v[lo:hi][active]for v in [source,expected,actual]]
 sx,sy,sz=[a.db(a.rms(v))for v in [x,y,z]]
 return dict(sourceSpeechDbfs=sx,expectedFixedSpeechDbfs=sy,processedSpeechDbfs=sz,
  measuredEffectiveGainDb=sz-sx,expectedFixedGainDb=sy-sx,transientSafetyChangeDb=sz-sy,speechSamples=int(active.sum()))
def main():
 c.validate(preserve_pcm=True);timeline_file=H/'timeline.json';t=c.read(timeline_file)
 build_file=c.O/'narration-build.json';build=c.read(build_file);alignment=c.read(c.O/'source-alignment.json')
 assert build['inputs']['timelineSha256']==c.sha(timeline_file)
 stem=c.R/build['narrationFile'];assert any(x['sha256']==c.sha(stem)for x in build['outputs'])
 caption_file=c.O.parent/'captions/captions.json';captions=c.read(caption_file);assert captions['inputs']['timelineSha256']==c.sha(timeline_file)
 byid={r['id']:r for r in alignment['scenes']};gains={r['id']:r for r in build['scenes']};rows=[]
 with sf.SoundFile(stem)as audio:
  for scene in t['scenes']:
   sid=scene['id'];raw,rate=sf.read(c.R/scene['rawVoiceFile'],dtype='int16');assert rate==24000
   reference=resample_poly(raw.astype(np.float32)/32768.,2,1);al=byid[sid]
   cached=c.read(c.R/al['asrFile']);assert cached['audio_sha256']==scene['rawVoiceSha256']
   mask=np.repeat(a.speech_mask(len(raw),24000,cached['words']),2)
   expected=reference*a.gain_curve(gains[sid],len(reference))*10**(build['constantGlobalGainDb']/20)
   for refinement in build.get('sentenceGainRefinement',{}).get('refinements',[]):
    if refinement['scene']!=sid:continue
    lo,li,ro,ri=refinement['gainRangeSamples48'];gain=refinement['gainDb']
    expected[lo:li]*=10**(np.linspace(0,gain,li-lo,dtype=np.float32)/20)
    expected[li:ro]*=10**(gain/20)
    expected[ro:ri]*=10**(np.linspace(gain,0,ri-ro,dtype=np.float32)/20)
   audio.seek(scene['startFrame']*800);actual=audio.read(len(reference),dtype='float32',always_2d=True)
   assert actual.shape==(len(reference),2)and np.max(abs(actual[:,0]-actual[:,1]))<1e-7;actual=actual[:,0]
   windows=[]
   for lo in range(0,len(reference)-19200+1,4800):
    hi=lo+19200
    if mask[lo:hi].sum()<7200:continue
    windows.append(dict(rawStart=lo/48000,rawEnd=hi/48000,globalStart=scene['startFrame']/60+lo/48000,**measure(reference,expected,actual,mask,lo,hi)))
   paragraphs=[]
   for line in al['lines']:
    lo=round(line['rawStart']*48000);hi=round(line['rawEnd']*48000)
    paragraphs.append(dict(line=line['line'],rawStart=line['rawStart'],rawEnd=line['rawEnd'],**measure(reference,expected,actual,mask,lo,hi)))
   sentences={}
   for cue in captions['cues']:
    if cue['scene']!=sid:continue
    key=(cue['line'],cue['sentence']);lo,hi=cue['rawStart'],cue['rawEnd']
    if key in sentences:sentences[key]['rawEnd']=max(sentences[key]['rawEnd'],hi)
    else:sentences[key]=dict(line=key[0],sentence=key[1],rawStart=lo,rawEnd=hi)
   sentences=[dict(row,**measure(reference,expected,actual,mask,round(row['rawStart']*48000),round(row['rawEnd']*48000)))for row in sentences.values()]
   flags=[w for w in windows if w['transientSafetyChangeDb']<-3 or w['transientSafetyChangeDb']>.1]
   rows.append(dict(scene=sid,sourceFile=scene['rawVoiceFile'],sourceSha256=scene['rawVoiceSha256'],wordFile=al['asrFile'],wordSha256=al['asrSha256'],
    windows=windows,paragraphs=paragraphs,sentences=sentences,processingCandidates=flags,
    sourceParagraphSpanDb=max(x['sourceSpeechDbfs']for x in paragraphs)-min(x['sourceSpeechDbfs']for x in paragraphs),
    processedParagraphSpanDb=max(x['processedSpeechDbfs']for x in paragraphs)-min(x['processedSpeechDbfs']for x in paragraphs),
    fixedGainGroups=gains[sid]['groups'],quietTransitions=gains[sid]['boundaries'],humanContextListening='pending'))
 joins=[]
 for left,right in zip(t['scenes'],t['scenes'][1:]):
  prev=byid[left['id']]['lines'][-1];nxt=byid[right['id']]['lines'][0]
  last_end=left['startFrame']/60+prev['rawEnd'];next_start=right['startFrame']/60+nxt['rawStart']
  joins.append(dict(previous=left['id'],next=right['id'],boundary=right['startFrame']/60,
    captionWordEnd=last_end,captionWordStart=next_start,wordTimestampQuietSpan=next_start-last_end,
    addedObservationSilence=0,onlyFramePaddingSamples24=left['frames']*400-left['rawVoiceSamples'],
    previousParagraphSpeechDbfs=next(x for x in rows if x['scene']==left['id'])['paragraphs'][-1]['processedSpeechDbfs'],
    nextParagraphSpeechDbfs=next(x for x in rows if x['scene']==right['id'])['paragraphs'][0]['processedSpeechDbfs'],
    contextualHumanListening='pending'))
 candidates=sum(len(x['processingCandidates'])for x in rows)
 assert sum(len(x['paragraphs'])for x in rows)==135
 report=dict(schemaVersion=1,part=1,inputs=dict(timelineSha256=c.sha(timeline_file),narrationBuildSha256=c.sha(build_file),alignmentSha256=c.sha(c.O/'source-alignment.json'),captionSha256=c.sha(caption_file),implementationSha256=c.sha(Path(__file__))),
  currentNarrationFile=c.rel(stem),currentNarrationSha256=c.sha(stem),sceneCount=21,paragraphCount=135,sentenceCount=sum(len(x['sentences'])for x in rows),
  method='Current source ASR timestamps,400ms/100ms windows with at least150ms timestamp-active samples; source resampled once, expected complete-group and any documented quiet-only sentence gains, actual original/local transient safety measured. Timestamp masks are not phonetic or listening proof.',
  sourcePcmUnchanged=True,voiceSpeed=1,voiceDucked=False,voiceSpeechFades=False,addedObservationSilence=0,
  actualLoudness=build['actualNarrationMeasurement'],scenes=rows,joins=joins,processingCandidateWindows=candidates,
  candidatesRequireContext=True,humanWholeListening='pending',voiceVisualPace='pending',finalEncodedMixContinuity='pending final master',
  note='Source prosody is retained. A local low RMS value is not automatically a defect; no repeated normalization or TTS inference was performed.')
 c.save(c.O/'narration-continuity-review.json',report)
 print('Current narration continuity measured:',135,'paragraphs;',report['sentenceCount'],'sentences;',candidates,'candidate windows; actual listening remains pending')
if __name__=='__main__':main()
