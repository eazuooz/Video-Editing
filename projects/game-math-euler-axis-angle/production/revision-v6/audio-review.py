"""CPU only: reuse the once-decoded final48k stereo WAV for local level QA.

No codec/model/render or waveform write. Compare AAC to the known final mix;
never mistake game interference or source prosody for narration processing.
Actual contextual listening and pronunciation remain pending.
"""
from pathlib import Path
import argparse, hashlib, json, math
import numpy as np
import soundfile as sf

R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle'
H=Path(__file__).parent;O=P/'production/local/revision-v6';RATE=48000
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def db(x):return 20*math.log10(max(float(x),1e-12))
def rms(x):return float(np.sqrt(np.mean(np.square(x,dtype=np.float64)))) if np.size(x) else 0.
def rel(p):return p.resolve().relative_to(R).as_posix()
def bounded(stream,start,count):
 stream.seek(start);data=stream.read(count,dtype='float32',always_2d=True)
 assert data.shape==(count,2),'Decoded/current reference sample range unavailable'
 return data
def measure(encoded,reference,voice,game,active):
 assert encoded.shape==reference.shape==voice.shape==game.shape
 assert active.shape==(len(encoded),)
 # Speech-active samples from the current source ASR, never energy-only VAD.
 e=encoded[active].astype(np.float64);m=reference[active].astype(np.float64)
 v=voice[active].astype(np.float64);g=game[active].astype(np.float64)
 if not len(e):return dict(speechSamples=0,status='no-current-source-word-mask')
 el,ml,vl,gl=[db(rms(x)) for x in [e,m,v,g]]
 energy=float(np.sum(m*m));projection=float(np.sum(e*m)/energy) if energy>1e-20 else None
 correlation=float(np.sum(e*m)/(np.sqrt(np.sum(e*e)*energy))) if energy>1e-20 and np.sum(e*e)>1e-20 else None
 mix_transfer=el-ml;source_dominance=vl-gl
 # The mix reference already contains the exact ducked game. Do not subtract
 # unrelated energies or infer an isolated AAC voice from a residual RMS.
 audible=vl>-60;dominant=source_dominance>=6 or gl<=-100
 mismatch=audible and (abs(mix_transfer)>1 or (projection is not None and not .88<=projection<=1.13))
 suspect=dominant and mismatch
 return dict(speechSamples=int(active.sum()),encodedMixSpeechDbfs=el,referenceMixSpeechDbfs=ml,knownVoiceSpeechDbfs=vl,knownGameSpeechDbfs=gl,
  encodedVsReferenceMixDb=mix_transfer,referenceWaveformProjection=projection,referenceWaveformCorrelation=correlation,
  encodedMinusKnownMixErrorRmsDbfs=db(rms(e-m)),voiceToGameDb=source_dominance,voiceDominant=dominant,
  referenceMismatchFlag=bool(mismatch),gameMasksIsolatedVoiceTransfer=bool(audible and not dominant),
  activeProcessingTransferFlag=bool(suspect),status='contextual-review-needed' if mismatch else 'numeric-reference-comparison-no-transfer-flag',humanListening='pending')
def mapped_word_mask(scene,words):
 size=scene['frames']*800;out=np.zeros(size,dtype=bool);crossed=[]
 for w in words:
  a,b=w['timestamp']
  if a is None or b is None or b<=a:continue
  left=max(0,round(a*24000));right=min(scene['rawVoiceSamples'],round(b*24000))
  if right<=left:continue
  for seg in scene['voiceSegments']:
   x=max(left,seg['sourceSampleStart']);y=min(right,seg['sourceSampleEnd'])
   if y>x:
    destination=seg['destinationSampleStart']+x-seg['sourceSampleStart']
    out[destination*2:(destination+y-x)*2]=True
  if not any(s['sourceSampleStart']<=left and right<=s['sourceSampleEnd'] for s in scene['voiceSegments']):crossed.append(dict(text=w['text'],timestamp=w['timestamp']))
 return out,crossed
