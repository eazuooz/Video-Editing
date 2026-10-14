"""Incremental hash-keyed local-level diagnostics; does not approve or auto-level speech."""
import pathlib,json,hashlib,re,datetime
import numpy as np,soundfile as sf
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
plan=rd(P/'production/local/threejs-revision-v1/pair-caption-decoder-v3/plan.json')
changes=rd(P/'production/beginner-revision-v1/changes.json');change={r['key']:r for r in changes['rows']}
log=(P/'production/local/beginner-revision-v1/tts/job.log').read_text(encoding='utf-8-sig',errors='replace')
complete=set(re.findall(r'Rendered (b\d+)-scene ',log))
out=P/'production/local/beginner-revision-v1/voice-levels.json'
report=rd(out) if out.exists() else dict(method='400ms unweighted RMS(dBFS),100ms hop; all windows retained. No inference that quiet syllables are silence.',rows={},humanContextListening='pending',approved=False)
group={}
for v in plan['voice']:group.setdefault(v['key'],[]).append(v)
for key,vs in group.items():
 if key in change:
  row=change[key]
  if row['ttsSceneId'] not in complete:continue
  path=R/row['replacementAudioPath'] if row.get('replacementAudioPath') else R/f"shared/output/narration/game-lighting-history-01/beginner-revision-v1/chunks/{row['ttsSceneId']}-scene.wav"
  data,sr=sf.read(path,dtype='float32');identity={'kind':'replacement','path':path.relative_to(R).as_posix()}
 else:
  parts=[]
  for v in vs:
   with sf.SoundFile(R/v['path']) as f:f.seek(v['sourceStartSample']);parts.append(f.read(v['samples'],dtype='float32'));sr=f.samplerate
  data=np.concatenate(parts);identity={'kind':'retained','placements':vs}
 assert sr==24000 and data.ndim==1
 digest=hashlib.sha256(data.tobytes()).hexdigest()
 if report['rows'].get(key,{}).get('decodedPcmSha256')==digest:continue
 win=int(.4*sr);hop=int(.1*sr);squared=data.astype(np.float64)**2;cum=np.concatenate(([0.],np.cumsum(squared)))
 starts=np.arange(0,max(1,len(data)-win+1),hop);ends=np.minimum(starts+win,len(data))
 levels=10*np.log10(np.maximum((cum[ends]-cum[starts])/(ends-starts),1e-12))
 # Percentiles are descriptive; actual speech/word boundaries are needed before
 # calling a low window a pause or a voice drop.
 row={**identity,'decodedPcmSha256':digest,'samples':len(data),'seconds':len(data)/sr,'windowSeconds':.4,'hopSeconds':.1,'allRmsDbfs':np.round(levels,3).tolist(),'peakDbfs':float(20*np.log10(max(np.max(np.abs(data)),1e-12))),'percentilesDbfs':dict(zip(['p10','p25','p50','p75','p90'],map(float,np.percentile(levels,[10,25,50,75,90])))),'speechBoundariesApplied':False,'contextListening':'pending'}
 report['rows'][key]=row
report['observedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();report['coverage']={'currentVoiceKeys':len(report['rows']),'expectedKeys':len(group),'changedCompleted':len(complete),'changedExpected':52}
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report['coverage']))
