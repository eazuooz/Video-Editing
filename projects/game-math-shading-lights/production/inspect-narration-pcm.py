"""Measure the untouched full voice and joins; never claim listening from numbers."""
from pathlib import Path
import hashlib,json
import numpy as np
import soundfile as sf
P=Path(__file__).resolve().parents[1];A=P/'production/local/audio-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
voice=A/'narration.wav';x,sr=sf.read(voice,dtype='float32');info=sf.info(voice)
timing=read(A/'narration.timing.json');assert x.ndim==1 and info.subtype=='FLOAT'
frame=round(.05*sr);rows=[];flags=[]
for e in timing['entries']:
    y=x[round(e['start']*sr):round(e['end']*sr)];size=len(y)//frame
    rms=np.sqrt(np.mean(y[:size*frame].reshape(size,frame).astype('float64')**2,axis=1))
    db=20*np.log10(np.maximum(rms,1e-12));gate=max(-55,float(np.max(db))-25);active=db>gate
    median=float(np.median(db[active]));peak=float(np.max(np.abs(y)))
    silent=[];start=None
    for k,on in enumerate(active):
        if not on and start is None:start=k
        if on and start is not None:
            if start>0 and (k-start)*.05>1.5:silent.append({'localStart':start*.05,'duration':(k-start)*.05})
            start=None
    row={'scene':e['scene_id'],'seconds':len(y)/sr,'activeMedianDbfs':median,'activeP10Dbfs':float(np.percentile(db[active],10)),'activeP90Dbfs':float(np.percentile(db[active],90)),'samplePeak':peak,'samplePeakDbfs':20*np.log10(max(peak,1e-12)),'internalSilenceOver1_5s':silent}
    if silent:flags.append({'scene':e['scene_id'],'type':'long-internal-pause','ranges':silent})
    rows.append(row)
joins=[]
for a,b,e,f in zip(rows,rows[1:],timing['entries'],timing['entries'][1:]):
    delta=b['activeMedianDbfs']-a['activeMedianDbfs'];gap=f['start']-e['end']
    joins.append({'from':a['scene'],'to':b['scene'],'activeMedianDeltaDb':delta,'gapSeconds':gap})
    if abs(delta)>4:flags.append({'scene':b['scene'],'type':'paragraph-level-jump','deltaDb':delta})
    if gap>1.5:flags.append({'scene':b['scene'],'type':'long-join','gapSeconds':gap})
out={'scope':'Entire original M21 mono floating-point PCM, 79 paragraphs and 78 joins; numeric review only','sourceSha256':hashlib.sha256(voice.read_bytes()).hexdigest(),'sampleRate':sr,'subtype':info.subtype,'duration':len(x)/sr,'originalPcmChanged':False,'sourceFloatAbove1IsNotIntegerClipping':True,'aboveUnitSamples':int(np.sum(np.abs(x)>1)),'requireFinalEncodedTruePeakCheck':True,'paragraphs':rows,'joins':joins,'flags':flags,'listeningPerformed':False}
(A/'review/pcm-quality.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'paragraphs':len(rows),'joins':len(joins),'flags':flags,'activeMedianRange':[min(r['activeMedianDbfs'] for r in rows),max(r['activeMedianDbfs'] for r in rows)],'sourceFloatPeak':float(np.max(np.abs(x))),'listeningPerformed':False}))
