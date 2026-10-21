"""Narrow20ms check of actual mixed-stem400ms peak-ceiling candidate spans."""
from pathlib import Path
import importlib.util,json,math
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_focus_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def db(x):return 20*math.log10(max(float(x),1e-12))
def rms(x):return float(np.sqrt(np.mean(np.square(x,dtype=np.float64))))if len(x)else 0.
def groups(rows,threshold):
 out=[]
 for row in rows:
  if row['energyReductionDb']<threshold:continue
  if out and abs(row['start']-out[-1]['end'])<.0001:out[-1]['end']=row['end']
  else:out.append(dict(start=row['start'],end=row['end']))
 return dict(totalQuantizedSeconds=len([r for r in rows if r['energyReductionDb']>=threshold])*.02,longestQuantizedSeconds=max([r['end']-r['start']for r in out],default=0),ranges=out)
def main():
 c.validate();report_file=c.O/'measured-mix-level-review.json';report=c.read(report_file);timeline=c.read(H/'timeline.json');bytime={s['id']:s for s in timeline['scenes']}
 source=c.read(c.O/'source-alignment.json');byasr={s['id']:s for s in source['scenes']};mixfile=c.O.parent/'mix/mix-report.json';mix=c.read(mixfile)
 assert report['inputs']['mixReportSha256']==c.sha(mixfile);files={Path(r['file']).name:r for r in mix['outputs']};stems={r['role']:r for r in mix['stems']}
 paths=[c.R/files['narration-global-gain.wav']['file'],c.R/files['narration-normalized.wav']['file'],c.R/stems['narration']['file'],c.R/mix['audioMix'],c.R/report['decodedFile']]
 rows=[]
 for scene in report['scenes']:
  sid=scene['scene'];asr=c.read(c.R/byasr[sid]['asrFile']);origin=bytime[sid]['startFrame']/60
  for candidate in scene['ceilingEnergyReductionGroups']:
   start=max(origin,math.floor((candidate['start']-.6)*50)/50);end=min(origin+bytime[sid]['rawVoiceSamples']/24000,math.ceil((candidate['end']+.6)*50)/50);a,b=round(start*48000),round(end*48000)
   arrays=[]
   for path in paths:
    with sf.SoundFile(path)as f:f.seek(a);arrays.append(f.read(b-a,dtype='float32',always_2d=True))
   mask=np.zeros(b-a,bool)
   for word in asr['words']:
    lo,hi=word['timestamp']
    if lo is None or hi is None or hi<=lo:continue
    left=max(0,round((origin+lo)*48000)-a);right=min(b-a,round((origin+hi)*48000)-a)
    if right>left:mask[left:right]=True
   windows=[]
   for lo in range(0,b-a-960+1,960):
    hi=lo+960;active=mask[lo:hi]
    if active.sum()<288:continue
    values=[db(rms(x[lo:hi][active]))for x in arrays];windows.append(dict(start=start+lo/48000,end=start+hi/48000,globalTargetDbfs=values[0],postCeilingDbfs=values[1],finalVoiceDbfs=values[2],
     finalMixDbfs=values[3],decodedAacMixDbfs=values[4],energyReductionDb=values[0]-values[1],encodedMixTransferDb=values[4]-values[3],timestampActiveSamples=int(active.sum())))
   rows.append(dict(scene=sid,candidate400msOverlapSpan=candidate,checkedRange=[start,end],energy20ms=windows,
    reductionByThreshold={str(t):groups(windows,t)for t in [1,3,6]},
    interpretation='400ms windows overlap; their0.5–0.7s union is not continuous gain reduction.20ms timestamp-active energy comparison below is a different,quantized measurement; not a phoneme or subjective listening proof.'))
 result=dict(revision='orientation-matrix-v8',inputs=dict(measuredLevelReviewSha256=c.sha(report_file),mixReportSha256=c.sha(mixfile),sourceAlignmentSha256=c.sha(c.O/'source-alignment.json'),implementationSha256=c.sha(Path(__file__))),
  regionCount=len(rows),regions=rows,actualCurrentStemsAndEncodedAac=True,sourceChanged=False,sourceSpeed=1,humanListening='pending',finalMasterPacketBinding='pending')
 c.save(c.O/'measured-mix-focus-review.json',result);print(json.dumps([dict(scene=r['scene'],span=r['candidate400msOverlapSpan'],thresholds=r['reductionByThreshold'])for r in rows],ensure_ascii=False))
if __name__=='__main__':main()
