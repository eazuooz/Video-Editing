"""Speech-boundary-aware source levels, preserving quiet recognized syllables."""
import pathlib,json,hashlib,datetime,collections
import numpy as np,soundfile as sf
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/beginner-revision-v1'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rms(data,sr):
 win=round(.4*sr);hop=round(.1*sr);a=np.arange(0,max(1,len(data)-win+1),hop);z=np.minimum(a+win,len(data));c=np.r_[0,np.cumsum(data.astype(np.float64)**2)];return a/sr,z/sr,10*np.log10(np.maximum((c[z]-c[a])/(z-a),1e-12))
def main():
 assert not (O/'speech-level-review.json').exists()
 plan=rd(O/'edit-plan-proposal.json');groups=collections.defaultdict(list)
 for v in plan['voice']:groups[v['key']].append(v)
 b=rd(P/'production/current-caption-boundary-review-v5.json');bp={r['key']:r for r in b['paragraphs']};guides=rd(P/'production/native-guides-direct-review-v1.json');changed={r['key']:r for r in rd(O/'voice-alignment-proposal.json')['rows']+rd(O/'native-guides-alignment-reviewed.json')['rows']};cache={};rows={}
 for key,vs in groups.items():
  pieces=[]
  for v in sorted(vs,key=lambda v:v['utteranceStartSample']):
   if v['path'] not in cache:cache[v['path']]=sf.read(R/v['path'],dtype='float32')[0]
   pieces.append(cache[v['path']][v['sourceStartSample']:v['sourceStartSample']+v['samples']])
  data=np.concatenate(pieces);origin=min(v['sourceStartSample'] for v in vs)/24000
  if key in changed:a=rd(R/changed[key]['asrPath']);offset=0;ap=changed[key]['asrPath']
  elif key.startswith('g'):ap=guides['asrPaths'][key];a=rd(R/ap);offset=0
  else:
   q=bp[key];ap=q['chosenCandidate']['file'];a=rd(R/ap);offset=q['sceneStartSeconds']+b['recognitionSourceHashes'][ap]['localWindowStartSeconds']-origin
  intervals=[]
  for w in a['chunks']:
   l,h=w['timestamp']
   if l is None or h is None or h<=l:continue
   l,h=max(0,l+offset),min(len(data)/24000,h+offset)
   if h>l:intervals.append([l,h])
  assert intervals,key
  mask=np.zeros(len(data),dtype=np.int8)
  for l,h in intervals:mask[round(l*24000):round(h*24000)]=1
  starts,ends,levels=rms(data,24000);m=np.r_[0,np.cumsum(mask)];coverage=(m[np.rint(ends*24000).astype(int)]-m[np.rint(starts*24000).astype(int)])/(np.rint((ends-starts)*24000))
  selected=levels[coverage>=.5];assert len(selected),key
  median=float(np.median(selected));flags=[];active=None
  for i,(lo,hi,level,cv) in enumerate(zip(starts,ends,levels,coverage)):
   low=cv>=.5 and level<=median-6
   if low and active is None:active=i
   if active is not None and (not low or i==len(starts)-1):
    last=i-1 if not low else i
    if ends[last]-starts[active]>=.5:flags.append(dict(sourceSeconds=[float(starts[active]),float(ends[last])],minimumDbfs=float(min(levels[active:last+1])),relativeToMedianDb=float(min(levels[active:last+1])-median),contextListening='pending',origin='source-PCM-before-mix'))
    active=None
  rows[key]=dict(decodedPcmSha256=hashlib.sha256(data.tobytes()).hexdigest(),samples=len(data),asrPath=ap,asrSha256=sha(R/ap),speechIntervals=intervals,speechWindowCoverage=np.round(coverage,3).tolist(),allRmsDbfs=np.round(levels,3).tolist(),speechMedianDbfs=median,speechP10Dbfs=float(np.percentile(selected,10)),speechP90Dbfs=float(np.percentile(selected,90)),sourcePeakDbfs=float(20*np.log10(max(np.max(np.abs(data)),1e-12))),sourceLowRuns=flags)
 ordered=list(dict.fromkeys(v['key'] for v in sorted(plan['voice'],key=lambda v:v['startFrame'])));joins=[]
 for a,z in zip(ordered,ordered[1:]):
  delta=rows[z]['speechMedianDbfs']-rows[a]['speechMedianDbfs']
  if abs(delta)>=3:joins.append(dict(before=a,after=z,deltaDb=delta))
 wr(O/'speech-level-review.json',dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),planSha256=sha(O/'edit-plan-proposal.json'),windowSeconds=.4,hopSeconds=.1,method='Every400ms window retained. Speech classification uses actual recognized word intervals, not an energy gate;50% window speech coverage for comparisons. Source low runs are flags, not automatic defects.',rows=rows,joinFlags=joins,sourceLowRunCount=sum(len(r['sourceLowRuns']) for r in rows.values()),humanContextListening='pending',introducedMixAttenuationChecked=False,approved=False))
 print(json.dumps(dict(keys=len(rows),medianRange=[min(r['speechMedianDbfs'] for r in rows.values()),max(r['speechMedianDbfs'] for r in rows.values())],joinFlags=joins,sourceLowRunCount=sum(len(r['sourceLowRuns']) for r in rows.values())),ensure_ascii=False))
if __name__=='__main__':main()
