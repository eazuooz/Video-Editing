"""Match only new whole utterances to retained speech, with raw trend holds intact.

No within-utterance envelope, compression, fade, trim or speed change is used.
Unchanged previously accepted utterances keep their exact original WAV/PCM.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,statistics,wave
import numpy as np
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def pcm(p):
 with wave.open(str(p),'rb')as w:
  assert(w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getcomptype())==(1,2,24000,'NONE');return w.readframes(w.getnframes())
def wav(p,data):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
 with wave.open(str(p),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(data)
 return dict(**pin(p),frames=len(data)//2,rate=24000,duration=len(data)/48000,pcmSHA256=hashlib.sha256(data).hexdigest())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--source-version',choices=['84'],required=True);a=ap.parse_args();assert a.project=='shorts-mariokart8-spin-boost';p=ROOT/'projects'/a.project;ver=a.source_version
 npth=p/f'planning/narration-repair-v{ver}.json';n=read(npth);vp=M/p.name/f'voice-repair-v{ver}/voice-generation-complete-proof.json';v=read(vp);rp=Path(read(M/p.name/f'asr-repair-v{ver}/status.json')['review']['path']);levels=read(rp.parent/'levels.json')
 intrinsic=[x for x in levels['flags']if x['kind']=='sustained-word-body-decline'and x['taskKey'].startswith('unit-')];assert not intrinsic,('Raw internal decline cannot be fixed with a gain',intrinsic)
 base=M/p.name/'voice-master-v115';assert not(base/'voice-generation-complete-proof.json').exists()
 oldsel=read(next(p/'production'/x for x in ['accepted-voice-selection-v27.json','accepted-voice-selection-v10.json']if(p/'production'/x).exists()));oldn=read(oldsel['narration']['path']);oldv=read(oldsel['voice']['path'])
 qpath=ROOT/'production/batches/architectural-111-20261106/first-level-continuity-review.py';s=importlib.util.spec_from_file_location('unchanged_whole_utterance_levels',qpath);q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
 original={u['id']:(u,r)for u,r in zip(oldn['units'],oldv['rawChunks'])};targets={}
 for para in n['paragraphs']:
  targets[para['id']]=statistics.median(q.levels(np.frombuffer(pcm(r['path']),dtype='<i2').astype(np.float32)/32768,24000)['bodyDbfs']for u,r in zip(oldn['units'],oldv['rawChunks'])if u['paragraph']==para['id'])
 word_rows={r['key'][5:]:r for r in levels['paragraphs']if r['kind']=='unit'}
 word_target=statistics.median(w['levels']['raw']['bodyDbfs']for u in n['units']if u['paragraph']=='p002'and u['id']in original for w in word_rows[u['id']]['words'])
 raw=[];units=[];processing=[]
 for u,r in zip(n['units'],v['rawChunks']):
  assert pin(r['path'])['sha256']==r['sha256'];data=pcm(r['path']);assert hashlib.sha256(data).hexdigest()==r['pcmSHA256'];x=np.frombuffer(data,dtype='<i2').astype(np.float64)/32768
  same=u['id']in original and original[u['id']][0]['ko']==u['ko']and original[u['id']][1]['pcmSHA256']==r['pcmSHA256']
  if same:actual=r;gain=1.;db=0.;target=None
  else:
   source_level=q.levels(x.astype(np.float32),24000)['bodyDbfs'];target=targets[u['paragraph']]
   if u['paragraph']=='p002':
    source_level=statistics.median(w['levels']['raw']['bodyDbfs']for w in word_rows[u['id']]['words']);target=word_target
   wanted=10**((target-source_level)/20);peak=float(np.max(np.abs(x)));gain=min(wanted,.97/max(peak,1e-12));db=20*np.log10(gain)
   data=np.rint(x*gain*32768).astype('<i2').tobytes();actual=wav(base/'chunks'/(u['id']+'.wav'),data)
  raw.append(actual);units.append(dict(u,sourceRaw=actual));processing.append(dict(unit=u['id'],paragraph=u['paragraph'],sourceRaw=r,master=actual,oldApprovedPcmByteExact=same,constantGain=gain,gainDb=db,targetBodyDbfs=target,internalEnvelopeChanged=False,rawUnitTrendPassed=True))
 parts=[];entries=[];position=0;gap=round(v['identity']['unitGapSeconds']*24000)
 for i,(u,r)in enumerate(zip(units,raw)):
  data=pcm(r['path']);parts.append(data);entries.append(dict(index=i+1,scene_id=u['id'],text=u['ko'],start=position/24000,end=(position+r['frames'])/24000));position+=r['frames']
  if i+1<len(units):parts.append(bytes(gap*2));position+=gap
 canonical=wav(base/'narration-master-v115.wav',b''.join(parts));timing=base/'unit-timing.json';save(timing,dict(sample_rate=24000,duration_seconds=position/24000,entries=entries,assembly='Exact selected PCM plus explicit natural utterance gap'))
 pt=[]
 for para in n['paragraphs']:
  es=[e for e,u in zip(entries,units)if u['paragraph']==para['id']];pt.append(dict(id=para['id'],text=para['ko'],start=es[0]['start'],end=es[-1]['end'],startSample=round(es[0]['start']*24000),endSample=round(es[-1]['end']*24000)))
 ptime=base/'paragraph-timing.json';save(ptime,dict(sampleRate=24000,entries=pt,sourceUnitTiming=pin(timing),rawBytesPreservedForOldApprovedUnits=True))
 gainproof=base/'whole-utterance-gain-proof.json';save(gainproof,dict(sourceVoice=pin(vp),sourceAsr=pin(rp),sourceLevels=pin(rp.parent/'levels.json'),levelPrimitive=pin(qpath),rawInternalDeclineHolds=intrinsic,originalParagraphHoldsPreserved=levels['flags'],paragraphTargets=targets,heldParagraphWordBodyTarget=dict(paragraph='p002',valueDbfs=word_target,metric='median of independently recognized word-body levels in retained approved utterances; only new whole utterance gains change'),units=processing,withinUtteranceDsp=False,oldApprovedUnitsByteExact=True,newRawWavsPreserved=True,actualListening=False,humanApproval=False))
 master_n=copy.deepcopy(n);master_n.update(origin=pin(npth),units=units,newUnits=[],reuseUnits=units,sourceVoice=pin(vp),sourceAsr=pin(rp),sourceLevels=pin(rp.parent/'levels.json'),sourceWholeUtteranceGain=pin(gainproof),voiceAcceptedForFilm=False)
 mpth=p/'planning/narration-master-v115.json';save(mpth,master_n);caps=read(p/f'planning/caption-clauses-repair-v{ver}.json');caps['source']=pin(mpth);save(p/'planning/caption-clauses-master-v115.json',caps)
 identity=dict(slug=p.name,sourceInputs=[pin(vp),pin(rp),pin(rp.parent/'levels.json'),pin(gainproof),pin(mpth),pin(__file__)],unitGapSeconds=gap/24000,unitGroups=units,paragraphs=n['paragraphs'],noGainSpeedTrimOrCompression=False,processing='One constant gain per newly generated utterance only; original accepted utterances byte-exact; no internal dynamics/speed/trim/fade',sourceModelCompleted=True)
 fingerprint=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest();save(base/'voice-generation-complete-proof.json',dict(fingerprint=fingerprint,identity=identity,rawChunks=raw,canonical=canonical,unitTiming=pin(timing),paragraphTiming=pin(ptime),modelCompleted=True,sourceModelProof=pin(vp),wholeUtteranceGainProof=pin(gainproof),voiceAcceptedForFilm=False,actualListening=False,humanApproval=False,finalFilmComplete=False))
 print(json.dumps(dict(slug=p.name,duration=canonical['duration'],unchangedApproved=sum(x['oldApprovedPcmByteExact']for x in processing),newMatched=sum(not x['oldApprovedPcmByteExact']for x in processing),newAsrRequired=True)))
if __name__=='__main__':main()
