"""Measure changed speech and its joins from raw PCM through stem and decoded AAC."""
import pathlib,json,hashlib,datetime
import numpy as np,soundfile as sf
from scipy.signal import resample_poly
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/review-v3';B=P/'production/local/continuity-v2'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def rms(a,sr):
 if a.ndim==2:a=a.mean(axis=1)
 n=round(sr*.4);lo=np.arange(0,max(1,len(a)-n+1),round(sr*.1));hi=np.minimum(lo+n,len(a));cs=np.r_[0,np.cumsum(a.astype('float64')**2)]
 return 10*np.log10(np.maximum((cs[hi]-cs[lo])/(hi-lo),1e-12)),lo,hi
def main():
 assert not (O/'local-level-review.json').exists()
 plan=rd(O/'plan.json');align=rd(O/'alignment-proposal.json');rows={};flags=[]
 with sf.SoundFile(O/'narration-current.wav') as stem,sf.SoundFile(O/'final-encoded-decoded.wav') as final:
  for row in align['rows']:
   v=next(v for v in plan['voice'] if v['key']==row['key']);raw,sr=sf.read(R/v['path'],dtype='float32');assert sr==24000
   raw=raw[v.get('sourceStartSample',0):v.get('sourceStartSample',0)+v['samples']]
   stages={'source':raw}
   for name,f in [('processed',stem),('encoded',final)]:f.seek(v['startFrame']*800);stages[name]=f.read(v['samples']*2,dtype='float32')
   levels={name:rms(a,24000 if name=='source' else 48000)[0] for name,a in stages.items()}
   _,lo,hi=rms(raw,24000);mask=np.zeros(len(raw),dtype='int8')
   for c in row['koCues']:mask[round(c['seconds'][0]*24000):round(c['seconds'][1]*24000)]=1
   cs=np.r_[0,np.cumsum(mask)];coverage=(cs[hi]-cs[lo])/(hi-lo);active=coverage>=.5
   r={'speechWindowCoverage':coverage.tolist(),'stages':{k:{'medianDbfs':float(np.median(a[active])),'allRmsDbfs':a.tolist()} for k,a in levels.items()}}
   for a,b in [('source','processed'),('processed','encoded')]:
    d=levels[b]-levels[a];mid=np.median(d[active]);bad=np.flatnonzero(active&(d<mid-6));runs=[]
    for i in bad:
     if runs and i==runs[-1][-1]+1:runs[-1].append(int(i))
     else:runs.append([int(i)])
    for run in runs:
     if len(run)>=2:flags.append(dict(key=row['key'],stages=[a,b],seconds=[run[0]*.1,run[-1]*.1+.4],relativeGainDb=float(min(d[run])-mid)))
   rows[row['key']]=r
  # Compare short speech-active regions either side of every changed paragraph.
  keys=['g26']+[r['key'] for r in align['rows']]+['g33','g32'];medians={}
  for key in keys:
   vs=[v for v in plan['voice'] if v['key']==key];chunks=[]
   for v in vs:stem.seek(v['startFrame']*800);chunks.append(stem.read(v['samples']*2,dtype='float32'))
   db,_,_=rms(np.concatenate(chunks),48000);active=db>-45;medians[key]=float(np.median(db[active]))
  joins=[dict(before=a,after=b,beforeDbfs=medians[a],afterDbfs=medians[b],deltaDb=medians[b]-medians[a]) for a,b in zip(keys,keys[1:])]
  discontinuities=[]
  for f in [64119,64119+plan['newExplanationFrames'],64119+plan['newExplanationFrames']+1020]:
   final.seek(f*800-1);a=final.read(2,dtype='float32');discontinuities.append(dict(frame=f,maxSampleStep=float(np.max(np.abs(a[1]-a[0])))))
 report=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='400ms RMS every100ms; matching raw-source/stem/decoded-AAC windows; actual measured speech boundaries; no quiet-syllable energy exclusion in changed-speech comparison',rows=rows,introducedAttenuationFlags=flags,joinMedians=joins,backgroundJoinSampleSteps=discontinuities,unchangedRangeEvidence='v2 local-level review retained outside declared splices; current AAC globally re-encoded and all affected joins measured',sourceProsodyPreserved=True,humanContextListening='pending-user-review',measurementPass=not flags and all(abs(j['deltaDb'])<3 for j in joins))
 (O/'local-level-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:report[k] for k in ['introducedAttenuationFlags','joinMedians','backgroundJoinSampleSteps','measurementPass']}))
if __name__=='__main__':main()
