"""Metadata-only context triage; never reads PCM or declares listening approval."""
from pathlib import Path
import json,statistics,hashlib
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'projects/game-math-euler-axis-angle/production/local/revision-v7-part1/audio'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def groups(items,filter_fn):
 out=[]
 for x in items:
  if not filter_fn(x):continue
  lo,hi=x['rawStart'],x['rawEnd']
  if out and lo<=out[-1]['rawEnd']+1e-6:
   out[-1]['rawEnd']=max(hi,out[-1]['rawEnd']);out[-1]['windows'].append(x)
  else:out.append(dict(rawStart=lo,rawEnd=hi,windows=[x]))
 for g in out:g['duration']=g['rawEnd']-g['rawStart']
 return out
def contextual(row,g):
 sentences=[x for x in row['sentences']if min(x['rawEnd'],g['rawEnd'])>max(x['rawStart'],g['rawStart'])]
 return dict(sentenceKeys=[f"L{x['line']:02}.S{x['sentence']:02}"for x in sentences],completeContextRange=[min((x['rawStart']for x in sentences),default=g['rawStart']),max((x['rawEnd']for x in sentences),default=g['rawEnd'])])
def adjacent(values,center,key):
 before=[x[key]for x in values if center-3<=(x['rawStart']+x['rawEnd'])/2<=center-.6]
 after=[x[key]for x in values if center+.6<=(x['rawStart']+x['rawEnd'])/2<=center+3]
 all_values=before+after
 return dict(referenceMedianDbfs=statistics.median(all_values)if all_values else None,beforeMedianDbfs=statistics.median(before)if before else None,afterMedianDbfs=statistics.median(after)if after else None,beforeWindows=len(before),afterWindows=len(after))
def near(values,center,before,key):
 selected=[x[key]for x in values if (center-1.7<=(x['rawStart']+x['rawEnd'])/2<=center-.2 if before else center+.2<=(x['rawStart']+x['rawEnd'])/2<=center+1.7)]
 return dict(medianDbfs=statistics.median(selected)if selected else None,windows=len(selected))
