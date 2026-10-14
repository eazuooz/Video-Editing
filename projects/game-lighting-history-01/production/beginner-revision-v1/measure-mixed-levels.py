"""Compare identical speech windows through edit gain, processed voice and AAC."""
import pathlib,json,datetime,hashlib,collections,importlib.util,sys
import numpy as np,soundfile as sf
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/beginner-revision-v1'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 current='--current' in sys.argv;output=O/('mixed-level-review-current.json' if current else 'mixed-level-review.json');assert not output.exists()
 plan=rd(O/'plan.json');source=rd(O/'speech-level-review.json');mix=rd(O/'mix-execution.json');assert mix['exitCode']==0
 sp=importlib.util.spec_from_file_location('level',H/'measure-current-levels.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 groups=collections.defaultdict(list)
 for v in plan['voice']:groups[v['key']].append(v)
 paths={'editGain':'leveled-narration.wav','processedVoice':mix.get('currentProcessedVoice','narration-normalized.wav'),'finalAAC':mix.get('currentDecodedAac','final-aac-decoded.wav')};files={k:sf.SoundFile(O/p) for k,p in paths.items()};rows={}
 for key,vs in groups.items():
  s=source['rows'][key];coverage=np.array(s['speechWindowCoverage']);row={}
  for stage,f in files.items():
   sr=f.samplerate;chunks=[]
   for v in sorted(vs,key=lambda v:v['utteranceStartSample']):
    f.seek(round(v['targetStartSample']*sr/24000));a=f.read(round(v['samples']*sr/24000),dtype='float32');chunks.append(a.mean(axis=1) if a.ndim==2 else a)
   data=np.concatenate(chunks);starts,ends,levels=m.rms(data,sr);assert len(levels)==len(coverage),(key,stage,len(levels),len(coverage))
   speech=levels[coverage>=.5];row[stage]=dict(speechMedianDbfs=float(np.median(speech)),speechP10Dbfs=float(np.percentile(speech,10)),speechP90Dbfs=float(np.percentile(speech,90)),allRmsDbfs=np.round(levels,3).tolist())
  row['medianProcessingGainDb']=row['processedVoice']['speechMedianDbfs']-row['editGain']['speechMedianDbfs'];row['sourceLowRuns']=s['sourceLowRuns'];rows[key]=row
 for f in files.values():f.close()
 ordered=list(dict.fromkeys(v['key'] for v in sorted(plan['voice'],key=lambda v:v['startFrame'])));joins=[]
 for a,z in zip(ordered,ordered[1:]):
  before=source['rows'][z]['speechMedianDbfs']-source['rows'][a]['speechMedianDbfs'];after=rows[z]['processedVoice']['speechMedianDbfs']-rows[a]['processedVoice']['speechMedianDbfs']
  if abs(before)>=3 or abs(after)>=3:joins.append(dict(beforeKey=a,afterKey=z,sourceDeltaDb=before,processedDeltaDb=after,stillFlagged=abs(after)>=3))
 introduced=[];actualDips=[]
 for key,r in rows.items():
  delta=np.array(r['processedVoice']['allRmsDbfs'])-np.array(r['editGain']['allRmsDbfs']);coverage=np.array(source['rows'][key]['speechWindowCoverage']);mid=np.median(delta[coverage>=.5]);ix=np.flatnonzero((coverage>=.5)&(delta<mid-6));runs=[]
  for i in ix:
   if runs and i==runs[-1][-1]+1:runs[-1].append(int(i))
   else:runs.append([int(i)])
  for run in runs:
   if (run[-1]-run[0])*.1+.4>=.5:introduced.append(dict(key=key,sourceSeconds=[run[0]*.1,run[-1]*.1+.4],relativeProcessingGainDb=float(min(delta[run])-mid)))
  a=np.array(r['editGain']['allRmsDbfs']);b=np.array(r['processedVoice']['allRmsDbfs']);bm=r['processedVoice']['speechMedianDbfs'];ix=np.flatnonzero((coverage>=.5)&(b<bm-6)&(a>r['editGain']['speechMedianDbfs']-6)&(delta<mid-6));runs=[]
  for i in ix:
   if runs and i==runs[-1][-1]+1:runs[-1].append(int(i))
   else:runs.append([int(i)])
  for run in runs:
   if (run[-1]-run[0])*.1+.4>=.5:actualDips.append(dict(key=key,sourceSeconds=[run[0]*.1,run[-1]*.1+.4],processedRelativeToMedianDb=float(min(b[run])-bm)))
 wr(output,dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),planSha256=sha(O/'plan.json'),inputs={p:sha(O/p) for p in paths.values()},method='400ms RMS/100ms step and actual ASR word boundaries. Identical utterance source offsets through edit copy, processed voice-only and decoded AAC. All windows retained, quiet syllables are not energy-gated.',rows=rows,joins=joins,sourceJoinFlagCount=len(source['joinFlags']),processedJoinFlagCount=sum(x['stillFlagged'] for x in joins),introducedLocalAttenuationFlags=introduced,actualIntroducedSpeechDips=actualDips,gainReductionIsNotAutomaticallyQuietSpeech=True,narrationDucking=False,backgroundDucking=True,amixNormalize=False,humanContextListening='pending',wholeHumanListening='pending',approval=False))
 print(json.dumps(dict(sourceJoinFlags=len(source['joinFlags']),processedJoinFlags=sum(x['stillFlagged'] for x in joins),gainReductionFlagCount=len(introduced),actualIntroducedSpeechDips=actualDips),ensure_ascii=False))
if __name__=='__main__':main()