def group_flags(rows,key):
 grouped=[]
 for row in rows:
  if not row.get(key):continue
  start,end=row['globalStart'],row['globalEnd']
  if grouped and start<=grouped[-1]['end']+.11 and row['scene']==grouped[-1]['scene']:
   grouped[-1]['end']=max(end,grouped[-1]['end']);grouped[-1]['windowCount']+=1
  else:grouped.append(dict(scene=row['scene'],start=start,end=end,windowCount=1,humanListening='pending'))
 return grouped
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--decoded',required=True,type=Path);parser.add_argument('--extraction',required=True,type=Path);parser.add_argument('--output',type=Path,default=O/'qa/audio-level-continuity.json');args=parser.parse_args()
 assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
 decoded=args.decoded.resolve();extraction=args.extraction.resolve();metadata=read(extraction)
 assert decoded.is_file() and extraction.is_file()
 decoded_hash=sha(decoded)
 assert decoded_hash==metadata['decodedSha256'],'Shared extraction receipt must bind this exact decoded WAV hash'
 declared=Path(metadata['decodedFile']);declared=declared if declared.is_absolute() else R/declared
 assert declared.resolve()==decoded and metadata['sampleRate']==RATE and metadata['channels']==2
 plan=read(H/'timeline.json');build=read(O/'audio-build.json')
 assert plan['timing']=='measured-and-asr-aligned' and build['inputs']['timelineSha256']==sha(H/'timeline.json')
 assert metadata['videoRangeSamples']==plan['totalFrames']*800
 assert metadata['bodyStartSample']==plan['introFrames']*800 and metadata['bodyEndSample']==plan['temporalContract']['outroStartFrame']*800
 files=[R/build[k] for k in ['audioMix','narrationStem','gameStem']]
 output_hashes={x['file']:x['sha256'] for x in build['outputs']}
 for f in files:assert sha(f)==output_hashes[rel(f)]
 inputs=dict(timelineSha256=sha(H/'timeline.json'),audioBuildSha256=sha(O/'audio-build.json'),decodedSha256=decoded_hash,extractionSha256=sha(extraction),implementationSha256=sha(Path(__file__)))
 if args.output.exists():
  prior=read(args.output)
  if prior.get('inputs')==inputs:print('Exact current numeric audio review reused; no codec/model/waveform run');return
  raise RuntimeError('Preserve an existing different QA receipt before a justified new output review')
 windows=[];paragraphs=[];joins=[];word_crossings=[];max_mix_error=0.
 with sf.SoundFile(decoded) as enc,sf.SoundFile(files[0]) as mix,sf.SoundFile(files[1]) as voice,sf.SoundFile(files[2]) as game:
  streams=[enc,mix,voice,game];total=plan['totalFrames']*800
  assert all(s.samplerate==RATE and s.channels==2 for s in streams)
  assert all(s.frames==total for s in [mix,voice,game])
  assert enc.frames==metadata['decodedSamples'] and total<=enc.frames<=total+2048,'Unexpected AAC duration/priming mismatch requires explicit review'
  for scene in plan['scenes']:
   asr_file=R/scene['rawAsrFile'];assert sha(asr_file)==scene['rawAsrSha256'];asr=read(asr_file);assert asr['audio_sha256']==scene['rawVoiceSha256']
   active,crossings=mapped_word_mask(scene,asr['words']);word_crossings.extend([dict(scene=scene['id'],**x) for x in crossings])
   base=scene['startFrame']*800;count=scene['frames']*800
   e,m,v,g=[bounded(s,base,count) for s in streams]
   max_mix_error=max(max_mix_error,float(np.max(np.abs(m.astype(np.float64)-v.astype(np.float64)-g.astype(np.float64)))))
   for start in range(0,count-round(.4*RATE)+1,round(.1*RATE)):
    end=start+round(.4*RATE);mask=active[start:end]
    if mask.sum()<round(.15*RATE):continue
    row=measure(e[start:end],m[start:end],v[start:end],g[start:end],mask)
    row.update(scene=scene['id'],globalStart=(base+start)/RATE,globalEnd=(base+end)/RATE,sceneRelativeStart=start/RATE)
    windows.append(row)
   for line in scene['lines']:
    left=max(0,math.floor(line['start']*RATE));right=min(count,math.ceil(line['end']*RATE))
    if right<=left:continue
    row=measure(e[left:right],m[left:right],v[left:right],g[left:right],active[left:right]);row.update(scene=scene['id'],line=line['line'],globalStart=(base+left)/RATE,globalEnd=(base+right)/RATE)
    paragraphs.append(row)
   del e,m,v,g,active
  for previous,current in zip(plan['scenes'],plan['scenes'][1:]):
   boundary=current['startFrame']/60
   rows=[x for x in windows if boundary-3<=x['globalStart']<=boundary+3]
   joins.append(dict(previous=previous['id'],next=current['id'],boundarySeconds=boundary,range=[boundary-3,boundary+3],speechActiveWindowCount=len(rows),transferFlags=sum(x['activeProcessingTransferFlag'] for x in rows),windowGlobalStarts=[x['globalStart'] for x in rows],humanListening='pending'))
 assert max_mix_error<2e-6,'The known final mix must still equal its actual source stems'
 flags=group_flags(windows,'activeProcessingTransferFlag')
 report=dict(schemaVersion=1,revision='article-flow-v6',inputs=inputs,sharedDecodedFile=rel(decoded),sharedExtractionFile=rel(extraction),
  captionedMasterFile=metadata['captionedMasterFile'],captionedMasterSha256=metadata['captionedMasterSha256'],
  sampleRate=RATE,channels=2,currentSourcePcmProof=build['sourcePcmProof'],sourceToStemReport=rel(O/'audio-build.json'),
  sourceToStemProcessingDropFlags=build['sourceToStemProcessingDropFlags'],knownMixEqualsStemsMaximumError=max_mix_error,
  windowSeconds=.4,stepSeconds=.1,speechMask='Valid positive-duration current source ASR words mapped through exact preserved sample segments; no energy-only speech assumption.',
  encodedComparison='Decoded AAC versus actual known voice+ducked-game mix. No residual-energy voice extraction. Voice-dominant processing flags only; game-masked cases remain contextual.',
  windows=windows,paragraphs=paragraphs,joins=joins,mappedWordCrossings=word_crossings,activeProcessingTransferFlags=flags,
  encodedReferenceMismatchRanges=group_flags(windows,'referenceMismatchFlag'),gameMaskedVoiceRanges=group_flags(windows,'gameMasksIsolatedVoiceTransfer'),
  status='numeric-analysis-complete-contextual-listening-pending',sourcePronunciation='pending',humanWholeListening='pending',humanPaceListening='pending',newCodecOrModelExecuted=False)
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('CPU known-reference/encoded audio comparison:',len(windows),'speech windows;',len(flags),'processing flag ranges; human listening pending')
if __name__=='__main__':main()