def main():
 file=O/'narration-continuity-review.json';d=read(file);rows=[];all_attenuated=[];all_drops=[];internal=[]
 for row in d['scenes']:
  windows=[]
  for x in row['windows']:
   center=(x['rawStart']+x['rawEnd'])/2;current=adjacent(row['windows'],center,'processedSpeechDbfs');source=adjacent(row['windows'],center,'sourceSpeechDbfs')
   item=dict(x,adjacentProcessed=current,adjacentSource=source)
   item['processedRelativeToAdjacentDb']=None if current['referenceMedianDbfs']is None else x['processedSpeechDbfs']-current['referenceMedianDbfs']
   item['sourceRelativeToAdjacentDb']=None if source['referenceMedianDbfs']is None else x['sourceSpeechDbfs']-source['referenceMedianDbfs']
   windows.append(item)
  attenuation=[]
  for g in groups(windows,lambda x:x['transientSafetyChangeDb']<-3):
   worst=min(g['windows'],key=lambda x:x['transientSafetyChangeDb']);actual_drop=any((x['processedRelativeToAdjacentDb']or 0)<-6 for x in g['windows'])
   info=dict(scene=row['scene'],rawStart=g['rawStart'],rawEnd=g['rawEnd'],duration=g['duration'],windowCount=len(g['windows']),**contextual(row,g),
    largestCounterfactualAttenuationDb=worst['transientSafetyChangeDb'],worstWindow=worst,
    hasAnyActualAdjacentDrop6Db=actual_drop,meaning='Limiter attenuation relative to counterfactual non-limited boost. This is not itself an actual volume drop relative to adjacent current speech.',humanListening='pending')
   attenuation.append(info);all_attenuated.append(info)
  drops=[]
  for g in groups(windows,lambda x:x['processedRelativeToAdjacentDb']is not None and x['processedRelativeToAdjacentDb']<-6):
   if g['duration']<.5-1e-6:continue
   worst=min(g['windows'],key=lambda x:x['processedRelativeToAdjacentDb'])
   source_low=all(x['sourceRelativeToAdjacentDb']is not None and x['sourceRelativeToAdjacentDb']<-6 for x in g['windows'])
   limited=any(x['transientSafetyChangeDb']<-3 for x in g['windows'])
   reason='Source already locally low under the same measured window criterion; retained prosody candidate.'if source_low else('Current low region includes peak-safety attenuation; actual context inspection required.'if limited else'Current local-level candidate without3dB peak-safety change; compare group boundaries and source context.')
   info=dict(scene=row['scene'],rawStart=g['rawStart'],rawEnd=g['rawEnd'],duration=g['duration'],windowCount=len(g['windows']),**contextual(row,g),
    minimumActualRelativeToAdjacentDb=worst['processedRelativeToAdjacentDb'],worstWindow=worst,allFlaggedSourceWindowsAlreadyBelow6Db=source_low,
    includesCounterfactualAttenuationAbove3Db=limited,provisionalCause=reason,humanListening='pending',notAnAutomaticDefect=True)
   drops.append(info);all_drops.append(info)
  for q in row['quietTransitions']:
   boundary=q['sampleOffset']/24000
   before=near(windows,boundary,True,'processedSpeechDbfs');after=near(windows,boundary,False,'processedSpeechDbfs')
   delta=None if before['medianDbfs']is None or after['medianDbfs']is None else after['medianDbfs']-before['medianDbfs']
   if delta is not None and abs(delta)>=3:
    internal.append(dict(scene=row['scene'],afterLine=q['afterLine'],boundary=boundary,before=before,after=after,currentSpeechDifferenceDb=delta,verifiedQuietBoundary=True,humanListening='pending',notAnAutomaticDefect=True))
  rows.append(dict(scene=row['scene'],attenuationMergedContexts=attenuation,actualSustainedDropCandidates=drops))
 joins=[]
 by={x['scene']:x for x in d['scenes']}
 for q in d['joins']:
  left,right=by[q['previous']],by[q['next']];lw=left['windows'];rw=right['windows']
  la=max(x['rawEnd']for x in lw);ra=min(x['rawStart']for x in rw)
  b=[x['processedSpeechDbfs']for x in lw if x['rawEnd']>=la-1.5];e=[x['processedSpeechDbfs']for x in rw if x['rawStart']<=ra+1.5]
  bs=[x['sourceSpeechDbfs']for x in lw if x['rawEnd']>=la-1.5];es=[x['sourceSpeechDbfs']for x in rw if x['rawStart']<=ra+1.5]
  delta=statistics.median(e)-statistics.median(b);original=statistics.median(es)-statistics.median(bs)
  if abs(delta)>=3:
   joins.append(dict(previous=q['previous'],next=q['next'],globalBoundary=q['boundary'],actualAdjacentSpeechDifferenceDb=delta,originalAdjacentSpeechDifferenceDb=original,
    previousCurrentMedianDbfs=statistics.median(b),nextCurrentMedianDbfs=statistics.median(e),comparison='Last/first1.5seconds timestamp-active400ms measurements; not whole-clip LUFS.',humanListening='pending',notAnAutomaticDefect=True))
 sentences=[dict(s,scene=row['scene'])for row in d['scenes']for s in row['sentences']]
 sentence_lows=[]
 for i,sentence in enumerate(sentences):
  others=[x for j,x in enumerate(sentences[max(0,i-2):i+3],max(0,i-2))if j!=i]
  reference=statistics.median(x['processedSpeechDbfs']for x in others)
  delta=sentence['processedSpeechDbfs']-reference
  if delta<-6:
   sentence_lows.append(dict(sentence,adjacentCompleteSentenceMedianDbfs=reference,currentDifferenceDb=delta,
    sourceAdjacentCompleteSentenceMedianDbfs=statistics.median(x['sourceSpeechDbfs']for x in others),
    classification='Complete spoken sentence mean is low; not inferred from a syllable-tail400ms window.',humanListening='pending'))
 full_sentence_joins=[]
 for left,right in zip(d['scenes'],d['scenes'][1:]):
  delta=right['sentences'][0]['processedSpeechDbfs']-left['sentences'][-1]['processedSpeechDbfs']
  paragraph=right['paragraphs'][0]['processedSpeechDbfs']-left['paragraphs'][-1]['processedSpeechDbfs']
  if abs(delta)>=3:full_sentence_joins.append(dict(previous=left['scene'],next=right['scene'],adjacentFullSentenceDifferenceDb=delta,adjacentFullParagraphDifferenceDb=paragraph,humanListening='pending'))
 worst=min(all_attenuated,key=lambda x:x['largestCounterfactualAttenuationDb'])
 result=dict(schemaVersion=1,part=1,inputFile=str(file.relative_to(R)).replace('\\','/'),inputSha256=sha(file),implementationSha256=sha(Path(__file__)),
  analysisKind='Metadata only: existing measured windows; no PCM read, audio reprocessing or extra model inference.',
  criteria=dict(counterfactualAttenuationDb=3,actualAdjacentDropDb=6,minimumMergedActualDropSeconds=.5,joinDifferenceDb=3,
    adjacentReference='Median timestamp-active windows centered0.6–3s before/after each target; available sides shown; source/current use identical windows.',
    mergedDuration='Union of overlapping400ms windows, not a claim of sample-exact attenuation duration.'),
  counterfactualWindowCount=d['processingCandidateWindows'],counterfactualMergedContextCount=len(all_attenuated),
  counterfactualMergedUnionSeconds=sum(x['duration']for x in all_attenuated),
  actualSustainedDropCandidateCount=len(all_drops),actualSustainedDropUnionSeconds=sum(x['duration']for x in all_drops),
  actualDropCandidatesAlreadyLowInEverySourceWindow=sum(x['allFlaggedSourceWindowsAlreadyBelow6Db']for x in all_drops),
  actualDropCandidatesIncludingPeakSafety=sum(x['includesCounterfactualAttenuationAbove3Db']for x in all_drops),
  completeSentenceLowCandidates=sentence_lows,completeSentenceJoinCandidates=full_sentence_joins,
  completeSentenceCount=len(sentences),all20CompleteParagraphJoinsWithin3Db=all(abs(b['paragraphs'][0]['processedSpeechDbfs']-a['paragraphs'][-1]['processedSpeechDbfs'])<3 for a,b in zip(d['scenes'],d['scenes'][1:])),
  internalQuietJoinCandidates=internal,sceneJoinCandidates=joins,worstCounterfactualContext=worst,scenes=rows,
  actualContextListening='pending',internalPass=False,unresolvedActualLevelCandidates=len(all_drops)+len(internal)+len(joins),
  limitations='Thresholds locate review candidates; natural stress, breath and phrase endings can qualify. Counterfactual limiter attenuation is separated from actual current speech dips. Existing windows cannot establish phonetic perception or approve listening.')
 out=O/'narration-context-flags.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:v for k,v in result.items()if k not in ['scenes','worstCounterfactualContext','internalQuietJoinCandidates','sceneJoinCandidates']},ensure_ascii=False))
 print('WORST',json.dumps({k:v for k,v in worst.items()if k!='worstWindow'},ensure_ascii=False))
 print('WORSTLEVEL',json.dumps(worst['worstWindow'],ensure_ascii=False))
 print('JOINS',json.dumps(joins,ensure_ascii=False))
if __name__=='__main__':main()
