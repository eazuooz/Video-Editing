"""New exact12 only: constant whole-utterance matching; raw sources stay intact."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,wave
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
SLUGS=['shorts-horizon-gpu-placement','shorts-spiderman-swing-anchor']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def pcm(p):
 with wave.open(str(p),'rb')as w:
  assert(w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,24000)
  return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').copy()
def wav(p,a):
 if p.exists():
  assert np.array_equal(pcm(p),a),'Preserve differing partial master'
  return dict(**pin(p),frames=len(a),rate=24000,duration=len(a)/24000,pcmSHA256=hashlib.sha256(a.astype('<i2').tobytes()).hexdigest())
 p.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(p),'wb')as w:w.setparams((1,2,24000,0,'NONE','not compressed'));w.writeframes(a.astype('<i2').tobytes())
 return dict(**pin(p),frames=len(a),rate=24000,duration=len(a)/24000,pcmSHA256=hashlib.sha256(a.astype('<i2').tobytes()).hexdigest())
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',choices=SLUGS,required=True);a=p.parse_args();slug=a.project
 candidate_path=MEDIA/'production-resume-20261115T055255Z/complete-sentence-level-match-candidate-v1.json';c=next(x for x in read(candidate_path)['results']if x['slug']==slug)
 assert not c['rawUnitFlags']and not c['masterFlags'];assert max(abs(x[k])for x in c['withinUnitTrendDeltaErrors']for k in ['lateDeltaError','projectedDeltaError']if x[k]is not None)<1e-5
 for k in ['rawVoiceProof','sourceAsr','rawLevels']:assert pin(c[k]['path'])==c[k]
 old=read(c['rawVoiceProof']['path']);qpath=ROOT/'production/batches/architectural-111-20261106/first-level-continuity-review.py';s=importlib.util.spec_from_file_location('unchanged_master_level_math',qpath);q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
 assert not any(x['taskKey'].startswith('unit-')for x in read(c['rawLevels']['path'])['flags'])
 out=MEDIA/slug/'voice-master-v8';dest=ROOT/'shared/output/original-tech-twelve-20261115'/slug/'voice-master-v8';assert not out.exists()
 oldcanon=pcm(old['canonical']['path']);newcanon=oldcanon.copy();timing=read(old['unitTiming']['path'])['entries'];rows=[];chunks=[];prepared_chunks=[];levels=read(c['rawLevels']['path']);after_units=[]
 for raw,e,u,g in zip(old['rawChunks'],timing,old['identity']['unitGroups'],c['gains']):
  assert u['id']==g['unit']and pin(raw['path'])['sha256']==raw['sha256'];src=pcm(raw['path']);gain=min(10**(g['constantGainDb']/20),np.floor(32768*10**(-1/20))/np.max(np.abs(src.astype(np.float64))));assert abs(20*np.log10(gain))<=12
  adjusted=np.rint(src.astype(np.float64)*gain);assert np.max(np.abs(adjusted))<=np.floor(32768*10**(-1/20));adjusted=adjusted.astype('<i2')
  start=round(e['start']*24000);assert np.array_equal(oldcanon[start:start+len(src)],src);newcanon[start:start+len(src)]=adjusted
  row=next(x for x in levels['paragraphs']if x['key']=='unit-'+u['id']);words=[]
  for w in row['words']:
   x,y=q.sample_window(w['startSeconds'],w['endSeconds'],24000);words.append(dict(w,levels=dict(raw=q.levels(adjusted[x:min(y,len(adjusted))].astype(np.float32)/32768,24000))))
  trend=q.trend(words,'raw');assert not trend['suspect'];before=row['trend']
  for key in ['lateMinusEarlyDb','projectedChangeDb']:
   if trend.get(key)is not None and before.get(key)is not None:assert abs(trend[key]-before[key])<.05,'Internal dynamics changed beyond rounding tolerance'
  residual=float(np.max(np.abs(adjusted.astype(np.float64)-src.astype(np.float64)*gain)));assert residual<=.500001
  prepared_chunks.append((dest/'chunks'/(u['id']+'.wav'),adjusted));rows.append(dict(unit=u['id'],original=raw,constantGainDb=float(20*np.log10(gain)),quantizationResidualPcmUnits=residual,rawTrend=before,masterTrend=trend,withinSentenceEnvelopeApplied=False));after_units.append(dict(unit=u['id'],trend=trend))
 # Check complete assembled paragraphs using the same independent word windows.
 paragraphs=[];review=read(c['sourceAsr']['path'])
 for r in review['results']:
  if r['task']['kind']!='paragraph':continue
  t=r['task'];data=newcanon[t['startSample']:t['endSample']].astype(np.float32)/32768;words=[]
  for w in r['rawRecognition']['chunks']:
   x,y=w['timestamp'];assert x is not None and y is not None and 0<=x<y<=len(data)/24000;lo,hi=q.sample_window(x,y,24000);words.append(dict(text=w['text'],startSeconds=x,endSeconds=y,durationSeconds=y-x,levels=dict(raw=q.levels(data[lo:min(hi,len(data))],24000))))
  trend=q.trend(words,'raw');assert not trend['suspect'];paragraphs.append(dict(paragraph=t['paragraph'],trend=trend))
 chunks=[wav(path,array)for path,array in prepared_chunks];canonical=wav(dest/'whole-sentence-master.wav',newcanon);proof=copy.deepcopy(old);identity=copy.deepcopy(old['identity']);identity.update(sourceInputs=[c['rawVoiceProof'],c['sourceAsr'],c['rawLevels'],pin(candidate_path),pin(qpath),pin(__file__)],newEngineUnits=[],engineSpoken=[],noGainSpeedTrimOrCompression=False,processing='One constant scalar per complete natural utterance; no within-utterance envelope, compression, trim, fade or speed change',rawVoiceSource=c['rawVoiceProof'],levelTargetDbfs=-22,peakCeilingDbfs=-1)
 proof.update(identity=identity,fingerprint=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest(),rawChunks=chunks,canonical=canonical,peakAllocatedMiB=0,peakReservedMiB=0,modelCompleted=True,voiceAcceptedForFilm=False,blindAsrReviewed=False,wholeWordBoundariesReviewed=False,levelTrendReviewed=False,masterCreatedWithoutModel=True)
 save(out/'voice-generation-complete-proof.json',proof);save(out/'constant-gain-proof.json',dict(sourceVoice=c['rawVoiceProof'],masterVoice=pin(out/'voice-generation-complete-proof.json'),sourceUnitsUnmodified=True,frameCountUnchanged=len(newcanon)==len(oldcanon),policy=q.POLICY,units=rows,paragraphs=paragraphs,rawUnitHolds=[],masterFlags=[],independentNewMasterAsrRequired=True,scope='Only these two new exact12 lessons. Never architectural111 or a raw unit with an internal hold.',actualListening=False,humanApproval=False));print(json.dumps(dict(project=slug,master=pin(out/'voice-generation-complete-proof.json'),independentAsrRequired=True)))
if __name__=='__main__':main()
