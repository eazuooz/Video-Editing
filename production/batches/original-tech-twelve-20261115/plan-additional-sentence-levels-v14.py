"""CPU-only conservative utterance matching for explicit remaining exact12 inputs."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,statistics,wave
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');RUN=MEDIA/'production-resume-20261115T055255Z'
SLUGS=['shorts-control-destruction-pipeline','shorts-returnal-particle-tentacles','shorts-ratchet-dimension-streaming','shorts-doom-push-forward-healing','shorts-botw-chemistry-rules']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',choices=SLUGS,required=True);p.add_argument('--target-body-dbfs',type=int,choices=[-22,-23,-24],default=-22);p.add_argument('--record-candidate',action='store_true');a=p.parse_args();slug=a.project;vp=MEDIA/slug/'voice-repair-v6/voice-generation-complete-proof.json';v=read(vp);rp=Path(read(MEDIA/slug/'asr-repair-v6/status.json')['review']['path']);r=read(rp);lp=rp.parent/'levels.json';levels=read(lp);primitive=ROOT/'production/batches/architectural-111-20261106/first-level-continuity-review.py';q=load('unchanged_additional_level_math',primitive);n=load('current_source_spelling',HERE/'review-corrected-voice-captions-v13.py');assert levels['levelPrimitive']==pin(primitive)and levels['policy']==q.POLICY and levels['asrReview']==pin(rp)
 unit_flags=[x for x in levels['flags']if x['taskKey'].startswith('unit-')];assert not unit_flags,'A constant scalar cannot repair an internal utterance hold'
 with wave.open(v['canonical']['path'],'rb')as w:assert(w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,24000);whole=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float32)/32768
 master=whole.copy();entries=read(v['unitTiming']['path'])['entries'];gains=[];errors=[];flags=[]
 for raw,e,u in zip(v['rawChunks'],entries,v['identity']['unitGroups']):
  assert pin(raw['path'])['sha256']==raw['sha256'];row=next(x for x in levels['paragraphs']if x['key']=='unit-'+u['id']);body=row['trend']['medianBodyDbfs'];peak=row['wholeTake']['samplePeakDbfs'];db=min(a.target_body_dbfs-body,-1-peak);assert abs(db)<=12;lo=round(e['start']*24000);samples=whole[lo:lo+raw['frames']];adjusted=samples*10**(db/20);master[lo:lo+len(samples)]=adjusted;words=[]
  for w in row['words']:
   x,y=q.sample_window(w['startSeconds'],w['endSeconds'],24000);words.append(dict(w,levels=dict(raw=q.levels(adjusted[x:y],24000))))
  trend=q.trend(words,'raw');errors.append(dict(key=row['key'],lateDeltaError=trend['lateMinusEarlyDb']-row['trend']['lateMinusEarlyDb'],projectedDeltaError=trend['projectedChangeDb']-row['trend']['projectedChangeDb']));shortfall=max(0,a.target_body_dbfs-(body+db));gains.append(dict(unit=u['id'],rawWordBodyMedianDbfs=body,constantGainDb=db,masterWordBodyMedianDbfs=body+db,rawSamplePeakDbfs=peak,masterSamplePeakDbfs=peak+db,targetShortfallDb=shortfall))
  if shortfall>-q.POLICY['normalizationTargetShortfallWarningDb']:flags.append(dict(kind='target-shortfall',unit=u['id'],shortfallDb=shortfall))
 paragraphs=[];content=[]
 for rec in r['results']:
  t=rec['task']
  if t['kind']!='paragraph':continue
  data=master[t['startSample']:t['endSample']];words=[]
  for w in rec['rawRecognition']['chunks']:
   x,y=w['timestamp'];assert x is not None and y is not None and 0<=x<y<=len(data)/24000;lo,hi=q.sample_window(x,y,24000);words.append(dict(text=w['text'],startSeconds=x,endSeconds=y,durationSeconds=y-x,levels=dict(raw=q.levels(data[lo:hi],24000))))
  trend=q.trend(words,'raw');paragraphs.append(dict(key=t['key'],trend=trend,wholeTake=q.levels(data,24000)));literal=n.norm(t['expected'],slug,t['paragraph'])==n.norm(rec['rawRecognition']['text'],slug,t['paragraph']);content.append(dict(paragraph=t['paragraph'],literal=literal,expected=t['expected'],recognized=rec['rawRecognition']['text']))
  if trend['suspect']:flags.append(dict(kind='sustained-word-body-decline',taskKey=t['key']))
  if not literal:flags.append(dict(kind='content-review-required',taskKey=t['key']))
 center=statistics.median(x['wholeTake']['bodyDbfs']for x in paragraphs)
 for x in paragraphs:
  if x['wholeTake']['bodyDbfs']-center<=q.POLICY['paragraphBelowMedianWarningDb']:flags.append(dict(kind='paragraph-below-median',taskKey=x['key']))
 result=dict(slug=slug,rawVoiceProof=pin(vp),sourceAsr=pin(rp),rawLevels=pin(lp),rawUnitFlags=[],rawParagraphFlags=[x['taskKey']for x in levels['flags']],proposedTargetWordBodyDbfs=a.target_body_dbfs,proposedPeakCeilingDbfs=-1,gains=gains,paragraphs=paragraphs,masterFlags=flags,withinUnitTrendDeltaErrors=errors,fullParagraphContent=content,rawInputsModified=False,actualMasterWritten=False,voiceAccepted=False)
 print(json.dumps(dict(project=slug,target=a.target_body_dbfs,flags=flags,maximumShortfallDb=max(x['targetShortfallDb']for x in gains)),ensure_ascii=False))
 if a.record_candidate:
  assert not flags,'Keep hold; do not write an adoptable candidate';out=RUN/('complete-sentence-level-match-candidate-v14-'+slug+'.json');assert not out.exists();out.write_text(json.dumps(dict(scope='Only explicit new exact12 lessons; architectural111 excluded',method='One constant scalar per complete utterance. No within-utterance envelope, compression, trim, fade or speed change.',planner=pin(__file__),results=[result]),ensure_ascii=False,indent=2)+'\n','utf8')
if __name__=='__main__':main()
